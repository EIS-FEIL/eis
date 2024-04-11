"MIME handling"

import base64
from io import BytesIO
import mimetypes
from email import encoders, charset
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email.mime.audio import MIMEAudio
from email import message_from_string
from email import message_from_bytes
from random import Random
import string
import gzip as gzip_

import logging
log = logging.getLogger(__name__)

# override the default handling of utf-8 (which is base64)
# as X-road protocol 4.0 insists using 8bit encoding for SOAP envelope parts
charset.add_charset('utf-8', charset.SHORTEST, '8bit')

class Attachment(object):
    "MIME attachment in X-road SOAP message"
    filename = None
    content_id = None
    data = None
    use_gzip = True

    def __init__(self, data=None, filename=None, content_id=None, use_gzip=True):
        self.data = data
        self.filename = filename
        self.content_id = content_id
        self.use_gzip = use_gzip

    def gen_content_id(self):
        "Generate identificator for an attachment"
        self.content_id = ''.join(Random().sample(string.ascii_letters+string.digits, 32))
        return self.content_id

    def gzip(self):
        "Encode"
        return gzip(self.data)
    
def encode_soap(xml, attachments, embedded_newlines=True, mtom=False):
    """Compose MIME message which contains SOAP envelope and attachments
    """
    if attachments:
        if mtom:
            # MTOM/XOP
            payload = encode_mtom(xml, attachments)
        else:
            # SOAP with attachments
            payload = encode(xml, attachments)
        payload = payload.replace('\n','\r\n')

        # extract HTTP header to be able
        # to use high level Http().request and add Content-Length
        headers, body = _extract_body(payload, embedded_newlines)
        body = body.encode('utf-8')
        headers['Content-Length'] = str(len(body))
        headers['SOAPAction'] = '""'
    else:
        # plain message without attachments, no need for MIME
        body = xml.encode('utf-8')
        headers={
            'Content-Type': 'text/xml; charset="UTF-8"',
            'Content-Length': str(len(body)),
            'SOAPAction': '""'
            }

    payload = ''
    for key in headers:
        payload += '%s: %s\r\n' % (key, headers[key])
    payload = payload.encode('utf-8') + b'\r\n' + body
    return payload, headers, body

def encode(body, attachments):
    """
    Compose MIME message for SOAP with attachments
    """
    msg = MIMEMultipart('related', type="text/xml")
    envelope = MIMEText(body, 'xml', _charset='utf-8')
    envelope.replace_header('Content-Transfer-Encoding', '8bit')
    msg.attach(envelope)
    for attachment in attachments:
        _add_part(msg, attachment)
    return msg.as_string()

def encode_mtom(body, attachments):
    """
    Compose MIME message for MTOM/XOP
    """
    msg = MIMEMultipart('related', type="application/xop+xml", start='<rootpart>', start_info='text/xml')
    envelope = MIMEBase('application', 'xop+xml', charset='utf-8', type='text/xml')
    envelope.set_payload(body)
    envelope['Content-Transfer-Encoding'] = '8bit'
    envelope['Content-ID'] = '<rootpart>'
    msg.attach(envelope)
    for attachment in attachments:
        _add_part(msg, attachment)
    return msg.as_string()

def _add_part(msg, attachment):            
    "Add a new attachment part to the MIME message"

    ctype, encoding = mimetypes.guess_type(attachment.filename or '')
    if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'

    maintype, subtype = ctype.split('/', 1)
    if maintype == 'text':
        part = MIMEText(attachment.data, _subtype=subtype)

    elif maintype == 'image':
        part = MIMEImage(attachment.data, _subtype=subtype)

    elif maintype == 'audio':
        part = MIMEAudio(attachment.data, _subtype=subtype)

    else:
        part = MIMEBase(maintype, subtype)
        data = attachment.data
        if isinstance(data, str):
            data = data.encode('utf-8')
        if attachment.use_gzip:
            part.set_payload(gzip(data))
            part.add_header('Content-Encoding', 'gzip')
        else:           
            part.set_payload(data)
        encoders.encode_base64(part)

    part.set_charset('utf-8')

    if attachment.filename:
        part.add_header('Content-Disposition', 'attachment', filename=attachment.filename)
    if attachment.content_id:
        part.add_header('Content-ID', '<%s>' % attachment.content_id)             

    msg.attach(part)

def decode(response):
    """Parse message (MIME or plain)
    """
    env = None
    attachments = []
    if isinstance(response, str):
        msg = message_from_string(response)
    else:
        msg = message_from_bytes(response)

    if msg.is_multipart():
        for part in msg._payload:
            fn = part.get_filename()
            content_id = part.get('Content-ID')
            data = part.get_payload()
            bdata = None
            ctype = part.get('Content-Type')
            if part.get('Content-Transfer-Encoding') == 'base64':
                bdata = base64.b64decode(data.encode('utf-8'))
            elif ctype.find('base64Binary') > -1:
                # DVK uses Content-Transfer-Encoding="binary"
                # and Content-Type="{http://www.w3.org/2001/XMLSchema}base64Binary"
                # for base64-encoded and gzipped data
                bdata = base64.b64decode(data.encode('utf-8'))

            if bdata and part.get('Content-Encoding') == 'gzip':
                bdata = gunzip(bdata)

            if bdata:
                data = bdata
                #data = bdata.decode('utf-8')

            if not env:
                # assume that first part is SOAP envelope
                env = data
            else:
                # others are attachments
                attachment = Attachment(data, filename=fn, content_id=content_id)
                attachments.append(attachment)
    else:
        # plain message
        env = msg.get_payload(decode=True)
        if not env and response:
            # probably XML declaration is missing
            env = response
        else:
            # remove crap (HTTPS)
            if isinstance(env, bytes):
                env = env.decode('utf-8')                
            n1 = env.find('<?xml')
            n2 = env.rfind('>')
            if n1 > -1 and n2 > -1:
                env = env[n1:n2+1]
                
    return env, attachments

def gzip(data, compresslevel=9):
    """
    Compresses the byte string :var:`data` with gzip using the compression level
    :var:`compresslevel`.
    """
    stream = BytesIO()
    compressor = gzip_.GzipFile(filename="", mode="wb", fileobj=stream, compresslevel=compresslevel)
    compressor.write(data)
    compressor.close()
    return stream.getvalue() 
  
def gunzip(data):
    """
    Uncompresses the byte string :var:`data` with gzip.
    """
    stream = BytesIO(data)
    compressor = gzip_.GzipFile(filename="", mode="rb", fileobj=stream)
    return compressor.read()

def _extract_body(payload, embedded_newlines):
    """
    Extract HTTP headers and body
    """
    headers_str, body = payload.split('\r\n\r\n',1)
    headers = {}
    for line in headers_str.splitlines():
        line = line.rstrip()
        if line.find(':') > -1:
            key, value = line.split(':',1)
            headers[key] = value
        else:
            if embedded_newlines:
                # SOAP input
                headers[key] += '\r\n' + line
            else:
                # SOAP output
                headers[key] += ' ' + line
    return headers, body
