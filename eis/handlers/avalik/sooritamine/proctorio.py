# Proctorio

import requests
import json
import hashlib
import hmac
import uuid
import urllib.parse
import base64
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class ProctorioController(BaseController):

    _get_is_readonly = False
    _log_params_post = True
    _log_params_get = True

    def start(self):
        c = self.c
        if not c.toimumisaeg.on_proctorio or \
               not c.sooritus.saab_alustada() and \
               c.sooritus.staatus not in (const.S_STAATUS_POOLELI, const.S_STAATUS_KATKESTATUD):
            url = self.url('sooritamine_alustamine', test_id=c.test_id, sooritaja_id=c.sooritus.sooritaja_id)
            raise HTTPFound(location=url)
     
        response = Response()
        # uuendame cookieconsenti, kui see on tehtud enne samesite=none secure kasutuselevõttu
        value = self.request.cookies.get('eis-cookieconsent')
        if value:
            li = value.split('-')
            log.debug('li=%s' % li)
            if len(li) == 1:
                value = f'1-{value}-1'
                response.set_cookie('eis-cookieconsent', value=value, max_age=31536000, samesite='none', secure=True)
                rc = True

        # lisame seansi kypsisele samesite=None
        settings = self.request.registry.settings
        session_key = settings.get('session.key')
        value = self.request.cookies.get(session_key)
        response.set_cookie(session_key, value=value, samesite='none', secure=True)

        raise HTTPFound(location=self.url_current('start1'),
                        headers=response.headers)
    
    def start1(self):
        """Küsime Proctoriost URLi ja suuname kasutaja sinna"""
        c = self.c
    
        # if sooritus_id == '0':
        #     # testimine
        #     k = c.user.get_kasutaja()
        #     if not k.has_permission('admin', const.BT_UPDATE):
        #         # ainult admin võib testida
        #         raise NotAuthorizedException('avaleht')

        sooritaja = c.sooritus.sooritaja
        sooritus_id = c.sooritus.id
        staatus = c.sooritus.staatus
        test_id = sooritaja.test_id
        testiosa_id = c.sooritus.testiosa_id

        if c.sooritus.staatus not in (const.S_STAATUS_ALUSTAMATA,
                                      const.S_STAATUS_KATKESTATUD,
                                      const.S_STAATUS_POOLELI) \
                                      and not c.sooritus.saab_alustada():
            self.error(_("Testi ei saa praegu sooritada"))
            url = self.url('sooritamine_alustamine', test_id=test_id, sooritaja_id=sooritaja.id)
            raise HTTPFound(location=url)

        if not c.toimumisaeg.on_proctorio:
            url = self.url('sooritamine_alustamine', test_id=test_id, sooritaja_id=sooritaja.id)
            raise HTTPFound(location=url)            

        take_url = self._get_take_url(test_id, c.sooritus, sooritaja, c.toimumisaeg)
        if not take_url:
            self.error(_("Tehnilistel põhjustel ei saa testi alustada"))
            take_url = self.url('sooritamine_alustamine', test_id=test_id, sooritaja_id=sooritaja.id)
        raise HTTPFound(location=take_url)

    def review(self):
        "Korraldaja vaatab Proctorio andmeid"
        c = self.c
        review_url = self._get_review_url(c.test_id, c.toimumisaeg)
        if not review_url:
            return Response(_("Proctorio seansse ei ole"))
        raise HTTPFound(location=review_url)

    def __before__(self):
        """Väärtustame testimiskorra id
        """
        c = self.c
        c.test_id = self.request.matchdict.get('test_id')
        if c.action == 'review':
            c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
            c.testiruum = model.Testiruum.get(self.request.matchdict.get('testiruum_id'))
            assert c.testiruum.testikoht.toimumisaeg_id == c.toimumisaeg.id, 'vale ruum'
        else:
            sooritus_id = self.convert_id(self.request.matchdict.get('sooritus_id'))
            c.sooritus = model.Sooritus.get(sooritus_id)
            c.testiosa = c.sooritus.testiosa
            c.toimumisaeg = c.sooritus.toimumisaeg
        
    def _has_permission(self):
        c = self.c
        if c.action == 'review':
            return c.user.has_permission('testiadmin', const.BT_VIEW, obj=c.testiruum)
        if c.sooritus and c.toimumisaeg:
            if c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE):
                if c.sooritus.tugiisik_kasutaja_id and c.sooritus.tugiisik_kasutaja_id != c.user.id:
                    # kasutaja pole tugiisik
                    return False
                sooritaja = c.sooritus.sooritaja
                if not c.sooritus.tugiisik_kasutaja_id and sooritaja.kasutaja_id != c.user.id:
                    # kasutaja pole sooritaja
                    return False
                if c.user.testpw_id and c.user.testpw_id != sooritaja.id:
                    # testiparooliga kasutajal on vale test
                    return False
                return True
        return False

    def _get_take_url(self, test_id, sooritus, sooritaja, toimumisaeg):
        rcd = model.Proctoriolog.get_last(toimumisaeg.id, sooritus.id)
        now = datetime.now()
        # take_url kehtib 5 tundi
        if rcd and rcd.created > now - timedelta(seconds=18000):
            url = rcd.take_url
        else:
            url, review_url = self._gen_proctorio_urls(test_id, sooritus, sooritaja, toimumisaeg)
        return url

    def _get_review_url(self, test_id, toimumisaeg):
        rcd = model.Proctoriolog.get_last(toimumisaeg.id, None)
        now = datetime.now()
        # review_url kehtib 1 tund
        if rcd and rcd.created > now - timedelta(seconds=3600):
            # kasutame olemasolevat linki
            url = rcd.review_url
        elif not rcd:
            # keegi pole veel sooritanud
            return
        else:
            # uuendame lingi
            take_url, url = self._gen_proctorio_urls(test_id, None, None, toimumisaeg)
        return url        

    def _gen_proctorio_urls(self, test_id, sooritus, sooritaja, toimumisaeg):

        if sooritus:
            # URLid päritakse testi sooritamiseks
            testiosa_id = sooritus.testiosa_id
            sooritus_id = sooritus.id
            staatus = sooritus.staatus
            sooritaja_id = sooritaja.id
            kasutaja = sooritaja.kasutaja
            user_id = kasutaja.isikukood or kasutaja.id
            fullname = sooritaja.nimi
            url_key = uuid.uuid4().hex
            url_sooritus_id = f'{sooritus_id}-{url_key}'
        else:
            # URLid päritakse ainult review_url saamiseks
            testiosa_id = sooritus_id = sooritaja_id = 0
            url_key = None
            url_sooritus_id = 0
            staatus = 0
            user_id = self.c.user.isikukood
            fullname = None

        settings = self.request.registry.settings
        consumer_key = settings.get('proctorio.key')
        secret = settings.get('proctorio.secret')
        #url = 'https://eu15499ws.proctor.io/6521ca945bd84cfc85d2767da06aa7c8'
        url = settings.get('proctorio.url')

        if not consumer_key or not secret:
            log.error('Proctorio seadistamata')
            return None, None

        if staatus == const.S_STAATUS_POOLELI or staatus == const.S_STAATUS_KATKESTATUD:
            launch_url = self.url('sooritamine_jatka_osa', test_id=test_id, testiosa_id=testiosa_id, id=url_sooritus_id, pw_url=True)
        else:
            launch_url = self.url('sooritamine_alusta_osa', test_id=test_id, testiosa_id=testiosa_id, id=url_sooritus_id, pw_url=True)
        exam_start = launch_url
        exam_end = self.url('sooritamine_alustamine', test_id=test_id, sooritaja_id=sooritaja_id, pw_url=True)

        pw_host = settings.get('eis.pw.url')
        url_prefix = pw_host + '/eis/'
        exam_take = url_prefix + 'sooritamine/%s/%s-?\\d*/s/%s(/.*)?' % (test_id, testiosa_id, url_sooritus_id)
        exam_tag = toimumisaeg.tahised.replace(' ', '_')
        exam_settings = toimumisaeg.verif_param or 'recordvideo'

        ## testimiseks
        #def _format_url(url):
        #    return '.*' + url.replace('https://','').replace('http://','').replace('/','\/')
        #
        #exam_take = _format_url(exam_take)
        #exam_end = _format_url(exam_end)

        ts = int(datetime.now().timestamp())
        nonce = uuid.uuid4().hex        

        params = [('launch_url', launch_url),
                  ('user_id', user_id),
                  ('oauth_consumer_key', consumer_key),
                  ('exam_start', exam_start),
                  ('exam_take', exam_take),
                  ('exam_end', exam_end),
                  ('exam_settings', exam_settings),
                  ]
        if fullname:
            params.append(('fullname', fullname))
        params.extend([
                  ('exam_tag', exam_tag),
                  #('expire_take', 18000),
                  #('expire_review', 3600),
                  ('oauth_signature_method', 'HMAC-SHA1'),
                  ('oauth_version', '1.0'),
                  ('oauth_timestamp', ts),
                  ('oauth_nonce', nonce),
                  ])

        log.info('PARAMS:%s' % params)

        params2 = [(key, urllib.parse.quote(str(value), safe='')) for (key, value) in params]
        param_str = '&'.join([f'{key}={value}' for key, value in params2])
        sig_base_str = 'POST&' + urllib.parse.quote(url, safe='') + '&' + urllib.parse.quote(param_str, safe='')


        hashed = hmac.new(secret.encode('ascii'), sig_base_str.encode('ascii'), hashlib.sha1)
        signature = hashed.digest()
        sig_str = base64.b64encode(signature).decode('ascii')        
        params.append(('oauth_signature', sig_str))

        http_proxy = settings.get('http_proxy')
        kw = {}
        if http_proxy:
            kw['proxies'] = {'https': http_proxy }

        response = take_url = review_url = None
        try:
            resp = requests.request('POST', url, data=params, **kw)
        except Exception as ex:
            log.error(f'proctorio post {url} {ex}')
            self._error(ex, 'Proctorio', False)
        else:
            try:
                response = resp.json()
            except:
                response = resp.text()
                #log.error(f'proctorio text: {response}')
                self._error(None, 'Proctorio text: '+response, False)
            else:
                log.info(response)
                if len(response) == 2:
                    take_url, review_url = response
                else:
                    errors = {2154: 'Account not active',
                              2155: 'Incorrect region',
                              2648: 'Fullname parameter is being sent without and exam_tag',
                              2653: 'Missing required parameters',
                              2654: 'Invalid parameter',
                              2655: 'Incorrect consumer key',
                              2656: 'Signature is invalid',
                              2657: 'The used timestamp is out of range',
                              2658: 'Invalid exam tag ID',
                              2659: 'Invalid settings',
                              2660: 'Invalid timestamp',
                              2851: 'The expire_take value is not an integer',
                              2852: 'The expire_take value is greater than 18000 seconds',
                              2853: 'The expire_review value is not an integer',
                              2854: 'The expire_review value is greater than 3600 seconds',
                              }
                    errcode = response[0]
                    error = errors.get(errcode)
                    if error:
                        buf = f'{errcode}: {error}'
                    else:
                        buf = str(response)
                    #log.error(f'proctorio error ' + buf)
                    self._error(None, 'Proctorio json '+buf, False)

        item = model.Proctoriolog(sooritus_id=sooritus_id,
                                  kasutaja_id=self.c.user.id,
                                  toimumisaeg_id=toimumisaeg.id,
                                  url_key=url_key,
                                  take_url=take_url,
                                  review_url=review_url)
        model.Session.commit()
        return take_url, review_url
