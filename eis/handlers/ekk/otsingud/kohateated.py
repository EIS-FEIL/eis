import random

from eis.lib.baseresource import *
_ = i18n._
from eis.lib.pdf.kohateade import KohateadeDoc
from eis.lib.pdf.muukiri import MuukiriDoc
from eis.lib.xtee.notifications import Notifications
log = logging.getLogger(__name__)

class KohateatedController(BaseResourceController):
    """Soorituste otsimine
    """
    _permission = 'aruanded-kohateated'
    _MODEL = model.Kasutaja
    _INDEX_TEMPLATE = 'ekk/otsingud/kohateated.mako'
    _LIST_TEMPLATE = 'ekk/otsingud/kohateated_list.mako'
    _SEARCH_FORM = forms.ekk.otsingud.KohateatedForm
    _DEFAULT_SORT = 'kasutaja.perenimi,kasutaja.eesnimi'
    _ignore_default_params = ['csv','xls','format','testkiri','epost','tpost','kalender','stateos','naita']
    
    def _query(self):
        q = model.Kasutaja.query
        return q

    def _search_default(self, q):
        self.c.kordus = True
        self.c.kool = True
        self.c.ise = True
        return None

    def _get_default_params(self, upath=None):
        """Taaskasutame varem samal otsinguvormil kasutatud parameetreid
        aga mitte loetelu näitamise parameetrit
        """
        params = BaseResourceController._get_default_params(self, upath)
        if params:
            if 'naita' in params:
                del params['naita']
            return params

    def _search(self, q):
        if not self.c.sessioon_id:
            return

        create_params = self._get_default_params(upath='kohateated-create')
        if create_params:
            self.c.taiendavinfo = create_params.get('taiendavinfo')
        
        q, f_epost, f_tpost = self._search_query(q)
        if q:
            q_epost = q.filter(f_epost)
            q_tpost = q.filter(~ f_epost).filter(f_tpost)
            q_puudu = q.filter(~ f_epost).filter(~ f_tpost)

            self.c.arv_epost = q_epost.count()
            self.c.arv_tpost = q_tpost.count()
            self.c.arv_puudu = q_puudu.count()

            self._get_protsessid()
            if self.c.naita == 'puudu':
                # kuvame sooritajad, kelle aadress puudub
                return q_puudu
            elif self.c.naita == 'epost':
                # kuvame sooritajad, kellele saadetakse teade e-postiga
                return q_epost
            elif self.c.naita == 'tpost':
                # kuvame sooritajad, kellele saadetakse teade tigupostiga
                return q_tpost

        return None

    def create(self):
        self.form = Form(self.request, schema=self._SEARCH_FORM)
        if self.form.validate():
            self._copy_search_params(self.form.data, save=True, upath='kohateated-create')
            kirityyp = self.request.params.get('kirityyp') or model.Kiri.TYYP_SOORITUSKOHATEADE
            taiendavinfo = self.request.params.get('taiendavinfo')
            if kirityyp == model.Kiri.TYYP_MUU and not taiendavinfo:
                self.error(_("Teate sisu puudub"))
                template = self._INDEX_TEMPLATE
                html = self.form.render(template, extra_info=self.response_dict)            
                return Response(html)

            q = self._query()
            q, f_epost, f_tpost = self._search_query(q)

            if q and self.c.sessioon_id:
                teatekanal = None
                if self.c.testkiri:
                    if not self.c.testaadress:
                        self.error(_("Testkirja saatmiseks palun sisestada saaja e-posti aadress"))
                    else:
                        testaadress = self.c.testaadress
                        teatekanal = const.TEATEKANAL_EPOST
                        q = q.filter(f_epost)
                        send_childfunc(self, None, q, teatekanal, self.c.testiliik, self._get_sooritused,
                                       kirityyp,
                                       testaadress=testaadress,
                                       taiendavinfo=taiendavinfo)
                else:
                    if self.request.params.get('epost'):
                        teatekanal = const.TEATEKANAL_EPOST
                        q = q.filter(f_epost)
                    elif self.request.params.get('tpost'):
                        # PDFi genereerimine
                        teatekanal = const.TEATEKANAL_POST
                        q = q.filter(~ f_epost).filter(f_tpost)                        
                    elif self.request.params.get('puudu'):
                        # aadress puudub, teade ainult EISi
                        teatekanal = const.TEATEKANAL_EIS
                        q = q.filter(~ f_epost).filter(~ f_tpost)
                    if teatekanal:
                        res = self._send_all(q, teatekanal, kirityyp, taiendavinfo)
                        if res:
                            # debug
                            return res
        else:
            # sisendparameetrid ei valideeru
            template = self._INDEX_TEMPLATE
            html = self.form.render(template, extra_info=self.response_dict)            
            return Response(html)

        return self._redirect('index', getargs=True)

    def _send_all(self, q, teatekanal, kirityyp, taiendavinfo):
        "Teadete saatmine"
        cnt = q.count()
        if cnt:
            if self.c.toimumisaeg_id:
                ta = model.Toimumisaeg.get(self.c.toimumisaeg_id)
                tahised = ta.tahised
            elif self.c.testimiskord_id:
                tk = model.Testimiskord.get(self.c.testimiskord_id)
                tahised = tk.tahised
            elif self.c.test_id:
                tahised = self.c.test_id
            else:
                tahised = ''
            skanal = self.c.opt.TEATEKANAL.get(teatekanal)
            if kirityyp == model.Kiri.TYYP_MUU:
                desc = 'Muude kirjade saatmine %s (%d teadet, %s)' % (tahised, cnt, skanal)
            else:
                desc = 'Soorituskohateadete saatmine %s (%d teadet, %s)' % (tahised, cnt, skanal)
            params = {'liik': model.Arvutusprotsess.LIIK_M_SOORITUSKOHT,
                      'kirjeldus': desc,
                      'test_id': self.c.test_id or None,
                      'testimiskord_id': self.c.testimiskord_id or None,
                      'toimumisaeg_id': self.c.toimumisaeg_id or None,
                      'testsessioon_id': self.c.sessioon_id or None,
                      }
            if teatekanal == const.TEATEKANAL_POST:
                childfunc = lambda rcd: gen_pdf_all(self,
                                                    rcd,
                                                    q,
                                                    self.c.testiliik,
                                                    self._get_sooritused,
                                                    kirityyp,
                                                    taiendavinfo)                
            else:
                childfunc = lambda rcd: send_childfunc(self,
                                                       rcd,
                                                       q,
                                                       teatekanal,
                                                       self.c.testiliik,
                                                       self._get_sooritused,
                                                       kirityyp,
                                                       taiendavinfo=taiendavinfo)                
            debug = 0
            res = model.Arvutusprotsess.start(self, params, childfunc, debug=debug)
            if debug:
                return utils.download(res, 'teade.pdf', const.CONTENT_TYPE_PDF)
            self.success('Saatmise protsess käivitatud')

    def _search_protsessid(self, q):
        sessioon_id = self.c.sessioon_id or self.request.params.get('sessioon_id')
        q = (q.filter(model.Arvutusprotsess.liik==model.Arvutusprotsess.LIIK_M_SOORITUSKOHT)
             .filter(model.Arvutusprotsess.testsessioon_id==sessioon_id)
             )
        return q

    def _search_query(self, q1):
        c = self.c
        if c.testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
            q = model.Kasutaja.query
        else:
            q = model.Sooritaja.query.join(model.Sooritaja.kasutaja)

        if c.isikukood:
            usp = validators.IsikukoodP(self.c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))
        if c.eesnimi:
            q = q.filter(model.Kasutaja.eesnimi.ilike(c.eesnimi))
        if c.perenimi:
            q = q.filter(model.Kasutaja.perenimi.ilike(c.perenimi))

        if c.koht_id or c.piirkond_id:
            # päring koha või piirkonna järgi
            f = sa.exists().\
                where(model.Sooritaja.id==model.Sooritus.sooritaja_id)
            if c.koht_id:
                f = f.where(model.Sooritus.testikoht_id==model.Testikoht.id).\
                    where(model.Testikoht.koht_id==c.koht_id)
            elif c.piirkond_id:
                piirkond = model.Piirkond.get(c.piirkond_id)
                piirkonnad_id = piirkond.get_alamad_id()
                if len(piirkonnad_id) > 1:
                    f = f.where(model.Sooritus.piirkond_id.in_(piirkonnad_id))
                else:
                    f = f.where(model.Sooritus.piirkond_id==c.piirkond_id)

            # kitsendame alampäringut samade tingimustega, mis on peapäringus juba olemas
            # nii saab kokkuvõttes kiiremini
            Sooritaja2 = sa.orm.aliased(model.Sooritaja)
            f = f.where(model.Sooritus.sooritaja_id==Sooritaja2.id)
            if c.toimumisaeg_id:
                f = f.where(model.Sooritus.toimumisaeg_id==c.toimumisaeg_id)
            if c.testimiskord_id:
                f = f.where(Sooritaja2.testimiskord_id==c.testimiskord_id)
            elif c.sessioon_id:
                Testimiskord2 = sa.orm.aliased(model.Testimiskord)
                f = f.where(Sooritaja2.testimiskord_id==Testimiskord2.id).\
                    where(Testimiskord2.testsessioon_id==c.sessioon_id)
                if c.test_id:
                    f = f.where(Sooritaja2.test_id==c.test_id)

            if c.testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
                q = q.filter(model.Kasutaja.sooritajad.any(f))
            else:
                q = q.filter(f)

        f_sooritaja = []
        if c.sessioon_id:
            f_sooritaja.append(model.Sooritaja.testimiskord.has(\
                    sa.and_(model.Testimiskord.osalemise_naitamine==True,
                            model.Testimiskord.testsessioon_id==int(c.sessioon_id))))
            if c.testimiskord_id:
                f_sooritaja.append(model.Sooritaja.testimiskord_id==int(c.testimiskord_id))
        else:
            return None, None, None

        if c.toimumisaeg_id:
            f_sooritaja.append(model.Sooritaja.sooritused.any(\
                    model.Sooritus.toimumisaeg_id==c.toimumisaeg_id))
        if c.test_id:
            f_sooritaja.append(model.Sooritaja.test_id==c.test_id)
        f_test = sa.and_(model.Test.testiliik_kood==c.testiliik,
                         model.Test.testityyp==const.TESTITYYP_EKK)
        if c.keeletase:
            f_test = sa.and_(f_test, model.Test.testitasemed.any(model.Testitase.keeletase_kood==c.keeletase))
        f_sooritaja.append(model.Sooritaja.test.has(f_test))

        
        tk = None
        if c.toimumisaeg_id:
            ta = model.Toimumisaeg.get(c.toimumisaeg_id)
            tk = ta.testimiskord
        elif c.testimiskord_id:
            tk = model.Testimiskord.get(c.testimiskord_id)
        if tk:
            li = [ta.tahised for ta in tk.toimumisajad if not ta.kohad_avalikud]
            if len(li) > 0:
                self.error(_("{s} soorituskohad pole avalikud").format(s=', '.join(li)))
                return None, None, None

        regviisid = []
        if c.kool:
            regviisid.append(const.REGVIIS_KOOL_EIS)
        if c.ise:
            regviisid.append(const.REGVIIS_SOORITAJA)
            regviisid.append(const.REGVIIS_EKK)
            regviisid.append(const.REGVIIS_XTEE)
        if len(regviisid) > 0 and len(regviisid) < 5:
            # kui on valitud mõni regviis, aga mitte kõik
            f_sooritaja.append(model.Sooritaja.regviis_kood.in_(regviisid))
        if c.kons:
            f_sooritaja.append(model.Sooritaja.soovib_konsultatsiooni==True)
        # kogu testi staatused, kes on reganud, aga pole veel kogu testi lõpetanud
        staatused = (const.S_STAATUS_TASUMATA,
                     const.S_STAATUS_REGATUD,
                     const.S_STAATUS_ALUSTAMATA,
                     const.S_STAATUS_POOLELI,
                     const.S_STAATUS_KATKESTATUD)
        f_sooritaja.append(model.Sooritaja.staatus.in_(staatused))
        f_sooritaja.append(~ model.Sooritaja.sooritused.any(model.Sooritus.testikoht_id==None))
        f_sooritaja.append(model.Sooritaja.testimiskord.has(\
                            ~ model.Testimiskord.toimumisajad.any(\
                                model.Toimumisaeg.kohad_avalikud==False)))

        ##################################
        # e-posti ja posti teel teavituste arvu päringud
        if not c.kordus:
            f_sooritaja.append(model.Sooritaja.meeldetuletusaeg==None)

        f_sooritaja = sa.and_(*f_sooritaja)
        if c.testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
            # sessiooni kõigil testidel ühine kutse
            q = q.filter(model.Kasutaja.sooritajad.any(f_sooritaja))
        else:
            # igal testil oma kutse
            q = q.filter(f_sooritaja)

        
        f_epost = (model.Kasutaja.epost != None)        
        f_tpost = sa.and_(model.Kasutaja.aadress.has(model.Aadress.kood1!=None),
                          model.Kasutaja.postiindeks!=None)

        # päringu tegemise ajal kasutatud parameetrid kasutamiseks URLides
        c.search_args = {'sessioon_id': c.sessioon_id,
                         'testiliik': c.testiliik,
                         'testimiskord_id': c.testimiskord_id,
                         'toimumisaeg_id': c.toimumisaeg_id,
                         'test_id': c.test_id,
                         'piirkond_id': c.piirkond_id,
                         'koht_id': c.koht_id,
                         'isikukood': c.isikukood,
                         'eesnimi': c.eesnimi,
                         'perenimi': c.perenimi,
                         'kirityyp': c.kirityyp,
                         'kordus': c.kordus and 1 or '',
                         'kons': c.kons and 1 or '',
                         'kool': c.kool and 1 or '',
                         'ise': c.ise and 1 or '',
                         }

        return q, f_epost, f_tpost

    def _get_sooritused(self, kasutaja):
        q = (model.Sooritus.query
             .join(model.Sooritus.sooritaja)
             .filter(model.Sooritus.toimumisaeg_id!=None)
             .filter(model.Sooritus.testikoht_id!=None)
             .filter(model.Sooritus.staatus > const.S_STAATUS_REGAMATA)
             .join(model.Sooritus.toimumisaeg)
             .join(model.Sooritaja.testimiskord)
             .filter(model.Toimumisaeg.kohad_avalikud==True)
             .filter(model.Testimiskord.osalemise_naitamine==True)
             )
        
        if isinstance(kasutaja, model.Sooritaja):
            q = q.filter(model.Sooritaja.id==kasutaja.id)
        else:
            q = q.filter(model.Sooritaja.kasutaja_id==kasutaja.id)

        if self.c.testimiskord_id:
            q = q.filter(model.Sooritaja.testimiskord_id==self.c.testimiskord_id)
        elif self.c.sessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==self.c.sessioon_id)
        if self.c.toimumisaeg_id:
            q = q.filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg_id)
        if self.c.test_id:
            q = q.filter(model.Sooritaja.test_id==self.c.test_id)
        f_test = sa.and_(model.Test.testiliik_kood==self.c.testiliik,
                         model.Test.testityyp==const.TESTITYYP_EKK)
        if self.c.keeletase:
            f_test.append(model.Test.testitasemed.any(model.Testitase.keeletase_kood==self.c.keeletase))
        q = q.filter(model.Sooritaja.test.has(f_test))

        q = q.outerjoin(model.Sooritus.testiruum).\
            order_by(model.Testiruum.algus)
        return q.all()
        
