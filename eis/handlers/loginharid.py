"Sisselogimine HarID kaudu"
import urllib.request
import urllib.parse
import uuid
import requests
import base64
import hashlib
import json
import jwt
from pyramid.security import remember
from eis.lib.base import *
_ = i18n._

import logging
log = logging.getLogger(__name__)

# Liidestumisinfo vt https://test.harid.ee/et/pages/dev-info

# HarID identsustõendi väljastaja avalik võti, eelnevalt alla tõmmatud
# wget https://test.harid.ee/jwks.json -O /srv/eis/etc/harid.jwks.json
# wget https://harid.ee/jwks.json -O /srv/eis/etc/harid.jwks.json
FN_JWKS = '/srv/eis/etc/harid.jwks.json'

class LoginharidController(BaseController):
    "HarID kaudu sisselogimise kontroller"
    _authorize = False
    _get_is_readonly = False
    _log_params_get = True
    
    def login(self):
        "Autentimispäringu alustamine"
        request = self.request
        #next = self._get_next()
        request_url = request.params.get('request_url')
        if not request_url or len(request_url) > 200:
            request_url = self.url('avaleht')
        settings = request.registry.settings
        auth_url = settings.get('harid.auth.url')
        secret = settings.get('harid.secret')
        client_id = settings.get('harid.client_id')
        redirect_uri = settings.get('harid.redirect.url')        
        state = uuid.uuid4().hex
        nonce = uuid.uuid4().hex
        state_hash = base64.b64encode(hashlib.sha256(state.encode('ascii')).digest()).decode('ascii')
        log.debug('\nstate=%s\nhash=%s\nnonce=%s' % (state, state_hash, nonce))
        params = urllib.parse.urlencode({'redirect_uri': redirect_uri,
                                         'scope': 'openid profile email personal_code roles custodies',
                                         'state': state_hash,
                                         'response_type': 'code',
                                         'client_id': client_id,
                                         'nonce': nonce})
        url = "%s?%s" % (auth_url, params)

        environ = request.environ
        def _max(value, n):
            return value and value[:n] or None
        remote_addr = request.remote_addr
        server_addr = environ.get('HOSTNAME') or environ.get('SERVER_ADDR')
        
        tl = model_log.Haridlog(nonce=nonce,
                                state=state_hash,
                                aut_aeg=datetime.now(),
                                aut_params=url,
                                request_url=request_url,
                                remote_addr=_max(remote_addr, 36),
                                server1_addr=_max(server_addr, 25))
        model_log.DBSession.add(tl)
        model_log.DBSession.flush()
        log.debug('HarID request %s' % url)
        req = HTTPFound(location=url)
        #req.set_cookie('eis-harid-state', value=state, httponly=True)
        return req
    
    def returned(self):
        "HARIDst autentimiselt tagasitulek"
        user = tl = None
        access_token, tl, err, amr = self._get_token()
        if not err:
            tl, epost, roles, err = self._get_userinfo(access_token, tl)
            if not err:
                #self._update_roles(tl, roles)
                user = User.from_harid(self, tl.isikukood, tl.eesnimi, tl.perenimi, epost, amr)
            
        model_log.DBSession.flush()
        if user:
            headers = remember(self.request, user.isikukood)
            home = tl.request_url or self._home_url()
            return HTTPFound(location=home, headers=headers)
        elif err:
            self.error(err)

        return HTTPFound(location=self._home_url())
        
    def _get_token(self):
        request = self.request
        log.debug('HarID response %s' % request.url)
        state = request.GET.get('state')
        code = request.GET.get('code')
        error = request.GET.get('error')

        tl = (model_log.DBSession.query(model_log.Haridlog)
              .filter(model_log.Haridlog.aut_aeg > datetime.now() - timedelta(hours=1))
              .filter(model_log.Haridlog.state==state)
              .first())
        if not tl:
            err = 'Sisenemine ebaõnnestus (viga 1)'
            tl = model_log.Haridlog(resp_aeg=datetime.now(),
                                    resp_params=request.url,
                                    err=1)
            model_log.DBSession.add(tl)
            return None, tl, err, None

        tl.resp_aeg = datetime.now()
        tl.resp_params = request.url

        environ = request.environ
        def _max(value, n):
            return value and value[:n] or None
        server2_addr = environ.get('HOSTNAME') or environ.get('SERVER_ADDR')
        tl.server2_addr = _max(server2_addr, 25)
        
        if error:
            err = request.GET.get('error_description')
            tl.err = 2
            return None, tl, err, None

        # identsustõendi päring
        settings = request.registry.settings
        client_id = settings.get('harid.client_id')
        token_url = settings.get('harid.token.url')
        redirect_uri = settings.get('harid.redirect.url')        
        data={'grant_type': 'authorization_code',
              'code': code,
              'redirect_uri': redirect_uri}
        auth = requests.auth.HTTPBasicAuth(client_id, settings.get('harid.secret'))
        headers = {'User-Agent': 'EIS'}
        http_proxy = settings.get('http_proxy')
        kw = {}
        if http_proxy:
            kw['proxies'] = {'https': http_proxy }
        r = requests.post(token_url, data=data, auth=auth, headers=headers, **kw)
        res = r.json()
        tl.token_data = json.dumps(res)
        # {'access_token': 'c157416f79723c4...',
        # 'token_type': 'bearer',
        # 'expires_in': 86396,
        # 'id_token': 'eyJ0eXAiOiJKV1QiLCJhbG....'}
        access_token = res['access_token']
        
        log.debug('HarID id response (%s) %s' % (code, str(res)))
        id_token = res.get('id_token')
        if not id_token:
            err = 'Puudub id_token, error=%s' % res.get('error')
            tl.err = 1
            return None, tl, err, None
        
        # 1. allkirja kontrollimine RS256, JWT standard
        with open(FN_JWKS, 'r') as fh:
            di = json.load(fh)
            verifying_key = jwt.jwk_from_dict(di['keys'][0])
        jwtoken = jwt.JWT()
        message = jwtoken.decode(id_token, verifying_key)       
        tl.token_msg = json.dumps(message)
        log.debug('HarID id msg %s' % (message))

        #{'iss': 'https://test.harid.ee',
        #'sub': 'fd08987d-084c-4cb6-80da-60c6140ec409',
        #'aud': '5f27446da60d1b4e466a11b3e9e5267a',
        #'exp': 1583136747,
        #'iat': 1583136447,
        #'nonce': 'af8adae779d24f3fa87ffecf6f5b4014',
        #'amr': '["pop"]'}
                        
        def _text(s, size):
            return s and len(s) > size and s[:size] or s

        amr = None
        _amr = message.get('amr')
        if _amr and isinstance(_amr, str):
            amr = _amr.replace('["','').replace('"]','')

        nonce = message['nonce']
        if nonce != tl.nonce:
            # nonss pole sama, mis oli sisendis
            err = 'Autentimine ebaõnnestus (viga 3)'
            tl.err = 3
            return None, tl, err, amr

        # 2. väljaandja kontrollimine
        if message['iss'] != settings.get('harid.issuer'):
            err = 'Tõendi väljastaja vale: %s' % message['iss']
            tl.err = 5
            return None, tl, err, amr
        
        # 3. adressaadi kontrollimine
        if message['aud'] != client_id:
            err = 'Tõendi saaja vale: %s' % message['aud']
            tl.err = 6
            return None, tl, err, amr
        
        # 4. tõendi ajalise kehtivuse kontrollimine
        now = datetime.utcnow()
        diff = timedelta(minutes=3)
        #nbf = datetime.utcfromtimestamp(message['nbf'])
        exp = datetime.utcfromtimestamp(message['exp'])
        if exp < now - diff:
            err = 'Tõend ei kehti enam: exp %s, now %s' % (exp, now)
            tl.err = 7
            return None, tl, err, amr

        return access_token, tl, None, amr

    def _get_userinfo(self, access_token, tl):
        # userinfo päring
        err = None
        request = self.request
        settings = request.registry.settings
        userinfo_url = settings.get('harid.userinfo.url')        

        headers = {"Authorization": "Bearer %s" % access_token,
                   "User-Agent": "EIS",
                   }
        http_proxy = settings.get('http_proxy')
        kw = {}
        if http_proxy:
            kw['proxies'] = {'https': http_proxy }

        r = requests.get(userinfo_url, headers=headers, **kw)
        #print(r.request.headers)
        #print(r.request.body)
        message = tl.userinfo_msg = r.text
        log.info('HarID userinfo msg\n%s' % (message))
        res = r.json()
        #'roles': [
        #{'marker': 'student', 'active': None, 'start_date': '2020-03-02', 'end_date': None, 'name_et': 'õpilane', 'name_en': 'student', 'name_ru': 'student', 'desc_et': None, 'desc_en': None, 'desc_ru': None, 'provider_ehis_id': None, 'provider_reg_nr': '48395793456', 'provider_name': 'Testasutus', 'created_at': '2020-03-02T09:42:37+02:00', 'updated_at': '2020-03-02T09:42:37+02:00', 'student_grade': None, 'student_parallel': None},
        #{'marker': 'faculty', 'active': None, 'start_date': '2020-03-02', 'end_date': None, 'name_et': 'õpetajaskond', 'name_en': 'Faculty', 'name_ru': 'faculty', 'desc_et': None, 'desc_en': None, 'desc_ru': None, 'provider_ehis_id': None, 'provider_reg_nr': '48395793456', 'provider_name': 'Testasutus', 'created_at': '2020-03-02T09:42:37+02:00', 'updated_at': '2020-03-02T09:42:37+02:00', 'student_grade': None, 'student_parallel': None}],
        #'ui_locales': 'et',
        #'custodies': []}

        def _text(s, size):
            return s and len(s) > size and s[:size] or s

        epost = res.get('email')
        roles = res.get('roles')
        personal_code = res.get('personal_code')
        if not personal_code:
            err = _("EISi sisenemiseks HarID kaudu on vaja eelnevalt HarID konto siduda isikukoodiga")
            tl.err = 2
            return tl, epost, roles, err
        if not personal_code.startswith('EE:EID:'):
            err = _("EISi saab siseneda ainult Eesti isikukoodiga")
            tl.err = 3
            return tl, epost, roles, err            
        
        tl.isikukood = _text(personal_code, 50) # EE:EID:xxxxxxxxxxx
        tl.perenimi = _text(res['family_name'], 50)
        tl.eesnimi = _text(res['given_name'], 50)

        log.info('HarID user %s/%s/%s' % (tl.isikukood, tl.eesnimi, tl.perenimi))
            
        tl.err = 0
        return tl, epost, roles, err

    # Alates 2023-10-19 ei arvesta enam HarIDi rolle,
    # sest HarID ei taga nende tõelevastavust ES-322
    # def _update_roles(self, tl, roles):
    #     isikukood = tl.isikukood
    #     if isikukood.startswith('EE:EID:'):
    #         ik = isikukood[7:]
    #         kasutaja = model.Kasutaja.get_by_ik(ik)
    #         if not kasutaja:
    #             kasutaja = model.Kasutaja.add_kasutaja(ik,tl.eesnimi,tl.perenimi)
    #             model.Session.commit()

    #         valid_roles = {}
    #         today = date.today()
    #         for role in roles:
    #             active = role['active']
    #             if not active:
    #                 continue
    #             marker = role['marker']
    #             ehis_id = role['provider_ehis_id']
    #             if ehis_id and marker in ('faculty', 'director'):
    #                 ehis_id = int(ehis_id)
    #                 reg_nr = role['provider_reg_nr']
    #                 start_date = role['start_date']
    #                 end_date = role['end_date']
    #                 start_date = start_date and utils.date_from_iso(start_date) or None
    #                 end_date = end_date and utils.date_from_iso(end_date) or None
    #                 if marker == 'director':
    #                     grupp_id = const.GRUPP_K_ADMIN
    #                 else:
    #                     grupp_id = const.GRUPP_OPETAJA
    #                 if (not start_date or start_date <= today) and (not end_date or end_date >= today):
    #                     if valid_roles.get(ehis_id) != const.GRUPP_K_ADMIN:
    #                         valid_roles[ehis_id] = grupp_id

    #         li1 = ['%s(%s)' % (ehis_id, grupp_id) for ehis_id, grupp_id in valid_roles.items()]
    #         li2 = ['%s(%s)' % (p.kool_id, p.kasutajagrupp_id) for p in kasutaja.pedagoogid]
    #         log.info('%s HARID %s / EHIS %s' % (tl.isikukood, ','.join(li1), ','.join(li2)))
    #         #return

    #         for p in list(kasutaja.pedagoogid):
    #             try:
    #                 grupp_id = valid_roles.pop(p.kool_id)
    #             except KeyError:
    #                 # rolli enam pole
    #                 if p.on_ehisest:
    #                     log.info('%s HARID del %s' % (ik, p.kool_id))
    #                     p.delete()
    #             else:
    #                 if p.kasutajagrupp_id != grupp_id:
    #                     if grupp_id == const.GRUPP_K_ADMIN:
    #                         # pedagoog direktoriks
    #                         p.kasutajagrupp_id = grupp_id
    #                     elif p.kasutajagrupp_id == const.GRUPP_K_ADMIN and p.on_ehisest:
    #                         # direktor pedagoogiks
    #                         p.kasutajagrupp_id = grupp_id

    #         for ehis_id, grupp_id in valid_roles.items():
    #             log.info('%s HARID add %s' % (ik, ehis_id))

    #             koht_id = None
    #             qk = (model.Session.query(model.Koht.id)
    #                   .filter_by(kool_id=ehis_id))
    #             for rk in qk.all():
    #                 koht_id = rk[0]
    #                 break
                
    #             p = model.Pedagoog(isikukood=ik,
    #                                eesnimi=tl.eesnimi,
    #                                perenimi=tl.perenimi,
    #                                kool_id=ehis_id,
    #                                koht_id=koht_id,
    #                                kasutajagrupp_id=grupp_id,
    #                                on_ehisest=True)
    #             kasutaja.pedagoogid.append(p)
    #         kasutaja.ametikoht_seisuga = datetime.now()
    #         model.Session.commit()
    
    def canceled(self):
        "HARID autentimine katkestati"
        raise HTTPFound(location=self._home_url())

    def _home_url(self):
        return self.h.url('avaleht')
