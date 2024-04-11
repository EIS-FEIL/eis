import math
from time import mktime
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import rahvastikuregister
from eis.handlers.ekk.korraldamine.soorituskohad import genereeri_oppurite_kohad, jaota_sooritajad

log = logging.getLogger(__name__)

class SooritajadController(BaseResourceController):
    _permission = 'korraldamine'
    _MODEL = model.Sooritaja
    _SEARCH_FORM = forms.ekk.korraldamine.KohtSooritajadForm
    _INDEX_TEMPLATE = '/ekk/korraldamine/koht.sooritajad.mako' 
    _LIST_TEMPLATE = '/ekk/korraldamine/koht.sooritajad_list.mako'
    _DEFAULT_SORT = 'testiruum.tahis,testiprotokoll.tahis,sooritus.tahis,sooritaja.lang_LS,sooritaja.perenimi sooritaja.eesnimi'
    _ignore_default_params = ['csv','xls','format','otsi']
    
    def _query(self):
        testikoht_id = self.c.testikoht_id or None
        # kui self.c.testikoht_id==0, siis otsitakse 
        # määramata soorituskohaga sooritajaid ehk testikoht_id=None
        q = (model.SessionR.query(model.Sooritus, 
                                 model.Sooritaja, 
                                 model.Kasutaja,
                                 model.Koolinimi.nimi,
                                 model.Piirkond.nimi,
                                 model.Testiruum)
             .join(model.Sooritus.sooritaja)
             .filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id)
             .filter(model.Sooritus.testikoht_id==testikoht_id)
             .filter(model.Sooritus.staatus>const.S_STAATUS_REGAMATA)
             .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
             .join(model.Sooritaja.kasutaja)
             .outerjoin(model.Sooritaja.koolinimi)
             .outerjoin(model.Sooritaja.piirkond)
             .outerjoin(model.Sooritus.testiruum)
             .outerjoin(model.Sooritus.testiprotokoll)
             )
        if not testikoht_id:
            # kui on soorituskohata sooritajad
            # ja kasutaja on piirkondlik korraldaja
            # siis kuvame ainult need sooritajad,
            # kes on kasutajale lubatud piirkonda soovinud
            piirkonnad_id = self.c.user.get_kasutaja().get_piirkonnad_id('korraldamine', const.BT_SHOW,
                                                                         testiliik=self.c.toimumisaeg.testiosa.test.testiliik_kood)
            # kas pole õigust kõigi piirkondade korraldamiseks?
            if None not in piirkonnad_id:
                # piirkondlik korraldaja ei või kõiki kohti vaadata, 
                # talle kuvatakse ainult nende piirkondade koolid, mis talle on lubatud
                q = q.filter(model.Sooritaja.piirkond_id.in_(piirkonnad_id))
                self.c.on_piirkondlik = True
            else:
                self.c.on_piirkondlik = False
        return q

    def _get_opt(self, q):
        "Leitakse filtri valikud vastavalt testikoha sooritajate andmetele"
        c = self.c
        NULL = '-'
        NULL_TITLE = _("puudub")
        def _opt(id_field, title_field=None, sort_field=None, ftitle=None, fid=None):
            if title_field is None:
                title_field = id_field
            if sort_field is None:
                sort_field = title_field
            q_opt = (q.with_entities(id_field, title_field)
                     .distinct()
                     .order_by(sort_field)
                     )
            li = []
            is_null = False
            for (id, title) in q_opt.all():
                if fid:
                    id = fid(id)
                if ftitle:
                    title = ftitle(title)
                if not id:
                    is_null = True
                else:
                    li.append((id, title or NULL_TITLE))
            if is_null:
                # et tyhi string ja None ei oleks eraldi valikud, lisame yhe korra
                li.append((NULL, NULL_TITLE))
            return li

        if c.testikoht:
            c.opt_testiruum = _opt(model.Sooritus.testiruum_id,
                                   model.Testiruum.tahis)
            c.opt_ruum = _opt(model.Testiruum.ruum_id,
                              ftitle=lambda r_id: r_id and model.Ruum.get(r_id).tahis)
            c.opt_tprotokoll = _opt(model.Sooritus.testiprotokoll_id,
                                    model.Testiprotokoll.tahis)
            c.opt_aeg = _opt(model.Sooritus.kavaaeg,
                             ftitle=self.h.str_from_datetime,
                             fid=lambda d: d and int(mktime(d.timetuple())))
            c.opt_kuupaev = _opt(model.Sooritus.kavaaeg,
                                 ftitle=self.h.str_from_date,
                                 fid=lambda d: d and int(mktime(d.timetuple())))
            c.opt_kuupaev = []
            for id, title in c.opt_aeg:
                kpv = title.split(' ', 1)[0]
                if kpv not in c.opt_kuupaev:
                    c.opt_kuupaev.append(kpv)
        else:
            c.opt_staatus = _opt(model.Sooritaja.staatus,
                                 ftitle=lambda st: c.opt.S_STAATUS.get(st))
        c.opt_koolinimi = _opt(model.Sooritaja.koolinimi_id, model.Koolinimi.nimi)
        c.opt_klass = _opt(model.Sooritaja.klass)
        c.opt_paralleel = _opt(model.Sooritaja.paralleel)
        c.opt_soorituskeel = _opt(model.Sooritaja.lang,
                                  sort_field=sa.func.lang_sort(model.Sooritaja.lang),
                                  ftitle=model.Klrida.get_lang_nimi)
        c.opt_piirkond = _opt(model.Sooritaja.piirkond_id, model.Piirkond.nimi)

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        NULL = '-'
        self._get_opt(q)

        def _fnull(field, value, empty=False):
            if value != NULL:
                return field == value
            elif not empty:
                return field == None
            else:
                return sa.or_(field==None, field=='')
        # kui mõni sooritaja on olemas, siis saab filtreerida ja kuvame filtri nuppu
        c.is_filter = q.count() > 0
        if c.testiruum_id:
            q = q.filter(_fnull(model.Sooritus.testiruum_id, c.testiruum_id))
        if c.ruum_id:
            if c.ruum_id == NULL:
                q = q.filter(sa.or_(model.Sooritus.testiruum_id==None,
                                    model.Testiruum.ruum_id==None))
            else:
                q = q.filter(model.Testiruum.ruum_id==c.ruum_id)
        if c.tprotokoll_id:
            q = q.filter(_fnull(model.Sooritus.testiprotokoll_id, c.tprotokoll_id))
        if c.koolinimi_id:
            q = q.filter(_fnull(model.Sooritaja.koolinimi_id, c.koolinimi_id))
        if c.klass:
            q = q.filter(_fnull(model.Sooritaja.klass, c.klass, True))
        if c.paralleel:
            q = q.filter(_fnull(model.Sooritaja.paralleel, c.paralleel, True))
        if c.lang:
            q = q.filter(_fnull(model.Sooritaja.lang, c.lang, True))
        if c.piirkond_id:
            q = q.filter(_fnull(model.Sooritaja.piirkond_id, c.piirkond_id))
        if c.aeg:
            if c.aeg == NULL:
                aeg = None
            else:
                aeg = datetime.fromtimestamp(int(c.aeg))
            q = q.filter(model.Sooritus.kavaaeg==aeg)
        if c.kuupaev:
            try:
                kuupaev = utils.date_from_str(c.kuupaev)
                q = (q.filter(model.Sooritus.kavaaeg >= kuupaev)
                     .filter(model.Sooritus.kavaaeg < kuupaev + timedelta(days=1)))
            except:
                q = q.filter(model.Sooritus.kavaaeg==None)
                
        if c.staatus:
            q = q.filter(model.Sooritaja.staatus==c.staatus)

        if c.testsessioon_id:
            q = q.filter(model.Toimumisaeg.testimiskord.has(
                    model.Testimiskord.testsessioon_id==int(c.testsessioon_id)))
        return q

    def _order_join(self, q, tablename):
        """Otsingupäringu sortimisel lisatakse päringule join 
        tabeliga, mille välja järgi tuleb sortida
        """
        if tablename == 'ruum':
            q = q.outerjoin(model.Testiruum.ruum)
        return q

    def _paginate(self, q):
        # ei pagineeri, sest Andres soovis 2011-01-19 koosolekul 
        # kõik sama kooli õpilased ühel lehel
        if self.c.ttabel:
            # kuvada tabelina
            if self.c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_KP):
                # kirjalik
                self.c.ttabel = ''
            else:
                self.c.ttabel_data = self._ttabel(q, self.c.intervall)
            self._tt_ajad()
        return q.all()

    def _tt_ajad(self):
        c = self.c
        dint = timedelta(minutes=c.intervall or 20)        

        # leiame päevad ja iga päeva varaseima soorituse aja
        q1 = (model.SessionR.query(sa.func.min(model.Sooritus.kavaaeg),
                                  sa.func.max(model.Sooritus.kavaaeg),
                                  sa.func.date_trunc('day', model.Sooritus.kavaaeg))
             .filter(model.Sooritus.testikoht_id==c.testikoht.id)
             .group_by(sa.func.date_trunc('day', model.Sooritus.kavaaeg))
             .order_by(sa.func.date_trunc('day', model.Sooritus.kavaaeg)))

        paevad = {}
        opt_paev = []
        opt_kell = []
        for min_aeg, max_aeg, day in q1.all():
            # leiame iga päeva sees vahemikud

            begin_day = datetime.combine(min_aeg, time(8,0))
            end_day = datetime.combine(min_aeg, time(14, 0))

            while min_aeg > begin_day:
                min_aeg -= dint
            max_aeg = max_aeg + dint
            if max_aeg < end_day:
                max_aeg = end_day

            Kell = model.SessionR.query(
                sa.func.generate_series(min_aeg, max_aeg, dint).label('kell')
                ).subquery()

            # leiame soorituste arvu vahemike ja ruumide lõikes
            sooritused = {}
            q2 = (model.SessionR.query(Kell.c.kell,
                                      model.Sooritus.testiruum_id,
                                      sa.func.count(model.Sooritus.id))
                  .filter(model.Sooritus.testikoht_id==c.testikoht.id)
                  .filter(model.Sooritus.kavaaeg >= Kell.c.kell)
                  .filter(model.Sooritus.kavaaeg < Kell.c.kell + dint)
                  .group_by(Kell.c.kell, model.Sooritus.testiruum_id))
            for kell, testiruum_id, cnt in q2.all():
                sooritused[(kell, testiruum_id)] = cnt

            # leiame kõik selle päeva ruumid
            q3 = (model.SessionR.query(model.Testiruum.id,
                                      model.Testiruum.tahis)
                  .filter_by(testikoht_id=c.testikoht.id)
                  .join(model.Testiruum.ruum)
                  .filter(model.Testiruum.algus >= day)
                  .filter(model.Testiruum.algus < day + timedelta(days=1))
                  .order_by(model.Ruum.tahis)
                  )
            testiruumid = list(q3.all())

            # teeme loetelu, kus iga vahemiku ja ruumi jaoks on rida
            s_paev = self.h.str_from_date(day)
            kell = min_aeg
            while kell < max_aeg:
                s_kell = self.h.str_time_from_datetime(kell)
                ts = int(kell.timestamp())
                for tr_id, r_tahis in testiruumid:
                    cell_id = '%s_%s' % (ts, tr_id)
                    label = '%s ruum %s' % (s_kell, r_tahis)
                    cnt = sooritused.get((kell, tr_id)) or 0
                    opt_kell.append((cell_id, label, cnt, s_paev))
                kell += dint
            opt_paev.append((s_paev, s_paev))

        c.opt_paev = opt_paev
        c.opt_kell = opt_kell

    def _ttabel(self, q, intervall):
        "Sooritajate loetelu andmed kellaaegade tabelis kuvamiseks"

        dint = timedelta(minutes=intervall or 20)
        class SooritusData:
            def __init__(self, sooritus_id, tahised, nimi, kavaaeg, testiruum_id):
                self.sooritus_id = sooritus_id
                self.tahised = tahised
                self.nimi = nimi
                self.kavaaeg = kavaaeg
                self.testiruum_id = testiruum_id
                
        # leiame päringu andmed
        items = []
        testiruumid_set = set()
        min_aeg = max_aeg = None
        for tos, sooritaja, kasutaja, k_nimi, prk_nimi, testiruum in q.all():
            tpr = tos.testiprotokoll
            tpr_tahis = tpr and tpr.tahis or ''
            
            item = SooritusData(tos.id, tpr_tahis, sooritaja.nimi, tos.kavaaeg, tos.testiruum_id)
            items.append(item)
            testiruumid_set.add(tos.testiruum_id)
            if not min_aeg or min_aeg > tos.kavaaeg:
                min_aeg = tos.kavaaeg
            if not max_aeg or max_aeg < tos.kavaaeg:
                max_aeg = tos.kavaaeg

        if not min_aeg:
            return
        if min_aeg.date() != max_aeg.date():
            # tabeli kuvame ainult yhe päeva kohta, muidu võib tekkida liiga palju ridu
            self.error(_("Palun valida kuupäev"))
            return

        # leiame ruumid tabeli veergudeks
        header = [_("Algus")]
        testiruumid_id = []
        q = (model.SessionR.query(model.Testiruum.id, model.Testiruum.tahis)
             .filter(model.Testiruum.id.in_(testiruumid_set))
             .order_by(model.Testiruum.tahis))
        for (testiruum_id, tahis) in q.all():
            header.append(_("Ruum {s}").format(s=tahis))
            testiruumid_id.append(testiruum_id)

        # kellaaja vahemikud tabeli ridadeks
        rows = []
        algus = min_aeg
        while algus <= max_aeg:
            lopp = algus + dint
            row = [algus]
            for testiruum_id in testiruumid_id:
                sooritused = [item for item in items \
                              if item.testiruum_id == testiruum_id \
                              and algus <= item.kavaaeg < lopp]
                row.append((testiruum_id, sooritused))
            rows.append(row)
            algus = lopp

        return header, rows

    def create(self):
        """Sooritajate lisamine ja suunamine
        """
        # peale sooritajate ümbersuunamist on vaja kogused uuesti arvutada
        # kuna p-testis protokollis peavad sooritajad olema tähestiku järjekorras
        if self.c.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
            self.c.toimumisaeg.on_kogused = 0
            self.c.toimumisaeg.on_hindamisprotokollid = 0
        self.c.toimumisaeg.on_ymbrikud = 0
        
        sub = self._get_sub()
        if self.request.params.get('proto'):
            # protokollirühmad luuakse uuesti
            return self._create_proto()
        elif sub == 'suunamine':
            # valitud sooritajate suunamine valitud kohta
            return self._create_suunamine()
        elif self.request.params.get('genereeri'):
            # soorituskohata soorituste suunamine oma kooli
            return self._create_genereeri()
        elif self.request.params.get('jaota'):
            # soorituskohata soorituste suunamine eelistatud piirkonna järgi
            return self._create_jaota()
        elif self.request.params.get('kell'):
            # suulise testi sooritajate kellaaegade salvestamine
            return self._create_kell()
        elif sub == 'tpr':
            # käsitsi uue testiprotokollirühma loomine
            return self._create_tpr()
        elif sub == 'teinekord':
            return self._create_teinekord()
        elif sub == 'jaotaruumi':
            return self._create_jaotaruumi()
        elif sub == 'markus':
            return self._create_markus()
        elif sub == 'parool':
            return self._create_parool()                        
        elif sub == 'klass':
            return self._create_klass()                        
        else:
            # valitud soorituste suunamine jooksvasse kohta
            return self._create_lisa()

    def _create_proto(self):
        "Protokollirühmad luuakse uuesti"

        q = (model.Sooritus.query
             .filter_by(testikoht_id=self.c.testikoht.id)
             .join(model.Sooritus.sooritaja))
        list_sort = self.request.params.get('list_sort')
        if q.filter(model.Sooritus.klastrist_toomata==True).count() > 0:
            self.error(_("Enam ei saa protokollirühmi muuta, sest sooritamine juba käib!"))
            return self._redirect('index', sort=list_sort)        
        if list_sort:
            # sorteerime sooritused selles järjekorras, milles kasutaja on loetelu järjestanud
            q = (q.join(model.Sooritaja.kasutaja)
                 .outerjoin(model.Sooritaja.kool_koht)
                 .outerjoin(model.Sooritaja.piirkond)
                 .join(model.Sooritus.testiruum)
                 .outerjoin(model.Testiruum.ruum)
                 .outerjoin(model.Sooritus.testiprotokoll))
            q = self._order(q, list_sort)
        else:
            # vaikimisi sordime nime järjekorras
            q = q.order_by(sa.text('lang_sort(lang),perenimi,eesnimi'))
        #model.log_query(q)
        sooritused = list(q.all())
                 
        # tyhistame varasemad protokollidesse jaotamised
        for tos in sooritused:
            tos.testiprotokoll = None
            #log.info('tos.id=%s tahis=%s ruum=%s' % (tos.id, tos.tahised, tos.testiruum_id))
            tos.tahis = tos.tahised = None
        self.c.testikoht.sooritused_seq = 0

        # eemaldame kõigilt protokollidelt tähise
        for tr in self.c.testikoht.testiruumid:
            for tpr in tr.testiprotokollid:
                tpr.tahis = '' # ei pea unikaalne olema
                tpr.tahised = '%s#' % tpr.tahised # peab olema unikaalne

        # valime kõigile sooritustele protokolli uuesti,
        # nii et protokollid järjest täituks
        # seejuures määratakse nii protokollirühmadele kui ka sooritustele uued tähised
        for tos in sooritused:
            # suuname ruumi
            rc, err = tos.suuna(tos.testikoht, tos.testiruum, err=True, valim_kontroll=False)
            if err:
                self.error(err)
            if list_sort:
                # genereerime tähise selleks, et kasutaja valitud järjekorda säilitada
                tos.gen_tahis()

        # eemaldame yle jäänud protokollid
        # nii, et kasutusel olevate protokollide tähiseid ei muudeta
        self.c.testikoht.reset_testiprotokollid(True)

        model.Session.commit()
        self.success(_("Sooritajad on uuesti protokollirühmadesse jaotatud"))
        return self._redirect('index', sort=list_sort)

    def _create_lisa(self):
        "Sooritajate lisamine jooksvasse kohta"

        assert self.c.testikoht is not None, _("Testikoht puudub")
        testiosa_id = self.c.toimumisaeg.testiosa_id

        testikoht = self.c.testikoht
        if not len(testikoht.testiruumid):
            testiruum = testikoht.give_testiruum(None)
            testiruum.give_labiviijad()

        testiruumid = set()
        warnings = set()
        
        def _get_testiruum(valimis):
            for testiruum in testikoht.testiruumid:
                if sooritaja.valimis and not testiruum.valim_lubatud:
                    continue
                vabukohti = testiruum.vabukohti
                if vabukohti is None or vabukohti > 0:
                    return testiruum
        
        cnt = cnt_err = 0
        for sooritaja_id in self.request.params.getall('valik_id'):
            rcd = model.Sooritus.query.\
                filter_by(sooritaja_id=int(sooritaja_id)).\
                filter_by(toimumisaeg_id=self.c.toimumisaeg.id).\
                first()
            if not rcd:
                self.error(_("Soorituse kirjet (sooritaja {s}) ei leitud").format(s=sooritaja_id))
                continue
            elif rcd.testikoht_id:
                self.error(_("Sooritaja {s} on juba suunatud").format(
                    s='%s %s' % (rcd.sooritaja.eesnimi, rcd.sooritaja.perenimi)))
                continue
            else:
                # leiame testiruumi, kus on vabu kohti
                found = False
                sooritaja = rcd.sooritaja
                testiruum = _get_testiruum(sooritaja.valimis)
                if not testiruum:
                    if sooritaja.valimis:
                        # otsime valimile keelatud ruume ja kui on, suuname sinna
                        testiruum = _get_testiruum(False)
                        if testiruum:
                            warnings.add(_("Valimis lubatud ajaga vaba testiruumi ei leitud"))
                    if not testiruum:
                        self.error(_("Vabu kohti on liiga vähe"))
                        continue
                    
                # suuname
                if rcd.testiruum:
                    testiruumid.add(rcd.testiruum)
                testiruumid.add(testiruum)
                if rcd.suuna(testikoht, testiruum, valim_kontroll=False):
                    cnt += 1
                else:
                    cnt_err += 1

        if cnt or cnt_err:
            for testiruum in testiruumid:
                testiruum.set_sooritajate_arv()

            model.Session.commit()
            if cnt == 1:
                self.success(_("Suunatud 1 sooritaja"))
            elif cnt:
                self.success(_("Suunatud {n} sooritajat").format(n=cnt))
            if cnt_err:
                self.error(_("Ei saanud suunata {n} sooritajat").format(n=cnt_err))
            for msg in warnings:
                self.warning(msg)
        return self._redirect('index')

    def _create_genereeri(self):
        """Soorituskohata sooritajate suunamine oma kooli. 
        Kui kool ei ole soorituskoht, siis lisatakse soorituskoht ja suunatakse ikkagi.
        """
        genereeri_oppurite_kohad(self, self.c.toimumisaeg)
        url = self.url('korraldamine_soorituskohad', toimumisaeg_id=self.c.toimumisaeg.id)
        return HTTPFound(location=url)

    def _create_jaota(self):
        """Soorituskohata sooritajate jaotamine eelistatud piirkonna järgi.
        """
        jaota_sooritajad(self)
        return self._redirect('index')

    def _create_suunamine(self):
        """Sooritaja suunamine soorituskohta
        """
        testiruum = None
        for key in self.request.params:
            # submit-nupu "Vali" nimi oli "valik_id_ID", siit saame uue testikoha ID
            prefix = 'valik_id_'
            if key.startswith(prefix):
                testiruum_id = key[len(prefix):]
                testiruum = model.Testiruum.get(testiruum_id)
                break
        
        if not testiruum:
            self.error(_("Vali testiruum, kuhu suunata"))
            return self._redirect('index')

        testikoht = testiruum.testikoht
        assert testikoht.toimumisaeg_id == self.c.toimumisaeg.id, _("Vale toimumisaeg")
        sooritused_id = self.request.params.getall('sooritus_id')
        lisatakse = len(sooritused_id)

        vabukohti = testiruum.vabukohti
        if vabukohti is not None and vabukohti < lisatakse:
            jubaruumis = model.SessionR.query(sa.func.count(model.Sooritus.id)).\
                         filter(model.Sooritus.id.in_(sooritused_id)).\
                         filter(model.Sooritus.testiruum_id==testiruum.id).\
                         scalar() or 0
            if vabukohti < lisatakse - jubaruumis:
                self.error(_("Valitud ruumis on vabu kohti ainult {n}").format(n=vabukohti))
                return self._redirect('index')
        
        # koolisisesel ümbersuunamisel võib olla valitud ka protokollirühm
        tpr_id = self.request.params.get('tpr_id')
        tpr = tpr_id and model.Testiprotokoll.get(tpr_id)

        testiruumid = set([testiruum])
        errors = set()
        warnings = set()
        cnt = cnt_err = 0
        for sooritus_id in sooritused_id:
            if not sooritus_id:
                continue
            rcd = model.Sooritus.get(sooritus_id)

            if rcd.testiruum:
                testiruumid.add(rcd.testiruum)

            rc, error = rcd.suuna(testikoht, testiruum, tpr=tpr, err=True, valim_kontroll=False)
            if rc:
                cnt += 1
                if error:
                    warnings.add(error)
            else:
                cnt_err += 1
                errors.add(error)
                
        if cnt or cnt_err:
            for testiruum in testiruumid:
                testiruum.set_sooritajate_arv()
            model.Session.commit()
            if cnt == 1:
                self.success(_("Suunatud 1 sooritaja"))
            elif cnt:
                self.success(_("Suunatud {n} sooritajat").format(n=cnt))
            if cnt_err:
                self.error(_("Ei saanud suunata {n} sooritajat").format(n=cnt_err))
                for error in errors:
                    self.error(error)
            for msg in warnings:
                self.warning(msg)
        return self._redirect('index')

    def _create_kell(self):
        """Suulise testi sooritajate alguse kellaaja salvestamine
        """
        # kellaaja salvestamine
        self.form = Form(self.request, schema=forms.avalik.admin.KSooritajadForm)
        if not self.form.validate():
            return self._error_create()
        is_all = True
        on_ttabel = self.request.params.get('upd_ttabel')
        for rcd in self.form.data.get('s'):
            moved = rcd.get('moved')
            if on_ttabel and not moved:
                # tabeliga salvestamine, aga midagi ei muudetud
                continue
            item = model.Sooritus.get(rcd.get('sooritus_id'))
            assert item.testikoht_id == self.c.testikoht.id and \
                   item.toimumisaeg_id == self.c.toimumisaeg.id, _("Vale koht")

            if on_ttabel:
                cell_id = rcd.get('cell_id')
                ts, uus_testiruum_id = map(int, cell_id.split('_'))
                kavaaeg = datetime.fromtimestamp(ts)

                if uus_testiruum_id and uus_testiruum_id != item.testiruum_id:
                    # kui ruum ka muutus
                    testiruum = model.Testiruum.get(uus_testiruum_id)
                    testikoht = item.testikoht
                    assert testiruum.testikoht_id == testikoht.id, 'Vale testiruum'
                    item.suuna(testikoht, testiruum, valim_kontroll=False)

                testiruum = item.testiruum
                assert testiruum.algus.date() == kavaaeg.date(), 'vale päev'
            else:
                kell = rcd.get('kellaaeg')
                if not kell:
                    is_all = False
                    continue
                testiruum = item.testiruum
                kavaaeg = datetime.combine(testiruum.algus, time(*kell))
            item.kavaaeg = kavaaeg
            log.debug('KELL %s %s' % (item.tahis, kavaaeg))

        if not is_all:
            self.warning(_("Kõigile sooritajatele ei olnud kellaaega sisestatud"))
        model.Session.commit()
        return self._redirect('index', lang=self.params_lang())

    def _create_tpr(self):
        """Protokollirühma lisamine
        """
        pakett = model.Testipakett.get(self.request.params.get('pakett_id'))
        assert pakett.testikoht_id == self.c.testikoht_id, _("Vale koht")

        testiruum = model.Testiruum.get(self.request.params.get('testiruum_id'))
        assert testiruum.testikoht_id == self.c.testikoht_id, _("Vale koht")

        tpr = model.Testiprotokoll(tahis='',
                                   tahised='',
                                   testiruum=testiruum,
                                   testipakett=pakett)
        tpr.gen_tahis()
        model.Session.commit()
        return self._redirect('index', lang=self.params_lang())

    def _new_teinekord(self):
        """Sooritajate jaotamine teisele testimiskorrale,
        määratakse sooritajate arv ja valitakse testimiskord.
        """
        c = self.c
        tkord = self.c.toimumisaeg.testimiskord
        q = (model.Testimiskord.query
             .filter(model.Testimiskord.test_id==tkord.test_id)
             .filter(model.Testimiskord.id!=tkord.id)
             .filter(sa.or_(model.Testimiskord.alates==None,
                            model.Testimiskord.alates>=date.today()))
             .filter(~ model.Testimiskord.toimumisajad.any(model.Toimumisaeg.kohad_kinnitatud==True))
             )
        c.teisedkorrad = q.all()

        c.sooritused_id = self.request.params.getall('sooritus_id')
        if c.sooritused_id:
            c.total_cnt = len(c.sooritused_id)
        else:
            q = (model.SessionR.query(sa.func.count(model.Sooritus.id))
                 .filter(model.Sooritus.testikoht_id==c.testikoht_id)
                 .filter(model.Sooritus.staatus==const.S_STAATUS_REGATUD))
            c.total_cnt = q.scalar()
        return self.render_to_response('/ekk/korraldamine/korravalik.mako')

    def _create_teinekord(self):
        """Sooritajate jaotamine teisele testimiskorrale.
        """
        c = self.c
        arv = self.request.params.get('arv')
        if arv: 
            arv = int(arv)
        else:
            arv = None
        soovitud_arv = arv    
        for key in self.request.params:
            if key.startswith('tk_'):
                uus_tk_id = int(key[3:])

        uus_tk = model.Testimiskord.get(uus_tk_id)
        keeled = uus_tk.get_keeled()
        testiruumid = set()
        testikoht_id = c.testikoht and c.testikoht.id or None
        
        # kõigi sobivate sooritajate päring
        q = (model.SessionR.query(model.Sooritaja.id)
             .join(model.Sooritaja.sooritused)
             .filter(model.Sooritus.toimumisaeg_id==c.toimumisaeg.id)
             .filter(model.Sooritus.testikoht_id==testikoht_id)
             .filter(model.Sooritaja.staatus==const.S_STAATUS_REGATUD)
             .filter(model.Sooritaja.lang.in_(keeled))
             )
        c.sooritused_id = self.request.params.getall('sooritus_id')
        if c.sooritused_id:
             sooritused_id = list(map(int, c.sooritused_id))
             q = q.filter(model.Sooritus.id.in_(sooritused_id))
        #model.log_query(q)
        cnt = q.count()
        valik = []
        # valime juhuslikud indeksid vahemikus [0, cnt)
        if arv is None or arv >= cnt:
            # kõik viiakse teisele testimiskorrale
            arv = cnt
        else:
            # valitakse juhuslikult osa sooritajatest, kes viiakse teisele testimiskorrale
            for n in range(arv):
                r = random.randrange(0, cnt)
                while r in valik:
                    r = r < cnt - 1 and r + 1 or 0
                valik.append(r)
        log.debug(f'valik={valik} arv={arv} cnt={cnt}')
        # valitud indeksitega sooritajad tõstame teise testimiskorda
        for n, (sooritaja_id,) in enumerate(q.all()):
            if not valik or (n in valik):
                sooritaja = model.Sooritaja.get(sooritaja_id)
                sooritaja.testimiskord = uus_tk
                for sooritus in sooritaja.sooritused:
                    testiosa = sooritus.testiosa
                    sooritus.reg_toimumispaev_id = None
                    sooritus.toimumisaeg = uus_tk.get_toimumisaeg(testiosa)
                    if sooritus.testiruum:
                        testiruumid.add(sooritus.testiruum)
                        sooritus.testiruum = None
                    sooritus.testikoht = None
                    if sooritus.algus and testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
                        sooritus.algus = None

        # arvutame ära viidud sooritajate vanade ruumide täituvuse üle
        for testiruum in testiruumid:
            testiruum.set_sooritajate_arv()

        if arv > 0:
            c.toimumisaeg.on_kogused = c.toimumisaeg.on_hindamisprotokollid = 0
            if soovitud_arv is not None and soovitud_arv > arv:
                self.success(_("Suunatud {n} sooritajat, rohkem polnud võimalik").format(n=arv))
            else:
                self.success(_("Suunatud {n} sooritajat").format(n=arv))
            model.Session.commit()
        else:
            self.error(_("Ühtki sooritajat polnud võimalik valitud testimiskorrale suunata"))

        return self._redirect('index', lang=self.params_lang())

    def _new_jaotaruumi(self):
        """Sooritajate jaotamine juhuslikult ruumidesse
        määratakse sooritajate arv ja valitakse ruumid
        """
        return self.render_to_response('/ekk/korraldamine/koht.jaotaruumivalik.mako')

    def _create_jaotaruumi(self):
        """Sooritajate jaotamine ruumidesse juhuslikult
        """
        arv = self.request.params.get('arv')
        if arv: 
            arv = int(arv)
        else:
            arv = None

        testiruumid = []
        for truum_id in self.request.params.getall('truum_id'):
            testiruum = model.Testiruum.get(truum_id)
            ruumiarv = self.request.params.get('arv_%s' % truum_id)
            ruumiarv = ruumiarv and int(ruumiarv) or None
            testiruumid.append([testiruum, ruumiarv])
        ruumiarvud_kokku = sum([r[1] or 0 for r in testiruumid])
        
        cnt_ruumid = len(testiruumid)
        if cnt_ruumid == 0:
            self.error(_("Ruumid on valimata"))
            return self._redirect('index', lang=self.params_lang())

        # kõigi sobivate sooritajate päring
        q = model.SessionR.query(model.Sooritus.id).\
            filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id).\
            filter(model.Sooritus.testikoht_id==self.c.testikoht_id).\
            filter(model.Sooritus.staatus==const.S_STAATUS_REGATUD)
        sooritused_id = [id for id, in q.all()]
        cnt = len(sooritused_id)

        # valime juhuslikud indeksid vahemikus [0, cnt)
        if arv is None or arv > cnt:
            valitud_id = sooritused_id
            arv = cnt
        else:
            valik = []
            for n in range(arv):
                r = random.randrange(0, cnt)
                while r in valik:
                    r = r < cnt - 1 and r + 1 or 0
                valik.append(r)
            valitud_id = [sooritused_id[n] for n in valik]

        if ruumiarvud_kokku > arv:
            koef = float(arv) / ruumiarvud_kokku
            for r in testiruumid:
                if r[1] is not None:
                    r[1] = math.ceil(r[1] * koef)
        
        n_ruum = -1 # ruumi indeks, kuhu tõstetakse
        cnt_maaratud = 0 # mitu sooritajat on suunatud

        # tõstame valitud ymber
        for sooritus_id in valitud_id:
            sooritus = model.Sooritus.get(sooritus_id)

            n_ruum += 1
            if cnt_ruumid == 0:
                self.error(_("Kõiki ei saanud jaotada, kuna valitud ruumides polnud piisavalt vabu kohti"))
                break

            while True:
                # valime ruumi
                testiruum = None
                
                # esmalt kasutame need ruumid, mille kohta oli antud arv
                for n, r in enumerate(testiruumid):
                    truum, ruumiarv = r
                    if ruumiarv and ruumiarv > 0:
                        ruumiarv -= 1
                        if ruumiarv == 0:
                            testiruumid.pop(n)
                            cnt_ruumid -= 1
                            n_ruum = -1
                        else:
                            r[1] = ruumiarv
                            n_ruum = n
                        testiruum = truum
                        break

                if not testiruum:
                    # siis jagame yhtlaselt nende ruumide vahel, kus on veel ruumi
                    if n_ruum >= cnt_ruumid:
                        n_ruum = 0

                    testiruum = testiruumid[n_ruum][0]
                    if sooritus.testiruum_id == testiruum.id:
                        # juba on selles ruumis
                        cnt_maaratud += 1
                        break

                vabukohti = testiruum.vabukohti
                if vabukohti is None or vabukohti > 0:
                    # siia ruumi saab panna
                    if sooritus.testiruum:
                        sooritus.testiruum.sooritajate_arv -= 1
                    if sooritus.suuna(testiruum.testikoht, testiruum, valim_kontroll=False):
                        testiruum.sooritajate_arv += 1
                        cnt_maaratud += 1
                    model.Session.flush()
                    break
                else:
                    # selles ruumis pole vabu kohti
                    if n_ruum != -1:
                        testiruumid.pop(n_ruum)
                        cnt_ruumid -= 1
                    if n_ruum >= cnt_ruumid:
                        n_ruum = 0
                    if cnt_ruumid == 0:
                        self.error(_("Kõiki ei saanud jaotada, kuna valitud ruumides polnud piisavalt vabu kohti"))
                        break

        if cnt_maaratud > 0:
            self.success(_("Jaotatud {n} sooritajat").format(n=cnt_maaratud))
            model.Session.commit()
        elif len(valitud_id) == 0:
            self.error(_("Pole ühtki registreeritud sooritajat, keda oleks saanud jaotada"))
        else:
            self.success(_("Ei jaotatud ühtki sooritajat"))
            
        return self._redirect('index', lang=self.params_lang())

    def _index_markus(self):
        return self.render_to_response('avalik/korraldamine/sooritajad.markus.mako')    

    def _create_markus(self):
        """Märkuse salvestamine
        """
        self.c.testikoht.markus = self.request.params.get('markus')
        model.Session.commit()
        self.success()
        return self._redirect('index', lang=self.params_lang())

    def _new_parool(self):
        self.c.items = []
        sooritused_id = self.request.params.getall('sooritus_id')
        for sooritus_id in sooritused_id:
            sooritus = model.Sooritus.get(sooritus_id)
            if self.c.testikoht:
                assert sooritus.testikoht_id == self.c.testikoht.id, _("Vale koht")
            self.c.items.append(sooritus)
        return self.render_to_response('/ekk/korraldamine/koht.sooritajad.paroolid.mako')            

    def _create_parool(self):
        self.c.items = []
        sooritused_id = self.request.params.getall('pwd_id')
        for sooritus_id in sooritused_id:
            sooritus = model.Sooritus.get(sooritus_id)
            if self.c.testiruum:
                assert sooritus.testiruum_id == self.c.testiruum.id, _("Vale ruum")
            sooritaja = sooritus.sooritaja
            kasutaja = sooritaja.kasutaja
            pwd = User.gen_pwd(6, True)
            sooritaja.set_password(pwd, userid=kasutaja.isikukood)
            self.c.items.append((kasutaja.isikukood, sooritaja.eesnimi, sooritaja.perenimi, pwd))
        model.Session.commit()
        return self.render_to_response('/ekk/korraldamine/koht.sooritajad.paroolid.print.mako')    

    def _new_klass(self):
        self.c.koht = self.c.testikoht.koht
        self.c.sooritused_id = self.request.params.getall('sooritus_id')
        for sooritus_id in self.c.sooritused_id:
            sooritus = model.Sooritus.get(sooritus_id)
            if self.c.testikoht:
                assert sooritus.testikoht_id == self.c.testikoht.id, _("Vale koht")
        return self.render_to_response('/ekk/korraldamine/koht.sooritajad.klass.mako')            

    def _create_klass(self):
        params = self.request.params
        eemalda = params.get('op') == 'eemalda'
        sooritused_id = params.getall('s_id')
        if eemalda:
            kool = klass = paralleel = oppekeel = None
        else:
            kool = self.c.testikoht.koht
            klass = params.get('klass')
            paralleel = params.get('paralleel')
            oppekeel = params.get('oppekeel')
        for sooritus_id in sooritused_id:
            sooritus = model.Sooritus.get(sooritus_id)
            if self.c.testiruum:
                assert sooritus.testiruum_id == self.c.testiruum.id, _("Vale ruum")
            sooritaja = sooritus.sooritaja
            sooritaja.kool_koht = kool
            sooritaja.set_kool_data(kool)
            sooritaja.klass = klass
            sooritaja.paralleel = paralleel
            sooritaja.oppekeel = oppekeel

        model.Session.commit()
        return self._redirect('index', testikoht_id=self.c.testikoht_id)
    
    def _delete_tpr(self, id):
        "Protokollirühma kustutamine"
        tpr = model.Testiprotokoll.get(id)
        if tpr and tpr.soorituste_arv == 0:
            assert tpr.testiruum.testikoht_id == self.c.testikoht_id, _("Vale koht")
            tpr.delete()
            model.Session.commit()
        return self._redirect('index', lang=self.params_lang())

    def __before__(self):
        c = self.c
        c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        if not c.toimumisaeg:
            return False
        c.testiosa = c.toimumisaeg.testiosa
        c.test = c.testiosa.test
        c.testikoht_id = int(self.request.matchdict.get('testikoht_id'))
        # kohatute sooritajate korral c.testikoht_id=0
        if c.testikoht_id:
            c.testikoht = model.Testikoht.get(c.testikoht_id)

    def _perm_params(self):
        if not self.c.toimumisaeg:
            return False
        if self.c.testikoht:
            return {'obj':self.c.testikoht}