def send_childfunc(handler, protsess, q, teatekanal, testiliik, get_sooritused, kirityyp, testaadress=None, taiendavinfo=None):    
    total = q.count()
    if not total:
        return
    if testaadress:
        n = random.randrange(total)
        q = q.slice(n, n+1)

    def itemfunc(rcd):
        if teatekanal in (const.TEATEKANAL_EPOST, const.TEATEKANAL_EIS):
            return send_epost_for(handler, rcd, testiliik, get_sooritused, kirityyp, testaadress, taiendavinfo, teatekanal)

    items = q.all()
    if not protsess:
        for rcd in items:
            itemfunc(rcd)
            if testaadress:
                break
    else:
        model.Arvutusprotsess.iter_mail(protsess, handler, total, q.all(), itemfunc)

def send_epost_for(handler, rcd, testiliik, get_sooritused, kirityyp, testaadress, taiendavinfo, teatekanal):
    if testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
        k = rcd
        sooritused = get_sooritused(k)
        if len(sooritused) == 0:
            return False, k.nimi
    else:
        sooritaja = rcd
        sooritused = rcd.sooritused
        k = sooritaja.kasutaja

    if teatekanal != const.TEATEKANAL_EPOST:
        # kirju päriselt ei saada, ainult salvestatakse EISi (vbl saadeti päris kiri paberil)
        to = None
    elif testaadress:
        # testkirja saatmine
        to = testaadress
    else:
        # päriselt kirja saatmine
        if not k.epost:
            return False, k.nimi
        to = k.epost

    if kirityyp == model.Kiri.TYYP_MUU:
        subject, body = _compose_epost_muu(handler, k, sooritused, testiliik, taiendavinfo)
        body = Mailer.replace_newline(body)
    elif testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
        subject, body = _compose_epost_riigieksam(handler, k, sooritused, testiliik, taiendavinfo)
        body = Mailer.replace_newline(body)
    elif testiliik == const.TESTILIIK_TASE:
        subject, body = _compose_epost_te(handler, k, sooritaja, taiendavinfo)
    elif testiliik == const.TESTILIIK_SEADUS:
        subject, body = _compose_epost_se(handler, k, sooritaja, taiendavinfo)
        body = Mailer.replace_newline(body)
    elif testiliik == const.TESTILIIK_SISSE:
        subject, body = _compose_epost_ss(handler, k, sooritaja, taiendavinfo)
        body = Mailer.replace_newline(body)
    elif testiliik == const.TESTILIIK_KUTSE:
        subject, body = _compose_epost_ke(handler, k, sooritaja, taiendavinfo)
        body = Mailer.replace_newline(body)
    else:
        raise Exception(_("Testiliigile {s} ei ole malli").format(s=testiliik))

    if teatekanal == const.TEATEKANAL_EPOST:
        # saadame kirja
        err = Mailer(handler).send(to, subject, body, out_err=False)
        if err:
            buf = '%s (%s %s)' % (err, k.nimi, to)
            model.Arvutusprotsess.trace(buf)
            return False, err
        else:
            log.debug(_("Saadetud kiri aadressile {s}").format(s=to))

    if not testaadress:
        # salvestame saadetud teate
        if testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
            for sooritus in sooritused:
                sooritus.sooritaja.meeldetuletusaeg = datetime.now()
        else:
            sooritaja.meeldetuletusaeg = datetime.now()

        kiri = model.Kiri(saatja_kasutaja_id=handler.c.user.id,
                          tyyp=kirityyp,
                          sisu=body,
                          teema=subject,
                          teatekanal=teatekanal)
        if testiliik in (const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_RV):
            sooritajad_id = set([s.sooritaja_id for s in sooritused])
            for sooritaja_id in sooritajad_id:
                model.Sooritajakiri(sooritaja_id=sooritaja_id, kiri=kiri)
        else:
            model.Sooritajakiri(sooritaja=sooritaja, kiri=kiri)
        model.Kirjasaaja(kiri=kiri, kasutaja_id=k.id, epost=k.epost)
        # vaja teha commit!
    return True, None
    
