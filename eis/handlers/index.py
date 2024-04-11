from eis.lib.base import *
from eis.scripts.remove_filecache import check_filecache
_ = i18n._

log = logging.getLogger(__name__)

class IndexController(BaseController):
    """Avaleht
    """
    _authorize = False

    @action(renderer='avaleht.mako')
    def index(self):
        "Avalehe kuvamine"
        c = self.c
        mask = c.user.mask
        c.user.clear_cache() # optimeerimisvõimalus 
        c.user.mask = mask
        self.request.response.headers['X-Frame-Options'] = 'DENY'
        c.is_textbanner = c.app_eis
        if c.app_ekk or c.app_plank:
            if not c.user.is_authenticated:
                # eksamikeskuse vaates ei saa ilma sisse logimata midagi teha
                return HTTPFound(location=self.url('login', action='index'))
            # avaleheteateid ei kuva
            c.di_info = []
        elif c.app_eis:
            if c.user.is_authenticated and not c.user.testpw_id:
                # koostatakse teade, mis viib sooritamisvalmis testidele
                self._get_test_cnt()
                self._get_tulemus()
                self._get_regamine()
                
            # millisele grupile määratud teateid kuvada?
            if c.user.is_authenticated:        
                on_sooritaja = c.user.uiroll == const.UIROLL_S
                on_pedagoog = c.user.uiroll == const.UIROLL_K
                on_admin = c.user.on_avalikadmin
                opilane = c.user.get_kasutaja().opilane
                klass = opilane and opilane.klass or None
            else:
                on_sooritaja = on_pedagoog = on_admin = False
                klass = False
                
            # kas kasutaja soovis ka vanu teateid?
            c.arh = self.request.params.get('arh') and True or False
            # avalehe teated
            c.di_info = self._get_info(on_sooritaja, on_pedagoog, on_admin, klass, c.arh)
            
        return self.response_dict

    def _get_test_cnt(self):
        "Mitu testi on kasutajale sooritamiseks suunatud?"
        c = self.c
        q = (model.SessionR.query(model.sa.func.count(model.Sooritaja.id))
             .filter(model.Sooritaja.kasutaja_id==c.user.id)
             .join(model.Sooritaja.test)
             .filter(~ model.Sooritaja.testimiskord.has(
                 model.Testimiskord.sooritajad_peidus_kuni>=datetime.now()))
             .filter(~ model.Sooritaja.nimekiri.has(
                 model.sa.or_(model.Nimekiri.alates>date.today(),
                              model.Nimekiri.kuni<date.today())))
             .filter(model.Test.testiosad.any(model.Testiosa.vastvorm_kood.in_(
                 (const.VASTVORM_KE, const.VASTVORM_SE))))
             .filter(model.Sooritaja.staatus.in_(
                 (const.S_STAATUS_REGATUD,
                  const.S_STAATUS_ALUSTAMATA,
                  const.S_STAATUS_POOLELI,
                  const.S_STAATUS_KATKESTATUD)))
                  )

        cnt_test = q.scalar()
        if cnt_test == 1:
            c.info_test = _("Sulle on sooritamiseks suunatud 1 test")
        elif cnt_test > 1:
            c.info_test = _("Sulle on sooritamiseks suunatud {n} testi").format(n=cnt_test)
        else:
            c.info_test = ''

        if cnt_test:
            # kas on äsja alanud või kohe algamas teste?
            now = datetime.now()
            q = (q.with_entities(model.Sooritaja.id,
                                 model.Sooritaja.test_id,
                                 model.Test.nimi,
                                 model.Sooritus.kavaaeg)
                 .join(model.Sooritaja.sooritused)
                 .filter(model.Sooritus.kavaaeg > now - timedelta(minutes=20))
                 .filter(model.Sooritus.kavaaeg < now + timedelta(minutes=20))
                 .order_by(model.Sooritaja.id, model.Sooritus.algus)
                 )
            sooritajad_id = []
            li = []
            for j_id, test_id, nimi, algus in q.all():
                if j_id not in sooritajad_id:
                    sooritajad_id.append(j_id)
                    li.append((j_id, test_id, nimi, algus))
            c.praegu = li
            
    def _get_tulemus(self):
        "Kas hiljuti on tulemusi avaldatud?"
        c = self.c
        # viimase seitsme päeva jooksul avaldatud tulemused
        alates = date.today() - timedelta(days=7)
        q = (model.SessionR.query(model.Sooritaja.id, model.Test.nimi)
             .filter(model.Sooritaja.kasutaja_id==c.user.id)
             .join(model.Sooritaja.test)
             .filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
             .filter(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD)
             .join(model.Sooritaja.testimiskord)
             .filter(model.Test.osalemise_peitmine==False)
             .filter(model.Testimiskord.osalemise_naitamine==True)
             .filter(model.Testimiskord.koondtulemus_avaldet==True)
             .filter(model.Testimiskord.koondtulemus_aval_kpv>=alates)
             .order_by(sa.desc(model.Testimiskord.koondtulemus_aval_kpv),
                       model.Test.nimi)
             )
        li = []
        for j_id, t_nimi in q.all():
            url = self.url('tulemus', id=j_id)
            lnk = f'<a href="{url}">{t_nimi}</a>'
            li.append(lnk)
        if li:
            if len(li) == 1:
                buf = li[0]
            else:
                buf = ', '.join(li[:-1]) + _(" ja ") + li[-1]
            c.info_tulemus = _("Sinu {s} tulemused on selgunud!").format(s=buf)
        else:
            c.info_tulemus = ''

    def _get_regamine(self):
        "Kas regamine on avatud?"
        c = self.c
        c.info_reg = ''
        opilane = c.user.get_kasutaja().opilane
        if opilane and opilane.klass in ('12','G3','G12'):
            today = date.today()
            q = (model.SessionR.query(sa.func.count(model.Test.id))
                 .filter(model.Test.testiliik_kood==const.TESTILIIK_RIIGIEKSAM)
                 .join(model.Test.testimiskorrad)
                 .filter(model.Test.eeltest_id==None)
                 .filter(model.Test.avaldamistase==const.AVALIK_EKSAM)
                 .filter(model.Testimiskord.reg_sooritaja==True)
                 .filter(model.Testimiskord.reg_sooritaja_alates<=today)
                 .filter(model.Testimiskord.reg_sooritaja_kuni>=today)
                 .filter(model.Test.staatus==const.T_STAATUS_KINNITATUD)
                 )
            if q.scalar() > 0:
                c.info_reg = _("Avatud on registreerumine riigieksamitele.")
        
    def _get_info(self, on_sooritaja, on_pedagoog, on_admin, klass, arh=False):
        "Avalehe teadete küsimine"
        if on_admin:
            kellele = [model.Avaleheinfo.KELLELE_PEDAGOOG, model.Avaleheinfo.KELLELE_ADMIN]
        elif on_pedagoog:
            kellele = [model.Avaleheinfo.KELLELE_PEDAGOOG,]
        elif on_sooritaja:
            kellele = [model.Avaleheinfo.KELLELE_SOORITAJA,]
        else:
            kellele = []
        if klass:
            kellele.append(model.Avaleheinfo.KELLELE_OPILANE)
            if klass == '9':
                kellele.append(model.Avaleheinfo.KELLELE_OPILANE9)
        f_kellele = model.Avaleheinfo.kellele.ilike(model.Avaleheinfo.KELLELE_X + '%')
        for value in kellele:
            f_kellele = sa.or_(f_kellele, model.Avaleheinfo.kellele.ilike('%' + value + '%'))

        # vaikimisi otsitakse praegu kehtivaid teateid
        dt_min = dt_max = date.today()
        if arh:
            # soovitakse näidata ka vanu teateid (viimased 3 kuud)
            dt_min = utils.add_months(dt_min, -3)
        q = (model.SessionR.query(model.Avaleheinfo)
             .filter(model.Avaleheinfo.alates <= dt_max)
             .filter(model.Avaleheinfo.kuni >= dt_min)
             .filter(model.Avaleheinfo.tyyp != model.Avaleheinfo.TYYP_EMERGENCY)
             .filter(f_kellele)
             .order_by(sa.desc(model.Avaleheinfo.id))
             )
        di = {}
        for ai in q.all():
            _kellele = ai.kellele.split(',')
            found = model.Avaleheinfo.KELLELE_X
            # tsykkel yle kõigi sihtryhmade, mille kaudu kasutaja võib seda teadet näha
            for key in kellele:
                # tsykkel yle teate kõigi sihtryhmade
                if key in _kellele:
                    # leiti sihtryhm, mille kaudu kasutaja teadet nägi
                    # klassi õpilase teated kuvatakse "õpilaste" all
                    if key == model.Avaleheinfo.KELLELE_OPILANE9:
                        found = model.Avaleheinfo.KELLELE_OPILANE
                    else:
                        found = key
                    break
            if found in di:
                di[found].append(ai)
            else:
                di[found] = [ai]
        return di

    def check(self):
        "Monitooringupäring"
        class Trace:
            def __init__(self):
                self.diffs = []
                self.t1 = datetime.now()

            def prf(self, label):
                LIMIT = 1
                t2 = datetime.now()
                diff = (t2 - self.t1).total_seconds()
                if diff > LIMIT:
                    log.info(f'check:{label}:{diff}ms')
                self.t1 = t2
                self.diffs.append(diff)

        trc = Trace()
                
        try:
            # minio puhvri tyhjendamine
            check_filecache()
            trc.prf('filecache')
            
            # andmebaaside kontroll
            model.Session.query(1).scalar()
            trc.prf('eisdb RW')
            model.SessionR.query(1).scalar()
            trc.prf('eisdb RO')
            model_log.DBSession.query(1).scalar()
            trc.prf('eisdblog')
        except Exception as ex:
            status = 500
            log.error(ex)
        else:
            status = 200
        # vastus
        res = {'server_addr': os.getenv('HOSTNAME'),
               'ver': eis.__version__,
               'diff': trc.diffs,
               }
        return Response(json_body=res, status=status)

    def keepsess(self):
        "Seansi alles hoidmise päring ajal, kui kasutaja on SEBis"
        res = {'rc': self.c.user.has_seb_session(),
               }
        return Response(json_body=res)
    
    def locale(self):
        "Keele valik"
        response = Response()
        location = self.request.environ.get('HTTP_REFERER') or self.h.url('avaleht')
        language = self.request.params.get('locale') or self.request.matchdict.get('locale')
        if language:
            if self.is_cconsent():
                # kui kasutaja on lubanud kypsiste kasutamise
                if self.is_devel:
                    secure = False
                    samesite = 'lax'
                else:
                    secure = True
                    samesite = 'none'
                response.set_cookie('_LOCALE_', value=language, max_age=31536000, secure=secure, samesite=samesite, httponly=True)  # max_age = year
            else:
                self.error(_("Keele valikut ei saa meelde jätta, kuna puudub nõusolek küpsiste kasutamiseks"))

        return HTTPFound(location=location,
                         headers=response.headers)

    @action(renderer='kasutustingimused.mako')
    def kasutustingimused(self):
        "Andmetöötlustingimuste kuvamine"
        return self.response_dict

    def emergency(self):
        "Erakorralise teate sulgemine - jätame meelde, et seda enam ei näita"
        modified = self.request.matchdict.get('modified')
        # kasutamine: vt user.get_emergency()
        self.request.session['emergency_closed'] = modified
        self.request.session.changed()
        response = Response(json_body={'rc':'ok'})
        return response
    
    def cookieconsent(self):
        "Nõustumine küpsiste kasutamisega"
        # cookie väärtuse osad:
        # - versioon (1)
        # - logikirje ID
        # - kas on luba mittevajalike kypsiste jaoks (0 ei ole luba, 1 on luba)
        various = (self.request.params.get('various') == '1') and 1 or 0
        response = Response(json_body={'rc': 'ok'})
        param = self._get_log_params()
        logi_id = self.log_add(const.LOG_USER,
                               None,
                               param and str(param) or None,
                               kontroller=self.c.controller,
                               tegevus=self.c.action)
        value = '1-%s-%s' % (logi_id or 1, various)
        # samesite=none requires secure=true
        if self.is_devel:
            secure = False
            samesite = 'lax'
        else:
            secure = True
            samesite = 'none'
        response.set_cookie('eis-cookieconsent', value=value, max_age=31536000, samesite=samesite, secure=secure, httponly=True)
        return response

    def showcookieconsent(self):
        "Küpsiste nõusoleku kaotamise nupp"
        return self.render_to_response('/common/cookieconsent.mako')

    def deletecookieconsent(self):
        "Kustutada küpsised"
        session_key = self.request.registry.settings['session.key']
        response = Response()
        for key in self.request.cookies:
            if key != session_key:
                response.delete_cookie(key)
        self.success(_("Küpsised kustutatud!"))
        return HTTPFound(location=self.url('avaleht'),
                         headers=response.headers)

    def avalehepilt(self):
        "Avalehel kuvatav pilt"
        id = self.request.matchdict.get('id')
        item = model.Avalehepilt.getR(id)
        filename = filedata = mimetype = None
        if item and item.has_file:
            filepath = item.path_for_response
            filename = item.filename
            mimetype = item.mimetype
            return utils.cache_download(self.request, filepath, filename, mimetype)
        else:
            return HTTPNotFound()
    
    @action(renderer='common/message.mako')
    def message(self):
        "Ainult teate kuvamine (kasutatakse siis, kui ei kasutata tervet akent)"
        return self.response_dict

    def _is_log_params(self):
        if self.c.action == 'cookieconsent':
            # juba logitud
            return False
        return BaseController._is_log_params(self)

    def response_on_error(self, error):
        "Vea korral antav vastus"
        if self.c.action in ('check', 'keepsess'):
            # jsoni vastus
            res = {'error': error}
            return Response(json_body=res, status=500)
        else:
            return super().response_on_error(error)
        
