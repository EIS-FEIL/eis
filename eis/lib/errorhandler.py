import traceback
import sys
import os
import html
import types
from datetime import date, datetime, timedelta
import logging
import eiscore.const as const
import eiscore.i18n as i18n
import eis
from eis.lib.exceptions import NotAuthorizedException, ProcessCanceled, HTTPFound, APIIntegrationError, real_uri
import eis.model as model
from eis.lib.mailer import Mailer

_ = i18n._
log = logging.getLogger(__name__)

class ErrorHandler:
    "Vearaporti koostamine"

    def _error(self, e, msg='', rollback=True):
        """Ootamatust veast toibumine.
        Kui viga leitakse tegevuse käigus, siis saab selle funktsiooniga vea logida.
        Kui viga kinni ei püüta, siis rakendub handlers.error ja logib vea ikkagi selle funktsiooniga.
        """
        if rollback:
            model.Session.rollback()
            if self.c.user:
                self.c.user.leave_session()

        api_msg = ''
        if isinstance(e, APIIntegrationError):
            # vajalik info on juba olemas
            api_msg = e.message
            if e.try_cnt is not None:
                api_msg += f' #{e.try_cnt}'
            if e.inp_data:
                api_msg += '\n\n' + str(e.inp_data)
            # eristav joon vahele
            api_msg += '\n\n' + ('-' * 50) + '\n\n'
            
        # leitakse muutujad
        e_msg, variables = self._error_traceback(e)

        txt = msg + ' ' + api_msg + e_msg
        subject = msg or txt and txt.splitlines()[0][:60] or ''
            
        try:
            log.error(txt)
        except:
            pass

        tyyp = const.LOG_ERROR
        param = self._pretty_params(self._get_log_params()).replace('\n','<br/>\n')
        logi_id = self._error_log(txt, param, tyyp)

        # kontrollime, kas sama sisuga veateade on hiljuti juba saadetud
        str_e = str(e) + msg
        now = datetime.now()
        try:
            need_mail = self._prev_error != str_e or self._prev_error_time < now - timedelta(minutes=3)
        except:
            # esimene viga
            need_mail = True
        if need_mail:
            self._prev_error = str_e
            self._prev_error_time = now
            # kiri saadetakse meiliga administraatorile
            self._error_mail(txt, param=param, info=variables, logi_id=logi_id, msg=subject)

        msg = msg + ' (logi #%s)' % (logi_id)
        return msg

    def _error_traceback(self, ex):
        # logime lokaalsed muutujad
        stack = []
        tb = sys.exc_info()[2]
        while tb:
            stack.append(tb.tb_frame)
            tb = tb.tb_next

        traceback_format_exc = traceback.format_exc()
        
        variables = ''
        for frame in stack:
            variables +=  "<br/><b>Frame %s in %s at line %s</b><br/>" % \
                (frame.f_code.co_name,
                 frame.f_code.co_filename,
                 frame.f_lineno)
            for key, value in list(frame.f_locals.items()):
                variables += " %s = " % key
                if key in ('settings','password','parool'):
                    # ei taha logida andmebaasi parooli
                    continue
                try:                   
                    if isinstance(value, types.FunctionType):
                        continue
                    elif isinstance(value, (float, (int, int))):
                        value = str(value)
                    elif isinstance(value, (dict, list, tuple, set)):
                        value = str(value)
                    elif value is None:
                        value = 'None'
                    elif isinstance(value, model.EntityHelper):
                        value = str(value)
                    elif isinstance(value, (datetime, date)):
                        value = str(value)
                    elif not isinstance(value, str):
                        value = '%s' % type(value)
                    value = html.escape(value)
                    maxlen = 2000
                    if len(value) < maxlen:
                        variables += value
                    else:
                        variables += value[:maxlen] + '...'
                except Exception as ex2:
                    variables += '<ERROR> %s' % ex2
                variables += '<br/>\n'

        try:
            e_msg = repr(ex)
        except:
            try:
                e_msg = ex.__repr__()
            except:
                e_msg = ex.__class__.__name__

        try:
            e_msg += '\n' + traceback_format_exc
        except:
            pass

        return e_msg, variables
    
    def _compose_error_text(self, txt, param, info, logi_id):
        "Veateate kirja koostamine"
        request = self.request
        # veakontrolleris olles saame algse handleri nii: request.handler
        try:
            c = request.handler.c
        except:
            c = self.c
        environ = request.environ
        remote_addr = request.remote_addr

        body = '<h2>Veateade</h2>\n'
        body += '<b>Kasutaja:</b> %s %s (%s)<br/>' % \
            (c.user and c.user.isikukood or '',
             c.user and c.user.fullname or '', 
             remote_addr)
        koht_nimi = c.user and c.user.koht_nimi
        if koht_nimi:
            if c.user.on_kohteelvaade:
                koht_nimi += ' (eelvaade)'
            body += '<b>Koht:</b> %s<br/>' % (koht_nimi)
        body += '<b>Rakendus:</b> %s (EIS v%s)<br/>' % (c.app_name, eis.__version__)

        url = request.url
        body += '<b>URL:</b> %s %s<br/>' % (request.method, url)
        try:
            r_url = real_uri(request)
        except Exception:
            pass
        else:
            if r_url != url:
                body += '<b>URL brauseris:</b> %s %s<br/>' % (request.method, r_url)
                
        body += '<b>Suunanud:</b> %s<br/>' % (environ.get('HTTP_REFERER'))
        body += '<b>Aeg:</b> %s<br/>' % (datetime.now())
        if logi_id:
            body += '<b>Logi id:</b> %s<br/>' % logi_id
        try:
            body += '<b>Päring:</b> %s<br/>' % request.__hash__()
        except Exception:
            pass
        body += '<b>Server:</b> %s<br/>' % (environ.get('HOSTNAME') or os.getenv('HOSTNAME') or '')
        body += '<b>Brauser:</b> %s<br/>' % (environ.get('HTTP_USER_AGENT'))
        body += '<b>Kontroller:</b> %s %s<br/>' % (c.controller, c.action)        
        if param:
            body += '<b>Parameetrid:</b><br/> %s<br/>' % param
        body += '<b>Viga:</b><br/>\n'
        body += html.escape(txt).replace('\n','<br/>') + '\n'
        if info:
            body += info
        return body
   
    def _error_mail(self, txt, param='', info='', logi_id=None, msg=None, composed=False):
        "Saadame vea kohta adminile kirja"
        c = self.c
        user_id = c.user and c.user.id
        if c.app_eis:
            if user_id and user_id > 90000000 or \
                   not user_id and 'osad/T' in self.request.url:
                # koormustesti vigu ei taha
                return
            if c.inst_name == 'prelive' and (not user_id or self.request.method == 'HEAD'):
                # koormustesti vigu ei taha (vbl sisselogimine ei õnnestu)
                return
            if c.action == 'check':
                # monitooringu vigu ei taha
                return
        if self.request.registry.settings.get('smtp.error_to'):
            try:
                if composed:
                    # kirja sisu on juba kokku pandud
                    body = txt
                else:
                    # paneme kirja sisu kokku
                    body = self._compose_error_text(txt, param, info, logi_id)

                subject = 'Veateade'
                if logi_id:
                    subject += ' %s' % (logi_id)
                if user_id:
                    subject += ' (%s)' % user_id
                if msg:
                    subject += ': ' + msg[:50].replace('\n',' ')
                Mailer(self).error(subject, body)
            except Exception as ex:
                log.error('Ei saa saata e-posti. %s' % ex)

    def _error_log(self, txt, param='', tyyp=const.LOG_ERROR):
        # logime vea andmebaasis logitabelis
        logi_id = self.log_add(tyyp, txt, param)
        return logi_id

    def _pretty_params(self, params):
        """
        Parameetrid väljastatakse hästiloetaval kujul (logi jaoks).
        
        params
        list [(key, value)]
        """
        if not params:
            return ''
        buf = ''
        if not isinstance(params, list):
            params = list(params.items())
        try:
            for (name, value) in params:
                buf = buf + "%s: %s\n" % (name, value)
        except UnicodeDecodeError:
            buf += '(UnicodeDecodeError)'
        return buf