def _compose_epost_muu(handler, k, sooritused, testiliik, taiendavinfo):
    "Muu kirja saatmine"
    template = 'mail/muukiri.mako'
    subject, body = handler.render_mail(template, 
                                      {'isik_nimi': k.nimi, 
                                       'user_nimi': handler.c.user.fullname,
                                       'aasta': date.today().year,
                                       'taiendavinfo': taiendavinfo,
                                       })
    return subject, body

def _compose_epost_riigieksam(handler, k, sooritused, testiliik, taiendavinfo=None):
    kohad = []
    testid_id = []
    for sooritus in sooritused:
        sooritaja = sooritus.sooritaja
        test = sooritaja.test
        if test.id not in testid_id:
            testid_id.append(test.id)
        testikoht = sooritus.testikoht
        testiruum = sooritus.testiruum
        testiprotokoll = sooritus.testiprotokoll
        koht = testikoht and testikoht.koht
        ruum = testiruum and testiruum.ruum
        algus = testiruum and testiruum.algus
        testiosa = sooritus.testiosa
        if testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_I, const.VASTVORM_SE, const.VASTVORM_SP):
            kavaaeg = sooritus.kavaaeg
        else:
            kavaaeg = algus

        kursus_nimi = sooritaja.kursus_nimi
        if test.aine_kood == const.AINE_M and test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
            lang_nimi = sooritaja.lang_nimi.lower()
        else:
            lang_nimi = None
        rcd = (test.nimi,
               sooritus.testiosa.nimi,
               koht and koht.nimi,
               ruum and ruum.tahis or '',
               koht and koht.tais_aadress or '',
               algus and algus.strftime('%d.%m.%Y') or '',
               kavaaeg and kavaaeg.strftime('%d.%m.%Y kell %H.%M') or '',
               kursus_nimi,
               lang_nimi)
        kohad.append(rcd)

    teade7pv = True
    if len(testid_id) == 1:
        if test.testiliik_kood == const.TESTILIIK_RV and test.aine_kood == const.AINE_EN:
            # kui on ainult ingl k rv eksam, siis ei kuvata lause "Kui ei soovi..."
            teade7pv = False
            
    if testiliik == const.TESTILIIK_RIIGIEKSAM:
        template = 'mail/kohateade_r.mako'
    elif testiliik == const.TESTILIIK_RV:
        template = 'mail/kohateade_rv.mako'
    else:
        raise Exception('vale testiliik')
    
    subject, body = handler.render_mail(template, 
                                      {'kohad':kohad,
                                       'isik_nimi': k.nimi, 
                                       'user_nimi': handler.c.user.fullname,
                                       'aasta': date.today().year,
                                       'taiendavinfo': taiendavinfo,
                                       'teade7pv': teade7pv,
                                       })
    return subject, body

