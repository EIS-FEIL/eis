import os
from simplejson import dumps
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.resultentry import ResultEntry
from eis.lib.resultstat import ResultStat
from eis.lib.pdf.kinnitamislisa import KinnitamislisaDoc
from eis.lib.examclient import ExamClient

log = logging.getLogger(__name__)

class ArvutusedController(BaseResourceController):
    _permission = 'ekk-hindamine'
    _INDEX_TEMPLATE = 'ekk/hindamine/arvutused.mako'
    _log_params_post = True
    
    def _c_index_params(self):
        # parameetrid c sisse
        has_params = self._has_search_params()
        # kui pole parameetreid antud, siis vaatame, kas neid on varasemast meeles
        if has_params:
            self.form = Form(self.request, schema=self._SEARCH_FORM, method='GET')
            self.form.validate()
            self._copy_search_params(self.form.data, save=True)
        else:
            default_params = not has_params and self._get_default_params()
            self._copy_search_params(default_params)        
        if not self.c.koik_kogumid:
            if not self.c.hindamiskogum_id and not self.c.ty_id:
                self.c.koik_kogumid = True

    def index(self):
        sub = self._get_sub()
        if sub and sub != 'staatus':
            return eval('self._index_%s' % sub)()

        self._c_index_params()
        c = self.c

        if c.testimiskord.sisaldab_valimit:
            c.cnts = self._get_cnt(False)
            c.cnts_valim = self._get_cnt(True)
            c.sisaldab_valimit = True
            c.cnt_arvutamata = c.cnts.arvutamata + c.cnts_valim.arvutamata
        else:
            c.cnts = self._get_cnt(None)
            c.sisaldab_valimis = False
            c.cnt_arvutamata = c.cnts.arvutamata

        c.err_hindamise_luba = self._check_hindamise_luba()
        self._get_protsessid()

        return self.render_to_response(self._INDEX_TEMPLATE)

    def _check_hindamise_luba(self):
        "Kui hindamise algus on läbi, aga luba puudub, siis kuvatakse teade"
        if not self.c.toimumisaeg.hindamise_luba:
            h_algus = self.c.toimumisaeg.hindamise_algus
            if h_algus and h_algus < datetime.now():
                s_algus = self.h.str_from_datetime(h_algus, hour0=False)
                return _("Hindamine algas {dt}, kuid hindamise lubamise märge puudub!").format(dt=s_algus)
            
    def _get_cnt(self, valimis):
        "Leitakse hinnatavate tööde arvud, alustamata tööde arvud jm arvud"
        c = self.c
        cnts = NewItem()
        testiosa = c.testiosa
        
        q = (model.SessionR.query(sa.func.count(model.Sooritus.id))
             .filter(model.Sooritus.toimumisaeg_id==c.toimumisaeg.id)
             .join(model.Sooritus.sooritaja))
        if valimis:
            q = q.filter(model.Sooritaja.valimis==True)
        elif valimis == False:
            q = q.filter(model.Sooritaja.valimis==False)

        # kui palju oli puudujaid
        q1 = q.filter(model.Sooritus.staatus==const.S_STAATUS_PUUDUS)
        cnts.puudus = q1.scalar()

        # kui palju on hinnatavaid sooritusi
        q2 = q.filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
        cnts.tehtud = q2.scalar()
        
        # kui paljude soorituste tulemused on arvutatud
        cnts.arvutatud = q2.filter(model.Sooritus.hindamine_staatus==const.H_STAATUS_HINNATUD).scalar()
        
        # kui paljude soorituste tulemusi ei ole arvutatud
        cnts.arvutamata = q2.filter(model.Sooritus.hindamine_staatus<const.H_STAATUS_HINNATUD).scalar()

        # kui paljudel sooritustel on hindamisprobleeme
        li = []
        cnt = (q2.filter(model.Sooritus.hindamisolekud.any(
            model.Hindamisolek.hindamisprobleem==const.H_PROBLEEM_SISESTAMATA))
               .scalar())
        if cnt > 0:
            if testiosa.vastvorm_kood not in (const.VASTVORM_KP, const.VASTVORM_SP):
                li.append(_("hindamata {n}").format(n=cnt))
            else:
                li.append(_("sisestamata {n}").format(n=cnt))
            
        cnt = (q2.filter(model.Sooritus.hindamisolekud.any(
            model.Hindamisolek.hindamisprobleem==const.H_PROBLEEM_SISESTUSERINEVUS))
               .scalar())
        if cnt > 0:
            li.append(_("sisestusvead {n}").format(n=cnt))

        cnt = (q2.filter(model.Sooritus.hindamisolekud.any(
            model.Hindamisolek.hindamisprobleem==const.H_PROBLEEM_HINDAMISERINEVUS))
               .scalar())
        if cnt > 0:
            li.append(_("hindamiserinevused {n}").format(n=cnt))

        cnt = (q2.filter(model.Sooritus.hindamisolekud.any(
            model.Hindamisolek.hindamisprobleem==const.H_PROBLEEM_TOOPUUDU))
               .scalar())
        if cnt > 0:
            li.append(_("töö puudu {n}").format(n=cnt))
        cnts.probleemid = ', '.join(li)

        # tegemata soorituste arvud
        if testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I, const.VASTVORM_SH):
            cnts.alustamata = q.filter(model.Sooritus.staatus.in_(
                (const.S_STAATUS_REGATUD, const.S_STAATUS_ALUSTAMATA))).scalar()
            cnts.pooleli = q.filter(model.Sooritus.staatus==const.S_STAATUS_POOLELI).scalar()
            if cnts.pooleli:
                if testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I):
                    max_aeg = None
                    qk = (model.SessionR.query(model.Klaster.int_host)
                          .filter_by(staatus=const.B_STAATUS_KEHTIV))
                    for exapi_host, in qk.all():
                        aeg = ExamClient(self, exapi_host).max_pooleli(c.toimumisaeg.id, valimis)
                        if aeg and (not max_aeg or max_aeg < aeg):
                            max_aeg = aeg
                    cnts.max_pooleli_aeg = max_aeg

        # kinnitamata protokollide arv
        q = (model.SessionR.query(sa.func.count(model.Toimumisprotokoll.id))
             .join(model.Toimumisprotokoll.testikoht)
             .filter(model.Testikoht.toimumisaeg_id==c.toimumisaeg.id)
             .filter(model.Toimumisprotokoll.staatus==const.B_STAATUS_KEHTIV)
             )
        if valimis:
            q = q.filter(sa.exists().where(
                sa.and_(model.Sooritaja.valimis==True,
                        model.Sooritaja.id==model.Sooritus.sooritaja_id,
                        model.Sooritus.testikoht_id==model.Testikoht.id)))
        elif valimis == False:
            q = q.filter(sa.exists().where(
                sa.and_(model.Sooritaja.valimis==False,
                        model.Sooritaja.id==model.Sooritus.sooritaja_id,
                        model.Sooritus.testikoht_id==model.Testikoht.id)))

        cnts.prot_kinnitamata = q.scalar()

        return cnts

    def _search_protsessid(self, q):
        tkord = self.c.testimiskord
        q = (q.filter(model.Arvutusprotsess.test_id==tkord.test_id)
             .filter(sa.or_(model.Arvutusprotsess.toimumisaeg_id==self.c.toimumisaeg.id,
                            model.Arvutusprotsess.toimumisaeg_id==None))
             )
        if tkord.analyys_eraldi:
            q = q.filter(model.Arvutusprotsess.testimiskord_id==tkord.id)
        else:
            q = q.filter(sa.or_(model.Arvutusprotsess.testimiskord_id==tkord.id,
                                model.Arvutusprotsess.testimiskord_id==None))
        return q

    def _create_kinnitamine(self):
        """Tulemuste kinnitamine
        """
        params = self.request.params
        if params.get('kinnita'):
            q = (model.Sooritus.query
                 .filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id)
                 .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
                 .filter(model.Sooritus.hindamine_staatus!=const.H_STAATUS_TOOPUUDU)
                 .filter(sa.or_(model.Sooritus.ylesanneteta_tulemus==None,
                                model.Sooritus.ylesanneteta_tulemus==False))
                 .filter(model.Sooritus.pallid==None)
                 .join(model.Sooritus.sooritaja))
            test = self.c.toimumisaeg.testiosa.test
            if not test.diagnoosiv and q.count() > 0:
                self.error(_("Tulemusi ei saa kinnitada, kuna kõik tulemused pole arvutatud"))
            else:
                self.c.toimumisaeg.hinnete_sisestus = False
                self.c.toimumisaeg.tulemus_kinnitatud = True
                kord = self.c.testimiskord
                kord.tulemus_kinnitatud = all([ta.tulemus_kinnitatud for ta in kord.toimumisajad \
                                               if ta.id != self.c.toimumisaeg.id])
                model.Session.commit()
                self.success(_("Tulemused on kinnitatud"))

        elif params.get('syrra'):
            if self.c.user.on_admin or self.c.test.testityyp == const.TESTITYYP_AVALIK:
                self.c.toimumisaeg.hinnete_sisestus = True
                self.c.toimumisaeg.tulemus_kinnitatud = False
                self.c.toimumisaeg.testimiskord.tulemus_kinnitatud = False
                model.Session.commit()
                self.success(_("Tulemuste kinnitus on eemaldatud"))

        return self._redirect('index')                      

    def _create_staatus(self):
        """Pooleli olekus soorituste lõpetamine (kui protokoll on jäetud täitmata)
        """
        params = self.request.params
        staatus = int(params.get('staatus'))
        valimis = params.get('valimis')
        q = (model.Session.query(model.Sooritaja, model.Sooritus.id)
             .join(model.Sooritaja.sooritused)
             .filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id)
             )
        if valimis == '1':
            q = q.filter(model.Sooritaja.valimis==True)
        elif valimis == '0':
            q = q.filter(model.Sooritaja.valimis==False)

        staatus2 = None
        if staatus == const.S_STAATUS_ALUSTAMATA:
            q = q.filter(model.Sooritus.staatus.in_(
                (const.S_STAATUS_REGATUD, const.S_STAATUS_ALUSTAMATA)))
            staatus2 = const.S_STAATUS_PUUDUS
        elif staatus == const.S_STAATUS_POOLELI:
            q = q.filter(model.Sooritus.staatus==staatus)
            staatus2 = const.S_STAATUS_TEHTUD

        if staatus2:
            for sooritaja, sooritus_id in q.all():
                for sooritus in sooritaja.sooritused:
                    if sooritus.id == sooritus_id:
                        if staatus2 == const.S_STAATUS_TEHTUD:
                            # vajadusel lõpetame klastris
                            self._end_test(sooritaja, sooritus, self.c.toimumisaeg, self.c.testiosa, staatus2, None)
                        if sooritus.staatus != staatus2:
                            sooritus.set_staatus(staatus2)
                        break
                sooritaja.update_staatus()
            model.Session.commit()
            self.success(_("Edukalt muudetud"))
        return self._redirect('index')                      

    def _end_test(self, sooritaja, sooritus, toimumisaeg, testiosa, staatus, stpohjus):
        "Lõpetame pooleliolevad testid"
        test = self.c.test
        if sooritaja.klaster_id and sooritus.klastrist_toomata:
            host = model.Klaster.get_host(sooritaja.klaster_id)
            if host:
                # lõpetame testi
                sooritused_id = [sooritus.id]
                alatestid = []
                kirjalik = jatk_voimalik = None
                ExamClient(self, host).set_staatus(sooritus.testiruum_id,
                                                   sooritused_id,
                                                   staatus,
                                                   stpohjus,
                                                   testiosa,
                                                   alatestid,
                                                   kirjalik,
                                                   jatk_voimalik)
                # toome soorituse kirje keskserverisse
                ExamSaga(self).from_examdb(host, sooritus, sooritaja, test, testiosa, toimumisaeg, sooritaja.lang, True)
    
    def _create_hluba(self):
        "Hindamise loa andmine/võtmine"
        params = self.request.params
        self.c.toimumisaeg.hindamise_luba = params.get('luba') == '1'
        model.Session.commit()
        err = self._check_hindamise_luba()
        if err:
            html = self.h.alert_warning(err, False)
        else:
            html = ''
        return Response(html)
    
    def _create_prot(self):
        """Kõigi kinnitamata protokollide kinnitamine ES-2057
        """
        c = self.c
        valimis = self.request.params.get('valimis')
        
        # katkestanud soorituste staatuse muutmine KATKESTATUD > KATKESPROT
        q = (model.Sooritus.query
             .filter(model.Sooritus.toimumisaeg_id==c.toimumisaeg.id)
             .filter(model.Sooritus.staatus == const.S_STAATUS_KATKESTATUD)
             )
        if valimis == '1':
            q = q.join(model.Sooritus.sooritaja).filter(model.Sooritaja.valimis==True)
        elif valimis == '0':
            q = q.join(model.Sooritus.sooritaja).filter(model.Sooritaja.valimis==False)

        for sooritus in q.all():
            sooritus.set_staatus(const.S_STAATUS_KATKESPROT)
            sooritus.sooritaja.update_staatus()

        # protokollide kinnitamine
        cnt = 0
        q = (model.Session.query(model.Toimumisprotokoll)
             .join(model.Toimumisprotokoll.testikoht)
             .filter(model.Testikoht.toimumisaeg_id==c.toimumisaeg.id)
             .filter(model.Toimumisprotokoll.staatus==const.B_STAATUS_KEHTIV)
             )
        if valimis == '1':
            q = q.filter(sa.exists().where(
                sa.and_(model.Sooritaja.valimis==True,
                        model.Sooritaja.id==model.Sooritus.sooritaja_id,
                        model.Sooritus.testikoht_id==model.Testikoht.id)))
        elif valimis == '0':
            q = q.filter(sa.exists().where(
                sa.and_(model.Sooritaja.valimis==False,
                        model.Sooritaja.id==model.Sooritus.sooritaja_id,
                        model.Sooritus.testikoht_id==model.Testikoht.id)))

        for tprot in q.all():
            tprot.staatus = const.B_STAATUS_EKK_KINNITATUD
            cnt += 1
        if cnt:
            model.Session.commit()
            self.success(_("Kinnitatud {n} protokolli").format(n=cnt))

        return self._redirect('index')                      

    def create(self):
        """Arvutusprotsessi käivitamine
        """
        params = self.request.params
        sub = params.get('sub')
        if sub:
            if sub == 'staatus':
                return self._create_staatus()
            elif sub == 'prot':
                return self._create_prot()
            elif sub == 'avaldamine':
                return self._create_avaldamine()
            elif sub == 'hluba':
                return self._create_hluba()
            return self._redirect('index')

        if params.get('kinnita') or params.get('syrra'):
            # testimiskorra tulemuste kinnitamine
            return self._create_kinnitamine()
        
        lvtood = params.get('lvtood')
        stat = params.get('stat')
        statv = params.get('statv')
        statt = params.get('statt')

        if not stat or (not statv and not statt):
            statv = statt = True            
        
        debug = params.get('debug')
        clu6 = params.get('clu6')
        args = {'hindamiskogum_id': params.getall('hindamiskogum_id'),
                'ty_id': params.getall('ty_id'),
                'debug': debug,
                'clu6': clu6,
                'statv': statv,
                'statt': statt,
                }
        # superserverisse suunab makos clu6 prefiksiga URL
        
        protsess_tkord = tkord = self.c.testimiskord
        olen_admin = self.c.user.on_admin
        if params.get('kontrollitud'):
            # märgime testimiskorra tulemused kontrollituks
            if olen_admin:
                tkord.tulemus_kontrollitud = True
                model.Session.commit()
            return self._redirect('index', **args)

        if tkord.tulemus_kontrollitud and not olen_admin:
            self.error('Tulemused on juba kontrollitud. Ainult administraator saab arvutusi käivitada')
            return self._redirect('index', **args)

        # algatame uue arvutamise
        if stat:
            liik = model.Arvutusprotsess.LIIK_STATISTIKA
            lis = []
            if statv:
                lis.append(_("Vastuste statistika"))
            if statt:
                lis.append(_("Vastuste väljavõte"))
            if len(lis) == 2:
                kirjeldus = _("Statistika arvutamine")
            else:
                kirjeldus = ', '.join(lis)
            toimumisaeg = None
            if not tkord.analyys_eraldi:
                protsess_tkord = None

            # arvutame ühisosa - siit võib tulla vigu ja see käib kiiresti
            buf = tkord.test.calc_yhisosa()
            if buf:
                self.error(buf)
                return self._redirect('index', **args)

        elif lvtood:
            liik = model.Arvutusprotsess.LIIK_TULEMUSED
            kirjeldus = _("Tööde arvu arvutamine")
            toimumisaeg = self.c.toimumisaeg
        else:
            liik = model.Arvutusprotsess.LIIK_TULEMUSED
            kirjeldus = _("Tulemuste arvutamine")
            toimumisaeg = self.c.toimumisaeg

        # tulemuste ja statistika arvutamine on võimalik hindamiskogumite või ylesannete kaupa
        if not lvtood:
            tapsustus = ''
            # kui ei arvutata kõiki kogumeid, siis lisame kirjeldusse, millised kogumid
            spec = self._specify(params)
            if not spec.koik_kogumid:
                if spec.tyy_id:
                    # on valitud ylesanded
                    q = (model.Session.query(model.Testiylesanne.tahis)
                        .filter(model.Testiylesanne.id.in_(spec.tyy_id)))
                    tapsustus = "ül " + ', '.join([tahis for tahis, in q.all() if tahis])
                elif spec.kogumid_id:
                    # on valitud hindamiskogumid
                    q = (model.Session.query(model.Hindamiskogum.tahis)
                         .filter(model.Hindamiskogum.id.in_(spec.kogumid_id))
                         .order_by(model.Hindamiskogum.tahis))
                    tapsustus = ', '.join([tahis for tahis, in q.all()])
                    
                else:
                    buf = _("Palun valida hindamiskogumid või ülesanded")
                    self.error(buf)
                    return self._redirect('index', **args)
        
            if tapsustus:
                kirjeldus += f' ({tapsustus})'
                    
        # märgime varasemad protsessid lõppenuks (katkestatuks),
        # mis paistavad pooleli olevat
        for rcd in self._query_protsessid(True):
            rcd.lopp = datetime.now()
        model.Session.commit()          
        
        toimumisaeg_id = self.c.toimumisaeg.id

        def childfunc(rcd):
            "Arvutuste tegemise funktsioon"
            if stat:
                self._calculate_stat(rcd, statv, statt, spec)
            elif lvtood:
                self._calculate_labiviijad(toimumisaeg_id)
            else:
                tahised = isikukood = None
                if debug:
                    if len(debug) == 11:
                        isikukood = debug
                    elif len(debug) > 6:
                        tahised = debug
                self._calculate_result(rcd, spec, tahised=tahised, isikukood=isikukood)
                self._calculate_labiviijad(toimumisaeg_id)

        params = {'toimumisaeg': toimumisaeg,
                  'testimiskord': protsess_tkord,
                  'test': tkord.test,
                  'liik': liik,
                  'kirjeldus': kirjeldus}
        model.Arvutusprotsess.start(self, params, childfunc)
        
        # deemon käivitatud, naaseme kasutaja juurde
        self.success(_("Arvutusprotsess on käivitatud"))
        return self._redirect('index', **args)

    def _specify(self, params):
        "Kas on täpsustatud, millised ülesanded arvutada"
        
        # kas arvutada kõik hindamiskogumid
        koik_kogumid = params.get('koik_kogumid')
        # kas arvutada valitud hindamiskogumid
        kogumid_id = params.getall('hindamiskogum_id')
        # või arvutada valitud ylesanded
        tyy_id = params.getall('ty_id')
        if not koik_kogumid and kogumid_id:
            # kasutaja valis hindamiskogumid
            kogumid_id = list(map(int, kogumid_id))
        if not koik_kogumid and tyy_id:
            # kasutaja valis ylesanded
            tyy_id = list(map(int, tyy_id))
            # leiame valitud ylesandeid sisaldavad hindamiskogumid
            if self.c.testiosa.lotv:
                q = (model.Session.query(model.Valitudylesanne.hindamiskogum_id).distinct()
                     .filter(model.Valitudylesanne.testiylesanne_id.in_(tyy_id)))
            else:
                q = (model.Session.query(model.Testiylesanne.hindamiskogum_id).distinct()
                     .filter(model.Testiylesanne.id.in_(tyy_id)))
            kogumid_id = [hk_id for hk_id, in q.all()]
        class SelectedY:
            pass
        spec = SelectedY()
        spec.koik_kogumid = koik_kogumid
        spec.kogumid_id = kogumid_id
        spec.tyy_id = tyy_id
        return spec
    
    def _calculate_result(self, protsess, spec, tahised=None, isikukood=None):
        """Tulemuste arvutamise protsessi sisu
        """
        params = self.request.params
        protsess_id = protsess and protsess.id or None

        ta = self.c.toimumisaeg
        toimumisaeg_id = self.c.toimumisaeg.id
        testiosa = self.c.toimumisaeg.testiosa
        testiosa_id = testiosa.id

        # valimi korral: kas kanda yle lõplikud tulemused algsest testimiskorrast
        kannayle = params.get('kannayle')
        # toimumisaeg, millelt tulemused yle kanda
        kanna_ta = kannayle and ta.testimiskord.valim_testimiskord.get_toimumisaeg(testiosa)
        kanna_ta_id = kanna_ta and kanna_ta.id or None
        # kontrollime üle, mis on vajalikud hindamiskogumid
        # korraldaja võis olla nende parameetreid vahepeal muutnud
        hindamistasemed = {}
        kehtivad_kogumid_id = []
        for hk in testiosa.hindamiskogumid:
            if hk.staatus == const.B_STAATUS_KEHTIV:
                kehtivad_kogumid_id.append(hk.id)
                for valimis in (False, True):
                    hindamistase = hk.get_hindamistase(valimis, ta)
                    hindamistasemed[hk.id, valimis] = hindamistase

        # leiame sooritused, mille tulemusi arvutada
        q = (model.Session.query(model.Sooritus.id)
             .filter(model.Sooritus.toimumisaeg_id==toimumisaeg_id)
             .filter(model.Sooritus.staatus.in_((const.S_STAATUS_TEHTUD,
                                                 const.S_STAATUS_EEMALDATUD,
                                                 const.S_STAATUS_PUUDUS,
                                                 const.S_STAATUS_VABASTATUD,
                                                 const.S_STAATUS_KATKESPROT)))
             )
        if tahised:
            q = q.filter(model.Sooritus.tahised==tahised)
        elif isikukood:
            q = (q.join(model.Sooritus.sooritaja)
                 .join(model.Sooritaja.kasutaja))
            usp = validators.IsikukoodP(isikukood)
            q = q.filter(usp.filter(model.Kasutaja))

        koguminfo = (spec, kehtivad_kogumid_id, hindamistasemed)
        label = 'Tulemused (ta %d) %s' % (toimumisaeg_id, ta.tahised)

        def _calculate_sooritused(min_id, max_id, data, pid):
            "Alamprotsessi arvutus"
            ta = testiosa_id and model.Toimumisaeg.get(testiosa_id) or None
            testiosa = model.Testiosa.get(testiosa_id)
            kanna_ta = kanna_ta_id and model.Toimumisaeg.get(kanna_ta_id) or None
            q1 = q.filter(model.Sooritus.id >= min_id)
            if max_id:
                q1 = q1.filter(model.Sooritus.id <= max_id)
            for pn, (sooritus_id,) in enumerate(q1.all()):
                if os.getppid() == 1:
                    # parent on surnud, lõpetame ise ka ära
                    break
                tos = model.Sooritus.get(sooritus_id)
                model.Arvutusprotsess.trace('%d. %s sooritus %s...' % (pn, toimumisaeg_id, tos.tahised), pid)
                self._calculate_sooritus(tos, testiosa, ta, kanna_ta, koguminfo)
            model.Session.commit()

        def _get_child_data(max_id, child_cnt):
            "Leiame portsu, mida korraga arvutada"
            if max_id:
                q1 = q.filter(model.Sooritus.id > max_id)
            else:
                q1 = q
            sooritused_id = list()
            min_id = max_id = None
            p_cnt = 0
            for sooritus_id, in q1.order_by(model.Sooritus.id):
                p_cnt += 1
                if min_id is None:
                    min_id = sooritus_id
                if p_cnt >= child_cnt:
                    # ports sai täis
                    max_id = sooritus_id
                    break
            return min_id, max_id, p_cnt, None

        total = q.count()
        progress_start = 0.
        progress_end = 100.
        child_cnt = 25
        rc = model.Arvutusprotsess.run_parallel(self,
                                                label,
                                                total,
                                                child_cnt,
                                                _calculate_sooritused,
                                                _get_child_data,
                                                protsess_id,
                                                progress_start,
                                                progress_end)                
        if rc:
            self._calc_hindamine3(toimumisaeg_id)
            model.Session.commit()
    
    def _calculate_sooritus(self, tos, testiosa, ta, kanna_ta, koguminfo):
        spec, kehtivad_kogumid_id, hindamistasemed = koguminfo
        sooritaja = tos.sooritaja
        if tos.klastrist_toomata and sooritaja.klaster_id:
            # tõmbame soorituse andmed klastrist
            host = model.Klaster.get_host(sooritaja.klaster_id)
            ExamSaga(self).from_examdb(host, tos, sooritaja, sooritaja.test, testiosa, ta, sooritaja.lang, False)
            
        resultentry = ResultEntry(self, None, testiosa.test, testiosa)
        valimis = sooritaja.valimis
        on_vaie = sooritaja.vaie_esitatud and True or False
        if on_vaie:
            # vaidlustatud töid hinnatakse alati pallide järgi, sest vaide-ekspert annab ainult palle
            resultentry.sisestusviis = const.SISESTUSVIIS_PALLID
        elif testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I):
            # kirjaliku e-testi töid hinnatakse alati vastuste järgi
            resultentry.sisestusviis = const.SISESTUSVIIS_VASTUS
        else:
            # muidu hinnatakse vastavalt ylesande sisestusviisile
            resultentry.sisestusviis = None

        if tos.staatus == const.S_STAATUS_TEHTUD:
            # valimi korral leiame algse testimiskorra soorituse, kust tulemused võtta
            kanna_tos = None
            if kanna_ta:
                kasutaja_id = sooritaja.kasutaja_id
                for kanna_tos in kanna_ta.get_sooritused(kasutaja_id=kasutaja_id):
                    break

            if not tos.ylesanneteta_tulemus:
                # ei arvuta siis, kui tulemused on sisestatud toimumise protokollile
                tos.give_hindamisolekud()

                # e-hindamise korral lisame puuduvad vastused statistika jaoks
                # ei lisa puuduvaid vastuseid p-hindamise korral, sest siis ei pea vastuseid andmebaasis alati olema
                resultentry.add_missing_kv(tos)

                if spec.koik_kogumid:
                    tyy_id = kogumid_id = None
                else:
                    tyy_id = spec.tyy_id
                    kogumid_id = spec.kogumid_id

                # arvutame kõigi hindamisolekute tulemused
                for holek in tos.hindamisolekud:
                    if holek.hindamiskogum_id not in kehtivad_kogumid_id:
                        # hindamiskogumeid on peale sooritamist muudetud
                        pass
                    elif not kogumid_id or holek.hindamiskogum_id in kogumid_id:
                        hkogum = holek.hindamiskogum

                        if on_vaie and not hkogum.arvutihinnatav:
                            algtase = const.HINDAJA5
                        else:
                            algtase = hindamistasemed.get((holek.hindamiskogum_id, valimis))

                        # kui ei ole arvutihinnatav
                        if algtase != const.HTASE_ARVUTI and kanna_tos:
                            algtase = const.HTASE_VALIMIKOOPIA
                            self._kanna_tulemus_yle(tos, kanna_tos, hkogum)

                        if algtase is not None and \
                           holek.hindamistase < const.HINDAJA3 and \
                           holek.hindamistase != algtase:
                            holek.hindamistase = algtase
                        resultentry.update_hindamisolek(sooritaja, tos, holek, True, False, tyy_id=tyy_id)
                # kysimustele jrk nr määramine 
                self._calculate_testjrk(tos, testiosa)

        sooritaja.update_staatus()
        resultentry.update_sooritus(sooritaja, tos)

    def _calculate_testjrk(self, tos, testiosa):
        """Sooritaja vastustele lisatakse jrk nr,
        mille järgi statistikutel on lihtsam andmeid järjestada (ES-2952)
        """
        q = (model.Session.query(model.Kysimusevastus)
             .join(model.Kysimusevastus.ylesandevastus)
             .filter(model.Ylesandevastus.sooritus_id==tos.id)
             .join((model.Kysimus,
                    model.Kysimus.id==model.Kysimusevastus.kysimus_id))
             .join(model.Kysimus.sisuplokk)
             .join((model.Testiylesanne,
                    model.Testiylesanne.id==model.Ylesandevastus.testiylesanne_id))
             .order_by(model.Testiylesanne.alatest_seq,
                       model.Testiylesanne.seq,
                       model.Sisuplokk.seq,
                       model.Kysimus.seq)
             )
        # eeldame, et testiosas pole rohkem kui 10000 kysimust
        jrk = testiosa.seq * 10000
        for kv in q.all():
             jrk += 1
             kv.testjrk = jrk
             
    def _kanna_tulemus_yle(self, tos, kanna_tos, hkogum):
        "Antud hindamiskogumi tulemused kopeeritakse valimi algselt testimiskorralt"
        for yv in tos.ylesandevastused:
            # vaatame, mis hindamiskogumist see ylesanne on
            if not yv.loplik:
                continue
            ty = yv.testiylesanne
            if ty.hindamiskogum_id == hkogum.id:
                kanna_yv = kanna_tos.get_ylesandevastus(ty.id)
                if kanna_yv:
                    # kopeerime ylesande tulemused
                    for kv in yv.kysimusevastused:
                        kanna_kv = kanna_yv.get_kysimusevastus(kv.kysimus_id)
                        if kanna_kv:
                            kv.toorpunktid = kanna_kv.toorpunktid
                            kv.pallid = kanna_kv.pallid
                            kv.nullipohj_kood = kanna_kv.nullipohj_kood

                    for kanna_va in kanna_yv.vastusaspektid:
                        va = yv.give_vastusaspekt(kanna_va.hindamisaspekt_id)
                        va.toorpunktid = kanna_va.toorpunktid
                        va.pallid = kanna_va.pallid

                    yv.toorpunktid = kanna_yv.toorpunktid
                    yv.toorpunktid_arvuti = kanna_yv.toorpunktid_arvuti
                    yv.toorpunktid_kasitsi = kanna_yv.toorpunktid_kasitsi
                    yv.pallid = kanna_yv.pallid
                    yv.pallid_arvuti = kanna_yv.pallid_arvuti
                    yv.pallid_kasitsi = kanna_yv.pallid_kasitsi
                    yv.yhisosa_pallid = kanna_yv.yhisosa_pallid

                    
    def _calc_hindamine3(self, toimumisaeg_id):
        # märgime kolmanda hindamise protokollide töödearvud
        sql = 'update hindamisprotokoll set tehtud_toodearv=(select count(h.id) '+\
              'from hindamine h where hindamisprotokoll.id=h.hindamisprotokoll_id) '+\
              'where liik=%s and testiprotokoll_id in ' % const.HINDAJA3 +\
              '(select tpr.id from testiprotokoll tpr, testiruum, testikoht '+\
              'where tpr.testiruum_id=testiruum.id '+\
              'and testiruum.testikoht_id=testikoht.id '+\
              'and testikoht.toimumisaeg_id=:toimumisaeg_id)'
        model.Session.execute(model.sa.text(sql), {'toimumisaeg_id': toimumisaeg_id})

        # eemaldame need kolmanda hindamise protokollid, mida enam pole vaja
        # (kuna lubatud hindamiserinevuse määra on vahepeal suurendatud)
        sql = 'delete from hindamisprotokoll where tehtud_toodearv=0 ' +\
              'and liik=%s and testiprotokoll_id in ' % const.HINDAJA3 +\
              '(select tpr.id from testiprotokoll tpr, testiruum, testikoht '+\
              'where tpr.testiruum_id=testiruum.id '+\
              'and testiruum.testikoht_id=testikoht.id '+\
              'and testikoht.toimumisaeg_id=:toimumisaeg_id)'
        model.Session.execute(model.sa.text(sql), {'toimumisaeg_id': toimumisaeg_id})

    def _calculate_labiviijad(self, toimumisaeg_id):
        toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        for lv in toimumisaeg.labiviijad:
            if lv.kasutaja_id and \
               (lv.kasutajagrupp_id in (const.GRUPP_INTERVJUU, const.GRUPP_VAATLEJA) or lv.liik):
                # kui on intervjueerija või vaatleja või hindaja
                lv.calc_toode_arv()
                lv.tasu = lv.get_tasu()
                log.debug(f'lv {lv.id} {lv.kasutajagrupp_id} {lv.kasutaja.nimi} hinnatud={lv.hinnatud_toode_arv}/{lv.toode_arv}')
            
    def _calculate_stat(self, protsess, statv, statt, spec):
        """Statistika arvutamise protsessi sisu
        """
        protsess_id = protsess and protsess.id
        testimiskord = self.c.testimiskord
        testimiskord_id = testimiskord.id
        toimumisaeg_id = self.c.toimumisaeg.id
        test = testimiskord.test
        stat_tk = testimiskord.analyys_eraldi and testimiskord or None
        resultstat = ResultStat(self, protsess, True, spec)
            
        model.Arvutusprotsess.trace('Statistika arvutamine calc_y')
        resultstat.calc_y(test, stat_tk)
        model.Arvutusprotsess.trace('calc_y arvutatud')        

        if statv:
            # vastuste statistika
            end = statt and 70 or 99
            self._calculate_statv(protsess_id, testimiskord_id, toimumisaeg_id, spec, end)
        if statt:
            # vastuste väljavõte
            self._calculate_statt(protsess_id, testimiskord_id, toimumisaeg_id, spec)
        if statv and statt and spec.koik_kogumid:
            testimiskord = model.Testimiskord.get(testimiskord_id)
            testimiskord.statistika_arvutatud = True
            
    def _calculate_statv(self, protsess_id, testimiskord_id, toimumisaeg_id, spec, end):
        """Küsimuste statistika arvutamine
        """
        protsess = protsess_id and model.Arvutusprotsess.get(protsess_id) or None
        testimiskord = model.Testimiskord.get(testimiskord_id)        
        test = testimiskord.test
        test_id = testimiskord.test_id
        stat_tk = testimiskord.analyys_eraldi and testimiskord or None
        resultstat = ResultStat(self, protsess, True, spec)

        model.Arvutusprotsess.trace('stat %s calc_kysimused...' % (protsess_id))
        # kogume kokku kõigi kysimuste listi
        data = resultstat.calc_kysimused_data(test, stat_tk)
        total = len(data)
        stat_tk_id = stat_tk and stat_tk.id or None
        label = 'Kysimused statv %s' % (toimumisaeg_id)        
        def _calculate_kysimused(min_id, max_id, child_data, pid):
            test = model.Test.get(test_id)
            testimiskord = stat_tk_id and model.Testimiskord.get(stat_tk_id) or None
            resultstat = ResultStat(self, None, True, spec)

            for pn, (_ta_id, ylesanne_id, kursus, vy_id, kysimus_id) in enumerate(child_data):
                if os.getppid() == 1:
                    # parent on surnud, lõpetame ise ka ära
                    break
                ta = _ta_id and model.Toimumisaeg.get(_ta_id) or None
                ylesanne = model.Ylesanne.get(ylesanne_id)
                kysimus = model.Kysimus.get(kysimus_id)
                nimekiri_id = None
                model.Arvutusprotsess.trace('%d/%d (%d). Yl %d kysimuse %s %d statistika %s...' % (pn+min_id, total, pn, ylesanne_id, kysimus.kood, kysimus.id, vy_id and '(vy %s)' % vy_id or '(komplektita)'))

                # küsimuse statistika arvutamine
                resultstat.calc_kysimus(kysimus, test, testimiskord, ta, kursus, nimekiri_id, vy_id)
            model.Session.commit()

        def _get_child_data(max_id, child_cnt):
            min_id = max_id
            max_id = min(total, max_id + child_cnt)
            p_cnt = max_id - min_id
            child_data = data[min_id : max_id]
            if max_id > total:
                max_id = None
            return min_id, max_id, p_cnt, child_data

        child_cnt = 5
        progress_start = protsess and protsess.edenemisprotsent or 0
        progress_end = end
        model.Arvutusprotsess.run_parallel(self,
                                           label,
                                           total,
                                           child_cnt,
                                           _calculate_kysimused,
                                           _get_child_data,
                                           protsess_id,
                                           progress_start,
                                           progress_end)                

    def _calculate_statt(self, protsess_id, testimiskord_id, toimumisaeg_id, spec):
        """Vastuste väljavõtte tabeli täitmine
        """
        protsess = protsess_id and model.Arvutusprotsess.get(protsess_id) or None
        resultstat = ResultStat(self, protsess, True, spec)

        testimiskord = model.Testimiskord.get(testimiskord_id)        
        test = testimiskord.test
        test_id = testimiskord.test_id
        resultstat.refresh_statvastus_t(test_id, testimiskord_id, progress_end=99.)

    def _index_avaldamine(self):
        "Tulemuste avaldamine"
        return self.render_to_response('ekk/hindamine/arvutused.avaldamine.mako')

    def _create_avaldamine(self):
        "Tulemuste avaldamine"
        params = self.request.params
        kord = self.c.testimiskord
        for key in ('koondtulemus_avaldet',
                    'alatestitulemused_avaldet',
                    'ylesandetulemused_avaldet',
                    'aspektitulemused_avaldet',
                    'ylesanded_avaldet'):
            avaldet = bool(params.get(key))
            oli_avaldet = kord.__getattr__(key)
            if oli_avaldet != avaldet:
                kord.__setattr__(key, avaldet)
        model.Session.commit()
        self.success()
        return self._redirect('index')
            
    def download(self):
        id = self.request.matchdict.get('id')
        if id == 'lisa1':
            doc = KinnitamislisaDoc(self.c.testimiskord, 1)
        elif id == 'lisa2':
            doc = KinnitamislisaDoc(self.c.testimiskord, 2)
            
        data = doc.generate()
        if doc.error:
            self.error(doc.error)
            return self._redirect('index')

        filename = '%s.pdf' % id
        mimetype = const.CONTENT_TYPE_PDF
        return utils.download(data, filename, mimetype)

    def __before__(self):
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        self.c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        self.c.testimiskord = self.c.toimumisaeg.testimiskord
        self.c.testiosa = self.c.toimumisaeg.testiosa
        self.c.test = self.c.testiosa.test
        
    def _perm_params(self):
        return {'obj':self.c.test}
