"Sisse ja välja logimine TARA kaudu"
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

# TARA identsustõendi väljastaja avalik võti, eelnevalt alla tõmmatud
# Test:
# wget https://tara-test.ria.ee/oidc/jwks -O /srv/eis/etc/tara.jwks.json
# Live:
# wget https://tara.ria.ee/oidc/jwks -O /srv/eis/etc/tara.jwks.json
FN_JWKS = '/srv/eis/etc/tara.jwks.json'

class LogintaraController(BaseController):
    "TARA kaudu sisselogimise kontroller"
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
        auth_url = settings.get('tara.auth.url')
        secret = settings.get('tara.secret')
        client_id = settings.get('tara.client_id')
        redirect_uri = settings.get('tara.redirect.url')        
        state = uuid.uuid4().hex
        nonce = uuid.uuid4().hex
        state_hash = base64.b64encode(hashlib.sha256(state.encode('ascii')).digest()).decode('ascii')
        log.debug('\nstate=%s\nhash=%s\nnonce=%s' % (state, state_hash, nonce))
        params = urllib.parse.urlencode({'redirect_uri': redirect_uri,
                                         'scope': 'openid idcard mid smartid eidas',
                                         'state': state_hash,
                                         'response_type': 'code',
                                         'client_id': client_id,
                                         'nonce': nonce})
        url = "%s?%s" % (auth_url, params)

        def _max(value, n):
            return value and value[:n] or None
        remote_addr = request.remote_addr
        tl = model_log.Taralog(nonce=nonce,
                               state=state_hash,
                               aut_aeg=datetime.now(),
                               aut_params=url,
                               request_url=request_url,
                               remote_addr=_max(remote_addr, 36))
        model_log.DBSession.add(tl)
        model_log.DBSession.flush()
        #model.Session.commit()
        log.debug('TARA request %s' % url)
        req = HTTPFound(location=url)
        #req.set_cookie('eis-tara-state', value=state, httponly=True)
        return req

    def tagasi(self):
        "TARAst autentimiselt tagasitulek"
        user, err = self._get_token()
        model_log.DBSession.flush()
        if user:
            headers = remember(self.request, user.isikukood)
            home = err or self._home_url()
            return HTTPFound(location=home, headers=headers)
        elif err:
            log.error(err)
            self.error(_("Autentimine ebaõnnestus!"))

        return HTTPFound(location=self._home_url())
        
    def _get_token(self):
        request = self.request
        log.debug('TARA response %s' % request.url)
        state = request.GET.get('state')
        code = request.GET.get('code')
        error = request.GET.get('error')

        tl = (model_log.DBSession.query(model_log.Taralog)
              .filter(model_log.Taralog.aut_aeg > datetime.now() - timedelta(hours=1))
              .filter(model_log.Taralog.state==state)
              .first())
        if not tl:
            err = 'Sisenemine ebaõnnestus (viga 1)'
            tl = model_log.Taralog(resp_aeg=datetime.now(),
                                   resp_params=request.url,
                                   err=1)
            model_log.DBSession.add(tl)
            return None, err

        tl.resp_aeg = datetime.now()
        tl.resp_params = request.url
        
        if error:
            err = request.GET.get('error_description')
            tl.err = 2
            return None, err

        # identsustõendi päring
        settings = request.registry.settings
        client_id = settings.get('tara.client_id')
        token_url = settings.get('tara.token.url')
        redirect_uri = settings.get('tara.redirect.url')        
        data={'grant_type': 'authorization_code',
              'code': code,
              'redirect_uri': redirect_uri}
        auth = requests.auth.HTTPBasicAuth(client_id, settings.get('tara.secret'))
        http_proxy = settings.get('http_proxy')
        kw = {}
        if http_proxy:
            kw['proxies'] = {'https': http_proxy }
        r = requests.post(token_url, data=data, auth=auth, **kw)
        res = r.json()
        tl.token_data = json.dumps(res)
        #{'access_token': '...', 'token_type': 'bearer', 'expires_in': 28800, 'id_token': '...'}

        log.debug('TARA id response (%s) %s' % (code, str(res)))
        id_token = res.get('id_token')
        if not id_token:
            err = 'Puudub id_token, error=%s' % res.get('error')
            tl.err = 1
            return None, err
        
        # 1. allkirja kontrollimine RS256, JWT standard
        with open(FN_JWKS, 'r') as fh:
            di = json.load(fh)
            keys = di['keys']

        # parsime id_tokeni esimese osa (päise) lahti, et leida sealt võtme id
        token_header, token_payload, token_sig = id_token.split('.')
        header_buf = base64.urlsafe_b64decode(token_header + '=' * (4 - len(token_header) % 4))
        # {'alg': 'RS256', 'kid': 'public:SOP0AEUxG6ZgUzYH'}
        header = json.loads(header_buf)
        kid = header['kid']

        # otsime selle id-ga võtit tara.jwks.json failist
        verifying_key = None
        for key in keys:
            if key['kid'] == kid:
                verifying_key = jwt.jwk_from_dict(key)
        if not verifying_key:
            err = 'Võti %s puudub' % kid
            tl.err = 1
            return None, err

        jwtoken = jwt.JWT()
        try:
            # nbf annab vea "Not valid yet", sest kell erineb 0,1 s võrra
            #message = jwtoken.decode(id_token, verifying_key) 
            message = jwtoken.decode(id_token, verifying_key, do_time_check=False)
        except jwt.exceptions.JWTDecodeError as err:
            # allkirja verifitseerimine ebaõnnestus
            raise
        
        tl.token_msg = json.dumps(message)
        log.debug('TARA id msg %s' % (message))
        def _text(s, size):
            return s and len(s) > size and s[:size] or s

        tl.isikukood = _text(message['sub'], 50)
        profile = message['profile_attributes']
        birth = utils.date_from_iso(profile['date_of_birth'])
        tl.perenimi = _text(profile['family_name'], 50)
        tl.eesnimi = _text(profile['given_name'], 50)
        
        nonce = message['nonce']
        if nonce != tl.nonce:
            # nonss pole sama, mis oli sisendis
            err = 'Autentimine ebaõnnestus (viga 3)'
            tl.err = 3
            return None, err

        # 2. väljaandja kontrollimine
        if message['iss'] != settings.get('tara.issuer'):
            err = 'Tõendi väljastaja vale: %s' % message['iss']
            tl.err = 5
            return None, err
        
        # 3. adressaadi kontrollimine
        if message['aud'] != client_id:
            err = 'Tõendi saaja vale: %s' % message['aud']
            tl.err = 6
            return None, err
        
        # 4. tõendi ajalise kehtivuse kontrollimine
        now = datetime.utcnow()
        diff = timedelta(minutes=3)
        nbf = datetime.utcfromtimestamp(message['nbf'])
        exp = datetime.utcfromtimestamp(message['exp'])
        if nbf > now + diff or exp < now - diff:
            err = 'Tõend ei kehti enam: nbf %s, exp %s, now %s' % (nbf, exp, now)
            tl.err = 7
            return None, err
        if nbf > now + timedelta(seconds=1):
            err = 'Tõend ei kehti veel: nbf %s, exp %s, now %s' % (nbf, exp, now)
            tl.err = 7
            return None, err

        # 5. autentimisviisi kontrollimine
        amr = None
        for value in message['amr']:
            amr = value
            if value not in ('idcard','mID','mid','smartid','eidas'):
                err = 'Vigane autentimisviis "%s"' % (value)
                tl.err = 8
                return None, err

        log.info('TARA user (%s) %s/%s/%s' % (code, tl.isikukood, tl.eesnimi, tl.perenimi))
        tl.err = 0
        user = User.from_tara(self, tl.isikukood, tl.eesnimi, tl.perenimi, birth, amr)
        return user, tl.request_url
    
    def katkes(self):
        "TARA autentimine katkestati"
        raise HTTPFound(location=self._home_url())

    def _home_url(self):
        return self.h.url('avaleht')