def _compose_epost_te(handler, k, sooritaja, taiendavinfo=None):
    "Tasemeeksami eksamikutse"
    sooritused = list(sooritaja.sooritused)
    sooritused.sort(key=lambda s: s.kavaaeg or s.algus or s.testiruum.algus or const.MAX_DATETIME)

    def get_aadress(koht, r_tahis):
        buf = koht and koht.nimi or ''
        if r_tahis:
            buf += ', ruum %s' % r_tahis
        tais_aadress = koht and koht.tais_aadress or ''
        if tais_aadress:
            buf += ', %s' % (tais_aadress or '')
        return buf

    kuupaevad = set()
    algused = []
    for s in sooritused:
        osa = s.testiosa.nimi
        algus = s.kavaaeg or s.algus or s.testiruum.algus
        if algus:
            aeg = algus.strftime('%d.%m.%Y kell %H.%M')
        else:
            aeg = ''
        ruum_tahis = s.testiruum.ruum and s.testiruum.ruum.tahis
        koht = s.testikoht.koht
        koht_aadress = get_aadress(koht, ruum_tahis)
        algused.append((osa, aeg, koht_aadress))
        if algus:
            kuupaevad.add(algus.date())

    if len(kuupaevad) == 1:
        # kui kõik testiosad toimuvad samal kuupäeval,
        # siis antakse teada ainult esimese testiosa algus
        algused = [algused[0]]
    
    konsultatsiooniruumid = []
    if sooritaja.soovib_konsultatsiooni:
        konsultatsiooniruumid = sooritaja.get_konsultatsiooniruumid()
        li = list()
        for (r_algus, koht, r_tahis) in konsultatsiooniruumid:
            if not r_algus:
                msg = "Konsultatsiooni alguse aeg on määramata ({koht}, {ruum})".format(koht=koht.nimi, ruum=r_tahis)
                raise Exception(msg)
            kons_aeg = r_algus.strftime('%d.%m.%Y kell %H.%M')
            kons_koht_aadress = get_aadress(koht, r_tahis)
            s = '%s asukohaga %s' % (kons_aeg, kons_koht_aadress)
            li.append(s)
        konsultatsiooniruumid = li

    test = sooritaja.test
    keeletase_kood = test.keeletase_kood
    if keeletase_kood=='A2':
        kestus = '1 tund ja 50 min (kirjutamine 30 min, kuulamine 30 min, lugemine 50 min)'        
    elif keeletase_kood=='B1':
        kestus = '2 tundi (kirjutamine 35 min, kuulamine 35 min, lugemine 50 min)'
    elif keeletase_kood=='B2':
        kestus = '3 tundi ja 5 min (kirjutamine 80 min, kuulamine 35 min, lugemine 70 min)'
    elif keeletase_kood=='C1':
        kestus = '3 tundi ja 15 min (kirjutamine 90 min, kuulamine 45 min, lugemine 60 min)'

    subject, body = handler.render_mail('mail/kohateade_te.mako', 
                                      {'keeletase_nimi': test.keeletase_nimi,
                                       'isik_nimi': k.nimi, 
                                       'user_nimi': handler.c.user.fullname,
                                       'algused': algused,
                                       'konsultatsioonikohad': konsultatsiooniruumid,
                                       'kestus': kestus,
                                       'taiendavinfo': taiendavinfo,                                       
                                       })
    return subject, body

