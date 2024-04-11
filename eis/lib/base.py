"""Baaskontroller, millest päritakse kõik teised kontrollerid (handlerid)
"""
import logging
import re
import cgi
import sys
import os 
from datetime import *
import random
from simplejson import dumps
from smtplib import SMTPRecipientsRefused
from pyramid_handlers import action
from pyramid.exceptions import NotFound
from pyramid.url import route_url
from pyramid.renderers import render_to_response, render
from webob import Response

# EISi baasmoodulid
import eis
import eiscore.const as const
import eiscore.i18n as i18n
import eis.lib.logclient as logclient

_ = i18n._
from eis.routingbase import find_route_by_action, find_route_args, find_action_by_name
from eis.lib.helpers import RequestHelpers
from eis.lib.validationerror import Form, ValidationError
import eiscore.utils as utils
from eiscore.recordwrapper import RecordWrapper
from eis.lib.mailer import Mailer
import eis.lib.xtee as xtee
from pyramid.httpexceptions import HTTPUnauthorized, HTTPForbidden
from eis.lib.exceptions import NotAuthorizedException, ProcessCanceled, HTTPFound, APIIntegrationError
import eis.model as model
import eis.model_s as model_s
import eis.model_log as model_log
from eis.model import sa
from eis.lib.user import User
import eis.forms as forms
import eis.forms.validators as validators
import inspect
log = logging.getLogger(__name__)

NewItem = utils.NewItem

from eis.lib.testsaga import TestSaga
from eis.lib.examsaga import ExamSaga
from eis.lib.errorhandler import ErrorHandler

