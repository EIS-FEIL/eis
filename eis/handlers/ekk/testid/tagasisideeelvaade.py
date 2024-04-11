from eis.lib.baseresource import *
_ = i18n._
import random
from eis.lib.feedbackreport import FeedbackReport

log = logging.getLogger(__name__)

class TagasisideeelvaadeController(BaseResourceController):
    """Tagasiside eelvaade
    """
    _permission = 'ekk-testid'
    _MODEL = model.Tagasisidevorm
    _INDEX_TEMPLATE = 'ekk/testid/tagasiside.eelvaade.mako'
    _SHOW_TEMPLATE = 'ekk/testid/tagasiside.eelvaade.mako'
    _actions = 'index,show,download'

    def _index_d(self):
        c = self.c
        items = model.Tagasisidevorm.get_list_f(c.test, c)
        if items:
            # leiame viimati kasutatud id
            params = self._get_default_params('tseelvaated')
            id = params and params.get('_tvorm_id')
            if not id or id not in [r.id for r in items]:
                # võtame esimese vormi id
                id = items[0].id
            return self._redirect('show', id=id)
        else:
            self.notice(_("Tagasisidevorme pole loodud"))
        return self.response_dict

    def _show_d(self):
        self.c.tvorm_id = id = self.request.matchdict.get('id')
        self._set_default_params({'_tvorm_id': id}, 'tseelvaated')
        if self.request.params.get('pdf'):
            format = 'pdf'
        elif self.request.params.get('xls'):
            format = 'xls'
        else:
            format = None

        tsvorm, liik, lang = self._get_vorm(id)
        self._get_filter(id, liik, lang)
        res = self._generate(id, tsvorm, format)
        if res:
            return res
        return self.response_dict

    def _get_filter(self, tsvorm_id, liik, lang):
        c = self.c
        # kas on systeemisisene d-testi tagasiside mall
        c.hardcoded_tv = c.test.tagasiside_mall == const.TSMALL_DIAG \
          and tsvorm_id in ('F1','F2','F3','F4')

        f_j = model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD
        if c.tsvorm_id == 'F1' and c.lang:
            # keel võetakse sooritaja keelest
            f_j = model.sa.and_(f_j, model.Sooritaja.lang==c.lang)

        # leiame testimiskordade valiku
        qtk = (model.Session.query(model.Testimiskord)
               .filter_by(test_id=c.test.id)
               .filter(model.Testimiskord.sooritajad.any(f_j))
               .order_by(model.Testimiskord.tahis))
        c.testimiskorrad = [tk for tk in qtk.all()]

        # leiame nimekirjade valiku (testimiskorrata)
        qn = (model.Session.query(model.Nimekiri.id, model.Nimekiri.nimi,
                                  model.Kasutaja.nimi, model.Koht.nimi)
              .filter_by(test_id=c.test.id).filter_by(testimiskord_id=None)
              .join(model.Nimekiri.esitaja_kasutaja)
              .join(model.Nimekiri.esitaja_koht)
              .filter(model.Nimekiri.sooritajad.any(f_j))
              .order_by(model.Koht.nimi, model.Kasutaja.nimi))
        c.nk_opt = [(nk_id, f'{nk_nimi} ({op_nimi}, {koht_nimi})') \
                    for nk_id, nk_nimi, op_nimi, koht_nimi in qn.all()]
        
        # kas on valimi tagasisidevorm
        def _leidub_valim(tk_id):
            # valimi tagasisidet saab kuvada ainult valimi olemasolul
            r = FeedbackReport.leia_valimi_testimiskord(c.test.id, tk_id)
            sis_valim_tk_id, valimid_tk_id, v_avaldet = r
            return (sis_valim_tk_id or valimid_tk_id) and True or False
        c.leidub_valim = _leidub_valim
        
        # leitakse statistika kirjed, mida kasutatakse grupi tagasiside filtris
        def _tk_statistikad_opt(tk):
            # testimiskordade valik
            li = []
            q = (model.SessionR.query(model.Koht.id, model.Koht.nimi)
                 .filter(sa.exists().where(
                     sa.and_(model.Sooritaja.testimiskord_id==tk.id,
                             model.Sooritaja.kool_koht_id==model.Koht.id,
                             model.Sooritaja.staatus==const.S_STAATUS_TEHTUD,
                             model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD))
                         )
                 .order_by(model.Koht.nimi)
                 )
            for koht_id, koht_nimi in q.all():
                li.append((koht_id, koht_nimi))
            return li

        c.tk_statistikad_opt = _tk_statistikad_opt
                
    def _show_fbdqry(self, id):
        "Tagasisidediagrammi uuendamine eraldi muust tagasisidevormist"
        c = self.c
        params = self.request.params
        fbd_id = params.get('fbd_id')

        # kogu ekraanivormi päringu parameetrid
        c.testimiskord_id = params.get('testimiskord_id')
        c.kool_koht_id = params.get('kool_koht_id')
        c.nimekiri_id = params.get('nimekiri_id')

        # tagasisidevormi leidmine
        tsvorm = model.Tagasisidevorm.get(id)
        assert tsvorm and tsvorm.test_id==c.test.id, 'vale vormi id'
        template = tsvorm.sisu
        liik = tsvorm.liik
        lang = tsvorm.lang
        err = None

        # väärtustatakse c.kool_koht_id jms
        if c.genrnd:
            # juhuslikud andmed
            sooritaja = GenRndSooritaja(self).create(id, tsmall, liik, lang)
        else:
            # genereeri päris andmete põhjal
            test = c.test
            sooritaja, err = self._gen_vaba(liik, test, lang)
            
        if err:
            html = ''
        else:
            # tabeli sisu genereerimine
            fr = FeedbackReport(self, None, c.test, template, liik, lang)
            err, html = fr.generate_dgm(fbd_id,
                                        params,
                                        testimiskord_id=c.testimiskord_id,
                                        kool_koht_id=c.kool_koht_id,
                                        nimekiri_id=c.nimekiri_id)
        if err:
            log.error(err)
        return Response(html or '')

    def _get_vorm(self, tsvorm_id):
        # tagasisidevormi leidmine
        c = self.c
        lang = None
        self._params_into_c('tseelvaade_vaba_show_%s_%s' % (c.test.id, tsvorm_id))
        if tsvorm_id == 'F1':
            tsvorm = None
            liik = model.Tagasisidevorm.LIIK_OPILANE
        elif tsvorm_id == 'F2':
            tsvorm = None
            liik = model.Tagasisidevorm.LIIK_OSALEJATETULEMUSED
        elif tsvorm_id == 'F3':
            tsvorm = None
            liik = model.Tagasisidevorm.LIIK_VALIM
        elif tsvorm_id == 'F4':
            tsvorm = None
            liik = model.Tagasisidevorm.LIIK_RIIKLIK            
        else:
            tsvorm = model.Tagasisidevorm.get(tsvorm_id)
            liik = None
            if c.test.testiliik_kood == const.TESTILIIK_KOOLIPSYH:
                self.error(_("Koolipsühholoogi testi tagasiside eelvaadet ei või päris sooritajate andmete põhjal näidata"))
                tsvorm = None

            elif not tsvorm or tsvorm.get_root().test_id != c.test.id:                
                raise NotFound()
            elif not tsvorm.sisu:
                self.error(_("Tagasisidevorm on tühi"))
                tsvorm = None
            else:
                liik = tsvorm.liik
                lang = tsvorm.lang
        c.tsvorm = tsvorm
        c.liik = liik
        c.lang = lang
        c.tsvorm_id = tsvorm_id
        c.is_preview = True
        return tsvorm, liik, lang
    
    def _generate(self, tsvorm_id, tsvorm, format=None, fbd_id=None):
        # tagasiside genereerimine
        c = self.c
        tsmall = c.test.tagasiside_mall
        
        liik = c.liik
        lang = c.lang
        on_opilane = model.Tagasisidevorm.is_individual(liik)
        on_grupp = not on_opilane
        sooritaja = err = None
        if c.genrnd:
            sooritaja = GenRndSooritaja(self).create(tsvorm_id, tsmall, liik, lang)
        else:
            # genereeri päris andmete põhjal
            test = c.test
            sooritaja, err = self._gen_vaba(liik, test, lang)
            if err:
                self.error(err)
                return
            
        # andmed olemas, genereerime vormi
        if sooritaja or c.kool_koht_id or c.nimekiri_id or c.testimiskord_id or c.ekk_preview_rnd:
            template = c.tsvorm and c.tsvorm.sisu
            fr = FeedbackReport(self, None, c.test, template, liik, lang)
            if format == 'pdf':
                filedata = fr.generate_pdf(sooritaja,
                                           testimiskord_id=c.testimiskord_id,
                                           kool_koht_id=c.kool_koht_id,
                                           nimekiri_id=c.nimekiri_id)
                if filedata:
                    return utils.download(filedata, 'tagasiside.pdf', const.CONTENT_TYPE_PDF)
            elif format == 'xls':
                c.is_xls = True
                filedata = fr.generate_xls(sooritaja,
                                           testimiskord_id=c.testimiskord_id,
                                           kool_koht_id=c.kool_koht_id,
                                           nimekiri_id=c.nimekiri_id)
                if filedata:
                    return utils.download(filedata, 'tagasiside.xlsx', const.CONTENT_TYPE_XLS)
            else:
                err, c.tagasiside_html = fr.generate(sooritaja,
                                                     testimiskord_id=c.testimiskord_id,
                                                     kool_koht_id=c.kool_koht_id,
                                                     nimekiri_id=c.nimekiri_id)
                c.can_xls = fr.can_xls
                if err:
                    self.error(_("Tagasiside genereerimine ei õnnestu") + ' ({})'.format(err))

    def _download(self, id, format=None):
        """Näita faili"""
        f_id = self.request.matchdict.get('id')
        tsvorm, liik, lang = self._get_vorm(f_id)
        res = self._generate(f_id, tsvorm, format)
        if res:
            return res
        self.error(_("Faili ei leitud"))
        return self._redirect('show', id=f_id)

    ###########################################################
    # vaba
    
    def _gen_vaba(self, liik, test, lang):
        err = None
        c = self.c

        # genereerida item jaoks
        sooritaja = kool_koht_id = None

        if liik in (model.Tagasisidevorm.LIIK_OPILANE, model.Tagasisidevorm.LIIK_OPETAJA):
            q = (model.Sooritaja.query
                 .filter(model.Sooritaja.test_id==c.test.id)
                 )
            if c.testimiskord_id:
                q = q.filter(model.Sooritaja.testimiskord_id==c.testimiskord_id)
            if c.nimekiri_id:
                q = q.filter(model.Sooritaja.nimekiri_id==c.nimekiri_id)
            if c.tookood or c.isikukood:
                if c.tookood:
                    q = (q.join(model.Sooritaja.sooritused)
                         .join(model.Sooritus.testiosa)
                         .filter(model.Testiosa.seq==1)
                         .filter(model.Sooritus.tahised==c.tookood)
                         )
                if c.isikukood:
                    q = q.join(model.Sooritaja.kasutaja)
                    usp = validators.IsikukoodP(c.isikukood)
                    q = q.filter(usp.filter(model.Kasutaja))
            elif c.sooritaja_id:
                q = q.filter(model.Sooritaja.id==c.sooritaja_id)
            elif lang:
                q = q.filter(model.Sooritaja.lang==lang)

            q2 = (q.filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
                  .filter(sa.or_(model.Sooritaja.hindamine_staatus==const.H_STAATUS_HINNATUD,
                                 model.Sooritaja.pallid!=None))
                  )
            # III hindamisel olevad tööd ei ole hinnatud, vt ES-3476
            sooritaja = q2.first()
            if not sooritaja:
                tookood = c.tookood or c.isikukood or ''
                if tookood or c.sooritaja_id:
                    sooritaja2 = q.first()
                    if sooritaja2:
                        if sooritaja2.staatus != const.S_STAATUS_TEHTUD:
                            err = _('Töö {s1} olek on: {s2}').format(s1=tookood, s2=sooritaja2.staatus_nimi)
                        elif (sooritaja2.hindamine_staatus != const.H_STAATUS_HINNATUD and sooritaja2.pallid is None):
                            err = _('Töö {s} on hindamata').format(s=tookood)

            if not sooritaja:
                if not err:
                    err = _('Sooritajat ei leitud')
            else:
                c.sooritaja_id = sooritaja.id
        else:
            # grupi statistika
            val = c.kool_koht_id
            try:
                c.kool_koht_id = int(val)
            except:
                c.kool_koht_id = None
            val = c.nimekiri_id
            try:
                c.nimekiri_id = int(val)
            except:
                c.nimekiri_id = None
        return sooritaja, err
    
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        c = self.c
        test_id = self.request.matchdict.get('test_id')
        c.test = model.Test.get(test_id)

        testiosa_id = int(self.request.matchdict.get('testiosa_id'))
        if testiosa_id:
            c.testiosa = model.Testiosa.get(testiosa_id)
            if c.testiosa.test_id != c.test.id:
                c.testiosa = None
        if not c.testiosa:
            for c.testiosa in c.test.testiosad:
                break
        
    def _perm_params(self):
        return {'obj':self.c.test}