def _compose_epost_se(handler, k, sooritaja, taiendavinfo=None):
    "Seaduse tundmise eksami eksamikutse"
    sooritused = list(sooritaja.sooritused)
    sooritused.sort(key=lambda s: s.kavaaeg or s.algus)

    def get_aadress(koht, r_tahis, sulg=False):
        buf = koht.nimi
        if r_tahis:
            buf += ', ruum %s' % r_tahis
        tais_aadress = koht.tais_aadress
        if tais_aadress:
            if sulg:
                buf += ' (%s)' % (tais_aadress or '')
            else:
                buf += ', %s' % (tais_aadress or '')
        return buf

    for s in sooritused:
        algus = s.kavaaeg or s.algus or s.testiruum.algus
        if algus:
            aeg = algus.strftime('%d.%m.%Y kell %H.%M')
        else:
            aeg = ''
        ruum_tahis = s.testiruum.ruum and s.testiruum.ruum.tahis
        koht = s.testikoht.koht
        koht_aadress = get_aadress(koht, ruum_tahis, True)
        break
    
    konsultatsiooniruumid = []
    if sooritaja.soovib_konsultatsiooni or True:
        konsultatsiooniruumid = sooritaja.get_konsultatsiooniruumid()
        li = list()
        for (r_algus, koht, r_tahis) in konsultatsiooniruumid:
            if not r_algus:
                msg = "Konsultatsiooni alguse aeg on määramata ({koht}, {ruum})".format(koht=koht.nimi, ruum=r_tahis)
                raise Exception(msg)
            kons_aeg = r_algus.strftime('%d.%m.%Y kell %H.%M')
            kons_koht_aadress = get_aadress(koht, r_tahis)
            s = '%s %s' % (kons_aeg, kons_koht_aadress)
            li.append(s)
        konsultatsiooniruumid = li

    subject, body = handler.render_mail('mail/kohateade_se.mako', 
                                      {'isik_nimi': k.nimi, 
                                       'user_nimi': handler.c.user.fullname,
                                       'aeg': aeg,
                                       'koht_aadress': koht_aadress,
                                       'ruum_tahis': ruum_tahis,
                                       'konsultatsioonikohad': konsultatsiooniruumid,
                                       'taiendavinfo': taiendavinfo,                                       
                                       })
    return subject, body

