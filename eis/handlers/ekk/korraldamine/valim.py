from cgi import FieldStorage
from collections import defaultdict
from eis.lib.baseresource import *
_ = i18n._
from .valjastus import create_toimumisprotokollid, create_hindamisprotokollid
log = logging.getLogger(__name__)

class ValimController(BaseResourceController):
    """Sooritajate valimi laadimine isikukoodide failina.
    Testimiskorrast luuakse koopia, milles on ainult valimis olevate isikute osalemise andmed.
    P-testi korral ei kopeerita sisestatud tulemusi.
    E-testi korral kopeeritakse antud vastused.
    Algse testimiskorra tulemused on koolides hinnatud ja need jäävad sooritajatele nähtavaks.
    Innove hindab koopia-testimiskorras olevate valimisse kuuluvate sooritajate sooritused üle,
    kuid uusi tulemusi sooritajatele ei avaldata.
    """
    _permission = 'korraldamine'
    _INDEX_TEMPLATE = 'ekk/korraldamine/valim.mako'
    _actions = 'index,create'
    
    def _index_d(self):
        return self.render_to_response(self._INDEX_TEMPLATE)        

    def _search_protsessid(self, q):
        tkord = self.c.toimumisaeg.testimiskord
        q = (q.filter(model.Arvutusprotsess.test_id==tkord.test_id)
             .filter(model.Arvutusprotsess.testimiskord_id==tkord.id)
             .filter(model.Arvutusprotsess.liik==model.Arvutusprotsess.LIIK_VALIM)
             )
        return q
   
    def create(self):
        err = None
        params = self.request.params
        if params.get('laadi'):
            # uue valimi moodustamine failist, testimiskorra siseselt või uue testimiskorrana
            err = self._laadi()
        elif params.get('tyhista'):
            # testimiskorrasisese valimi tyhistamine
            self._tyhista_valim()
        elif params.get('loouus'):
            # testimiskorra sisesest valimit uue testimiskorra moodustamine
            err = self._loouus()
        if err:
            self.error(err)
        return HTTPFound(location=self.url('korraldamine_soorituskohad', toimumisaeg_id=self.c.toimumisaeg.id))

    def _tyhista_valim(self):
        "Testimiskorrasisese valimi tyhistamine"
        self.c.testimiskord.sisaldab_valimit = False
        q = (model.Session.query(model.Sooritaja)
             .filter(model.Sooritaja.testimiskord_id==self.c.testimiskord.id)
             .filter(model.Sooritaja.valimis==True))
        for j in q.all():
            j.valimis = False
        model.Session.commit()

    def _loouus(self):
        "Testimiskorra sisesest valimist eraldi testimiskorra loomine"
        q = (model.Session.query(model.Sooritaja.id)
             .filter_by(testimiskord_id=self.c.testimiskord.id)
             .filter_by(valimis=True))
        sooritajad_id = [j_id for j_id, in q.all()]
        if sooritajad_id:
            self._uustk(sooritajad_id)
        else:
            err = _("Testimiskorra sisese valimi sooritajaid ei ole")
            return err
        
    def _laadi(self):
        "Uue valimi moodustamine failist"
        err, sooritajad_id = self._sooritajad_failist()
        if err or not sooritajad_id:
            return err
        testimiskord = self.c.testimiskord
        uustk = self.request.params.get('uustk')
        if uustk:
            self._uustk(sooritajad_id)
        else:
            # valimi eraldamine algse testimiskorra siseselt
            q = (model.Session.query(model.Sooritaja)
                 .filter(model.Sooritaja.testimiskord_id==testimiskord.id))
            if testimiskord.sisaldab_valimit:
                # kui testimiskorra sisene valim oli juba varem olemas,
                # siis võtame senised valimi sooritajad valimist välja
                for j in q.filter(model.Sooritaja.valimis==True).all():
                    if j.id not in sooritajad_id:
                        j.valimis = False
            # praegu laaditud sooritajad määratakse valimisse
            for j in q.filter(model.Sooritaja.valimis==False).all():
                if j.id in sooritajad_id:
                    j.valimis = True
            testimiskord.sisaldab_valimit = True
            model.Session.commit()
            self.success(_("Valim on eraldatud"))

            # koolidele valimi teate saatmine
            cnt = send_valimiteade(self, testimiskord)
            if cnt:
                self.notice(_("Valimisse kuulumise teade saadeti {n} koolile").format(n=cnt))

    def _uustk(self, sooritajad_id):
        # valimi eraldamine uude testimiskorda
        buf = _("Valimi eraldamine")
        tk = self.c.testimiskord
        test = tk.test

        params = {'testimiskord': tk,
                  'test': test,
                  'liik': model.Arvutusprotsess.LIIK_VALIM,
                  'kirjeldus': buf,
                  }
            
        def childfunc(protsess):
            self._copy_tkord_set(protsess, tk, sooritajad_id)

        model.Arvutusprotsess.start(self, params, childfunc)
        self.success(_("Valimi eraldamise protsess on käivitatud"))
            
    def _sooritajad_failist(self):
        err = None
        sooritajad_id = []
        value = self.request.params.get('ik_fail')
        if not isinstance(value, FieldStorage):
            err = _("Faili ei leitud")
        else:
            tk = self.c.testimiskord
            # value on FieldStorage objekt
            value = value.value

            # faili sisuks on lahendajate isikukoodid, igayks ise real
            # aga võib olla ka semikooloneraldatud CSV, mille esimene veerg on isikukood
            # ja ylejäänud veerge ei arvestata
            missing = []
            q = (model.Session.query(model.Sooritaja.id)
                 .filter(model.Sooritaja.testimiskord_id==tk.id)
                 .filter(model.Sooritaja.staatus>const.S_STAATUS_TYHISTATUD)
                 .join(model.Sooritaja.kasutaja))
            for n_line, line in enumerate(value.splitlines()):
                line = utils.guess_decode(line)
                li = [s.strip() for s in line.split(';')]
                ik = li[0]
                if not ik:
                    continue
                usp = validators.IsikukoodP(ik)
                if not usp.isikukood:
                    err = _("Isikukoodide fail on vigane. Esimene vigane isikukood: {s}").format(s=ik)
                    break
                ik = usp.isikukood
                if ik in sooritajad_id or ik in missing:
                    # korduv isikukood
                    continue
                log.debug('%d. rida %s...' % (n_line, ik))
                res = q.filter(usp.filter(model.Kasutaja)).first()
                if res:
                    sooritajad_id.append(res[0])
                else:
                    missing.append(ik)

            if err:
                pass
            elif len(missing):
                s_missing = ', '.join(missing)
                if len(missing) == 1:
                    err = _("Testimiskorra {s1} sooritajate seas ei ole sooritajat isikukoodiga {s2}").format(s1=tk.tahised, s2=s_missing)
                else:
                    err = _("Testimiskorra {s1} sooritajate seas ei ole sooritajaid isikukoodidega {s2}").format(s1=tk.tahised, s2=s_missing)                    

            elif len(sooritajad_id) == 0:
                err = _("Valimis ei ole ühtki antud testimiskorra sooritajat")

        return err, sooritajad_id
    
    def _copy_tkord_set(self, protsess, tk, sooritajad_id):
        protsess_id = protsess and protsess.id or None
        tk_id = tk.id
        
        # loome koopia
        cp_tk_id = self._copy_tkord(protsess, tk, sooritajad_id)
        cp_tk = model.Testimiskord.get(cp_tk_id)
        tk = model.Testimiskord.get(tk_id)
        cp_tk.valim_testimiskord_id = tk_id
            
        # koopia ei ole mõeldud avaldamiseks, vaid Innoves töötlemiseks
        cp_tk.reg_sooritaja = False
        cp_tk.reg_sooritaja_alates = None
        cp_tk.reg_sooritaja_kuni = None
        cp_tk.reg_xtee = False
        cp_tk.reg_xtee_alates = None
        cp_tk.reg_xtee_kuni = None
        cp_tk.reg_kool_ehis = False
        cp_tk.reg_kool_eis = False
        cp_tk.reg_kool_alates = None
        cp_tk.reg_kool_kuni = None
        cp_tk.reg_ekk = False
        cp_tk.tulemus_kinnitatud = False
        cp_tk.statistika_arvutatud = False
        cp_tk.osalemise_naitamine = False
        cp_tk.tulemus_koolile = False
        cp_tk.tulemus_admin = False
        cp_tk.koondtulemus_avaldet = False
        cp_tk.koondtulemus_aval_kpv = None
        cp_tk.alatestitulemused_avaldet = False
        cp_tk.alatestitulemused_aval_kpv = None
        cp_tk.ylesandetulemused_avaldet = False
        cp_tk.ylesandetulemused_aval_kpv = None
        cp_tk.ylesanded_avaldet = False
        cp_tk.ylesanded_aval_kpv = None
        cp_tk.vaide_algus = None
        cp_tk.vaide_tahtaeg = None

        model.Session.flush()
        tk_tahised = cp_tk.tahised
        
        # arvutame sooritajate arvud
        if protsess:
            protsess.edenemisprotsent = 94
            model.Session.commit()
        model.Arvutusprotsess.trace(f'{tk_tahised} holekud...')
        for cp_ta in cp_tk.toimumisajad:
            cp_ta.update_hindamisolekud()

        if protsess:
            protsess.edenemisprotsent = 95
            model.Session.commit()

        model.Arvutusprotsess.trace(f'{tk_tahised} testikohad...')
        q = (model.Session.query(model.Testikoht)
             .join(model.Testikoht.toimumisaeg)
             .filter(model.Toimumisaeg.testimiskord_id==cp_tk_id))
        for cp_testikoht in q.all():
            max_tahis = (model.Session.query(sa.func.max(model.Sooritus.tahis))
                         .filter_by(testikoht_id=cp_testikoht.id)
                         .scalar())
            try:
                cp_testikoht.sooritused_seq = int(max_tahis)
            except:
                cp_testikoht.sooritused_seq = 0
            cp_testikoht.set_tahised()
        if protsess:
            protsess.edenemisprotsent = 96
            model.Session.commit()

        model.Arvutusprotsess.trace(f'{tk_tahised} testiruumid...')
        q = (model.Session.query(model.Testiruum)
             .join(model.Testiruum.testikoht)
             .join(model.Testikoht.toimumisaeg)
             .filter(model.Toimumisaeg.testimiskord_id==cp_tk_id))
        for cp_testiruum in q.all():
            cp_testiruum.set_sooritajate_arv()
        if protsess:
            protsess.edenemisprotsent = 97
            model.Session.commit()

        model.Arvutusprotsess.trace(f'{tk_tahised} testiprotokollid...')
        q = (model.Session.query(model.Testiprotokoll)
             .join(model.Testiprotokoll.testiruum)
             .join(model.Testiruum.testikoht)
             .join(model.Testikoht.toimumisaeg)
             .filter(model.Toimumisaeg.testimiskord_id==cp_tk_id))
        for cp_tpr in q.all():
            q = (model.Session.query(sa.func.count(model.Sooritus.id))
                 .filter_by(testiprotokoll_id=cp_tpr.id))
            cp_tpr.toodearv = q.filter(model.Sooritus.staatus>const.S_STAATUS_REGAMATA).scalar()
            cp_tpr.tehtud_toodearv = q.filter_by(staatus=const.S_STAATUS_TEHTUD).scalar()

        if protsess:
            protsess.edenemisprotsent = 98
        model.Session.commit()
        model.Arvutusprotsess.trace(f'{tk_tahised} toimumisprotokollid...')
        for cp_ta in cp_tk.toimumisajad:
            create_toimumisprotokollid(self, cp_ta)
            create_hindamisprotokollid(self, cp_ta)                    
        model.Session.commit()

        n_sooritajad = len(sooritajad_id)
        msg = "Loodud testimiskorra koopia {s} koos {n} sooritajaga".format(s=tk_tahised, n=n_sooritajad)
        model.Arvutusprotsess.trace(msg)
        if protsess:
            protsess.viga = msg
        
    def _copy_tkord(self, protsess, tk, sooritajad_id):
        self._copied_testikohad = dict()
        self._copied_testiruumid = dict()
        self._copied_testipaketid = dict()
        self._copied_testiprotokollid = dict()

        if protsess:
            protsess.edenemisprotsent = 2
            model.Session.commit()
        model.Arvutusprotsess.trace('testimiskord...')
        cp_tk = tk.copy(gen_tahis='VALIM')
        cp_tk.sisaldab_valimit = False
        tk_tahised = cp_tk.tahised
        # loome vastavuse toimumisaegade koopiate ja originaalide vahel
        map_ta = dict()
        map_paev = dict()
        for ta in tk.toimumisajad:
            model.Arvutusprotsess.trace(f'{tk_tahised} toimumisaeg {ta.tahised}...')
            for cp_ta in list(cp_tk.toimumisajad):
                log.debug('  cp_ta %s...' % (cp_ta.id))                
                cp_ta.tulemus_kinnitatud = False
                if cp_ta.testiosa_id == ta.testiosa_id:
                    map_ta[ta.id] = cp_ta
                    log.debug('  paevad...')
                    # loome vastavuse toimumispäevade koopiate ja originaalide vahel
                    for paev in ta.toimumispaevad:
                        log.debug('  paev=%s' % paev.id)
                        for cp_paev in cp_ta.toimumispaevad:
                            log.debug('    cp_paev=%s' % cp_paev.id)
                            if cp_paev.aeg == paev.aeg:
                                map_paev[paev.id] = cp_paev
                                break
                    break

        if protsess:
            protsess.edenemisprotsent = 3
        model.Session.commit()

        # kopeerime sooritajad, testikohad, testiruumid ja protokollid
        model.Arvutusprotsess.trace(f'{tk_tahised} sooritajad...')
        total = len(sooritajad_id)
        for sooritaja_id in sooritajad_id:
            sooritaja = model.Sooritaja.get(sooritaja_id)
            self._copy_sooritaja(sooritaja, cp_tk, map_ta, map_paev)
                
        if protsess:
            protsess.edenemisprotsent = 5
        model.Session.commit()
        cp_tk_id = cp_tk.id
        model.Arvutusprotsess.trace(f'{tk_tahised} vastused...')

        # kopeerime vastused
        protsess_id = protsess and protsess.id or None
        progress_start = 5
        progress_end = 93
        child_cnt = 25

        def _worker(min_id, max_id, data, pid):
            model.Arvutusprotsess.trace(f'{tk_tahised} sooritajad: {data}', pid)
            for ind, sooritaja_id in enumerate(data):
                sooritaja = model.Sooritaja.get(sooritaja_id)
                q = (model.Sooritaja.query
                     .filter_by(testimiskord_id=cp_tk_id)
                     .filter_by(kasutaja_id=sooritaja.kasutaja_id))
                cp_sooritaja = q.first()
                for sooritus in sooritaja.sooritused:
                    testiosa_id = sooritus.testiosa_id
                    cp_sooritus = cp_sooritaja.get_sooritus(testiosa_id=testiosa_id)
                    self._copy_vastused(sooritus, cp_sooritus)
            model.Session.commit()
            
        def _get_child_data(max_id, child_cnt):
            "Leiame portsu, mida korraga arvutada"
            min_n = max_id
            p_cnt = min(child_cnt, total-min_n)
            max_n = min_n + p_cnt
            data = sooritajad_id[min_n:max_n]
            return min_n, max_n, p_cnt, data

        rc = model.Arvutusprotsess.run_parallel(self,
                                                tk_tahised,
                                                total,
                                                child_cnt,
                                                _worker,
                                                _get_child_data,
                                                protsess_id,
                                                progress_start,
                                                progress_end)
        return cp_tk_id

    def _copy_sooritaja(self, sooritaja, cp_tk, map_ta, map_paev):
        ignore = ['testimiskord_id',
                  'nimekiri_id',
                  'piirkond_id',
                  'pallid',
                  'osapallid',
                  'tulemus_protsent',
                  'tulemus_piisav',
                  'yhisosa_pallid',
                  'hinne',
                  ]
        cp_sooritaja = sooritaja.copy(ignore=ignore,
                                      testimiskord=cp_tk,
                                      hindamine_staatus=const.H_STAATUS_HINDAMATA)
        for sooritus in sooritaja.sooritused:
            cp_ta = map_ta[sooritus.toimumisaeg_id]
            self._copy_sooritus(sooritus, cp_sooritaja, cp_ta, map_paev)

    def _copy_sooritus(self, sooritus, cp_sooritaja, cp_ta, map_paev):
        ignore = ['toimumisaeg_id',
                  'hindamine_staatus',
                  'pallid',
                  'pallid_arvuti',
                  'pallid_kasitsi',
                  'pallid_enne_vaiet',
                  'pallid_peale_vaiet',
                  'yhisosa_pallid',
                  'tulemus_protsent',
                  'testikoht_id',
                  'testiruum_id',
                  'testiarvuti_id',
                  'testiprotokoll_id',
                  ]
        cp_sooritus = sooritus.copy(ignore=ignore,
                                    toimumisaeg=cp_ta,
                                    sooritaja=cp_sooritaja,
                                    ylesanneteta_tulemus=False)
        if sooritus.testikoht_id and sooritus.testiruum_id:
            cp_testikoht = self._copy_testikoht(sooritus.testikoht, cp_ta)
            cp_sooritus.testikoht = cp_testikoht
            testiruum = sooritus.testiruum
            cp_testiruum = self._copy_testiruum(testiruum, cp_testikoht, map_paev)
            cp_sooritus.testiruum = cp_testiruum
            tpr = sooritus.testiprotokoll
            if tpr:
                cp_sooritus.testiprotokoll = self._copy_testiprotokoll(tpr,
                                                                       cp_testikoht,
                                                                       cp_testiruum)

    def _copy_vastused(self, sooritus, cp_sooritus):
        for sk in sooritus.soorituskomplektid:
            cp_sk = sk.copy(sooritus_id=cp_sooritus.id)
        for atos in sooritus.alatestisooritused:
            cp_atos = atos.copy(sooritus_id=cp_sooritus.id,
                                pallid=None,
                                pallid_enne_vaiet=None,
                                tulemus_protsent=None)
        for yv in sooritus.ylesandevastused:
            self._copy_yv(yv, cp_sooritus)
        for hv in sooritus.helivastused:
            cp_hv = hv.copy(ignore=['sooritus_id'], sooritus_id=cp_sooritus.id)

    def _copy_yv(self, yv, cp_sooritus):
        ignore = ['sooritus_id',        
                  'pallid',
                  'toorpunktid',
                  'pallid_arvuti',
                  'pallid_kasitsi',
                  'toorpunktid_enne_vaiet',
                  'pallid_enne_vaiet',
                  'yhisosa_pallid']
        cp_yv = yv.copy(ignore=ignore, sooritus_id=cp_sooritus.id)
        for kv in yv.kysimusevastused:
            self._copy_kv(kv, cp_yv)

    def _copy_kv(self, kv, cp_yv):
        ignore = ['ylesandevastus_id',
                  'toorpunktid',
                  'pallid',
                  'nullipohj_kood']
        cp_kv = kv.copy(ignore=ignore, ylesandevastus=cp_yv)
        for kvs in kv.kvskannid:
            kvs.copy(kysimusevastus=cp_kv)
        for kvs in kv.kvsisud:
            ignore = ['kysimusevastus_id',
                      'toorpunktid']
            kvs.copy(kysimusevastus=cp_kv, ignore=ignore)

    def _copy_testikoht(self, testikoht, cp_ta):
        cp = self._copied_testikohad.get(testikoht.id)
        if not cp:
            ignore = ['toimumisaeg_id',
                      'tahised']
            cp = testikoht.copy(ignore=ignore,
                                toimumisaeg=cp_ta,
                                sooritused_seq=0)
            self._copied_testikohad[testikoht.id] = cp
            cp.set_tahised()
        return cp

    def _copy_testiruum(self, testiruum, cp_testikoht, map_paev):
        cp = self._copied_testiruumid.get(testiruum.id)
        if not cp:
            cp_paev = map_paev.get(testiruum.toimumispaev_id)
            cp = testiruum.copy(toimumispaev=cp_paev,
                                testikoht=cp_testikoht,
                                sooritajate_arv=0,
                                valimis_arv=0)
            self._copied_testiruumid[testiruum.id] = cp

            # live baasis on ruumita testiruume mitu (uniq_toimumispaev), valimis teeme neile yhe testiruumi
            if not testiruum.ruum_id:
                for r2 in testiruum.testikoht.testiruumid:
                    if r2 != testiruum and not r2.ruum_id and r2.toimumispaev_id==testiruum.toimumispaev_id:
                        self._copied_testiruumid[r2.id] = cp
        return cp

    def _copy_testiprotokoll(self, tpr, cp_testikoht, cp_testiruum):
        cp = self._copied_testiprotokollid.get(tpr.id)
        if not cp:
            pakett = tpr.testipakett
            if pakett:
                cp_pakett = self._copy_testipakett(pakett, cp_testikoht, cp_testiruum)
            else:
                cp_pakett = None
            ignore = ['testipakett_id',
                      'testiruum_id']
            tahised = '%s-%s' % (cp_testikoht.tahised, tpr.tahis)        
            cp = tpr.copy(ignore=ignore,
                          testipakett=cp_pakett,
                          testiruum=cp_testiruum,
                          toodearv=None,
                          tehtud_toodearv=None,
                          tahised=tahised)
            self._copied_testiprotokollid[tpr.id] = cp
        return cp

    def _copy_testipakett(self, pakett, cp_testikoht, cp_testiruum):
        cp = self._copied_testipaketid.get(pakett.id)
        if not cp:
            ignore = ['testikoht_id',
                      'testiruum_id',
                      'valjastuskottidearv',
                      'valjastusymbrikearv',
                      'tagastuskottidearv',
                      'tagastusymbrikearv',
                      'erivajadustoodearv',
                      'filename',
                      'filesize',
                      'fileversion']
            cp = pakett.copy(ignore=ignore,
                             testikoht=cp_testikoht,
                             testiruum=pakett.testiruum and cp_testiruum or None)
            self._copied_testipaketid[pakett.id] = cp
        return cp
    
    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        self.c.testimiskord = self.c.toimumisaeg and self.c.toimumisaeg.testimiskord