class GenRndSooritaja:
    "Pseudosooritaja genereerimine testimiseks"
    def __init__(self, handler):
        self.handler = handler

    def create(self, id, tsmall, liik, lang1):
        # genereeri juhuslikult sooritaja
        c = self.handler.c
        test = c.test
        testiosa = c.testiosa
        lang = c.lang
        on_opilane = model.Tagasisidevorm.is_individual(liik)        
        sooritaja = None
        if id == 'F1':
            sooritaja = model.tempSooritaja(c, test, lang, True)
            if tsmall == const.TSMALL_DIAG:
                # genereerime testandmed
                self._gen_diag_opil_rnd(sooritaja, testiosa)                
            elif tsmall == const.TSMALL_PSYH:
                # genereerime testandmed
                self._gen_psyh_opil_rnd(sooritaja, test)
            elif tsmall == const.TSMALL_OPIP:
                # genereerime testandmed
                self._gen_opip_opil_rnd(sooritaja, test)                        
        elif id in ('F2','F3','F4'):
            if tsmall == const.TSMALL_DIAG:
                # testandmed genereeritakse hiljem, koos tagasisidega
                c.ekk_preview_rnd = True
        elif on_opilane:
            # juhuslik vaba vormi tagasiside
            sooritaja = model.tempSooritaja(c, test, lang, True)
            self._gen_opip_opil_rnd(sooritaja, test)
        else:
            c.ekk_preview_rnd = True                
            c.testimiskord_id = -1

        if sooritaja:
            for sooritus in sooritaja.sooritused:
                if sooritus.testiosa_id == c.testiosa.id:
                    c.sooritus = sooritus
                    break
                
        return sooritaja

    #############################################################
    # Psyh

    def _gen_psyh_opil_rnd(self, sooritaja, test):
        "Juhuslikult genereeritud psyh tagasiside eelvaade"

        for testiosa in test.testiosad:
            sooritus = model.TempSooritus(testiosa_id=testiosa.id)
            sooritus.sooritaja = sooritaja
            for kv in testiosa.komplektivalikud:
                for k in kv.komplektid:
                    sooritus._set_komplekt(k)
                    break

            for np in testiosa.normipunktid:
                npv = sooritus.add_npvastus(np)
                li_ns = [ns for ns in np.normiprotsentiilid]
                if li_ns:
                    ns = random.choice(li_ns)
                    value = ns.protsentiil
                else:
                    value = .5
                npv.set_value(value)
                
            sooritaja.sooritused.append(sooritus)
    
    #############################################################
    # Opip

    def _gen_opip_opil_rnd(self, sooritaja, test):
        "Juhuslikult genereeritud õpipädevuse tagasiside eelvaade"
        for testiosa in test.testiosad:
            sooritus = model.TempSooritus(testiosa_id=testiosa.id)
            sooritus.sooritaja = sooritaja
            for kv in testiosa.komplektivalikud:
                for k in kv.komplektid:
                    sooritus._set_komplekt(k)
                    break

            for np in testiosa.normipunktid:
                npv = sooritus.add_npvastus(np)
                li_ns = [ns for ns in np.sooritusryhmad]
                if li_ns:
                    ns = random.choice(li_ns)
                    value = ns.lavi
                elif np.min_vaartus is not None and np.max_vaartus is not None:
                    value = random.uniform(np.min_vaartus, np.max_vaartus)
                else:
                    value = .5
                #log.debug('np%s li=%s value=%s' % (np.id, len(li_ns), value))
                npv.set_value(value)

            sooritaja.sooritused.append(sooritus)
                
    ###############################################################
    # diag

    def _gen_diag_opil_rnd(self, sooritaja, testiosa):
        komplekt = testiosa.komplektivalikud[0].komplektid[0]
        sooritus = model.TempSooritus(testiosa.id, None, komplekt)
        for np in testiosa.normipunktid:
            li_ns = [ns for ns in np.nptagasisided if ns.tagasiside]
            if li_ns:
                ns = random.choice(li_ns)
                npv = sooritus.add_npvastus(np)
                value = ns.tingimus_vaartus
                npv.set_value(value)
                npv.nptagasiside_id = ns.id
        sooritaja.sooritused.append(sooritus)