def _compose_epost_ss(handler, k, sooritaja, taiendavinfo=None):
    "Sisseastumiseksami toimumise teade"
    kohad = []
    sooritused = list(sooritaja.sooritused)
    sooritused.sort(key=lambda s: s.kavaaeg or s.algus)

    for sooritus in sooritused:
        testikoht = sooritus.testikoht
        testiruum = sooritus.testiruum
        koht = testikoht and testikoht.koht
        ruum = testiruum and testiruum.ruum
        algus = testiruum and testiruum.algus
        testiosa = sooritus.testiosa
        if testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_I, const.VASTVORM_SE, const.VASTVORM_SP):
            kavaaeg = sooritus.kavaaeg
        else:
            tpr = sooritus.testiprotokoll
            kavaaeg = tpr and tpr.algus or algus
                
        rcd = (sooritus.testiosa.test.nimi,
               sooritus.testiosa.nimi,
               koht and koht.nimi,
               ruum and ruum.tahis or '',
               koht and koht.tais_aadress or '',
               algus and algus.strftime('%d.%m.%Y') or '',
               kavaaeg and kavaaeg.strftime('%d.%m.%Y kell %H.%M') or '')
        kohad.append(rcd)

    template = 'mail/kohateade_ss.mako'
    subject, body = handler.render_mail(template, 
                                      {'kohad':kohad,
                                       'isik_nimi': k.nimi, 
                                       'user_nimi': handler.c.user.fullname,
                                       'aasta': date.today().year,
                                       'taiendavinfo': taiendavinfo,
                                       })
    return subject, body

def _compose_epost_ke(handler, k, sooritaja, taiendavinfo=None):
    "Kutseeksami toimumise teade"
    kohad = []
    sooritused = list(sooritaja.sooritused)
    sooritused.sort(key=lambda s: s.kavaaeg or s.algus)

    for sooritus in sooritused:
        koht = sooritus.testikoht and sooritus.testikoht.koht
        ruum = sooritus.testiruum and sooritus.testiruum.ruum
        algus = sooritus.testiruum and sooritus.testiruum.algus
        testiosa = sooritus.testiosa
        if testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_I, const.VASTVORM_SE, const.VASTVORM_SP):
            kavaaeg = sooritus.kavaaeg
        else:
            kavaaeg = algus
            
        rcd = (sooritus.testiosa.test.nimi,
               sooritus.testiosa.nimi,
               koht and koht.nimi,
               ruum and ruum.tahis or '',
               koht and koht.tais_aadress or '',
               algus and algus.strftime('%d.%m.%Y') or '',
               kavaaeg and kavaaeg.strftime('%d.%m.%Y kell %H.%M') or '')
        kohad.append(rcd)

    template = 'mail/kohateade_ke.mako'
    subject, body = handler.render_mail(template, 
                                      {'kohad':kohad,
                                       'isik_nimi': k.nimi, 
                                       'user_nimi': handler.c.user.fullname,
                                       'aasta': date.today().year,
                                       'taiendavinfo': taiendavinfo,
                                       })
    return subject, body

