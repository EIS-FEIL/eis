import base64
import smtplib
import socket
import re
import mimetypes
from email import encoders
from email.utils import formatdate, formataddr, make_msgid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.audio import MIMEAudio
import logging
log = logging.getLogger(__name__)

import eiscore.i18n as i18n
_ = i18n._

class AddressNotPermitted(Exception):
    "Püütakse saata kiri aadressile, kuhu on parem mitte saata"
    def __init__(self, msg):
        self.message = msg
    
class ProxySMTP(smtplib.SMTP):
    """Connects to a SMTP server through a HTTP proxy."""

    def __init__(self, host='', port=0, p_address='',p_port=0, local_hostname=None,
             timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        """Initialize a new instance.

        If specified, `host' is the name of the remote host to which to
        connect.  If specified, `port' specifies the port to which to connect.
        By default, smtplib.SMTP_PORT is used.  An SMTPConnectError is raised
        if the specified `host' doesn't respond correctly.  If specified,
        `local_hostname` is used as the FQDN of the local host.  By default,
        the local hostname is found using socket.getfqdn().

        """
        self.p_address = p_address
        self.p_port = p_port
        smtplib.SMTP.__init__(self, host=host, port=port, timeout=timeout)

    def _get_socket(self, host, port, timeout):
        # This makes it simpler for SMTP to use the SMTP connect code
        # and just alter the socket connection bit.
        new_socket = socket.create_connection((self.p_address,self.p_port), timeout)

        s = "CONNECT %s:%s HTTP/1.1\r\n\r\n" % (host,port)
        new_socket.sendall(s.encode('ascii'))
        for x in range(2): 
            line = recvline(new_socket)
        return new_socket

def recvline(sock):
    """Receives a line."""
    stop = 0
    line = b''
    while True:
        i = sock.recv(1)
        if i == b'\n': stop = 1
        line += i
        if stop == 1:
            break
    return line

class Mailer(object):
    "Kirjade saatmine"
    
    def __init__(self, handler):
        self.handler = handler
        self.request = handler.request
        self.settings = handler.request.registry.settings
        
    def send(self, to, subject, body, attachments=[], out_err=True):
        """Teate saatmine koos veast teavitamisega
        Vea korral tagastab veateate!
        """
        err = None
        try:
            self.send_ex(to, subject, body, attachments)
        except smtplib.SMTPRecipientsRefused as e:
            err = _("Vigane aadress") + f' ({to})'
        except AddressNotPermitted as e:
            # pre-live: kirja ei saada
            #err = _("Keskkond ei saada kirju aadressile {s}").format(s=to)
            return
        except Exception as e:
            msg = _("Ei saa kirja saata") + f' ({to})'
            err = self.handler._error(e, msg, rollback=False)

        if err and out_err:
            self.handler.error(err)
        return err
    
    def send_ex(self, to, subject, body, attachments=[], replyto=None):
        """Teate saatmine EISi kasutajalt, vea korral viskab erindi
        """
        fromAddress = self.settings.get('smtp.from')
        self.send_html(fromAddress, to, subject, body, attachments, replyto=replyto)

    def send_ettepanek(self, saatja, epost, subject, body, attachments=[]):
        """Teate saatmine kasutaja nimega, vea korral viskab erindi
        """
        to = self.settings.get('smtp.tugi') or 'eis@tugi.edu.ee'
        fromAddress = self.settings.get('smtp.from')
        m = re.match(r'.*<(.*)>.*', fromAddress)
        if m:
            fromAddress = m.groups()[0]
        fromAddress = f'{saatja} <{fromAddress}>'
        self.send_html(fromAddress, to, subject, body, attachments, replyto=epost)

    def error(self, subject, body):
        """Veateade administraatorile.
        """
        fromAddress = self.settings.get('smtp.from')
        to = self.settings.get('smtp.error_to')
        self.send_html(fromAddress, to, subject, body)

    @classmethod
    def replace_newline(cls, body):
        return body.replace('\n', '<br/>\n')

    def send_html(self, fromAddress, to, subject, body, attachments=[], replyto=None):
        """
        Sends a HTML e-mail
        """
        self.body = body
        body = '<html><head>\n'+\
             '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">\n'+\
             '</head><body>'+\
             body + \
             '</body></html>'

        self._send(fromAddress, to, subject, body, attachments, 'text/html', replyto=replyto)

    def _send(self,
              fromAddress, 
              to, 
              subject, 
              body, 
              attachments = [],
              contentType = 'text/plain',
              replyto=None):
        """
        fromAddress - one address in standard format.
        to - a list of multiple addresses or one address string.
        subject - UTF-8 encoded subject
        body - UTF-8 encoded message body.
        attachments - list of (filename, file data) tuples.

        SMTP transmission raises errors according to smtplib.SMTP.sendmail().
        Additionally, an Exception is raised if message transmission to any address fails.
        """
        assert fromAddress is not None, 'saatja puudub'
        assert to is not None, 'saaja puudub'
        assert subject is not None, 'teema puudub'
        assert body is not None, 'sisu puudub'
        assert attachments is not None, 'manuste jada puudub'

        # eraldame saatja nime ja eposti aadressi
        m = re.match(r'(.*)<(.*)>.*', fromAddress)
        if m:
            fromName, fromAddress = m.groups()
        else:
            fromName = ''
            
        # Format the To: header.
        toString = ''

        if not isinstance(to, list):
            to = to.split(',')            
        if self.settings.get('inst_name') == 'prelive':
            to2 = [e for e in to if e.endswith('@hm.ee') or e.endswith('@harno.ee')]
            if not to2:
                msg = 'prelive ei saada kirju aadressile {s}'.format(s=','.join(to))
                log.error(msg)
                raise AddressNotPermitted(msg)
            to = to2
        toString = ', '.join(list(set(to)))
            
        msg = MIMEMultipart()
        msg.set_charset('utf-8')
        msg['Subject'] = subject

        # formataddr kodeerib vajadusel nime, jättes aadressi kodeerimata
        msg['From'] = fromName and formataddr((fromName, fromAddress)) or fromAddress
        msg['To'] = toString
        if replyto:
            msg.add_header('Reply-To', replyto)
        msg['Date'] = formatdate(localtime=True)
        msg['Message-ID'] = make_msgid()
        
        part = MIMEText(body, 'html', 'utf-8')
        msg.attach(part)

        self._attach(msg, attachments)

        smtp_server = self.settings['smtp.server']
        smtp_port = self.settings.get('smtp.port') or '25'
        smtp_user = self.settings.get('smtp.user')
        smtp_pass = self.settings.get('smtp.pass')

        proxy_host = self.settings.get('smtp.proxy.host')
        proxy_port = self.settings.get('smtp.proxy.port')
        
        try:
            timeout = 30
            if proxy_host and proxy_port:
                smtp = ProxySMTP(host=smtp_server,
                                 port=int(smtp_port),
                                 p_address=proxy_host,
                                 p_port=int(proxy_port),
                                 timeout=timeout)
                smtp.ehlo()
                smtp.starttls()
                smtp.ehlo()
            elif smtp_port == '465':
                smtp = smtplib.SMTP_SSL(smtp_server, smtp_port, None, None, None, timeout)
            else:
                smtp = smtplib.SMTP(smtp_server, smtp_port, None, timeout)

            if smtp_user and smtp_pass:
                smtp.login(smtp_user, smtp_pass)

        except Exception as e:
            log.info('SMTP viga (%s:%s, proxy %s:%s): %s' % (smtp_server, smtp_port, proxy_host, proxy_port, e))
            import traceback
            log.error(traceback.format_exc())
            raise


        buf = 'to: %s (subject: %s)' % (toString, subject)
        result = {}
        try:
            content = msg.as_string().encode('utf-8')
            result = smtp.sendmail(fromAddress, to, content)
            smtp.quit()
            if len(result) != 0:
                raise Exception(result)
            log.info('SENT %s' % buf)
        except Exception as e:
            log.info('FAILED %s: %s' % (buf, e))
            with open('/tmp/tmp.txt','wb') as f:
                f.write(content)
            raise
        
        smtp.close()

    def _attach(self, outer, attachments):
        for (fn, data) in attachments:
            ctype, encoding = mimetypes.guess_type(fn)
            if ctype is None or encoding is not None:
                # No guess could be made, or the file is encoded (compressed), so
                # use a generic bag-of-bits type.
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            if maintype == 'text':
                # Note: we should handle calculating the charset
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                msg = MIMEText(data, _subtype=subtype)

            elif maintype == 'image':
                msg = MIMEImage(data, _subtype=subtype)

            elif maintype == 'audio':
                msg = MIMEAudio(data, _subtype=subtype)

            else:
                msg = MIMEBase(maintype, subtype)
                msg.set_payload(data)

                # Encode the payload using Base64
                encoders.encode_base64(msg)

            # Set the filename parameter
            msg.add_header('Content-Disposition', 'attachment', filename=fn) 
            log.debug('ATTACH %s' % fn)
            outer.attach(msg)

if __name__ == '__main__':
    MyMailer = Mailer
    from eis.scripts.scriptuser import *
    to = noname_args[0]
    if not to:
       print('argumendiks eposti aadress')
    else:
       subject = 'testkiri'
       body = 'Kirja saatmise test'
       ml = MyMailer(handler)
       ml.send_ex(to, subject, body)
    