def send_valimiteade(handler, testimiskord, protsess_id=None):
    "Valimi koolidele valimisse kuulumise teadete saatmine"
    test = testimiskord.test

    # kui protsess_id pole antud, siis saadetakse kõigile valimisse kuuluvatele koolidele
    koolid_id = None
    if protsess_id:
        # saata teated ainult nende isikukoodidega sooritajate koolidele 
        q = (model.Session.query(model.Sooritaja.kool_koht_id).distinct()
             .filter(model.Sooritaja.valimis==True)
             .filter(model.Sooritaja.testimiskord_id==testimiskord.id)
             .join((model.Kasutajaprotsess,
                    sa.and_(model.Kasutajaprotsess.kasutaja_id==model.Sooritaja.kasutaja_id,
                            model.Kasutajaprotsess.arvutusprotsess_id==protsess_id)))
             )
        koolid_id = [koht_id for koht_id, in q.all() if koht_id]
        if not koolid_id:
            # valitud isikukoodidega isikud pole valimis või ei õpi koolis
            return 0
        
    q = (model.Session.query(model.Sooritaja.kool_koht_id,
                             model.Sooritaja.klass,
                             sa.func.count(model.Sooritaja.id))
         .filter(model.Sooritaja.testimiskord_id==testimiskord.id)
         .filter(model.Sooritaja.valimis==True)
         .filter(model.Sooritaja.klass!=None)
         .filter(model.Sooritaja.kool_koht_id!=None)
         )
    if koolid_id:
        q = q.filter(model.Sooritaja.kool_koht_id.in_(koolid_id))
    q = (q.group_by(model.Sooritaja.kool_koht_id,
                   model.Sooritaja.klass)
         .order_by(model.Sooritaja.kool_koht_id,
                   model.Sooritaja.klass)
         )
    data = defaultdict(list)
    for koht_id, klass, cnt in q.all():
        data[koht_id].append((klass, cnt))
    is_live = handler.is_live
    host = handler.request.registry.settings.get('eis.pw.url')        
    # testi toimumise aeg
    millal = testimiskord.millal
    # kas valimil on sh eraldi aeg?
    q = (model.Session.query(model.Toimumispaev.aeg)
         .filter(model.Toimumispaev.valim==True)
         .join(model.Toimumispaev.toimumisaeg)
         .filter(model.Toimumisaeg.testimiskord_id==testimiskord.id)
         .order_by(model.Toimumispaev.aeg))
    millalvalim = []
    prev = None
    for aeg, in q.all():
        s_aeg = handler.h.str_from_date(aeg)
        if s_aeg != prev:
            prev = s_aeg
            millalvalim.append(s_aeg)
    if millalvalim:
        millalvalim = utils.joinand(millalvalim)

    cnt_sent = 0
    for koht_id, koht_data in data.items():
        koht = model.Koht.get(koht_id)

        # leiame kooli adminid ja nende aadressid
        tolist = []
        kasutajad = []
        for kasutaja in koht.get_admin():
            epost = kasutaja.epost
            if epost:
                if not is_live and not kasutaja.on_kehtiv_ametnik:
                    log.error(f'Testkeskkonnas ei saada kirja kasutajale {epost}')
                else:
                    tolist.append(epost)
                    kasutajad.append(kasutaja)

        if not tolist:
            continue

        klassid = ', '.join([f'{klass}.' for (klass, cnt) in koht_data])
        total = sum([cnt for (klass, cnt) in koht_data])
        # kooli registreerimise url
        url = f'{host}/eis/nimekirjad/testimiskorrad/{testimiskord.id}' # FIXURL
        params = {'kool_nimi': koht.nimi,
                  'klassid': klassid,
                  'opilastearv': total,
                  'test_nimi': test.nimi,
                  'on_testiliik_t': test.testiliik_kood == const.TESTILIIK_TASEMETOO,
                  'millal': millal,
                  'millalvalim': millalvalim,
                  'url': url,
                  'reg_alates': handler.h.str_from_date(testimiskord.reg_kool_alates),
                  'reg_kuni': handler.h.str_from_date(testimiskord.reg_kool_kuni),
                  'user_nimi': handler.c.user.fullname,
                  }

        # e-kirja kujul teate koostamine
        mako = 'mail/valimiteade.mako'
        subject, body = handler.render_mail(mako, params)

        # teate saatmine
        err = Mailer(handler).send(tolist, subject, body, out_err=False)
        if not err:
            teatekanal = const.TEATEKANAL_EPOST
            log.debug(_("Saadetud kiri aadressile {s}").format(s=', '.join(tolist)))

            # kirja salvestamine süsteemis
            kiri = model.Kiri(saatja_kasutaja_id=handler.c.user.id,
                              tyyp=model.Kiri.TYYP_KOOL_VALIM,
                              sisu=body,
                              teema=subject,
                              teatekanal=const.TEATEKANAL_EPOST)
            for k in kasutajad:
                model.Kirjasaaja(kiri=kiri, kasutaja_id=k.id, epost=k.epost, koht_id=koht.id)
            model.Session.commit()
            cnt_sent += 1

    # koolide arv, kellele saadeti teade
    return cnt_sent
        
