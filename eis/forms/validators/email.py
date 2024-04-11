# -*- coding: utf-8 -*-

from .identifier import *

#import smtplib
import socket
import jellyfish
# vt validate_email.py
import DNS
DNS.DiscoverNameServers()

# tuntud domeenid on saadud päringuga:
# select substr(epost, strpos(epost, '@')), count(*) cnt from kasutaja where epost is not null group by substr(epost, strpos(epost, '@')) having count(*) >= 20 order by cnt desc 
KNOWN_HOSTS = ('gmail.com', 'mail.ru', 'hot.ee', 'hotmail.com', 'mail.ee', 'eesti.ee', 'list.ru', 'bk.ru', 'yandex.ru', 'rambler.ru', 'inbox.ru', 'yahoo.com', 'ut.ee', 'gag.ee', 'live.com', 'outlook.com', 'msn.com', 'real.edu.ee', 'windowslive.com', 'starline.ee', 'online.ee', 'one.ee', 'tdl.ee', 'khk.ee', 'mail.com', 'live.ru', 'tkvg.ee', 'email.ee', 'innove.ee', 'hitsa.ee', 'tpu.ee', 'politsei.ee', 'tptlive.ee', 'ivkh.ee', 'just.ee', 'icloud.com', 'neti.ee', 'ttu.ee', 'tlu.ee', 'ehtehg.ee', 'narva.ee', 'yahoo.co.uk', 'solo.ee', 'ya.ru', 'infonet.ee', 'stv.ee', 'uninet.ee', 'students.nvtc.ee', 'me.com', 'hanza.net', 'kjlv.ee', 'inbox.lv', 'smail.ee', 'estpak.ee', 'gmail.ru', 'eau.ee', 'nvtc.ee', 'rescue.ee', 'web.de', 'energia.ee', 'ida.pol.ee', 'starman.ee', 'yandex.com', 'pohja.pol.ee', 'valgapk.edu.ee', 'tyg.edu.ee', 'math.ut.ee', 'vilgym.edu.ee', 'gmx.de', 'usa.net', 'g.viimsi.edu.ee', 'rvg.edu.ee', 'raad.tartu.ee', 'hotmail.ee', 'elvag.edu.ee', 'km.ru', 'hm.ee', 'ekk.edu.ee', 'mig.ee', 'physic.ut.ee', 'tg.edu.ee', 'maikool.parnu.ee', 'yahoo.de', 'htg.tartu.ee', 'solo.delfi.ee', 'hotmail.co.uk', 'tartu.maavalitsus.ee', 'uno.ee', 'ukr.net', 'laanemere.tln.edu.ee', 'lv.parnu.ee', 'soldino.edu.ee', 'ttc.ee', 'tamme.tartu.ee', 'hotmail.ru', 'harno.ee')

MX_DNS_CACHE = {}
MX_CHECK_CACHE = {}
SMTP_TIMEOUT = 5

class Email(Email):

    ikRE = re.compile(r"^[0-9]+@eesti.ee$")
    badIk = "Please use format firstname.lastname_NNNN@eesti.ee, not IDCODE@eesti.ee"
   
    def _validate_python(self, value, state):
        super(Email, self).validate_python(value, state)

        if value:
            _ = state and state._ or (lambda s: s)
            try:
                value.encode('ascii')
            except UnicodeEncodeError:
                raise Invalid(_("Vigane e-posti aadress"), value, state)
            
            if self.ikRE.search(value):
                raise Invalid(_(self.badIk), value, state)

            user, domain = value.split('@')
            if domain not in KNOWN_HOSTS:
                # kontrollime, kas domeen on registreeritud
                if not self._check_domain(domain, SMTP_TIMEOUT):
                    similar = self._get_similar(user, domain)
                    if similar:
                        err = _("Vale e-posti aadress, kas peaks olema {s}?").format(s=', '.join(similar))
                    else:
                        err = _("Vale e-posti aadress")
                    raise Invalid(err, value, state)                

    def _get_mx_ip(self, hostname):
        if hostname not in MX_DNS_CACHE:
            try:
                MX_DNS_CACHE[hostname] = DNS.mxlookup(hostname)
            except DNS.ServerError as e:
                if e.rcode == 3:  # NXDOMAIN (Non-Existent Domain)
                    MX_DNS_CACHE[hostname] = None
                else:
                    raise
            except DNS.TimeoutError as e:
                log.error('DNS.TimeoutError %s' % hostname)
                return True
        return MX_DNS_CACHE[hostname]
    
    def _check_domain(self, hostname, smtp_timeout):
        try:
            mx_hosts = self._get_mx_ip(hostname)
            #log.debug('get_mx_ip(%s)=%s' % (hostname, mx_hosts))
            if mx_hosts is None:
                return False
            # kehtiva hosti mx_hosts võib olla ka []
        except AssertionError:
            return False
        except (DNS.ServerError, socket.error) as e:
            log.debug('ServerError or socket.error exception raised (%s).', e)
        return True

    def _get_similar(self, user, hostname):
        "Leitakse võimalik õige aadress, kui sisestati vale"
        li = []
        for host in KNOWN_HOSTS:
            if jellyfish.levenshtein_distance(hostname, host) < 2:
                addr = '"%s@%s"' % (user, host)
                li.append(addr)
        return li
    
if __name__ == '__main__':
    import sys
    value = sys.argv[1]
    try:
        Email().to_python(value)
    except Invalid as ex:
        print((ex.msg))
    else:
        print('OK')
