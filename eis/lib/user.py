from datetime import datetime, timedelta, date
import random
import re
import pickle
from pyramid.httpexceptions import HTTPFound
from eis.lib.exceptions import TooManyUsersException, NotAuthorizedException
import sqlalchemy as sa
import eis.model_s as model_s
import eis.model_log as model_log
from eis import model
from eis.model import const
from eis.lib.xtee import (
    ehis,
    set_rr_pohiandmed,
    Rahvastikuregister,
    uuenda_rr_pohiandmed,
    vrd_rr_nimi,
    anna_synnikoht
    )
from eis.forms import validators
from . import menu
# menyy moodul - teiste rakenduste korral muudetakse seda
menumod = menu

import logging
log = logging.getLogger(__name__)

import eiscore.i18n as i18n
_ = i18n._

class User(object):
    "Kasutaja seansiandmed ja autentimine"
    id = const.USER_NOT_AUTHENTICATED # kasutaja.id 
    isikukood = None
    eesnimi = None
    perenimi = None
    epost = None
    telefon = None
    koht_id = None
    koht_nimi = None
    valitsus_tasekood = None
    uiroll = None
    mask = None
    verified_id = None
    helpmaster = False
    auth_type = None
    auth_subtype = None
    menu_left = None
    menu_right = None
    testpw_id = None # testiparooli või SEBi korral sooritaja.id    
    testpw_test_id = None
    seb_s_id = None # SEBi kasutaja sooritus.id
    _kasutaja = None # kasutaja kirje

    current_user_count_time = None
    # praegune kasutajate arv
    current_user_count = None 
    # minimaalne kasutajate piirang
    min_user_count = None 
    # lugemata kirjade arv
    cnt_new_msg = None
    handler = None
    session = None
    
    def __init__(self, handler):
        self.handler = handler
        self.request = handler.request
        self.session = self.request.session

    def __repr__(self):
        return f'<User {self.id} {self.isikukood} {self.fullname}>'

    @property
    def fullname(self):
        if self.eesnimi and self.perenimi:
            return f'{self.eesnimi} {self.perenimi}'

    @property
    def is_authenticated(self):
        "Kas kasutaja on autenditud"
        return self.id and True or False

    @property
    def has_pw(self):
        return self.auth_type == const.AUTH_TYPE_PW

    @property
    def has_id(self):
        return self.auth_type in (const.AUTH_TYPE_ID, const.AUTH_TYPE_ID2)

    @property
    def has_c(self):
        if self.has_id:
           auth_type = self.session.get('USER.AUTH_TYPE')
           return auth_type == const.AUTH_TYPE_C
        else:
           return self.auth_type == const.AUTH_TYPE_C

    @property
    def koht(self):
        if self.koht_id:
            return model.Koht.getR(self.koht_id)

    @property
    def app_name(self):
        return self.handler.c.app_name

    @classmethod
    def gen_pwd(cls, len=8, simple=False):
        return _gen_pwd(len, simple)
    
    @classmethod
    def logout(cls, session):
        "Väljumine, seansi lõpetamine"
        cls.set_session_logout(session)
        cls.clean_session(session)
        session.clear()
        #session.delete()
        session.invalidate()

    @classmethod
    def clean_session(cls, session):
        for key in ('USER.UID', # isikukood
                    'USER.ID', # kasutaja.id
                    'USER.FIRSTNAME',
                    'USER.LASTNAME',
                    'USER.KOHT',
                    'USER.KOHT_NIMI',
                    'USER.UIROLL',
                    'USER.VALITSUS_TASEKOOD',                    
                    'USER.AUTH_TYPE',
                    'USER.HELPMASTER', # kas kasutaja tohib abiinfot muuta
                    'USER.LOGIN_%s' % const.APP_EKK, # kas on loginud eksamikeskuse vaatesse
                    'USER.LOGIN_%s' % const.APP_EIS, # kas on loginud avalikku vaatesse
                    'USER.MASK_%s' % const.APP_EKK, # menyy
                    'USER.MASK_%s' % const.APP_EIS, # menyy
                    'USER.ALLOWED_CACHE_%s' % const.APP_EKK, # õiguste puhver
                    'USER.ALLOWED_CACHE_%s' % const.APP_EIS, # õiguste puhver
                    'USER.DENIED_CACHE_%s' % const.APP_EKK, # keelatud õiguste puhver
                    'USER.DENIED_CACHE_%s' % const.APP_EIS, # keelatud õiguste puhver
                    'kohteelvaade',
                    'USER.VERIFIED_ID',
                    'USER.NEWMSG',
                    'USER.CACHE_PERM',
                    'USER.CACHE_TESTILIIK',
                    'USER.CACHE_AINE',
                    'USER.sooritused_id',
                    ):
            session.pop(key, None)

    @classmethod
    def from_session(cls, handler):
        """Kui kasutaja on kuidagi autenditud, siis tehakse temast objekt
        """
        session = handler.request.session
        try:
            k_id = session.get('USER.ID')
        except KeyError as ex:
            # KeyError: '_accessed_time'
            k_id = None
        if k_id:
            # autentinud kasutaja andmed saame seansist
            auth_type = session.get('USER.AUTH_TYPE')
            if handler.c.app_ekk and auth_type in (const.AUTH_TYPE_PW, const.AUTH_TYPE_L):
                # Innove vaatesse ei luba parooliga sisselogijaid
                if handler.c.inst_name not in ('test','dev'):
                    return

            user = cls(handler)
            user.auth_type = auth_type
            user.testpw_id = session.get('TESTPW_ID')
            user.perenimi = session.get('USER.LASTNAME')
            user.eesnimi = session.get('USER.FIRSTNAME')
            user.isikukood = session.get('USER.UID')
            
            user.id = k_id
            user.telefon = session.get('USER.PHONENO')
            user.verified_id = session.get('USER.VERIFIED_ID')
            user.get_new_msg(session)
                
            if handler.c.app_ekk:
                user.koht_id = const.KOHT_EKK
            else:
                user.koht_id = session.get('USER.KOHT') or None                
                user.koht_nimi = session.get('USER.KOHT_NIMI')
                user.valitsus_tasekood = session.get('USER.VALITSUS_TASEKOOD')
                user.uiroll = session.get('USER.UIROLL')
                # kui SEB kasutaja info on salvestamata, siis salvestame
                user.set_session_info_seb()
            return user

    @classmethod
    def from_none(cls, handler):
        """Luuakse autentimata kasutaja objekt
        """
        user = cls(handler)
        user.isikukood = const.USER_NOT_AUTHENTICATED
        return user

    @classmethod
    def from_tara(cls, handler, isikukood, eesnimi, perenimi, synnikpv, amr):
        "Sisselogimine TARA kaudu"

        # puhastame seansi, alustame uut seanssi
        session = handler.request.session

        user = cls(handler)
        usp = validators.IsikukoodP(isikukood)
        if not usp.isikukood:
            handler.error(_("Vigane isikukoodi formaat"))
            return
        user.isikukood = usp.isikukood
        user.auth_type = const.AUTH_TYPE_TARA
        user.auth_subtype = amr
        user.eesnimi = eesnimi
        user.perenimi = perenimi
        if not user.give_kasutaja(synnikpv=synnikpv):
            handler.error('Isikut ei leitud')
            return
        user.remember_login(session, eesnimi, perenimi)
        return user

    @classmethod
    def from_harid(cls, handler, isikukood, eesnimi, perenimi, epost, amr):
        "Sisselogimine HarID kaudu"

        # puhastame seansi, alustame uut seanssi
        session = handler.request.session

        user = cls(handler)
        try:
            country, eid, ik = isikukood.split(':')
        except:
            country = eid = ik = None
            return
    
        isikukood = f'{country}{ik}'
        usp = validators.IsikukoodP(isikukood)
        if not usp.isikukood:
            handler.error(_("Vigane isikukoodi formaat"))
            return
        user.isikukood = usp.isikukood
        user.auth_type = const.AUTH_TYPE_HARID
        user.auth_subtype = amr        
        user.eesnimi = eesnimi
        user.perenimi = perenimi
        user.epost = epost
        if not user.give_kasutaja():
            handler.error('Isikut ei leitud')
            return
        user.remember_login(session, eesnimi, perenimi)
        return user

    @classmethod
    def from_seb(cls, handler, kasutaja, sooritaja_id, sooritus_id, namespace):
        "Sisselogimine SEBiga"

        # puhastame seansi, alustame uut seanssi
        session = handler.request.session

        user = cls(handler)
        user.id = kasutaja.id
        user.isikukood = kasutaja.isikukood
        user.auth_type = const.AUTH_TYPE_SEB
        user.eesnimi = kasutaja.eesnimi
        user.perenimi = kasutaja.perenimi
        user.epost = kasutaja.epost
        user.seb_s_id = sooritus_id
        user.testpw_id = sooritaja_id
        user.remember_login(session, kasutaja.eesnimi, kasutaja.perenimi, from_session_id=namespace)

    def get_seb_id(self):
        """Kontrollitakse, kas on tulnud SEBiga antud sooritust sooritama
        """
        session = self.request.session
        try:
            return session['SEB_S_ID']
        except:
            return None

    def set_session_info_seb(self):
        """SEB teisel pöördumisel salvestakse kasutajainfo
        (esimesel korral ei olnud veel beakeri kirjet)
        """
        session = self.request.session
        try:
            fs_id = session['SEB_FS_ID']
        except:
            return
        if fs_id:
            session.pop('SEB_FS_ID')
            session.changed()
            self.set_session_info(fs_id)

    def has_seb_session(self):
        """Kas kasutajal on SEB sessioon?"""
        request = self.request
        sql = "SELECT count(*) FROM beaker_cache WHERE autentimine='%s'" % const.AUTH_TYPE_SEB +\
            " AND kasutaja_id=:kasutaja_id AND remote_addr=:remote_addr " +\
            " AND kehtetu IS NULL AND accessed > :accessed "
        remote_addr = request.remote_addr or ''
        params = {'kasutaja_id': self.id, 
                  'remote_addr': remote_addr[:60],
                  'accessed': datetime.now() - timedelta(minutes=60),
                  }
        cnt = model_s.DBSession.execute(model.sa.text(sql), params).scalar()
        return cnt
    
    @classmethod
    def _decode_asn1(cls, value):
        """ASN1 kodeeringus string teisendatakse tavaliseks stringiks
        """
        value = value.replace('\\x00','')
        c_set = set(re.findall(r'\\x..', value))
        for c in c_set:
            if c == '\\x00':
                c_replace = ''
            else:
                c_replace = eval('"'+c+'"')
            value = value.replace(c, c_replace)
        return value

    @classmethod
    def login_legacy(cls, handler, isikukood):
        "Sisselogimine eesti.ee portaalist"

        # puhastame seansi, alustame uut seanssi
        session = handler.request.session
        #cls.clean_session(session)

        user = cls(handler)
        usp = validators.IsikukoodP(isikukood)
        if not usp.valid:
            return
        
        user.isikukood = usp.isikukood
        user.auth_type = const.AUTH_TYPE_L

        kasutaja = model.Kasutaja.get_by_ikR(usp.isikukood)        
        if not kasutaja and model.Kasutaja.is_isikukood_ee(usp.isikukood):
            userid = f'{const.RIIK_EE}{usp.isikukood}'
            rr_reg = Rahvastikuregister(handler=handler, userId=userid)
            kasutaja = set_rr_pohiandmed(handler, None, usp.isikukood, reg=rr_reg)
            if not kasutaja:
                handler.error('Isikut ei leitud')
                return
            model.Session.commit()
        user.eesnimi = kasutaja.eesnimi
        user.perenimi = kasutaja.perenimi
        user.id = kasutaja.id
        user.remember_login(session)
        return user
            
    @classmethod
    def set_user(cls, handler):
        session = handler.request.session
        # kas on varem autenditud?
        user = cls.from_session(handler)
        if not user:
            # pole sisse loginud
            # loome autentimata kasutaja objekti
            user = cls.from_none(handler)
        else:
            # on sisse loginud
            user.mask = session.get('USER.MASK_%s' % handler.c.app_name)
            user.helpmaster = session.get('USER.HELPMASTER')

        # jätame meelde andmemudeli jaoks
        handler.c.user = user
        model.usersession.set_user(user)
        if user.isikukood != const.USER_NOT_AUTHENTICATED:
            # kasutaja on sisse loginud mingil viisil
            if not session.get('USER.UID') or not session.get('USER.LOGIN_%s' % handler.c.app_name) or not user.id:
                # kui äsja saabus, siis sisustame seansi
                user.remember_login(session)

        if user.koht_id or handler.c.app_plank:
            # kasutajal on või peab olema koht
            # veendume, et see koht on lubatud
            kohad = user.opt_kohad()
            #log.debug('set_user kohad=%s' % kohad)
            if user.koht_id not in [r[0] for r in kohad] and not user.on_adminkoht and not user.on_kohteelvaade:
                # kasutaja tuli avalikust vaatest plankide moodulisse
                # ja lubatud kohad erinevad
                koht_id = len(kohad) and kohad[0][0] or None
                uiroll = koht_id and const.UIROLL_K or const.UIROLL_S
                user.set_koht(session, uiroll, koht_id)

        if not user.mask:
            # autentimata kasutajal ei pruugi maski veel olla
            # mask antakse muidu autentimisel
            try:
               session['USER.ID'] = user.id
            except KeyError:
               log.error('USER KeyError!')
               session.invalidate()
               session['USER.ID'] = user.id
            user.get_mask(session, user.uiroll, user.koht_id)

        # usersessionis peab olema teada rakendus
        user.app_ekk = handler.c.app_ekk
        return user
    
    @classmethod
    def authenticate_pw(cls, handler, userid, password):
        "Kasutaja logib sisse parooliga"
        if not userid or not password:
            log.debug('Login: puuudub isikukood või parool')
            return
        err = None
        user = cls(handler)
        kasutaja = user.get_kasutaja(userid.strip())
        if kasutaja:
            password = password.strip()
            # kas on kasutaja õige parool
            rc = kasutaja.check_password(password)
            if password and not rc:
                # kontrollime vana räsi
                rc = kasutaja.check_password_old(password)
                if rc:
                    # asendame räsi uuemaga
                    kasutaja = model.Kasutaja.get(kasutaja.id)
                    kasutaja.set_password(password, False)
                    model.Session.commit()
            if password and not rc:
                # kas oleme testresiimis ja see on testimise parool
                settings = handler.request.registry.settings
                rc = password == settings.get('debug.passwd')
            if rc:
                # parool on loetud õigeks
                user.isikukood = kasutaja.isikukood
                user.eesnimi = kasutaja.eesnimi
                user.perenimi = kasutaja.perenimi
                user.id = kasutaja.id
                user.auth_type = const.AUTH_TYPE_PW
                return user
            else:
                # testiparooli saab kasutada ainult avalikus vaates,
                # aga lubame sisse logida ka plankide moodulisse,
                # kust kohe suuname edasi avalikku vaatesse.
                # kas on sisse loginud testiparooliga?
                q = (model.SessionR.query(model.Sooritaja.id,
                                          model.Sooritaja.test_id,
                                          model.Sooritaja.staatus,
                                          model.Nimekiri.alates,
                                          model.Nimekiri.kuni)
                     .filter(model.Sooritaja.kasutaja_id==kasutaja.id)
                     .outerjoin(model.Sooritaja.nimekiri)
                     .order_by(model.sa.desc(model.Sooritaja.id)))

                hash_p = model.hash_pwd(password, userid=userid)
                r = q.filter(model.Sooritaja.testiparool==hash_p).first()
                if not r:
                    # proovime vana SHA1
                    hash_p = model.hash_pwd_old(password)
                    r = q.filter(model.Sooritaja.testiparool==hash_p).first()
                if r:
                    sooritaja_id, test_id, staatus, nk_alates, nk_kuni = r
                    err = None
                    handler.request.log_isikukood = kasutaja.isikukood
                    if nk_kuni and nk_kuni < date.today():
                        err = _("Sisestatud parool on seotud testiga, mille lahendamise ajavahemik on juba läbi")
                    elif nk_alates and nk_alates > date.today():
                        err = _("Sisestatud parool on seotud testiga, mille lahendamise ajavahemik pole veel alanud")
                    if err:
                        handler.error(err)
                    else:
                        if staatus == const.S_STAATUS_TEHTUD:
                            err = _("Sisestatud parool on seotud testiga, mis on juba sooritatud")
                            handler.warning(err)
                        user.isikukood = kasutaja.isikukood
                        user.eesnimi = kasutaja.eesnimi
                        user.perenimi = kasutaja.perenimi
                        user.id = kasutaja.id
                        user.auth_type = const.AUTH_TYPE_TESTPW
                        user.testpw_id = sooritaja_id
                        user.testpw_test_id = test_id
                        return user

            settings = handler.request.registry.settings
            err = _('Login: vale parool')
        else:
            err = _('Login: vale isikukood')
        log.info(err + ': ' + userid)
            
    def set_koht(self, session, uiroll, koht_id):
        if self.has_c:
            # kui on sisse loginud keskserveri kaudu, siis ei luba tal endal kohta valida
            return
        self.clear_cache()
        self.get_mask(session, uiroll, koht_id)
        if self.on_kohteelvaade:
            session.pop('kohteelvaade')
            session.changed()
        if not self.handler.c.app_ekk:
            c = self.handler.c
            if c and c.is_devel and c.inst_name != 'dev':
                return
            kasutaja = self.get_kasutaja()
            if kasutaja and (kasutaja.koht_id != self.koht_id or kasutaja.uiroll != self.uiroll):
                # pärime kasutaja write-tabelist
                kasutaja = model.Kasutaja.get(kasutaja.id)
                kasutaja.koht_id = self.koht_id
                kasutaja.uiroll = self.uiroll
                model.Session.commit()

                if self.koht_id:
                    k_nimi = koht_id and model.Koht.getR(koht_id).nimi or None
                    self.handler.log_add(const.LOG_KOHT, k_nimi, '')

    def start_kohteelvaade(self, session, koht_id):
        "Algab soorituskoha admini eelvaade"
        session['kohteelvaade'] = True
        self.remember_login(session, uiroll=const.UIROLL_K, koht_id=koht_id)

    def testpw_home_url(self):
        "Testi alustamise URL, kui kasutaja on sisse loginud testiparooliga"
        if self.app_name == const.APP_EIS:
            testpw_id = self.testpw_id
            sooritaja = model.Sooritaja.getR(testpw_id)
            if not sooritaja:
                err = _("Testi sooritamiseks suunamine tühistati")
                log.error(err + ' (%s)' % testpw_id)
                User.logout(self.session)
                self.handler.error(err)
                self.menu_left = None
                return '/eis'
                #raise NotAuthorizedException('/eis', err) # mako seest ei pyyta kinni
            url = self.handler.url('sooritamine_alustamine', test_id=sooritaja.test_id, sooritaja_id=sooritaja.id)
        else:
            url = '/eis'
        return url

    def remember_login(self, session, eesnimi=None, perenimi=None, uiroll=None, koht_id=None, from_session_id=None):
        """Kasutaja andmete meeldejätmine koheselt peale autentimist või
        peale autentimist esmakordsel rakenduse kasutamisel
        """
        if self.handler._is_error_controller:
            return False

        is_old_login = session.get('USER.UID')
        self.clear_cache() # unustame sisselogimata kasutaja õigused
        if self.app_name == const.APP_EKK:
            # EKK vaatesse sisenemisel on vaja kirjutatavat kirjet, et salvestada viimati_ekk
            kasutaja = self.get_kasutaja(write=True)
        else:
            kasutaja = self.get_kasutaja()
        if kasutaja and kasutaja.isikukood:
            # kui nimi erineb, siis kontrollpäring RRist
            # x-tee päringu userId välja jaoks omistame c.user
            self.handler.c.user = self
            # usersession jätame meelde andmemudeli jaoks, et kirjutada Kasutaja.modifier
            model.usersession.set_user(self)       

            if not from_session_id:
                # kui ei ole SEB
                settings = self.handler.request.registry.settings
                # võimalusel uuendatakse nimi RRis, kui pole ammu uuendanud
                if vrd_rr_nimi(self.handler, kasutaja, eesnimi, perenimi):
                    model.Session.commit()

            self.eesnimi = kasutaja.eesnimi
            self.perenimi = kasutaja.perenimi
            self.isikukood = kasutaja.isikukood
            self.id = kasutaja.id

        session['USER.FIRSTNAME'] = self.eesnimi
        session['USER.LASTNAME'] = self.perenimi
        session['USER.AUTH_TYPE'] = self.auth_type
        session['TESTPW_ID'] = self.testpw_id
        # SEB korral soorituse ID
        session['SEB_S_ID'] = self.seb_s_id
        # SEB korral käivitaja seansi ID
        session['SEB_FS_ID'] = from_session_id
        session['USER.UID'] = self.isikukood
        
        session['USER.ID'] = self.id
        self.get_new_msg(session)
        session.changed()
        
        if self.app_name != const.APP_EIS and self.testpw_id:
            self.set_session_info(from_session_id)
            self.log_login(is_old_login)
            raise NotAuthorizedException('/eis')            

        if self.app_name == const.APP_EKK:
            # Eksamikeskuse vaatesse ei luba niisuguseid sisse logida, kellel kontot pole
            if not kasutaja or not kasutaja.on_kehtiv_ametnik:
                if kasutaja:
                    err = _("Kasutajal pole siseveebi vaate ligipääsuõigust")
                    log.error('%s: %s %s' % (err, kasutaja.isikukood, kasutaja.nimi))
                    if self.handler.is_live:
                        # suuname kasutaja avalikku vaatesse, ei tohi teda välja logida, kuna
                        # võib-olla on tal test pooleli ja suunati kogemata EKK vaatesse
                        raise NotAuthorizedException('/eis', err)
                    else:
                        User.logout(session)
                        self.handler.error(err)
                return False
            multisession = self.handler.request.registry.settings.get('multi.session')
            if multisession != 'true':
                kasutaja.viimati_ekk = datetime.now()
                model.Session.commit()

        if not kasutaja:
            if self.app_name == const.APP_EIS:
                # kui id-kaardiga logib avalikus vaates sisse kasutaja, 
                # kellel kasutajakirjet veel pole, siis teeme selle kirje
                kasutaja = model.Kasutaja.add_kasutaja(self.isikukood, self.eesnimi, self.perenimi)
                kasutaja.on_ametnik = False
                kasutaja.on_labiviija = False
                log.info('Uus kasutaja %s,%s %s' % (self.isikukood,
                                                    self.eesnimi,
                                                    self.perenimi))
                model.Session.commit()
            else:
                log.error('Logout - pole kasutaja')
                User.logout(session)
                self.handler.error(_("Kasutajakonto puudub"))
                return False

        if kasutaja:
            if self.epost and not kasutaja.epost:
                try:
                    epost = validators.Email().to_python(self.epost)
                except validators.formencode.api.Invalid as ex:
                    pass
                else:
                    kasutaja = self.get_kasutaja(write=True)
                    kasutaja.epost = epost
                    
            if kasutaja.telefon:
                try:
                    telefon = validators.MIDphone().to_python(kasutaja.telefon)
                except validators.formencode.api.Invalid as ex:
                    pass
                else:
                    session['USER.PHONENO'] = self.telefon = telefon
                    session.changed()
            if not self.id:
                session['USER.ID'] = self.id = kasutaja.id
                session.changed()

        kohad = []
        if self.app_name == const.APP_EKK:
            uiroll = None
            koht_id = const.KOHT_EKK
        else:
            kohad = kasutaja.get_kohad_nimi(self.app_name)            
            if self.app_name == const.APP_PLANK:
                uiroll = const.UIROLL_K
                koht_id = kasutaja.koht_id
                if kohad and koht_id not in [r[0] for r in kohad]:
                    koht_id = kohad[0][0]
            else:
                if not uiroll and kasutaja.koht_id in [r[0] for r in kohad]:
                    # vaikimisi kasutame seda rolli, mis kasutajal viimati oli
                    uiroll = kasutaja.uiroll
                    koht_id = kasutaja.koht_id

        # leiame õiguste maski
        self.get_mask(session, uiroll, koht_id)

        if kasutaja and kasutaja.bgcolor:
            # kasutajal on oma stiil
            self.handler.c.style = session['style'] = self.gen_style(kasutaja.bgcolor)

        if kasutaja and not self.testpw_id:
            if not kasutaja.epost \
               or not kasutaja.epost_seisuga \
               or kasutaja.epost_seisuga < datetime.now() - timedelta(days=365):
                if kohad or self.on_koolipsyh or self.on_logopeed:
                    # kasutajalt on vaja kysida e-posti aadressi (ES-2530)
                    session['chk.email'] = True
            
        # on selles vaates sisse loginud
        session['USER.LOGIN_%s' % self.app_name] = True
        session['default_params'] = self._prev_default_params() or {}
        session.changed()

        # kui on autenditud kasutaja, siis jätame kasutajakonto 
        # juures meelde, et ta on meid kylastanud
        # ja kustutame sama kasutaja muud seansid
        self.set_session_info(from_session_id)
        self.log_login(is_old_login)
        return True

    def set_verified(self, request, verifflog_id):
        session = request.session
        self.verified_id = session['USER.VERIFIED_ID'] = verifflog_id
        session.changed()
        
    def gen_style(self, bgcolor):
        "Kasutajaliidese värvide genereerimine menüü taustavärvi baasil"
        if not bgcolor:
            # vaikimisi stiilifailis olev oranz
            return None

        r,g,b = [int(v, 16) for v in (bgcolor[1:3], bgcolor[3:5], bgcolor[5:7])]
        def _shift(dr,dg,db):
            r1 = min(max(r+dr,0),255)
            g1 = min(max(g+dg,0),255)
            b1 = min(max(b+db,0),255)
            return '#%.02X%.02X%.02X' % (r1,g1,b1)
        style = {'bgcolor': bgcolor,
                 'bghover': _shift(-42,-41,-21),
                 'outline': _shift(19,-14,29),
                 'link': _shift(-7,-9,5),
                 'fheader': _shift(150,78,131),
                 }
        return style

    def get_mask(self, session, uiroll, koht_valitud=None):
        "Leitakse kasutaja rollile ja kohale vastavad õigused ja õiguste mask"
        valitsus_tasekood = None
        koht_id = koht_nimi = None
        kohatu = False
        kohad = []
        if self.handler.c.app_ekk:
            # EKK vaade
            koht_id = const.KOHT_EKK
        elif self.testpw_id or uiroll == const.UIROLL_S:
            # testiparooliga sooritaja
            koht_id = None
            kohad = self.opt_kohad()            
        else:
            # leiame avaliku vaate kasutajal olevad rollid
            kohad = self.opt_kohad()
            if koht_valitud:
                koht_valitud = int(koht_valitud)
                for k in kohad:
                    if k[0] == koht_valitud:
                        koht_id = koht_valitud
                        koht_nimi = k[1]
                if koht_valitud != koht_id:
                    # valitud koht ei ole kohtade loetelus
                    on_adminkoht = self.on_adminkoht
                    on_kohteelvaade = self.on_kohteelvaade
                    if (on_adminkoht or on_kohteelvaade) and koht_valitud:
                        # plankide halduril on õigus kõigil kehtivatel kohtadel
                        koht = model.Koht.getR(koht_valitud)
                        if koht.staatus == const.B_STAATUS_KEHTIV:
                            koht_id = koht_valitud
                            koht_nimi = koht.nimi
                        else:
                            log.debug('valitud koht ei ole kehtiv')
                    else:
                        log.debug('valitud koht {} ei ole lubatud kohtade loetelus {}'.format(koht_valitud, [k[0] for k in kohad]))
            elif kohad:
                self.clear_cache()
                koht_id = kohad[0][0]
                koht_nimi = kohad[0][1]
            if self.handler.c.app_eis:
                if not uiroll and koht_id:
                    # kui rolli pole, aga koht on valitud, siis on õpetaja roll
                    uiroll = const.UIROLL_K
                elif not koht_id:
                    # kui rolli pole ja kohtapole, siis on testisooritaja roll
                    uiroll = const.UIROLL_S
                elif uiroll == const.UIROLL_S and koht_id:
                    # kui on testisooritaja roll, siis pole kohta
                    koht_id = None

        # kui kohta valida ei saa, aga mingites kohtades on õigusi
        kohatu = not koht_id and len(kohad) == 0            
                    
        if self.handler.c.app_ekk:
            self.koht_id = koht_id
        else:
            # kehtiv roll on leitud
            session['USER.KOHT'] = self.koht_id = koht_id or None
            session['USER.KOHT_NIMI'] = self.koht_nimi = koht_id and koht_nimi or None
            if koht_id:
                koht = model.Koht.getR(koht_id)
                valitsus_tasekood = koht and koht.valitsus_tasekood
            session['USER.VALITSUS_TASEKOOD'] = valitsus_tasekood
            session['USER.UIROLL'] = self.uiroll = uiroll
            #log.debug('SET ROLL %s KOHT %s/%s' % (uiroll, koht_id, koht_nimi))
            
        # leiame kehtivale rollile vastavad õigused
        permissions = self.get_permissions()
        # kas kasutaja tohib muuta abiinfot
        session['USER.HELPMASTER'] = self.has_permission('abi', const.BT_UPDATE)
        #log.debug('get_mask koht_id=%s, permissions=%s' % (koht_id, permissions))

        # leiame täismenüü
        menu_left = menumod.get_menu(self.handler, self)
        # eemaldame täismenüüst valikud, millele pole õigusi
        mask = menu_left.remove_not_permitted(permissions, koht_id, kohatu, valitsus_tasekood)
        # moodustame õigustele vastava menüü maski
        # erijuhul eriõigused
        if permissions == ['ALL']:
            mask = '1'*100
        session['USER.MASK_%s' % self.app_name] = self.mask = mask
        
    def leave_session(self):
        # peale sessiooni lõpetamist unustame kasuta kirje,
        # kuna see ei ole enam sessiooniga seotud ja ei toimi
        self._kasutaja = None

    def get_kasutaja(self, userid=None, write=False):
        "Leitakse kasutaja kirje andmebaasis"
        if userid:
            vip = validators.IsikukoodP(userid)
            self._kasutaja = vip.get(model.Kasutaja, write=write)
        elif self.id:
            if not self._kasutaja or self._kasutaja.id != self.id \
               or (write and not self._kasutaja.is_writable):
                if write:
                    self._kasutaja = model.Kasutaja.get(self.id)
                else:
                    self._kasutaja = model.Kasutaja.getR(self.id)
                if not self._kasutaja:
                    # kasutaja võidi just yhendada teise kirjega
                    User.logout(self.session)
                    raise Exception("Kasutaja {id} puudub".format(id=self.id))
        return self._check_prelive(self._kasutaja)
    
    def give_kasutaja(self, synnikpv=None):
        "Kasutaja leidmine. Kui ei leia ja on isikukood, siis luuakse RR põhjal."
        kasutaja = self.get_kasutaja()        
        if not kasutaja and self.isikukood:
            kasutaja = model.Kasutaja.get_by_ikR(self.isikukood)
            kasutaja = self._check_prelive(kasutaja)
            if not kasutaja and self.handler.c.app_eis:
                # avalikus vaates luuakse kasutaja automaatselt, välja arvatud prelive
                if self.handler.c.inst_name == 'prelive':
                    return
                if self.request.is_ext() and model.Kasutaja.is_isikukood_ee(self.isikukood):
                    handler = self.handler
                    userId = f'{const.RIIK_EE}{self.isikukood}'
                    rr_reg = Rahvastikuregister(handler=handler, userId=userId)
                    kasutaja = set_rr_pohiandmed(handler, None, self.isikukood, reg=rr_reg)
                else:
                    kasutaja = model.Kasutaja.add_kasutaja(self.isikukood,self.eesnimi,self.perenimi, synnikpv)
                if kasutaja:
                    kasutaja.on_ametnik = False
                    kasutaja.on_labiviija = False
                    model.Session.commit()
            if kasutaja:
                self.id = kasutaja.id
                self.isikukood = kasutaja.isikukood
                self._kasutaja = kasutaja
        return kasutaja       

    def _check_prelive(self, kasutaja):
        # prelive ei luba sisse logida kõrvalistel kasutajatel
        if kasutaja and self.handler.c.inst_name == 'prelive':
            ik = kasutaja.isikukood
            epost = kasutaja.epost
            if not ik or \
              not (ik.startswith('TEST') or
                   (epost and (epost.endswith('@harno.ee') or epost.endswith('@hm.ee')))):
                log.error(f'pole prelive luba: {ik}')
                return
        return kasutaja

    def get_pedagoogid(self, koht_id=None):
        """Leitakse pedagoogide kirjed
        """
        q = (model.SessionR.query(model.Pedagoog)
             .filter_by(kasutaja_id=self.id)
             .filter(sa.or_(model.Pedagoog.kehtib_kuni==None,
                            model.Pedagoog.kehtib_kuni>=date.today()))
             )
        if koht_id:
            q = q.filter_by(koht_id=koht_id)
        return q.all()

    def opt_kohad(self):
        """Leitakse andmebaasist kasutajale lubatud kohad
        """
        kohad = []
        need_rr = False
        if self.testpw_id:
            pass
            
        elif self.app_name == const.APP_EKK:
            # eksamikeskuse vaates on ainult yks koht võimalik
            return [(const.KOHT_EKK, _("Haridus- ja Noorteamet"))] 

        else:
            # avalik vaade või muud rakendused
            if self.is_authenticated:
                # autenditud kasutaja: 
                # - kasutajarollidega määratud kohad
                # - pedagoogi kohad
                # - läbiviija kohad

                # esmalt otsime puhvrist
                cache_name = 'USER.CACHE_KOHAD_%s' % self.app_name
                cache = self.session.get(cache_name)
                cache_key = 'opt'
                kohad = cache and cache.get(cache_key)
                if kohad is not None:
                    return kohad
                # kui puhvris polnud, siis otsime andmebaasist
                kasutaja = self.get_kasutaja()
                if not kasutaja:
                    log.debug('Kasutaja puudub')
                    raise Exception(_("Kasutaja puudub"))

                # vajadusel uuendame EHISe pedagoogi ametikohtade andmeid
                if not model.is_read_only() and kasutaja.isikukood_ee:
                    settings = self.handler.request.registry.settings
                    is_ext = settings.get('is_ext') == 'true'
                    if is_ext and kasutaja.opilane_uuendada(settings, kasutaja):
                        # teeme EHISest õppimise päringu, kui pole 2 kuud tehtud
                        ehis.uuenda_opilased(self.handler, [kasutaja.isikukood])
                        model.Session.commit()
                    if is_ext and kasutaja.ametikoht_uuendada(settings, True):
                        # teeme EHISest ametikohtade päringu
                        userId = f'{const.RIIK_EE}{self.isikukood}'
                        reg = ehis.Ehis(handler=self.handler, userId=userId)
                        message, ametikohad = reg.ametikohad([self.isikukood])
                        kasutaja = model.Kasutaja.get(kasutaja.id)
                        kasutaja.ametikoht_proovitud = datetime.now()
                        if message:
                            self.handler.error(message)
                        else:
                            log.debug('Uuendasin ametikoha (%s)!' % (self.isikukood))
                            if kasutaja.update_pedagoogid(ametikohad):
                                uuenda_rr_pohiandmed(self.handler, kasutaja)
                            model.Session.commit()
                # leiame võimalikud kohad
                kohad = kasutaja.get_kohad_nimi(self.app_name)

                # jätame puhvris meelde
                if cache is None:
                    self.session[cache_name] = dict()
                self.session[cache_name][cache_key] = kohad
                self.session.changed()

        return kohad

    def uuenda_klass(self, kool_id, klass, paralleel):
        "Klassi õpilaste uuendamine EHISest"
        rcd = model.Klass.get_by_klass(kool_id, klass, paralleel)

        handler = self.handler
        settings = handler.request.registry.settings
        cache_hours = int(settings.get('ehis.cache.klass',0))
        if not rcd or not rcd.seisuga \
               or cache_hours != -1 \
               and rcd.seisuga < datetime.now() - timedelta(hours=cache_hours):
            # on vaja uuendada
            log.debug(f'oppurid_kool({kool_id},{klass},{paralleel})')
            reg = ehis.Ehis(handler=self.handler)
            message, oppimised = reg.oppurid_kool(kool_id,
                                                  klass, 
                                                  paralleel)
            if message:
                handler.error(message)
            else:
                model.Opilane.update_klass(oppimised, 
                                           kool_id, 
                                           klass, 
                                           paralleel)
                model.Session.commit()

    def join_permissions(self, d1, d2):
        for key, value in d2.items():
            if key in d1:
                d1[key] |= value
            else:
                d1[key] = value

    def get_permissions(self):
        "Leitakse rollile vastavad õigused"
        add_k = False
        if not self.is_authenticated:
            permissions = menumod.get_permissions_notauthenticated(self.handler)
        elif self.testpw_id:
            # testiparooliga
            if self.app_name == const.APP_EIS:
                permissions = menumod.get_permissions_testpw(self.handler)
            else:
                permissions = {}
        elif self.app_name == const.APP_EIS and not self.koht_id:
            permissions = menumod.get_permissions_student(self.handler)
            # koolipsyh!
            add_k = True
        else:
            permissions = menumod.get_permissions_public(self.handler)
            if self.on_kohteelvaade:
                # lisame vaatamisõiguse kõigile soorituskoha admini õigustele
                # ei kasuta kasutaja päris õigusi
                g_oigused = model.Kasutajagrupp.get_oigused(const.GRUPP_K_ADMIN)
                self.join_permissions(permissions, g_oigused)
            else:
                add_k = True
        if add_k:
            # lisame kasutaja rollidega saadud õigused
            cache_name = 'USER.CACHE_PERM'
            cache = self.session.get(cache_name)
            koht_id = self.koht_id or None
            key = (self.app_name, koht_id)
            permissions_k = cache and cache.get(key)
            if permissions_k is None:
                kasutaja = self.get_kasutaja()
                if kasutaja:
                    permissions_k = kasutaja.get_permissions(koht_id)
                    if cache is None:
                        self.session[cache_name] = dict()
                    self.session[cache_name][key] = permissions_k
                    self.session.changed()
            if permissions_k:
                self.join_permissions(permissions, permissions_k)
        return permissions

    def get_testiliigid(self, permission, perm_bit=const.BT_INDEX):
        """Leitakse testiliigid, millega tegelemiseks on antud õigus olemas
        """
        cache_name = 'USER.CACHE_TESTILIIK'
        cache = self.session.get(cache_name)

        li_all = []
        for perm in permission.split(','):
            key = (self.id, perm, perm_bit)
            li = cache and cache.get(key)
            if not li:
                if self.app_name == const.APP_EIS and self.on_pedagoog:
                    return [None] # kõik liigid
                li = self.get_kasutaja().get_testiliigid(perm, perm_bit)
                if cache is None:
                    self.session[cache_name] = dict()
                self.session[cache_name][key] = li
                self.session.changed()
            li_all.extend(li)
        return li_all

    def get_ained(self, permission, perm_bit=const.BT_INDEX, notnull=False):
        """Leitakse ained, millega tegelemiseks on antud õigus olemas
        """
        cache_name = 'USER.CACHE_AINE'
        cache = self.session.get(cache_name)

        li_all = []
        for perm in permission.split(','):
            key = (self.id, perm, perm_bit)
            li = cache and cache.get(key)
            if not li:
                li = self.get_kasutaja().get_ained(perm, perm_bit)
                if cache is None:
                    self.session[cache_name] = dict()
                self.session[cache_name][key] = li
                self.session.changed()
            li_all.extend(li)
        if notnull:
            return [r for r in li_all if r]
        return li_all

    @property
    def on_pedagoog(self):
        if self.app_name == const.APP_EKK:
            # EKK vaate avalik kasutaja, kas on kuskil pedagoog?
            return self.has_permission('klass', const.BT_SHOW)
        elif self.koht_id:
            # avalik vaade, kas on antud kohas pedagoog?
            return self.has_permission('klass', const.BT_SHOW, koht_id=self.koht_id)
        else:
            return False

    @property
    def on_koolipsyh(self):
        return self.has_permission('koolipsyh', const.BT_SHOW)

    @property
    def on_logopeed(self):
        return self.has_permission('logopeed', const.BT_SHOW)

    @property
    def on_avalikadmin(self):
        return self.koht_id and \
               self.has_permission('avalikadmin', const.BT_UPDATE, koht_id=self.koht_id) or \
               self.on_kohteelvaade

    @property
    def on_testiadmin(self):
        if self.koht_id:
            q = (model.SessionR.query(model.Labiviija.id)
                 .filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_T_ADMIN)
                 .join(model.Labiviija.testikoht)
                 .filter(model.Testikoht.koht_id==self.koht_id))
            return q.limit(1).count() > 0

    @property
    def on_admin(self):
        return self.has_permission('admin', const.BT_UPDATE)

    @property
    def on_plangiadmin(self):
        return self.has_permission('plangid-admin', const.BT_UPDATE)

    @property
    def on_kohteelvaade(self):
        return self.app_name == const.APP_EIS and self.session.get('kohteelvaade')

    @property
    def on_adminkoht(self):
        "Kas kasutaja on selline admin, kellel on õigus kõigil kohtadel"
        # Innove plankide adminil plankide rakenduses on selline õigus
        if not self.handler.is_live and 0:
            return True
        return self.on_plangiadmin and self.handler.c.app_name == const.APP_PLANK

    def check_synnikoht(self, kasutaja):
        "Vajadusel küsitakse parameetris oleva kasutaja sünnikoht RRist"
        if anna_synnikoht(self.handler, kasutaja):
            model.Session.commit()
        
    def _perm_keys(self, permission, perm_bit, obj, **kw):
        data = [(model.Ylesanne, 'Y', 'ylesanne_id'),
                (model.Test, 'T', 'test_id'),
                (model.Koht, 'K', 'koht_id'),
                (model.Nimekiri, 'N', 'nimekiri_id'),
                (model.Testimiskord, 'R', 'tk_id'),
                (model.Testiruum, 'U', 'testiruum_id'),
                (model.Testikoht, 'O', 'testikoht_id'),
                (model.Toimumisprotokoll, 'M', 'toimumisprotokoll_id'),
                (model.Ylesandekogu, 'G', 'ylesandekogu_id'),
                (model.Tookogumik, 'D', 'tookogumik_id'),
                (model.Sooritaja, 'J', 'sooritaja_id'),
                ]

        obj_id = id_value = None
        cache_valid = None
        for (cl, ch, key) in data:
            if obj and isinstance(obj, cl):
                id_value = obj.id
                try:
                    cache_valid = str(obj.cache_valid)
                except:
                    cache_valid = None
            else:
                id_value = kw.get(key)
            if id_value:
                obj_id = ',%s%s' % (ch, id_value)
                if not obj:
                    obj = cl.get(id_value)
                break

        if obj and not obj_id:
            try:
                # obj ei ole EISi paketi mudelist (nt Kysitlus)
                obj_id = ',%s%s' % (obj.__class__.__name__, obj.id)
            except:
                pass
            
        testiliik = kw.get('testiliik')
        piirkond_id = kw.get('piirkond_id')
        aine = kw.get('aine')
        gtyyp = kw.get('gtyyp')
        params = (permission, perm_bit, obj_id, gtyyp, testiliik, piirkond_id, aine, cache_valid)
        return obj, obj_id, params

    def _perm_check(self, permission, perm_bit, obj, obj_id, **kw):
        buf = ''
        group_id = None
        if permission == 'EKK':
            # kas on EKK vaate õigus
            k = self.get_kasutaja()
            if not k:
                return False, ''
            rc = k.on_kehtiv_ametnik
        elif permission == 'GRUPP':
            group_id = perm_bit
            if obj and isinstance(obj, model.Test):
                rc = model.Testiisik.has_role(group_id, self.id, obj.id)
            elif obj and isinstance(obj, model.Ylesanne):
                rc = model.Ylesandeisik.has_role(group_id, self.id, obj.id)
            else:
                permission = perm_bit = None
                # peab päring kasutaja.has_permission
                rc = None                
        elif obj and isinstance(obj, (model.Test, model.Ylesanne)):
            lang = self.handler.c.lang or ''                    
            rc = obj.has_permission(permission, perm_bit, lang, self)
            buf += 'obj'
        elif obj and not isinstance(obj, str) \
          and not (isinstance(obj, model.Koht) and (obj.id == self.koht_id) and self.on_kohteelvaade):
            rc = obj.has_permission(permission, perm_bit, self)
            buf += 'obj'
        else:
            # pole objekti
            permissions = self.get_permissions()
            p = permissions.get(permission)
            if not (p and p & perm_bit):
                # õigus kindlasti puudub
                rc = False
                buf += '%s & %s = %s' % (p, perm_bit, rc)
            elif not (kw.get('testiliik') or kw.get('piirkond_id') or kw.get('aine') or kw.get('gtyyp')):
                # ei pea kontrollima kitsamalt
                rc = True
            else:
                # peab kontrollima kitsamalt
                rc = None

        if rc is None:
            k = self.get_kasutaja()
            if not k:
                return False, ''
            testiliik = kw.get('testiliik')
            piirkond_id = kw.get('piirkond_id')
            aine = kw.get('aine')
            gtyyp = kw.get('gtyyp')
            rc = k.has_permission(permission,
                                  perm_bit,
                                  piirkond_id=piirkond_id,
                                  testiliigid=testiliik and [testiliik] or [],
                                  aine_kood=aine,
                                  grupp_id=group_id,
                                  gtyyp=gtyyp)
            buf += 'kasutaja'
        #log.debug(f'perm_check {permission} bit={perm_bit} {obj} {obj_id} {kw}={rc}')
        return rc, buf

    def has_group(self, group_id, obj=None, **kw):
        return self.has_permission('GRUPP', group_id, obj, **kw)

    def has_ekk(self):
        "Kas on EKK vaate õigus"
        return self.has_permission('EKK', const.BT_SHOW)
    
    def has_permission(self, permission, perm_bit, obj=None, **kw):
        """Kontrollitakse õiguse olemasolu. Kasutatakse puhvrit.
        permission - õiguse nimi
        perm_bit - muutmine/vaatamine vm
        piirkond_id, aine, testiliik - kasutajarolli parameetrid
        obj - muu objekt, mille õiguste kontrolli funktsiooni kasutada
        ylesanne_id, test_id, koht_id, nimekiri_id, tk_id, testiruum_id, testikoht_id, sooritaja_id -
          muu objekti id, kui objekti ennast pole
        """
        #if self.handler.is_devel:
        #    return True
        obj, obj_id, params = self._perm_keys(permission, perm_bit, obj, **kw)
        buf = ''
        # vaatame õiguste puhvrist, kas oleme seda õigust juba varem kontrollinud
        now = datetime.now()
        cache_delta = timedelta(minutes=15) # kui kaua usaldada puhvris olevaid andmeid
        rc = None
        for c_rc, cache_name in ((True, 'USER.ALLOWED_CACHE_%s' % self.app_name),
                                 (False, 'USER.DENIED_CACHE_%s' % self.app_name)):
            cache = self.session.get(cache_name)
            if cache:
                if isinstance(cache, list):
                    # ajutiselt!
                    cache = dict()
                dt_in_cache = cache.get(params)
                if dt_in_cache:
                    if dt_in_cache < now - cache_delta:
                        # puhver on aegunud
                        dt_in_cache = None
                    if dt_in_cache:
                        # leiti puhvrist
                        rc = c_rc
                        buf += 'cached'
                        break

        if rc is None:
            # ei leitud puhvrist
            rc, buf1 = self._perm_check(permission, perm_bit, obj, obj_id, **kw)
            # salvestame õiguste puhvris
            if rc:
                cache_name = 'USER.ALLOWED_CACHE_%s' % self.app_name
            else:
                cache_name = 'USER.DENIED_CACHE_%s' % self.app_name                
            if isinstance(self.session.get(cache_name), list):
                # ajutiselt!
                self.session[cache_name] = dict()
            if self.session.get(cache_name) is None:
                self.session[cache_name] = dict()
            self.session[cache_name][params] = now
            self.session.changed()
        #log.debug('has_permission(%s)=%s (%s)' % (str(params), rc, buf))
        return rc

    def clear_cache(self):
        self.mask = self.session['USER.MASK_%s' % self.app_name] = None
        self.session['USER.ALLOWED_CACHE_%s' % self.app_name] = dict()
        self.session['USER.DENIED_CACHE_%s' % self.app_name] = dict()
        self.session['USER.CACHE_TESTILIIK'] = dict()
        self.session['USER.CACHE_AINE'] = dict()
        self.session['tempsooritus'] = []
        self.session['tempsooritused'] = None
        self.session.changed()

    def set_allowed_tos(self, id, data):
        """Jätame meelde, et sooritus id on lubatud sooritada
        """
        session = self.request.session
        log.debug(f'SET_ALLOWED_TOS {id}: {data}')
        if 'USER.sooritused_id' not in session:
            session['USER.sooritused_id'] = {id: data}
            session.changed()
            #elif id not in session['USER.sooritused_id']:
        else:
            session['USER.sooritused_id'][id] = data
            session.changed()
        log.debug(f'USER.sooritused_id={session["USER.sooritused_id"]}')
        
    def is_allowed_tos(self, id):
        """Kontrollitakse, kas on jäetud meelde õigus sooritust sooritada
        """
        session = self.request.session
        try:
            return session['USER.sooritused_id'].get(id)
        except:
            return None

    def rm_allowed_tos(self, id):
        """Eemaldatakse meelespidamine soorituse kohta
        """
        if self.is_allowed_tos(id):
            session = self.request.session
            if session['USER.sooritused_id'].pop(id):
                # andmed olid olemas, eemaldati
                session.changed()
                return True
        
    def get_menu(self):
        """
        Tagastatakse kasutajale lubatud menüü.
        """
        #log.debug('user get_menu mask=%s' % self.mask)
        menu_left = menumod.get_menu(self.handler, self)
        if self.mask:
            # kui varasemast korrast on õigused maskina meeles, 
            # siis saab seda ära kasutada
            menu_left.remove_not_in_mask(self.mask)
        else:
            # küsime andmebaasist õigused ja viskame 
            # ülearused asjad menüüst välja
            permissions = menumod.get_permissions_notauthenticated(self.handler)
            kohatu = not self.koht_id and len(self.opt_kohad()) == 0
            menu_left.remove_not_permitted(permissions, self.koht_id, kohatu)
        self.menu_left = menu_left

    def log_login(self, is_old_login):
        """Logime sisselogimise
        """
        request = self.handler.request
        remote_addr = request.remote_addr
        buf = '%s (%s,%s)' % (self.fullname, self.id or '-', remote_addr)

        # esindamise koht
        koht = self.koht
        if koht:
            buf += '\nt: %s' % koht.nimi

        # õppimise koht
        q = (model.SessionR.query(model.Opilane.koht_id, model.Koht.nimi)
             .filter(model.Opilane.kasutaja_id==self.id)
             .filter(model.Opilane.on_lopetanud==False)
             .outerjoin(model.Opilane.koht)
             .order_by(sa.desc(model.Opilane.prioriteet)))
        r = q.first()
        if r:
            oppekoht_id, oppekoht_nimi = r
            buf += '\nõ: %s' % oppekoht_nimi
        else:
            oppekoht_id = None
            
        if self.auth_type == const.AUTH_TYPE_TESTPW:
            buf += '\ntest: %s' % self.testpw_test_id

        for cookie_name in request.cookies:
            if cookie_name.startswith(const.COOKIE_REG):
                buf += '\n%s' % (cookie_name)
            
        auth_types = {const.AUTH_TYPE_PW: 'parool',
                      const.AUTH_TYPE_ID: 'id',
                      const.AUTH_TYPE_ID2: 'digi-id',
                      const.AUTH_TYPE_M: 'm-id',
                      const.AUTH_TYPE_C: 'kesk',
                      const.AUTH_TYPE_L: 'xtee',
                      const.AUTH_TYPE_TESTPW: 'testiparool',
                      const.AUTH_TYPE_TARA: 'TARA',
                      const.AUTH_TYPE_SMARTID: 'smart-id',
                      const.AUTH_TYPE_HARID: 'HarID',
                      const.AUTH_TYPE_SEB: 'SEB',
                      }
        auth_type_s = auth_types.get(self.auth_type) or self.auth_type
        if is_old_login:
            auth_type_s = 'session/%s' % auth_type_s
        if self.auth_subtype:
            # TARA korral
            auth_type_s += '/' + self.auth_subtype
            
        log.info('LOGIN %s %s:%s %s' % (self.app_name, 
                                        auth_type_s, 
                                        self.id, 
                                        buf))

        self.handler.log_add(const.LOG_LOGIN,
                             buf,
                             auth_type_s,
                             kontroller='LOGIN',
                             user=self,
                             oppekoht_id=oppekoht_id)

    def _prev_default_params(self):
        "Leitakse eelmisel seansil kasutatud vaikimisi parameetrid"
        sql = "SELECT data FROM beaker_cache " + \
              "WHERE kasutaja_id=:kasutaja_id AND namespace!=:session_id " + \
              "ORDER BY id DESC LIMIT 1"
        params = {'kasutaja_id': self.id, 
                  'session_id': self.session.id,
                  }
        data = model_s.DBSession.execute(model.sa.text(sql), params).scalar()
        if data:
            try:
                prev_sess = pickle.loads(data.tobytes())
                return prev_sess['session']['default_params']
            except:
                pass

    def set_session_info(self, from_session_id):
        """Peale sisselogimist kustutab muud sama kasutaja seansid,
        et ei saaks korraga mitmelt poolt sees olla
        """
        self.handler.prf()
        request = self.handler.request
        multisession = request.registry.settings.get('multi.session')
        if multisession != 'true':
            # kui ei lubata mitmekordselt sees olla,
            # siis teiste sama kasutaja seansside kirjed kustutatakse
            sql = "DELETE FROM beaker_cache " +\
                  "WHERE kasutaja_id=:kasutaja_id AND namespace!=:session_id " 
            params = {'kasutaja_id': self.id, 
                      'session_id': self.session.id,
                      }
            if from_session_id:
                # SEBi seansi korral jätame puutumata algse seansi
                sql += " AND namespace!=:from_session_id "
                params['from_session_id'] = from_session_id
            self.handler.prf()
            cnt = model_s.DBSession.execute(model.sa.text(sql), params).rowcount

        # salvestame kasutaja andmed seansi tabelis,
        # et get_user_count() saaks vaadata, kui palju on kasutajaid sees
        sql = "UPDATE beaker_cache SET kasutaja_id=:kasutaja_id, "+\
            "autentimine=:autentimine, remote_addr=:remote_addr, "+\
            "app=:app "+\
            "WHERE namespace=:session_id"
        remote_addr = request.remote_addr or ''
        params = {'kasutaja_id': self.id, 
                  'session_id': self.session.id,
                  'autentimine': self.auth_type,
                  'remote_addr': remote_addr[:60],
                  'app': self.app_name,                      
                  }
        cnt = model_s.DBSession.execute(model.sa.text(sql), params).rowcount            
        self.handler.prf()
        model_s.DBSession.flush()
        self.handler.prf()

    def set_session_bankinfo(self):
        # pangalingi jaoks kasutaja andmed
        request = self.handler.request
        remote_addr = request.remote_addr or ''
        sql = "UPDATE beaker_cache SET kasutaja_id=:kasutaja_id, "+\
              "autentimine=:autentimine, remote_addr=:remote_addr, "+\
              "app=:app "+\
              "WHERE namespace=:session_id" 
        params = {'kasutaja_id': self.id, 
                  'session_id': self.session.id,
                  'autentimine': self.auth_type,
                  'remote_addr': remote_addr[:60],
                  'app': self.app_name,                      
                  }
        q = model_s.DBSession.execute(model.sa.text(sql), params)            
        model_s.DBSession.flush()
             
    @classmethod
    def set_session_logout(cls, session):
        # praeguse seansi juurde jäetakse lahkumine meelde
        sql = "UPDATE beaker_cache SET kehtetu=true "+\
              "WHERE namespace=:session_id" 
        params = {'session_id': session.id,
                  }
        q = model_s.DBSession.execute(model.sa.text(sql), params)            
        #model_s.DBSession.commit()

    @classmethod
    def get_user_count(cls, minutes=5, aut=None):
        "Leiame erinevate kasutajate arvu viimase N minuti jooksul"
        t = datetime.now() - timedelta(minutes=minutes)
        if aut:
            # autenditud kasutajad
            sql = "SELECT count(distinct kasutaja_id) FROM beaker_cache "+\
                  " WHERE accessed > :now "+\
                  " AND kasutaja_id IS NOT NULL "
        elif aut == False:
            # autentimata kasutajad, kes ei ole seanssi lõpetanud autentimisega
            sql = "SELECT count(*) FROM beaker_cache "+\
                  " WHERE accessed > :now " +\
                  " AND kasutaja_id IS NULL AND kehtetu IS NULL"
        else:
            # seansside koguarv
            sql = "SELECT count(*) FROM beaker_cache "+\
                  " WHERE accessed > :now "
        cnt = model_s.DBSession.execute(model.sa.text(sql), {'now': t}).scalar()
        return cnt

    @classmethod
    def get_distinct_user_count(cls, alates, kuni=None):
        "Leiame erinevate kasutajate arvu"
        q = (model_log.DBSession.query(sa.func.count(sa.distinct(model_log.Logi.isikukood)))
             .filter_by(tyyp=const.LOG_LOGIN)
             .filter(model_log.Logi.aeg>=alates)
             )
        if kuni:
            q = q.filter(model_log.Logi.aeg<kuni)
        cnt = q.scalar()
        return cnt

    @classmethod
    def get_current_user_count(cls):
        "Leiame erinevate kasutajate arvu viimase N minuti jooksul"
        t = datetime.now()
        r = model.Olekuinfo.give(model.Olekuinfo.ID_KASUTAJA)
        if not r.seisuga or r.seisuga < datetime.now() - timedelta(seconds=60):
            # uuendame kasutajate arvu olekuinfo tabelis
            try:
                r.seis_id = cls.get_user_count()
                r.seisuga = datetime.now()
                model.Session.commit()
            except Exception as e:
                model.Session.rollback()
                log.error(str(e))
        return r.seis_id
    
    @classmethod
    def get_min_user_count(cls):
        "Leiame kõige madalama piirangu"
        if not cls.min_user_count:
            sql = "SELECT min(max_koormus) FROM kasutajagrupp"
            cls.min_user_count = model.SessionR.execute(model.sa.text(sql)).scalar()
        return cls.min_user_count

    @classmethod
    def get_testtaker_count(cls, op):
        "Pooleli olevate testisoorituste arv"
        if op == 1:
            # praegu pooleli soorituste arv
            aeg = datetime.now() - timedelta(minutes=5)
            q = (model_log.DBSession.query(sa.func.count(model_log.Logi.isikukood.distinct()),
                                           sa.func.avg(model_log.Logi.kestus))
                 .filter(model_log.Logi.aeg > aeg)
                 .filter(model_log.Logi.tyyp==const.LOG_USER)
                 .filter(model_log.Logi.testiosa_id!=None)
                 )
            r = q.first()
            if r:
                cnt, kestus = r
            else:
                cnt = kestus = None
            return cnt, kestus
        elif op == 3:
            # keskmine pöördumise aeg
            aeg = datetime.now() - timedelta(minutes=1)
            q = (model_log.DBSession.query(sa.func.avg(model_log.Logi.kestus))
                 .filter(model_log.Logi.aeg > aeg)
                 .filter(model_log.Logi.tyyp == const.LOG_USER)
                 )
            r = q.first()
            if r:
                kestus = r[0]
            else:
                kestus = None
            return kestus

    def get_new_msg(self, session, cache_min=15):
        "Leitakse lugemata kirjade arv"
        cnt = session.get('USER.NEWMSG')
        dt = session.get('USER.NEWMSG_DT')
        now = datetime.now()
        if not cache_min or not dt or now - dt > timedelta(minutes=cache_min):
            # uuendame arvu
            q = (model.SessionR.query(sa.func.count(model.Kirjasaaja.id))
                 .filter_by(kasutaja_id=self.id)
                 .filter_by(staatus=const.KIRI_UUS)
                 .filter(model.Kirjasaaja.created > now - timedelta(days=180))
                 )
            n = q.scalar()
            session['USER.NEWMSG_DT'] = now
            if n != cnt:
                cnt = session['USER.NEWMSG'] = n
                session.changed()
        self.cnt_new_msg = cnt

    def get_emergency(self, is_refresh=False):
        """Erakorralise teadeande päring
        is_refresh=False - väljastada teade, mida kasutaja pole veel sulgenud
                   (uue lehe loomisel)
        is_refresh=True - väljastada ainult uus teade, mida sessioon veel pole näinud
                   (olemasoleva lehe teate uuendamisel)
        Tagastab modified,sisu - kui kasutajale on vaja näidata antud ajal uuendatud teadet antud sisuga
        või None,None - kui teadet pole või kasutaja on selle juba kinni pannud
        """
        # last_m - kasutaja seansile teadaolev viimatine teate uuendamise aeg
        last_m = self.session.get('emergency_last') or ''
        # modified - teenindavale protsessile teadaolev viimatine teate uuendamise aeg
        modified, sisu = model.Avaleheinfo.get_emergency(last_m)
        if modified and modified > last_m:
            # kasuaja seansis veel viimast infot pole
            # jätame sessioonis järgmiste pöördumiste jaoks meelde, et on vaja teade uuendada
            self.session['emergency_last'] = modified
            self.session.changed()
        if sisu and self.session.get('emergency_closed') != modified:
            # emergency_closed on kasutaja poolt suletud teate aeg (mida ta enam ei taha näha)
            # erakorraline teade on olemas
            # ja kasutaja pole aktiivset erakorralist teadet kinni pannud
            # vt index.py:emergency()
            if (is_refresh == False) or (last_m != modified):
                # kuvada kõik sulgemata teated või pole seda veel kasutajale näidatud
                return modified, sisu
        return None, None
        
