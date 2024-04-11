from eis.lib.base import *
_ = i18n._
import os
import hashlib
from OpenSSL import crypto
import base64
import formencode
import requests
from eis.forms import validators
log = logging.getLogger(__name__)

class LoginController(BaseController):
    """Sisse ja välja logimine
    """
    _authorize = False
    _is_login_controller = True
    _get_is_readonly = False
    _log_params_post = True
    _log_params_get = True
    _kohteelvaade_readonly = False
    
    @action(renderer='minu/login.mako')
    def index(self):
        """Autentimisvormi näitamine
        """
        if self.c.user.id:
            # on juba sisse loginud
            raise HTTPFound(location=self.url('avaleht'))
        self.request.response.headers['X-Frame-Options'] = 'DENY'
        # mitte kuvada sisselogimise vormile viivat nuppu päises,
        # sest juba olema sisselogimise vormil
        self.c.is_login_page = True
        return self.response_dict

    @action(renderer='minu/login.mako')
    def login(self):
        return self.index()

    def signin(self):
        """Autentimine
        Kui kasutaja soovis ID-kaardiga autentida, siis
        kontrollime serdi olemasolu ja eraldame sealt isiku andmed.

        Kui kasutaja soovis parooliga autentida, siis
        kontrollime baasist, kas kasutajatunnus ja parool on õiged.
        """
        user = None
        username = None
        cookie_data = None
        # parooliga autentimine
        schema = eis.forms.minu.LoginParoolForm
        form = Form(self.request, schema=schema, method='POST')
        if not form.validate():
            self.error(_("Vigased parameetrid"))
        else:
            self.c.username = form.data.get('username')
            parool = form.data.get('parool')
            if not parool:
                self.error(_("Palun sisestada parool"))
            elif not self.c.username:
                # võib olla tegemist arvuti registreerimisega eksamile
                rc, msg, cookie_data = self._reg_testiarvuti(parool)
                if not rc:
                    if msg:
                        self.error(msg)
                    else:
                        self.error(_("Palun sisestada isikukood"))
            else:
                self.c.username = self.c.username.lower()
                user = User.authenticate_pw(self, self.c.username, parool)
                if not user and not self.has_errors():
                    self.error(_("Kasutajakonto puudub või on vale parool"))
                    
        return self._after_authentication(user, cookie_data)

    def _after_authentication(self, user, cookie_data=None):
        if not user:
            # autentimine ei sujunud
            response = self.render_to_response('minu/login.mako')
            if cookie_data:
                self._set_cookie(response, cookie_data)
            return response
        else:
            # kasutaja on autenditud, jätame ta meelde ja leiame õigused
            #log.debug('kasutaja on autenditud')
            if not user.remember_login(self.request.session):
                # autenditi, aga ei saa ikka sisse lasta
                # näiteks kui eksamivaates on ID-kaardiga autenditud, kuid puudub konto
                return HTTPFound(location=self.url('login', action='index'))

            if user.testpw_id:
                # testiparooliga sisenenud kasutaja suunatakse testi alustamisele
                return HTTPFound(location=user.testpw_home_url())
            if user.has_pw:
                kasutaja = user.get_kasutaja()
                if kasutaja.muuda_parool:
                    # kuvame parooli vahetamise soovituse ainult korra
                    kasutaja.muuda_parool = False
                    model.Session.commit()
                    self.notice(_("Palun vaheta parool!"))
                    return HTTPFound(location=self.url('minu_parool', request_url=self.c.request_url))
            return self._after_login()
            
    def signout(self):
        auth_type = self.c.user.auth_type
        User.logout(self.request.session)

        if auth_type in (const.AUTH_TYPE_ID, const.AUTH_TYPE_ID2):
            # serdiga autentimisel ei ole tegelikult võimalik väljuda
            self.error(_("Turvaliseks väljumiseks sule palun kõik brauseri aknad!"))

        after_logout = self.url('avaleht')
        return HTTPFound(location=after_logout)

    def koht(self, on_login=False, uiroll=None, koht_id=None):
        "Koha valik peale sisenemist"
        koht_nimi = None

        # kas mõni koht on valitud?
        if not koht_id:
            koht_id = self.request.params.get('koht_id')
            if koht_id:
                # koht_id valiti lehe päisest "Muu kool..." > kohavalik.mako
                uiroll = const.UIROLL_K
            
        if uiroll == const.UIROLL_K and not koht_id:
            # koha valimise aken 
            self.c.user.get_menu()
            return self.render_to_response('/minu/kohavalik.mako')

        log.debug("Valitud roll %s koht %s" % (uiroll, koht_id))
        # set_koht/get_mask kontrollib kohale ligipääsuõigust
        self.c.user.set_koht(self.request.session, uiroll, koht_id)
        self.c.user.get_menu()
        self.request.session.changed()            
        return self._after_login()

    def role(self):
        "Rolli ja koha valik lehe päisest"
        vkoht = self.request.matchdict.get('role')
        if vkoht and vkoht in (const.UIROLL_S, const.UIROLL_K):
            uiroll = vkoht
            koht_id = None
        elif vkoht:
            uiroll, koht_id = vkoht.split('.')
        else:
            uiroll = const.UIROLL_S
            koht_id = None
        return self.koht(False, uiroll, koht_id)
    
    def _after_login(self):
        c = self.c
        if c.request_url:
            # suunatakse kasutaja sinna, kuhu ta algselt minna tahtis, 
            # aga kohe ei saanud, sest oli autentimata
            return HTTPFound(location=c.request_url)
        else:
            # vaikimisi suunatakse kasutaja avalehele
            return HTTPFound(location=self.url('avaleht'))

    def signin_arvuti(self):
        """Arvuti registreerimine testiruumis
        """
        rc = False
        cookie_data = None
        if self.request.POST:
            parool = self.request.params.get('parool').strip()
            if not parool:
                self.error(_("Palun sisestada parool"))
            else:
                rc, msg, cookie_data = self._reg_testiarvuti(parool)
                if not rc:
                    if msg:
                        self.error(msg)
                    else:
                        self.error(_("Vale parool"))

        if cookie_data:
            # suuname uuesti samale aadressile, et lisatav cookie oleks vastuse koostamisel juba näha
            response = HTTPFound(location=self.url('arvuti'))
            # lisame registreeringu cookie
            self._set_cookie(response, cookie_data)
        else:
            # kuvame registreeringud ja võimaluse registreerida
            response = self.render_to_response('minu/arvuti.mako')
        return response
    
    def _reg_testiarvuti(self, parool):
        """Arvuti registreerimine testiruumis
        Kui õnnestub, siis tagastatakse True, muidu False.
        """
        rc = False
        msg = None
        cookie_data = {}
        
        q = (model.Testiruum.query.filter_by(parool=parool)
             .filter_by(arvuti_reg=const.ARVUTI_REG_ON)
             )
        li = q.all()
        cnt = len(li)
        if cnt > 1:
            msg = _("Palun genereerida uus parool ja proovida uuesti")
        elif cnt == 1:
            testiruum = li[0]
            txt = ''
            arvuti = None
            # leiame testi ID
            q = (model.Session.query(model.Testiosa.test_id)
                 .join(model.Testikoht.testiosa)
                 .join(model.Testikoht.testiruumid)
                 .filter(model.Testiruum.id==testiruum.id))
            test_id = q.scalar()
            cookie_value = User.gen_pwd(50) + User.gen_pwd(50)
            MAX_AGE = 50400 # 14 tundi
            arvuti, cookie_name, old_cookies = model.Testiarvuti.save(test_id, testiruum, cookie_value, MAX_AGE, self.request)
            cookie_data['name'] = cookie_name
            cookie_data['value'] = cookie_value
            cookie_data['max_age'] = MAX_AGE
            cookie_data['old'] = old_cookies
            model.Session.commit()
            txt = _("Arvuti on edukalt registreeritud") + ' - %s' % (arvuti.info())
            self.notice(txt)
            rc = True
        return rc, msg, cookie_data

    def _set_cookie(self, response, cookie_data):
        "Arvuti registreerimise cookie"
        # mozilla asendab cookie, aga IE jätab vana cookie alles

        # kustutame varasemad sama testiruumi registreeringud
        for old_cookie in cookie_data.get('old') or []:
            response.delete_cookie(old_cookie)

        params = {'max_age': cookie_data['max_age'],
                  'samesite': 'none', # proctorio jaoks on vaja samesite=none
                  'httponly': True,
                  'secure': True,
                  }
        
        if self.is_devel and self.request.url.startswith('http:'):
            # secure cookie saadetakse brauserile ainult HTTPS päringu korral
            # testimiseks vajame mitte-secure cookiesid
            params['secure'] = False
            params['samesite'] = 'Lax'

        response.set_cookie(cookie_data['name'], cookie_data['value'], **params)
        # cookie olemasolu kontroll vt handlers/avalik/sooritamine/sooritus.py

    def __before__(self):
        # kuhu kasutaja soovis minna
        self.c.request_url = self.request.params.get('request_url') or self.url('avaleht') 
        # kui on protokoll ja domeen, siis eemaldame need
        # või kui on ainult protokoll, siis eemaldame selle
        m = re.match(r'https?://[^/]+(/.*)', self.c.request_url) or \
            re.match(r'https?:(.*)', self.c.request_url)
        if m:
            self.c.request_url = m.groups()[0]

        BaseController.__before__(self)
        