def gen_pdf_all(handler, protsess, q, testiliik, get_sooritused, kirityyp, taiendavinfo=None):
    "PDFi genereerimine teate edastamiseks postiga"
    kasutajad = list(q.all())
    if kirityyp == model.Kiri.TYYP_MUU:
        doc = MuukiriDoc(handler, testiliik, protsess)
    else:
        doc = KohateadeDoc(handler, testiliik, protsess)
    filedata = doc.generate(kasutajad=kasutajad, get_sooritused=get_sooritused, taiendavinfo=taiendavinfo)
    if doc.error:
        if protsess:
            protsess.set_viga(doc.error)
        else:
            handler.error(doc.error)
    if protsess and filedata:
        protsess.filename = 'teade.pdf'
        protsess.filedata = filedata
    return filedata

def _get_regteade_sooritused(k, testiliik, on_epost, kordus=False):
    q = model.Session.query(model.Sooritaja, 
                            model.Toimumisaeg, 
                            model.Test)
    q = (q.join(model.Sooritaja.test)
         .join(model.Sooritaja.testimiskord)
         .filter(model.Testimiskord.osalemise_naitamine==True)
         .filter(model.Sooritaja.kasutaja_id==k.id)
         .join(model.Sooritaja.sooritused)
         .join(model.Sooritus.toimumisaeg)
         .filter(sa.or_(model.Toimumisaeg.kuni==None,
                        model.Toimumisaeg.kuni>=date.today()))
         .filter(model.Sooritaja.staatus==const.S_STAATUS_REGATUD)
         )

    # e-kiri 2015-11-24: mitte saata kirju tasumata registreeringute korral ja saata rv ja riigieksam korraga
    if testiliik in (const.TESTILIIK_RV, const.TESTILIIK_RIIGIEKSAM):
        q = q.filter(model.Test.testiliik_kood.in_((const.TESTILIIK_RV, const.TESTILIIK_RIIGIEKSAM)))
    elif testiliik:
        q = q.filter(model.Test.testiliik_kood==testiliik)

    if kordus == False:
        # mitte saata kordusteateid
        if on_epost:
            q = q.filter(model.Sooritaja.regteateaeg==None)
        else:
            q = q.filter(~ sa.exists().where(sa.and_(\
                    model.Sooritajakiri.sooritaja_id==model.Sooritaja.id,
                    model.Sooritajakiri.kiri_id==model.Kiri.id,
                    model.Kiri.tyyp==model.Kiri.TYYP_REGAMISTEADE)))

    q = q.order_by(model.Test.nimi, model.Toimumisaeg.tahised)
    li = list(q.all())
    if not li:
        q = q.with_entities(model.Sooritaja.id)
        log.debug('Registreeringuid ei leitud:\n%s' % model.str_query(q, True))
    return li  