class BaseController(ErrorHandler):
    """
    Baaskontroller
    """
    # kontrolleris, mille _authorize on False, ei ole õiguseid vaja
    _authorize = True

    # kontrolleri kasutamiseks vajalik õigus
    # (või komaeraldatud õigused, millest vähemalt üks peab olemas olema)
    _permission = None
 
    # kas kasutaja peab olema seotud kohaga
    _perm_koht = False

    # õiguse puudumise korral: milline õigus puudub
    _miss_perm = ''
    # kas tõlkimine toimub create() kaudu
    _create_is_tr = False
    # kas sisend on valideeritud
    _validated = False

    # kas oleme veakontrolleris
    _is_error_controller = False
    # kas oleme sisselogimiskontrolleris
    _is_login_controller = False
    
    # kas kuvada lehekylje päis kitsana (et mitte raisata ekraanipinda)
    _is_small_header = False

    # kas peale create-meetodit kutsuda index-meetod (vaikimisi kutsutakse edit)
    # ja kas peale õigusteta edit,update,create tegemise katset proovida index või show
    _index_after_create = False

    # parameetrite nimed, mida ei peeta meeles vaikimisi parameetritena
    _ignore_default_params = ['csv','xls','format','otsi','reuse','partial','pdf']

    # kas logida POST-parameetrid
    _log_params_post = False
    # kas logida GET-parameetrid
    _log_params_get = False
    # kas logimine ära jätta (isegi siis, kui konf nõuab logimist)
    _log_params_never = False
    # vaikimisi parameetrid varasemast ajast (hoitakse alles logi jaoks)
    _log_default_params = None
    # otsingutingimuste salvestamise võti
    _upath = None
    
    # kas GET päringu korral võib kasutada read-only transaktsiooni
    _get_is_readonly = True
    # kas soorituskoha administraatori eelvaade on read-only
    _kohteelvaade_readonly = True

    # jooksva kasutaja objekt (eis.lib.user.User)
    user = None

    # parameetrite valideerimise vorm (pyramid_simpleforms)
    form = None

    @property
    def is_live(self):
        return self.request.registry.settings.get('live') != 'false'

    @property
    def is_test(self):
        return self.request.registry.settings.get('test') == 'true'

    @property
    def is_devel(self):
        return self.request.registry.settings.get('devel') == 'true'
      
    def __init__(self, request, pseudo=False):        
        # kasutaja aadress
        environ = request.environ
        # logikirjete jada
        try:
            # erijuhul, kui on ErrorController,
            # on logrows päris kontrolleri poolt tehtud
            request.logrows
        except AttributeError:
            # enamasti ei ole seda olemas ja tuleb luua
            request.logrows = []
            
        remote_addr = environ.get('HTTP_X_ORIGINAL_FORWARDED_FOR') or environ.get('HTTP_X_FORWARDED_FOR')
        if remote_addr:
            request.remote_addr = remote_addr
            
        # jätame meelde requesti ja kasutame seda edaspidi igal pool
        self.request = request
        if not pseudo:
            request._log_started = datetime.now()
            try:
                # kui request.handler on juba olemas, siis oleme veakontrolleris
                # ja jätame request.handler viitama algsele kontrollerile
                _old_handler = request.handler
                # veakontrolleris võib vahel olla transaktsioon juba alustatud
                model.Session.rollback()
            except:
                request.handler = self
            # lisame callbacki, et pärast alati andmebaasiseanss vabastataks
            request.add_finished_callback(rollback_callback)

        # vormile renderdatavate andmete hoidmise objekt
        c = self.c = NewItem()
        # vormil kasutatavad helper-funktsioonid
        self.h = RequestHelpers(request)
        # valikud
        c.opt = model.Opt(self)
        c.ExamSaga = ExamSaga
        c.TestSaga = TestSaga
        # tuvastame jooksva kontrolleri ja tegevuse (logimise ja õiguste kontrolli jaoks)
        c.action = self._get_action(request)
        c.controller = self.__class__.__name__.lower()[:-len('Controller')]

        if not pseudo:
            log.debug('-----%s %s (%s)' % (request.method, request.url, self.__class__.__module__))

        # vormile renderdamisel kasutatavad muutujad:
        # kõik tegevused, mis ei väljasta Response-objekti,
        # peavad väljastama self.response_dict
        # kus c sees on selle tegevusega valmis pandud andmed
        self.response_dict = {'c':c,
                              'request':request,
                              'h': self.h,
                              }

        # konfiguratsioonifaili sisu
        settings = request.registry.settings

        # me ei kasuta c = self.request.tmpl_context
        # sest selles peavad kõik kasutatavad muutujad olema loodud
        # (pole vaikimisi väärtust '')
  
        # jätame meelde, mis on rakenduse nimi
        set_app_name(self, settings)

        cconsent = request.cookies.get('eis-cookieconsent')
        if not cconsent:
            c.no_cookies = c.no_cookies_various = True
        else:
            c.no_cookies = False
            c.no_cookies_various = cconsent.endswith('-0')
            
        #if not self.is_devel and self.request.session.get('debug-gtm'):
        if not self.is_devel and not c.no_cookies_various:
            # Google Tag Manager haldab ka cookie consent (cconsent) dialoogi
            # c.analytics = settings.get('google.analytics')
            # c.plumbr_account = settings.get('plumbr.account')
            c.google_gtm = settings.get('google.gtm')

        self._set_locale()
        
        # kas on päring ainult osa lehe kohta (AJAX)
        try:
            c.partial = request.params.get('partial')       
        except:
            # pangalingist tagasi
            pass
        # leiame kasutaja
        self._get_user()

        # kas kuvada vormiväljad vaikimisi muutmisresiimis või vaatamisresiimis
        c.is_edit = c.action in ('new', 'create', 'edit', 'update', 'index')
        c.includes = {} 
        # klass, mille objekte kasutame vormil (grid) tabelis uue (tühja) kirje kuvamisel
        c.new_item = NewItem

        # leivapururida
        c.pagehistory = self.request.session.get('pagehistory') or []
        c.is_debug = self.request.session.get('is_debug')
        try:
            c.params = self.request.params
        except:
            pass

        # jätame meelde URLi, kuhu tegelikult soovitakse minna
        c.ref = self.request.url

        # eksamikeskuse vaates tõsiste tegevuste korral kuvame lehekülje päise kitsamalt,
        # et ekraani paremini ära kasutada
        if c.controller not in ('index','login') and \
               c.ref.find('/minu/') == -1 and \
               c.action not in ('login', 'avaleht', 'message') or \
               self._is_small_header:
            c.small_header = True

        if not pseudo:
            # autoriseerime praeguse tegevuse
            self._do_authorize()
            self.prf()
            # logime parameetrid
            self._log_params_start()
            self.prf()
            self._trans_readonly()
            self.prf()

    def _get_action(self, request):
        if request.matched_route:
            return request.matchdict.get('action') or \
                find_action_by_name(self.__class__, request.matched_route.name)
            
    def _set_locale(self):
        # kasutajaliidese keel
        request = self.request
        try:
            # kontrollerile jõuga kehtestatud keel (nt testi sooritamiseks)
            locale_name = request._LOCALE_
            settings = request.registry.settings
            assert locale_name in settings['ui_languages'].split()
        except:
            # kasutaja valitud kasutajaliidese keel
            locale_name = request.localizer.locale_name
        request.locale_name = locale_name
            
    def _trans_readonly(self):
        # võtab aega?
        #if self.request.method == 'GET' and self._get_is_readonly:
        if self.c.user.on_kohteelvaade and self._kohteelvaade_readonly:
            # eelvaates on näha, nagu oleks kõik admini õigused,
            # aga tegelikult ei tohi muuta
            model.Session.execute('SET TRANSACTION READ ONLY')            
        if self.is_devel and 0:
            # kui tegelikult pole read only
            model.SessionR.execute('SET TRANSACTION READ ONLY')
            
    def _get_user(self):
        self.c.user = User.set_user(self)
        # jätame logimise jaoks meelde pöördumise alguses kehtinud ID
        self.request.log_isikukood = self.c.user.isikukood
        
    def __before__(self):
        """Kutsutakse enne actioni meetodit.
        """
        pass
        
    def error(self, msg):
        """Veateate lisamine (kuvamine vt common/message.mako)"""
        self.request.session.flash(msg, 'error')
        self.set_log_error(msg)
        
    def set_log_error(self, msg):
        # jätame vea meelde, et hiljem logida
        try:
            self.request._lierror.append(msg)
        except:
            self.request._lierror = [msg]
        
    def notice(self, msg):
        """Infoteate lisamine"""
        self.request.session.flash(msg, 'notice')

    def notice2(self, msg):
        """Infoteate lisamine, mis kuvatakse mujal kui message.mako kaudu"""
        self.request.session.flash(msg, 'notice2')

    def warning(self, msg):
        """Infoteate lisamine"""
        self.request.session.flash(msg, 'warning')

    def success(self, msg=None):
        """Eduka salvestamise teate lisamine"""
        if msg is None:
            msg = _("Andmed on salvestatud")
        self.request.session.flash(msg, 'success')

    def beep(self):
        self.request.session.flash(None, 'beep')

    def has_errors(self):
        "Kas on veateateid"
        return bool(self.request.session.get('_f_error'))

    def has_success(self):
        "Kas on eduteateid"
        return bool(self.request.session.get('_f_success'))

    @property
    def is_error_fullpage(self):
        "Kas ootamatu vea korral kuvada kogu kujundusega avaleht"
        # võib arvestada self.c.action
        return True   

    def response_on_error(self, error):
        "Vastus vea korral, vt error:error()"
        if self.is_error_fullpage:
            # vastus on kasutajaliidese lk
            self.error(error)
            return self.render_to_response('avaleht.mako')
        else:
            # vastus kuvatakse mingis lk osas või on mõeldud javascriptile
            return Response(error)
    
    def _trace_log(self, txt, cookies=False):
        # logime andmebaasis logitabelis
        param = ''
        for k, v in self.request.params.items():
            param += '%s=%s\n' % (k, v)
        if cookies:
            param += 'COOKIES:\n'
            for k,v in self.request.cookies.items():
                param += ' %s=%s\n' % (k, v)
        log.debug(txt + '\n' + param)
        logi_id = self.log_add(const.LOG_TRACE, txt, param)
        return logi_id

    def _get_permission(self):
        base = self._permission
        if self.request.params.get('is_tr'):
            action = self.c.action
            if action in ('edit', 'update') or \
              (action == 'create' and self._create_is_tr):
                if self.params_lang():
                    return '%s-tolkimine' % base
                else:
                    return '%s-toimetamine' % base
        return base

    def _get_perm_bit(self):
        action = self.c.action
        if action in ('new','create'):
            return const.BT_CREATE
        elif action in ('edit', 'update'):
            return const.BT_UPDATE
        elif action == 'delete':
            return const.BT_DELETE
        elif action == 'index':
            return const.BT_INDEX
        else:
            return const.BT_SHOW

    def _is_modify(self):
        return self.c.action in ('edit','update','delete','create', 'new')

    def _do_authorize(self):
        "Kasutaja autoriseerimise kontroll"
        # teeme vajalikud eelnevad tegevused
        # (tehakse enne autoriseerimist, aga võivad eeldada, et kasutaja on autenditud)
        self.__before__()
        if self._authorize == False:
            # selle kontrolleri kasutamiseks pole vaja sisse logida
            return
        is_authenticated = self.c.user and self.c.user.is_authenticated
        # vaatame, millist õigust praegune väljakutse vajab
        # ja kontrollime selle olemasolu
        rc = is_authenticated and self._has_permission()
        self.prf()
        if not rc:
            # visatakse erind
            self._raise_not_authorized(is_authenticated)

    def _raise_not_authorized(self, is_authenticated):
        "Mis tehakse kasutajaga, kellel pole õigus"
        if self.has_errors():
            message = None
        else:
            message = _("Puudub ligipääsuõigus")

        user_agent = self.request.environ.get('HTTP_USER_AGENT') or ''
        if 'SEBEISTEST-' in user_agent:
            # SEBiga kasutaja proovib pääseda kuhugi, kuhu ei tohi
            # suuname kohta, kus on SEBi quit urliga nupp
            url = self.url('seb_notauthorized')
            raise NotAuthorizedException(url)
        if not is_authenticated:
            # kui pole sisse loginud, siis suuname sisse logima
            raise NotAuthorizedException('login')
        if self.c.partial:
            raise NotAuthorizedException('avaleht', message=message)
        else:
            if self.c.app_plank and not self.c.user.has_permission('plangid', const.BT_SHOW):
                # plankide moodulisse on tulnud keegi, kellel pole seal õigust
                raise HTTPFound(location='/eis')
            action = self.c.action
            log.debug('%s %s %s' % (message, self._miss_perm, action))

            url = self._no_permission_url(action)
            if url:
                # on url, kuhu suunata (veateadet ei anta)
                raise NotAuthorizedException(url)
            
            # kuvame veateate ja suuname avalehele 
            if message:
                self.error(message)
            self.request.session.changed()
            raise NotAuthorizedException('avaleht')

    def _no_permission_url(self, action):
        "URL, kuhu kasutaja suunata, kui õigus puudub"

        url = 'avaleht'
        if action in ('edit','update','delete','create','new'):
            try:
                if action in ('edit','update','delete'):
                    # suuname muutmisvormilt vaatamisvormile
                    # ei kuva teadet, et ei peaks alati enne muutmisvormile suunamist õigust kontrollima
                    if self._index_after_create:
                        url = self.url_current('index')
                    else:
                        url = self.url_current('show')
                elif action in ('create','new'):
                    # suuname loetelu vaatamisele
                    url = self.url_current('index')
            except AssertionError:
                # ei leia ruutingut, suuname avalehele
                return
            else:
                # suuname vaatamisvormile
                return url
            
    def _has_permission(self):
        # vajaliku õiguse nimi
        permission = self._get_permission()
        if not permission:
            return False
        # kas toimub muutmine või vaatamine?
        perm_bit = self._get_perm_bit()
        kw = self._perm_params()
        if kw == False:
            # ei lubata ligipääsu
            rc = False            
        elif self._perm_koht and not self.c.user.koht_id:
            # peab olema kohaga seotud kasutaja
            rc = False
        else:
            if kw is None:
                kw = {}
            for perm in permission.split(','):
                rc = self.c.user.has_permission(perm, perm_bit, **kw)
                #log.debug('has_perm(%s, %s, %s) = %s' % (perm, perm_bit, str(kw), rc))
                if rc:
                    break
                
        #log.debug('has_permission(%s, %s, %s)=%s' % (permission, perm_bit, str(kw), rc))
        if not rc:
            # ei lubatud ligipääsu
            li = [permission]
            if kw:
                testiliik = kw.get('testiliik')
                aine = kw.get('aine')
                piirkond_id = kw.get('piirkond_id')
                obj = kw.get('obj')
                if testiliik:
                    li.append(model.Klrida.get_str('TESTILIIK', testiliik) or testiliik)
                if aine:
                    li.append(model.Klrida.get_str('AINE', aine) or aine)
                if piirkond_id:
                    prk = model.Piirkond.get(piirkond_id)
                    li.append(prk and prk.nimi or str(piirkond_id))
                if obj:
                    li.append('%s' % (obj.__class__.__name__))                
            self._miss_perm = ', '.join(li)
            
        return rc
  
    def _perm_params(self):
        """Tagastab ligipääsuõigus kontrollimise parameetrid dictina,
        milles on sellisd keyd:
        piirkond_id, aine, testiliik - väärtused, mille piires peab olema antud kasutajaroll
        obj - muu objekt, mille õiguste kontrolli funktsiooni kasutada
        ylesanne_id, test_id, koht_id, nimekiri_id, tk_id, testiruum_id, testikoht_id, sooritaja_id -
          muu objekti id, kui objekti ennast pole        

        Tühja dicti asemel võib tagastada None.
        Kui on kohe selge, et ligipääsuõigust pole, siis tagastab False.
        """
        return None

    def _get_log_params_list(self, params):
        li = []
        for key, value in params.items():
            if key in ('parool', 'password'):
                value = '*'
            elif isinstance(value, date):
                value = self.h.str_from_date(value)
            elif isinstance(value, datetime):
                value = self.h.str_from_datetime(value)
            elif isinstance(value, cgi.FieldStorage):
                value = 'file:%s' % value.filename
            li.append((key, value))
        return li

    def _get_log_params(self):
        """
        Meetod tagastab sisendparameetrid logimiseks.
        Kui turva- vm kaalutlustel ei saa kõiki andmeid logida, siis tuleb
        meetod kontrolleris üle laadida.
        """
        if self.request.content_type == 'application/json':
            try:
                return self.request.json_body
            except Exception as ex:
                # simplejson.errors.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
                log.error('get_log_params: %s' % str(ex))
                return
        params = self.request.params
        if params:
            return self._get_log_params_list(params)
        else:
            return self.request.environ.get('body_copy')

    def _is_log_params(self):
        "Kas toimub sisendparameetrite logimine"
        if self._log_params_never:
            # selline kontroller, kus ei logita mitte mingil juhul
            return False
        if self.c.user and self.c.user.is_authenticated:
            # autenditud kasutajate tegevus logitakse alati
            return True
        method = self.request.method.upper()
        if self._log_params_post and method == 'POST':
            # selline kontroller, mille POST logitakse alati
            return True
        if self._log_params_get and method == 'GET':
            # selline kontroller, mille GET logitakse alati
            return True
        if self.request.registry.settings.get('log.params'):
            # konfis seadistatud, et autentimata kasutajate kogu tegevus logitakse
            if self.request.path != '/eis':
                # monitooring teeb /eis päringuid
                return True

        # kui on handler.error() veateateid, siis logitakse
        try:
            if self.request._lierror:
                return True
        except:
            pass

        # ei logi
        return False

    def _log_params_start(self):
        "Sisendparameetrite logimine kontrolleri töö alguses (ainult arenduskeskkonnas)"
        if self.is_devel:
            request = self.request
            controller = self.c.controller
            action = self.c.action
            param = self._get_log_params()
            log.debug('ROUTE: %s, CONTROLLER: %s, ACTION: %s' % \
                      (request.matched_route and request.matched_route.name, controller, action))
            buf = self._pretty_params(param) + self._pretty_params(request.matchdict)
            if buf:
                log.debug('PARAMEETRID:\n' + buf)

    def _log_params_end(self, isikukood=None, testiosa_id=None, tyyp=const.LOG_USER):
        "Sisendparameetrite logimine kontrolleri töö lõpus"
        is_log = self._is_log_params()
        if not is_log or self.c.action == 'check':
            # ei logi
            return
        request = self.request
        controller = self.c.controller
        action = self.c.action
        param = self._get_log_params()

        now = datetime.now()
        diff = now - request._log_started
        s_diff = str(diff).split('.')[0]
        kestus = diff.total_seconds()
        if not isikukood and not (self.c.user and self.c.user.is_authenticated):
            try:
                isikukood = request.log_isikukood
            except Exception:
                pass
        if not isikukood and self.c.user:
            isikukood = self.c.user.isikukood

        if self.is_devel:
            log.debug('+++++%.3f %s %s %s' % (kestus, isikukood, request.method, request.url))
        controller, param, sisu = self._log_params_sisu(controller, param)

        # handler.error() veateated
        try:
            errors = self.request._lierror
        except:
            pass
        else:
            if errors:
                sisu = (sisu or '') + '\n' + '\n'.join(errors)

        # vormi valideerimise vead
        try:
            # kas esines vormi valideerimise vigu?
            errors = self.form.errors
        except:
            errors = None
        else:
            if errors:
                sisu = (sisu or '') + '\n' + str(errors)

        sparam = param and str(param) or None
        if self._log_default_params:
            param2 = self._get_log_params_list(self._log_default_params)
            sparam = (sparam or '') + '\nVAIKIMISI:\n' + str(param2)
        self.log_add(tyyp,
                     sisu,
                     sparam,
                     kontroller=controller,
                     tegevus=action,
                     isikukood=isikukood,
                     testiosa_id=testiosa_id,
                     kestus=kestus)

    def _log_params_sisu(self, controller, param):
        "Võimalus muuta logi sisu"
        return controller, param, None

    def _copy_search_params(self, form_data=None, save=False, upath=None):
        """
        Otsinguparameetrite säilitamine.
        Parameetrid kopeeritakse sisendist c sisse, et neid otsinguvormil näidataks.
        Lisaks kopeeritakse need soovi korral eraldi dicti ja jäetakse see seansis meelde.
        """
        # dict selleks, et parameetrid lisaks c-le veel kuskil meelde jätta
        params = {}
        # säilitame otsinguparameetrid
        if form_data:
            # kopeerime valideerimisvormilt
            for key in list(form_data.keys()):
                values = form_data.get(key)
                if isinstance(values, str):
                    values = values.strip()
                self.c.__setattr__(key, values)
                if values:
                    params[key] = values
        else:
            # kopeerime valideerimata parameetrid
            for key in self.request.params.mixed():
                values = self.request.params.getall(key)
                if len(values) > 1:
                    # multiple select
                    # kui on mitu valikut tehtud ja yks neist on "Kõik", siis see on vastuolu,
                    # mis kuulub kõrvaldamisele valiku "Kõik" kõrvaldamise läbi
                    self.c.__setattr__(key, values)
                else:
                    if isinstance(values[0], cgi.FieldStorage):
                        values = None
                    else:
                        values = values[0].strip()
                    self.c.__setattr__(key, values)
                if values:
                    params[key] = values
        if isinstance(params.get('sort'), list):
            # kui sort parameetreid on mitu, siis kehtib viimasena antu
            self.c.sort = params['sort'] = params.get('sort')[-1]
        if save:
            # jätame parameetrid meelde vaikimisi parameetritena järgmiseks korraks,
            # kui jälle samale lehele tullakse
            self._set_default_params(params, upath)

    def _get_current_upath(self):
        "Tegevuse tunnus, mille järgi jäetakse meelde vaikimisi parameetrid"
        return self._upath or self.request.upath_info

    def _set_default_params(self, params, upath=None):
        if upath is None:
            # lehekylg
            upath = self._get_current_upath()
        page = self.c.app_name + upath
        if not 'default_params' in self.request.session:
            self.request.session['default_params'] = {}
        self.request.session['default_params'][page] = params
           
    def _get_default_params(self, upath=None, force=False):
        """Taaskasutame varem samal otsinguvormil kasutatud parameetreid
        """
        if 'default_params' in self.request.session or force:
            if upath is None:
                upath = self._get_current_upath()
            page = self.c.app_name + upath
            dp = self.request.session.get('default_params') or {}
            params = dp.get(page)
            if params:
                for key in self._ignore_default_params:
                    if key in params:
                        del params[key]
                self._log_default_params = params
                return params

    def get_c_default_params(self, upath):
        "Luuakse uus c-sarnane objekt vaikimisi parameetritega"
        c1 = NewItem()
        params = self._get_default_params(upath)
        if params:
            for key in list(params.keys()):
                values = params.get(key)
                if isinstance(values, str):
                    values = values.strip()
                c1.__setattr__(key, values)
        return c1
        
    def url_current(self, action=None, getargs=False, namepart=None, **args):
        """Sama handleri sees teise tegevuse URLi moodustamine
        """
        if not action:
            # sama tegevus
            action = self.c.action

        name = find_route_by_action(self.__class__, action, namepart)
        assert name, 'ei leia ruutingut: %s, %s ' % (self.__class__.__name__, action)
        # kontrollime, et kõigile URLis olema pidavatele parameetritele on väärtused olemas
        route_args = find_route_args(name)
        if route_args:
            for key in route_args:
                if args.get(key) is None:
                    # kui ei ole, siis kasutame praegust
                    args[key] = self.request.matchdict.get(key) or ''
                
        if getargs:
            # säilitame lisaks kohustuslikele parameetritele
            # ka kõik muud GET-parameetrid
            for key, value in self.request.GET.mixed().items():
                if key not in args:
                    if isinstance(value, list):
                        continue
                    if not re.search('<script', value, re.IGNORECASE):
                        args[key] = value
        return self.url(name, **args)

    def url(self, name, rid=False, _anchor=None, pw_url=False, **args):
        """URLi moodustamine.
        Erinevalt funktsioonist request.route_url ei ole GET-parameetrid argumentide seas eraldi dictina.
        name - ruutingu nimi
        rid - kas lisada juhuslik suurus
        **args - URLi sees olevad parameetrid
        """
        
        # GET-parameetrid
        _query = {}
        route_args = find_route_args(name) or []

        # eristame GET-parameetrid
        for key in list(args.keys()):
            value = args[key]
            if key not in route_args:
                del args[key]
                if value or value == 0:
                    _query[key] = value

        if rid:
            # lisatakse juhuslik suurus, 
            # et URL oleks unikaalne ja brauser ei puhverdaks
            _query['rid'] = str(random.random())[6:]
                   
        # kas peaks kontrollima nimesiseste parameetrite olemasolu?
        if len(_query) > 0:
            args['_query'] = _query

        if _anchor:
            args['_anchor'] = _anchor
        if pw_url:
            # URL koos protokolli ja domeeniga (kasutamiseks kirjades)
            url = self.request.route_url(name, **args)
            url = self._set_pw_url(url)
        else:
            # URL ilma protokolli ja domeenita (kasutamiseks kasutajaliidese siseselt)
            url = self.request.route_path(name, **args)
        return url

    def _set_pw_url(self, url):
        "Konteineri hostiga URLis asendatakse host EISi õige domeeniga"
        # domeen
        #pw_host = self.request.registry.settings.get('eis.pw.url')
        environ = self.request.environ
        scheme = environ.get('HTTP_X_HTM_FORWARDED_PROTO') or \
            environ.get('HTTP_X_FORWARDED_PROTO') or \
            environ['wsgi.url_scheme']
        host = environ.get('HTTP_X_HTM_FORWARDED_HOST') or \
            environ.get('HTTP_X_FORWARDED_HOST') or \
            environ['HTTP_HOST']
        pw_host = scheme + '://' + host

        # asendame domeeni
        return pw_host + '/' + url.split('/', 3)[-1]
    
    def _set_https(self, url):
        """URLile lisatakse vajadusel https (vaikimisi tuleb http,
        kuna rakendusserver saab koormusjaoturilt pöördumised http kaudu)
        """
        if url and not self.is_devel:
            if url.startswith('http:'):
                # http asendada https
                url = 'https:' + url[5:]
            elif not url.startswith('http'):
                # protokoll puudub hoopis
                url = 'https:' + url
        return url

    def _redirect(self, action, id=None, getargs=False, **args):
        """Peale POSTitamist suuname ümber GET-URLile, et page refresh ei tülitaks.
        """
        return HTTPFound(location=self.url_current(action, id=id, getargs=getargs, **args))

    def render_to_response(self, renderer_name, value=None):
        if value is None:
            value = self.response_dict
        log.debug(f'render: {renderer_name}')
        response = render_to_response(renderer_name, value, self.request) 
        if not self._authorize or self.c.app_ekk:
            # X-Frame-Options ei või kasutada testi sooritamisel, muidu ei toimi Proctorio
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        return response
        
    def render(self, renderer_name, value=None):
        if value is None:
            value = self.response_dict
        return render(renderer_name, value, self.request) 

    def render_mail(self, template, data):
        """Kirja koostamine malli põhjal
        """
        r = self.render_to_response(template, data)
        subject = None
        body = r.ubody
        li = body.split('\n', 1)
        if len(li) == 2:
            hdr = 'Subject:'
            if li[0].startswith(hdr):
                subject = li[0][len(hdr):]
                body = li[1]
        return subject, body

    def is_cconsent(self):
        # Kas kasutaja on andnud nõusoleku mitte-hädavajalike küpsiste kasutamiseks
        return self.request.cookies.get('eis-cookieconsent') and True or False

    def convert_id(self, value_id, on_esitlus=False):
        """
        Parameetrina saadud ID teisendamine.
        Koormustesti korral võidakse anda ID kujul, mis vajab teisendamist.
        """
        if value_id:
            m = re.match(r'^T(\d+)$', value_id)
            if m:
                # T kodeerib seda, et ID saamiseks tuleb liita suur arv
                value_id = 90000000 + int(m.groups()[0])
            else:
                try:
                    value_id = int(value_id)
                except:
                    pass
            return value_id

    def params_get(self, key, regexp):
        "Parameetri lugemine ja kontroll"
        value = self.request.params.get(key)
        if not value or re.match(regexp, value):
            return value

    def params_lang(self):
        "Keele parameetri lugemine ja kontroll"
        return self.params_get('lang', '[a-z]{2}$')
    
    def set_debug(self):
        "Vastavalt parameetrile muudetakse debug-info kuvamist"
        if 'debug' in self.request.params:
            self.request.session['is_debug'] = self.c.is_debug = self.request.params.get('debug') and True or False

    def log_add(self, tyyp, sisu, param, **kw):
        return logclient.log_add(self, tyyp, sisu, param, **kw)
            
    ###############################################################################
    # profileerimine
    _is_prf = False
    
    def prf(self, label='', t1=None):
        "Profileerimisel ajahetke tabamine"
        if self._is_prf:
            f = inspect.currentframe().f_back
            (filename, lineno, function_name, lines, index) = inspect.getframeinfo(f)
            filename = filename.split('/eis/')[-1]
            dt = datetime.now().timestamp()
            request = self.request
            if t1:
                dt_last = t1
            else:
                try:
                    dt_last = request._prf_last
                except:
                    dt_last = request._log_started.timestamp()
            elapse = dt - dt_last
            value = (elapse, f'{filename}:{lineno}:{function_name}:{label}')
            try:
                request._liprf.append(value)
            except:
                request._liprf = [value]
            request._prf_last = dt
            return dt

    def prf_log(self):
        "Profileerimise logi salvestamine pöördumise lõpus"
        request = self.request
        try:
            liprf = request._liprf
        except:
            return
        if liprf:
            self.prf()
            MINLOG = 10
            total = request._prf_last - self.request._log_started.timestamp()
            if total >= MINLOG or self.c.user.isikukood and self.c.user.isikukood.startswith('test'):
                buf = 'PRF:%06.3f:%s %s\n' % (total, request.method, request.url)
                prev = None
                for elapse, txt in request._liprf:
                    line = '%.3f:%s\n' % (elapse, txt)
                    if elapse < .01:
                        # ei logi väikesi
                        prev = line
                    else:
                        if prev:
                            buf += prev
                            prev = None
                        buf += line
                self.log_add(const.LOG_TRACE, buf, 'PRF', oppekoht_id=int(total*100), kestus=total)
                