def _gen_pwd(len, simple):
    "Parooli genereerimine" 
    if simple:
        # genereerime lihtsa parooli
        vchars = 'aeiou'
        cchars = 'bdghjkmnprstv'
        cchars2 = 'fhjkmnprstv'
        nchars = ''
    else:
        vchars = 'aeiouyAEUY'
        cchars = 'bcdfghjkmnprstvwxzBCDFGHJKLMNPQRSTVWXZ'
        cchars2 = 'hjkmnprstvHJKLMNPQRSTVZ'            
        nchars = '23456789-.-'
    allchars = vchars + cchars + nchars
    allchars2 = vchars + cchars2
    pwd = ''
    last_v = last_c = 0
    # genereerime parooli nii, et oleks lihtsam meelde jätta
    for n in range(len):
        if n == 0:
            # esimene täht ei või olla bdg
            buf = allchars2
        elif last_v == 2:
            # peab tulema konsonant
            buf = cchars + nchars
        elif ch == 'j':
            # peab tulema vokaal, aga mitte i
            buf = 'aeou'
        elif last_c == 2 or n == 1 and last_c == 1 or ch in 'bdgv':
            # peab tulema vokaal
            buf = vchars 
        elif last_c == 1 or n == len - 1:
            # konsonandi järel ja kõige viimane täht ei või olla bdg
            buf = allchars2
            # soodustame mõningaid lihtsalt hääldatavaid yhendeid
            if ch == 'n':
                buf += 'dj' * 8
            elif ch == 'h':
                buf += 'v' * 8
            elif ch == 't':
                buf += 's' * 8
            elif ch == 'k':
                buf += 's' * 8
        else:
            buf = allchars
        ch = random.choice(buf)
        pwd += ch
        if ch in vchars:
            last_c = 0
            last_v += 1
        else:
            last_v = 0
            last_c += 1

    return pwd