def send_regteade(handler, kasutaja, testiliik, kontrolli_teatekanal=True, kordus=False):
    """Registreerimise teate saatmine (enne soorituskohateadet)
    Toimub testile registreerimise kinnitamisel.
    Ei toimu otsingute kasutajaliidese alt, aga funktsiooni hoiame siin.
    """
    h = handler.h
    def _get_koolitus_data(sooritaja, testimiskord):
        algus = lopp = koht_nimi = None
        # kas sooritaja on juba määratud ruumi? siis võib ruumi aega kasutada
        for tos in sooritaja.sooritused:
            testikoht = tos.testikoht
            if testikoht:
                koht_nimi = testikoht.koht.nimi
            testiruum = tos.testiruum
            if testiruum and testiruum.algus:
                algus = testiruum.algus
                lopp = testiruum.lopp
            break
        
        # kui ei ole määratud ruumi, siis kasutame toimumisaja aega
        if not algus:
            for ta in testimiskord.toimumisajad:
                for tp in ta.toimumispaevad:
                    if not algus or tp.aeg and algus > tp.aeg:
                        algus = tp.aeg
                    if not lopp or tp.lopp and lopp < tp.lopp:
                        lopp = tp.lopp
                # arvestame esimese toimumisaja aegu
                break
        alates = h.str_from_datetime(algus, hour0=False, skell=True)
        if not algus:
            vahemik = None                                                
        elif lopp.hour < 23 or lopp.minute < 59:
            vahemik = h.str_from_datetime(algus, skell=True) + ' kuni ' + h.str_from_datetime(lopp, skell=True)
        else:
            vahemik = h.str_from_date(algus) + ' kuni ' + h.str_from_date(lopp)
        return {'alates': alates,
                'vahemik': vahemik,
                'koht_nimi': koht_nimi,
                }
    
    def _get_params():
        testiliik_nimi = model.Klrida.get_str('TESTILIIK', testiliik)
        to = kasutaja.epost
        sooritajad_id = []
        sooritajad = []
        toimumisajad = []
        testimiskorrad_id = set()
        keeletasemed = set()
        reg_auto = False
        for rcd in _get_regteade_sooritused(kasutaja, testiliik, True, kordus=kordus):
            sooritaja = rcd[0]
            sooritaja_id = sooritaja.id
            if sooritaja_id not in sooritajad_id:
                sooritajad_id.append(sooritaja_id)
                extra = {}
                testimiskord = sooritaja.testimiskord
                if testiliik == const.TESTILIIK_KOOLITUS:
                    extra.update(_get_koolitus_data(sooritaja, testimiskord))
                if testimiskord.reg_kohavalik:
                    extra['koht_aeg'] = sooritaja.kohavalik_nimi or ''
                if testiliik == const.TESTILIIK_TASE:
                    if sooritaja.piirkond_id and sooritaja.soovib_konsultatsiooni:
                        likons = testimiskord.get_kons_prk(sooritaja.piirkond_id)
                        extra['kons'] = '; '.join(likons)
                sooritajad.append((sooritaja, extra))
                # extra sisaldab koolituse korral: alates, vahemik, koht_nimi
                # extra sisaldab kohavaliku korral: koht_aeg
                
            testimiskorrad_id.add(rcd[0].testimiskord_id)
            toimumisajad.append(rcd[1])
            test = rcd[2]
            keeletasemed.add(test.keeletase_kood)
            if rcd[0].reg_auto:
                reg_auto = True

        if len(sooritajad) > 0:
            teade6pv = True
            if len(keeletasemed) == 1:
                tmp_sooritaja = sooritajad[0][0]
                tmp_test = tmp_sooritaja.test or model.Test.get(tmp_sooritaja.test_id)
                keeletase = tmp_test.keeletase_nimi
                if tmp_test.testiliik_kood == const.TESTILIIK_RV and tmp_test.aine_kood == const.AINE_EN:
                    teade6pv = False
            else:
                keeletase = None
            params = {'sooritajad': sooritajad,
                      'testimiskorrad_id': testimiskorrad_id,
                      'keeletase': keeletase,
                      'testiliik_kood': testiliik,
                      'testiliik_nimi': testiliik_nimi,
                      'on_eksam': testiliik in const.TESTILIIGID_EKSAMID,
                      'on_lisaeksam': 'lisaeksam' in test.nimi,
                      'isik_nimi': kasutaja.nimi, 
                      'user_nimi': handler.c.user.fullname,
                      'teade6pv': teade6pv,
                      'reg_auto': reg_auto,
                      }
            return params
    model.Session.flush()
    params = _get_params()
    buf = 'Regteate saatmine %s, kasutaja.id %s:' % (kasutaja.isikukood, kasutaja.id)
    if not params:
        buf += ' registreeringud puuduvad'
        return False
    
    # e-kirja kujul teate koostamine
    mako = 'mail/regteade.mako'
    to = kasutaja.epost
    subject, body = handler.render_mail(mako, params)

    teatekanal = const.TEATEKANAL_EIS
    if kasutaja.epost:
        # kui e-posti aadress on olemas, siis saadame e-postiga
        err = Mailer(handler).send(to, subject, body, out_err=False)
        if not err:
            teatekanal = const.TEATEKANAL_EPOST
            log.debug(_("Saadetud kiri aadressile {s}").format(s=to))

    # kirja salvestamine süsteemis
    now = datetime.now()        
    kiri = model.Kiri(saatja_kasutaja_id=handler.c.user.id,
                      tyyp=model.Kiri.TYYP_REGAMISTEADE,
                      sisu=body,
                      teema=subject,
                      teatekanal=teatekanal)
    sooritajad = params['sooritajad']
    for sooritaja, extra in sooritajad:
        model.Sooritajakiri(sooritaja=sooritaja, kiri=kiri)
        sooritaja.regteateaeg = now
    model.Kirjasaaja(kiri=kiri, kasutaja_id=kasutaja.id, epost=to)
    model.Session.commit()

    log.info(buf)
    return True

def send_tyhteade(handler, kasutaja, sooritaja):
    """Registreerimise tühistamise teate saatmine
    Toimub kinnitatud registreerimise tühistamisel.
    Ei toimu otsingute kasutajaliidese alt, aga funktsiooni hoiame siin.
    """
    if sooritaja.staatus < const.S_STAATUS_REGATUD:
        # teateid saadetakse ainult registreeritud olekust tyhistamisel
        return
    if not sooritaja.regteateaeg:
        # kui pole saadetud registreerimisteadet, siis ei saada ka tyhistusteadet
        return
    to = kasutaja.epost
    test = sooritaja.test
    params = {'sooritaja': sooritaja,
              'isik_nimi': kasutaja.nimi, 
              'user_nimi': handler.c.user.fullname,
              'test_nimi': test.nimi,
              }

    buf = 'Tühistusteate saatmine %s, kasutaja.id %s:' % (kasutaja.isikukood, kasutaja.id)
    if not params:
        buf += ' registreeringud puuduvad'
        log.debug(buf)
        return False

    # e-kirja kujul teate koostamine
    mako = 'mail/tyhteade.mako'
    to = kasutaja.epost
    subject, body = handler.render_mail(mako, params)
    body = Mailer.replace_newline(body)

    teatekanal = const.TEATEKANAL_EIS
    if kasutaja.epost:
        # kui e-posti aadress on olemas, siis saadame e-postiga
        err = Mailer(handler).send(to, subject, body, out_err=False)
        if not err:
            teatekanal = const.TEATEKANAL_EPOST
            log.debug(_("Saadetud kiri aadressile {s}").format(s=to))

    # kirja salvestamine süsteemis
    kiri = model.Kiri(saatja_kasutaja_id=handler.c.user.id,
                      tyyp=model.Kiri.TYYP_TYHISTUSTEADE,
                      sisu=body,
                      teema=subject,
                      teatekanal=teatekanal)
    model.Sooritajakiri(sooritaja=sooritaja, kiri=kiri)
    model.Kirjasaaja(kiri=kiri, kasutaja_id=kasutaja.id, epost=to)
    model.Session.commit()

    log.info(buf)
    return True