class HandledError(Exception):
    """Erind, mida kasutatakse protsessi katkestamiseks peale seda,
    kui mingi teine erind on kinni püütud ja töödeldud.
    """
    def __init__(self):
        pass

def rollback_callback(request):
    model.Session.rollback()
    model.Session.close()
    model.SessionR.close()
    model_s.DBSession.close()

    # vea korral kasutab ErrorController sama requesti
    # väldime kasutuslogi topeltkirje tegemist
    try:
        has_endlog = request.has_endlog
    except AttributeError:
        has_endlog = False

    if not has_endlog:
        # loome pöördumise kohta logikirje
        try:
            request.handler._log_params_end()
            request.handler.prf_log()
        except Exception as ex:
            log.error(ex)
        request.has_endlog = True

    # kõigi pöördumise kestel loodud logikirjete salvestamine
    logclient.flush_log(request)
    
def set_app_name(handler, settings):
    """Rakendusest sõltuvad seaded
    (teistes rakendustes see funktsioon asendatakse)
    """
    c = handler.c
    c.app_name = settings.get('app_name')
    if c.app_name == const.APP_EIS:
        c.app_eis = True
    elif c.app_name == const.APP_EKK:
        c.app_ekk = True

    # kas on ATS2020
    c.is_ats = (c.app_eis or c.app_ekk or c.app_eksam) and not handler.request.is_ext()
    c.inst_name = settings.get('inst_name')
    c.inst_title = settings.get('inst_title')
    
    c.is_devel = handler.is_devel
    c.is_test = handler.is_test
    c.is_live = handler.is_live

    session = handler.request.session
    try:
        # kasutaja on valinud värvid
        c.my_inst_name = session['my_inst_name']
    except:
        pass
