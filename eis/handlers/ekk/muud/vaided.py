from eis.lib.baseresource import *
from eis.lib.resultentry import ResultEntry
from eis.lib.pdf.vaidelist import VaidelistDoc
from eis.lib.pdf.vaideavaldus import VaideavaldusDoc
from eis.lib.pdf.vaideotsus import VaideotsusDoc
import eis.lib.ddocs as ddocs
_ = i18n._
log = logging.getLogger(__name__)

class VaidedController(BaseResourceController):
    """HTMi vaidekomisjoni liikme tegevused vaietega:
    vaiete sisestamine, menetlusse võtmine, otsuste koostamine,
    avalduste ja otsuste edastamine.
    """
    _permission = 'vaided'
    _MODEL = model.Vaie
    _INDEX_TEMPLATE = 'ekk/muud/vaided.otsing.mako'
    _EDIT_TEMPLATE = 'ekk/muud/vaie.mako' 
    _LIST_TEMPLATE = 'ekk/muud/vaided.otsing_list.mako'
    _CHOICE_TEMPLATE = 'ekk/muud/vaie.isikuvalik.mako'
    _NEW_TEMPLATE = 'ekk/muud/vaie.uus.mako'

    _SEARCH_FORM = forms.ekk.muud.VaidedOtsingForm 
    _ITEM_FORM = forms.ekk.muud.VaieUusForm
    _DEFAULT_SORT = '-vaie.id'

    _ignore_default_params = ['pdf', 'csv', 'hindajad_csv']
    _actions = 'index,create,new,download,downloadfile,show,update,delete,edit'

    def _query(self):
        self.c.prepare_item = self._prepare_item
        self.c.prepare_header = self._prepare_header
        q = (model.SessionR.query(model.Vaie, 
                                model.Sooritaja, 
                                model.Kasutaja,
                                model.Test,
                                model.Testimiskord,
                                model.Koht)
             .join(model.Vaie.sooritaja)
             .join(model.Sooritaja.testimiskord)
             .join(model.Sooritaja.test)
             .join(model.Sooritaja.kasutaja)
             .outerjoin(model.Sooritaja.kool_koht))

        # sortimiseks joinime esimese soorituse ja protokolli
        q = (q.join(model.Sooritaja.sooritused)
             .join(model.Sooritus.testiosa)
             .filter(model.Testiosa.seq==1)
             .outerjoin(model.Sooritus.testiprotokoll))
        if None not in self.lubatud_testiliigid:
            q = q.filter(model.Test.testiliik_kood.in_(self.lubatud_testiliigid))
        return q

    def _search_default(self, q):
        """Otsingu tingimuste seadmine siis, kui otsing toimub 
        kohe otsinguvormi avamisel ja kasutaja pole veel saanud 
        otsingutingimusi valida.
        """
        self.c.staatus = const.V_STAATUS_MENETLEMISEL
        return None

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if c.sessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==c.sessioon_id)
        if c.test_id:
            q = q.filter(model.Sooritaja.test_id==c.test_id)
        if c.isikukood:
            usp = validators.IsikukoodP(c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))
        if c.eesnimi:
            q = q.filter(model.Sooritaja.eesnimi.ilike(c.eesnimi))
        if c.perenimi:
            q = q.filter(model.Sooritaja.perenimi.ilike(c.perenimi))

        if c.staatus == const.V_STAATUS_MENETLEMISEL:
            if c.valjaotsitud and not c.valjaotsimata:
                q = q.filter(model.Vaie.valjaotsitud==True)
            elif c.valjaotsimata and not c.valjaotsitud:
                q = q.filter(model.Vaie.valjaotsitud==False)

            if c.allkirjastatud and not c.allkirjastamata:
                q = q.filter(model.Vaie.allkirjad>=2)
            elif c.allkirjastamata and not c.allkirjastatud:
                q = q.filter(model.Vaie.allkirjad<2)

            if 0 < len(list(filter(None, [c.hindamata, c.eelnouta, c.arakuulamisel]))) < 3:
                li = []
                if c.hindamata:
                    li.append(model.Vaie.staatus == const.V_STAATUS_MENETLEMISEL)
                if c.eelnouta:
                    li.append(sa.and_(model.Vaie.staatus == const.V_STAATUS_ETTEPANDUD,
                                      model.Vaie.arakuulamine_kuni==None))
                if c.arakuulamisel:
                    li.append(sa.and_(model.Vaie.staatus == const.V_STAATUS_ETTEPANDUD,
                                      model.Vaie.arakuulamine_kuni!=None))
                q = q.filter(sa.or_(*li))
            else:
                q = q.filter(model.Vaie.staatus.in_((const.V_STAATUS_MENETLEMISEL,
                                                     const.V_STAATUS_ETTEPANDUD)))
        elif c.staatus or c.staatus == 0:
            q = q.filter(model.Vaie.staatus==c.staatus)            

        if c.aine:
            q = q.filter(model.Test.aine_kood==c.aine)
        if c.keeletase:
            q = q.filter(model.Test.testitasemed.any(model.Testitase.keeletase_kood==c.keeletase))
        if c.alates:
            q = q.filter(model.Vaie.esitamisaeg>=c.alates)
        if c.kuni:
            q = q.filter(model.Vaie.esitamisaeg<c.kuni+timedelta(1))

        liigid = c.user.get_testiliigid(self._permission)
        if None not in liigid:
            q = q.filter(model.Test.testiliik_kood.in_(liigid))

        if c.pdf:
            return self._index_pdf(q)
        if c.csv:
            return self._index_csv(q)
        if c.hindajad_csv:
            if not c.test_id:
                self.error(_("Palun valida test"))
            else:
                return self._index_hindajad_csv(q)
        #model.log_query(q)
        return q

    def _index_pdf(self, q):
        q = self._order(q)
        header, items = self._prepare_items(q)
        doc = VaidelistDoc(header, items)
        data = doc.generate()
        if doc.error:
            self.error(doc.error)
            return self._redirect('index')
        filename = 'vaided.pdf'
        mimetype = const.CONTENT_TYPE_PDF
        return utils.download(data, filename, mimetype)

    def _index_csv(self, q):
        header, items = self._prepare_items(q, on_markus=True)
        data = self._csv_data(header, items)
        data = utils.encode_ansi(data)
        filename = 'vaided.csv'
        return utils.download(data, filename, const.CONTENT_TYPE_CSV)

    def _index_hindajad_csv(self, q):
        "Vaidlustatud sooritusi hinnanud hindajate andmed soorituste ja alatestide kaupa"
        test = model.Test.get(self.c.test_id)

        # päiserida
        header = [_("Eesnimi"),
                  _("Perekonnanimi"),
                  _("Isikukood"),
                  ]
        if test.keeletase_kood:
            header.append(_("Tase"))

        header.append(_("Testi ID"))

        osad_id = [] # list: [(testiosa.id, [(alatest_id, [hindamiskogum_id])])]
        for testiosa in test.testiosad:
            header.append(_("Töö kood"))
            on_alatestid = False
            alatestid_id = []
            for alatest in testiosa.alatestid:
                on_alatestid = True
                hindamiskogumid_id = set([ty.hindamiskogum_id for ty in alatest.testiylesanded])
                alatestid_id.append((alatest.id, hindamiskogumid_id))
                for liik in (_("I hindaja"), _("II hindaja"), _("III hindaja")):
                    header.append('%s %s' % (alatest.nimi, liik))
            if not on_alatestid:
                alatestid_id = [(None, None)]
                for liik in (_("I hindaja"), _("II hindaja"), _("III hindaja")):
                    header.append('%s %s' % (testiosa.nimi, liik))
            osad_id.append((testiosa.id, alatestid_id))
        
        # sooritajad ja hindajad

        def _get_hindajad(sooritus, hindamiskogumid_id=None):
            "Leitakse dict, milles hindamise liigile vastab list hindajate nimedest"
            hindajad = dict()
            for holek in sooritus.hindamisolekud:
                if hindamiskogumid_id and holek.hindamiskogum_id not in hindamiskogumid_id:
                    # kui on antud alatesti hindamiskogumid, siis 
                    # jätame välja need hindamiskogumid, mis ei sisalda yhtki ylesannet antud alatestist
                    continue

                for hindamine in holek.hindamised:
                    if hindamine.liik < const.HINDAJA4 and hindamine.sisestus == 1:
                        if not hindamine.tyhistatud and hindamine.staatus == const.H_STAATUS_HINNATUD:
                            k = hindamine.hindaja_kasutaja
                            if k:
                                if hindamine.liik not in hindajad:
                                    hindajad[hindamine.liik] = [k.nimi]
                                else:
                                    hindajad[hindamine.liik].append(k.nimi)
            return hindajad

        items = []
        for rcd in q.all():
            vaie, sooritaja, k, r_test, tkord, kool_koht = rcd
            item = [sooritaja.eesnimi,
                    sooritaja.perenimi,
                    k.isikukood or self.h.str_from_date(k.synnikpv),
                    ]
            if test.keeletase_kood:
                item.append(r_test.keeletase_nimi)
            item.append(r_test.id)

            row_cnt = 1
            t_item = []
            for testiosa_id, alatestid_id in osad_id:
                sooritus = sooritaja.get_sooritus(testiosa_id)
                t_item.append(sooritus.tahised)

                for (alatest_id, hindamiskogumid_id) in alatestid_id:
                    hindajad = _get_hindajad(sooritus, hindamiskogumid_id)

                    for liik in (const.HINDAJA1, const.HINDAJA2, const.HINDAJA3):
                        li_nimi = hindajad.get(liik)
                        if li_nimi and len(li_nimi) > row_cnt:
                            # kui mõnes alatestis on mitu samaliigilist hindajat, 
                            # siis teeme CSV-sse mitu rida
                            row_cnt = len(li_nimi)
                        t_item.append(li_nimi or '')
            
            for n in range(row_cnt):
                # enamasti peaks olema yks rida soorituse kohta,
                # aga kui mõnes alatestis on mitu samaliigilist hindajat, siis on mitu rida
                t1_item = []
                for r in t_item:
                    if not isinstance(r, list):
                        value = r
                    elif len(r) > n:
                        value = r[n]
                    else:
                        value = ''
                    t1_item.append(value)
                items.append(item + t1_item)


        data = ';'.join(header) + '\n'
        for item in items:
            row = []
            for s in item:
                if s is None:
                    s = ''
                #elif isinstance(s, list):
                #    s = ', '.join(s)
                else:
                    s = str(s).replace('\n', ' ').replace('\r', ' ')
                row.append(s)
            data += ';'.join(row) + '\n'

        data = utils.encode_ansi(data)
        filename = 'vaid_tulem_hindajad.csv'
        return utils.download(data, filename, const.CONTENT_TYPE_CSV)

    def _prepare_header(self, on_markus=False):
        if self.c.pdf:
            header = [('test.nimi', _("Test")),
                      ('testiprotokoll.tahised', _("Protokollirühm")),
                      ('sooritus.tahised', _("Testitöö")),
                      ('kasutaja.isikukood', _("Isikukood")),
                      ('sooritaja.perenimi,sooritaja.eesnimi', _("Nimi")),
                      ('koht.nimi', _("Kool")),
                      ('vaie.esitamisaeg', _("Esitamise aeg")),
                      ('vaie.staatus', _("Olek")),
                      ('vaie.otsus_kp', _("Otsuse kuupäev")),
                      ('vaie.pallid_enne', _("Esialgne tulemus")),
                      ('vaie.pallid_parast', _("Uus tulemus")),
                      ('vaie.muutus', _("Muutus")),
                      ]
        else:
            header = [('test.nimi', _("Test")),
                      ('test.id', _("Testi tähis")),
                      ('testimiskord.tahis', _("Testimiskord")),
                      ('testiprotokoll.tahised', _("Protokollirühm")),
                      ('sooritus.tahised', _("Testitöö")),
                      ('kasutaja.isikukood', _("Isikukood")),
                      ('sooritaja.perenimi,sooritaja.eesnimi', _("Nimi")),
                      ('koht.nimi', _("Kool")),
                      ('vaie.esitamisaeg', _("Esitamise aeg")),
                      ('vaie.staatus', _("Olek")),
                      ('vaie.otsus_kp', _("Otsuse kuupäev")),
                      ('vaie.pallid_enne', _("Esialgne tulemus")),
                      ('vaie.pallid_parast', _("Uus tulemus")),
                      ('vaie.muutus', _("Muutus")),
                      ]
        if on_markus:
            header.append(_("Vaidlustamise põhjendus"))
        header.append(_("Eksperdid"))
        header.append(('vaie.ettepanek_pohjendus', _("Ekspertkomisjoni ettepanek")))
        return header
    
    def _prepare_items(self, q, on_markus=False):
        header = self._prepare_header(on_markus=on_markus)
        items = [self._prepare_item(rcd, on_markus) for rcd in q.all()]
        return header, items

    def _prepare_item(self, rcd, on_markus=False):
        "Loetelu kirje vormistamine CSV ja PDF jaoks"
        
        vaie, sooritaja, k, test, tkord, kool_koht = rcd

        li_tpr = []
        li_tos = []
        for tos in sooritaja.sooritused:
            li_tpr.append(tos.testiprotokoll and tos.testiprotokoll.tahised or '')
            li_tos.append(tos.tahised or '')

        staatus_nimi = vaie.staatus_nimi
        if vaie.staatus == const.V_STAATUS_ETTEPANDUD:
            if vaie.allkirjad >= 2:
                staatus_nimi += ' (allkirjastatud)'
            else:
                staatus_nimi += ' (hinnatud)'

        h = self.h
        item = [test.nimi,]
        if not self.c.pdf:
            item.append(str(test.id))
            item.append(tkord and tkord.tahis or '')
        item.extend([
                li_tpr,
                li_tos,
                k.isikukood,
                sooritaja.nimi,
                kool_koht and kool_koht.nimi or '',
                h.str_from_date(vaie.esitamisaeg) or '',
                staatus_nimi,
                h.str_from_date(vaie.otsus_kp) or '',
                h.fstr(vaie.pallid_enne) or '',
                h.fstr(vaie.pallid_parast) or '',
                h.fstr(vaie.muutus) or '',
                ])
        if on_markus:
            item.append(vaie.markus or '')

        # leiame läbi vaadanud ekspertide nimed
        q_x = (model.SessionR.query(model.Kasutaja.nimi).distinct()
               .join(model.Kasutaja.labiviijad)
               .filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAMISEKSPERT)
               .join(model.Labiviija.toimumisaeg)
               .filter(model.Toimumisaeg.testimiskord_id==sooritaja.testimiskord_id)
               .join(model.Labiviija.labivaatused)
               .join(model.Labivaatus.hindamine)
               .join(model.Hindamine.hindamisolek)
               .join(model.Hindamisolek.sooritus)
               .filter(model.Sooritus.sooritaja_id==sooritaja.id)
               .order_by(model.Kasutaja.nimi)
               )
        eksperdid = [nimi for nimi, in q_x.all()]
        item.append(eksperdid)

        if vaie.staatus >= const.V_STAATUS_ETTEPANDUD:
            ettepanek = '%s %s' % (vaie.gen_ettepanek_txt() or '', vaie.ettepanek_pohjendus or '')
            if not self.c.csv:
                ettepanek = ettepanek.replace('\n', '<br/>')
        else:
            ettepanek = ''
        item.append(ettepanek)
        return item

    def new(self, format='html'):
        """Uue vaide alustamise vormi kuvamine.
        """
        kasutaja_id = self.request.params.get('kasutaja_id')
        if kasutaja_id:
            # isik on vist määratud
            self._get_sooritajad(kasutaja_id)
        if self.c.kasutaja:
            # isik on määratud
            return self.render_to_response(self._NEW_TEMPLATE)
        else:
            # isiku otsimine isikukoodi või synnikpv/nime järgi
            return self._otsi_isik()
        
    def _otsi_isik(self):
        """Uue vaide lisamisel vaidlustaja otsimine
        """
        c = self.c
        self.form = Form(self.request, schema=forms.ekk.muud.VaieIsikuvalikForm)
        if not self.form.validate():
            html = self.form.render(self._CHOICE_TEMPLATE, extra_info=self.response_dict)
            return Response(html)

        err = None
        c.isikukood = self.form.data.get('isikukood')
        c.synnikpv = self.form.data.get('synnikpv')
        c.eesnimi = self.form.data.get('eesnimi')
        c.perenimi = self.form.data.get('perenimi')
        if c.isikukood:
            c.kasutaja = model.Kasutaja.get_by_ik(c.isikukood)
            if not c.kasutaja:
                err = _("Sellise isikukoodiga eksaminandi ei leitud")
        else:
            if not c.synnikpv or not c.eesnimi or not c.perenimi:
                if self.request.params.get('otsi'):
                    # kui kasutaja juba otsib
                    err = _("Palun sisestada kas isikukood või sünniaeg ja nimi")
            else:
                q = model.Kasutaja.query
                if c.synnikpv:
                    q = q.filter_by(synnikpv=c.synnikpv)
                if c.eesnimi:
                    q = q.filter(model.Kasutaja.eesnimi.ilike(c.eesnimi))
                if c.perenimi:
                    q = q.filter(model.Kasutaja.perenimi.ilike(c.perenimi))
                cnt = q.count()
                if cnt == 1:
                    c.kasutaja = q.first()
                elif cnt > 100:
                    err = _("Palun kitsendada otsingutingimusi, selliste andmetega isikuid on väga palju")
                elif not cnt:
                    err = _("Selliste andmetega isikuid ei leitud")
                else:
                    c.items = q.order_by(model.Kasutaja.eesnimi, model.Kasutaja.perenimi).all()
        if err:
            # uuesti otsingutingimusi sisestama
            self.error(err)
            return self.render_to_response(self._CHOICE_TEMPLATE)
        elif c.kasutaja:
            # leiti täpselt 1 isik, testi valima
            self._get_sooritajad(c.kasutaja.id)
            return self.render_to_response(self._NEW_TEMPLATE)
        else:
            # leiti mitu isikut, isikut valima või uuesti otsingutingimusi sisestama
            return self.render_to_response(self._CHOICE_TEMPLATE)

    def _get_sooritajad(self, kasutaja_id=None):
        """Otsitakse antud isikukoodiga sooritaja andmed
        """
        c = self.c
        if not kasutaja_id:
            kasutaja_id = self.request.params.get('kasutaja_id')
        c.kasutaja = model.Kasutaja.get(kasutaja_id)

        if c.kasutaja:
            dt = date.today()
            # EH-253 - vaidlustada saab neid sooritusi,
            # mis on tehtud ja hinnatud või kust sooritaja on eemaldatud
            # EH-289 - vaidlustada ei saa rahvusvahelise eksami sooritusi,
            # kuna nendega tegeleb vastavat eksamit koordineeriv organisatsioon,
            # ning vaide tulemused viiakse eksperthindamisena sisse ilma vaideta
            q = (model.SessionR.query(model.Sooritaja.id,
                                     model.Test.nimi,
                                     model.Test.testiliik_kood)
                 .filter_by(kasutaja_id=kasutaja_id)
                 .join(model.Sooritaja.testimiskord)
                 .filter(model.Testimiskord.vaide_tahtaeg >= dt)
                 .filter(sa.or_(model.Testimiskord.vaide_algus==None,
                                model.Testimiskord.vaide_algus<=dt))
                 .filter(model.Testimiskord.tulemus_kinnitatud==True)
                 .filter(sa.or_(sa.and_(model.Sooritaja.hindamine_staatus == const.H_STAATUS_HINNATUD,
                                        model.Sooritaja.pallid != None),
                                model.Sooritaja.staatus==const.S_STAATUS_EEMALDATUD))
                 .join(model.Sooritaja.test)
                 .filter(model.Test.testiliik_kood!=const.TESTILIIK_RV)
                 .order_by(model.Test.nimi)
                 )

            opt_sooritaja = [o for o in q.all()]
            if not len(opt_sooritaja):
                self.error(_("Isikul ei ole midagi vaidlustada"))
            else:
                if None not in self.lubatud_testiliigid:
                    li = [r for r in opt_sooritaja if r[2] in self.lubatud_testiliigid]
                    if not li:
                        li_liigid = ['"%s"' % model.Klrida.get_str('TESTILIIK', r) for r in self.lubatud_testiliigid]
                        testiliigid = ', '.join(li_liigid)
                        self.error(_("Isikul ei ole testiliigiga {s} teste, mida saaks vaidlustada").format(s=testiliigid))
                    opt_sooritaja = li
            c.opt_sooritaja = [(r[0], r[1]) for r in opt_sooritaja]
            c.esitamisaeg = date.today()

    def _create_index(self):
        "Väljaotsitud vaiete märkimine"
        valitud_id = self.request.params.getall('vaie_id')
        endised_id = self.request.params.getall('endine_id')

        uued_id = set(valitud_id) - set(endised_id)
        if len(uued_id):
            for vaie_id in uued_id:
                model.Vaie.get(vaie_id).valjaotsitud = True

        eemaldatud_id = set(endised_id) - set(valitud_id)
        if len(eemaldatud_id):
            for vaie_id in eemaldatud_id:
                model.Vaie.get(vaie_id).valjaotsitud = False

        model.Session.commit()
        return HTTPFound(location=self.request.params.get('list_url'))

    def create(self):
        """Uue vaide loomine
        On sisestatud sooritaja isikukood ja valitud test.
        """
        if self.request.params.get('sub') == 'index':
            return self._create_index()

        self.form = Form(self.request, schema=self._ITEM_FORM)
        if not self.form.validate():
            self._get_sooritajad()
            return Response(self.form.render(self._NEW_TEMPLATE,
                                             extra_info=self.response_dict))

        item = self._create()
        if isinstance(item, Response):
            return item
        if self.has_errors():
            return self._redirect('new')
        # uus vaie on loodud
        model.Session.commit()
        return self._redirect(action='edit', id=item.id)

    def _create(self, **kw):
        kasutaja_id = self.form.data.get('kasutaja_id')
        kasutaja = model.Kasutaja.get(kasutaja_id)
        sooritaja = model.Sooritaja.get(self.form.data.get('sooritaja_id'))
        err = None
        assert sooritaja.kasutaja_id == kasutaja.id, 'sooritaja ja kasutaja ei klapi'
        if sooritaja.pallid == None or sooritaja.hindamine_staatus != const.H_STAATUS_HINNATUD:
            if sooritaja.staatus != const.S_STAATUS_EEMALDATUD:
                err = _("Sooritust ei saa vaidlustada")
        if not err:
            if None not in self.lubatud_testiliigid:
                test = sooritaja.test
                if test.testiliik_kood not in self.lubatud_testiliigid:
                    err = _("Puudub õigus antud testiliigiga testi vaiet lisada")
        if not err:
            item = sooritaja.give_vaie()
            item.esitamisaeg = self.form.data.get('esitamisaeg')
            item.otsus_epostiga = self.form.data.get('otsus_epostiga')
            item.markus = self.form.data.get('markus')
            kasutaja.from_form(self.form.data, 'k_')
            model.Aadress.adr_from_form(kasutaja, self.form.data, 'a_')
            if item.otsus_epostiga and not kasutaja.epost:
                err = _("E-postiga otsuse saatmiseks palun sisestada e-posti aadress")

            vfail = self.form.data.get('vfail')
            if vfail != b'':
                filedata = vfail.value
                filename = vfail.filename
                if filedata:
                    vf = model.Vaidefail(vaie=item,
                                         filename=filename,
                                         filedata=filedata)
                    item.vaidefailid.append(vf)
        if err:
            self._get_sooritajad(kasutaja_id)
            html = self.form.render(self._NEW_TEMPLATE, extra_info=self.response_dict)
            return Response(html)            

        item.flush()
        item.vaide_nr = item.id
        self._gen_avaldus_dok(item)
            
        return item

    def _edit(self, item):
        self.c.today = date.today()
        # kas otsus on allkirjastamiseks valmis
        # ja kas minu allkirjastamisjärjekord on käes
        self.c.can_sign = item.staatus == const.V_STAATUS_OTSUSTAMISEL \
            and item.otsus_pdf is not None \
            and self._kas_saan_allkirjastada(item)
        # kui on allkirjastgamisel, siis kas kõik allkirjad on olemas
        self.c.all_signed = item.staatus == const.V_STAATUS_OTSUSTAMISEL \
            and self._kas_allkirjastatud(item)
        
    def _update_edastaavaldus(self, item):
        "DVKga edastamist ei toimu, vaie märgitakse esitatuks"
        if item.staatus != const.V_STAATUS_ESITAMATA:
            self.error(_("Vaide olek on juba: {s}").format(s=item.staatus_nimi))
            return 

        if item.avaldus_dok is None:
            self.error(_("Avaldust pole koostatud"))
            return
        item.staatus = const.V_STAATUS_ESITATUD
        model.Session.commit()
        self.success(_("Avaldus on esitatud"))

    def _gen_avaldus_pdf(self, vaie):
        doc = VaideavaldusDoc(self, vaie)
        data = doc.generate()
        if doc.error:
            self.error(doc.error)
            return        
        return data

    def _gen_avaldus_dok(self, item):
        # loome avalduse PDFi
        item.avaldus_dok = self._gen_avaldus_pdf(item)
        item.avaldus_ext = const.PDF
        model.Session.commit()
        
    def _download(self, id, format):
        """Näita faili"""
        item = self._MODEL.get(id)
        if not item:
            raise NotFound(_("Ei leitud"))

        filedata = None

        liik = self.request.params.get('liik')
        if liik == 'avaldus':
            filedata = item.avaldus_dok
            filename = 'vaideavaldus.%s' % (item.avaldus_ext)
        elif liik == 'votatagasi':
            filedata = item.tagasivotmine_dok
            filename = 'tagasivotmine.%s' % (item.tagasivotmine_ext)
        elif liik == 'ettepanek':
            filedata = item.ettepanek_dok
            filename = 'vaideettepanek.%s' % (item.ettepanek_ext)
        elif liik == 'eelnou':
            filedata = item.eelnou_pdf
            filename = 'eelnou.pdf'
        elif liik == 'otsus':
            if format == 'pdf':
                filedata = item.otsus_pdf
                filename = 'otsus.pdf'
                mimetype = const.CONTENT_TYPE_PDF
            else:
                filedata = item.otsus_dok
                filename = 'vaideotsus.%s' % (item.otsus_ext)

        if not filedata:
            raise NotFound(_("Dokumenti ei leitud"))

        return utils.download(filedata, filename)

    def _downloadfile(self, id, file_id, format):
        "Vaidefaili allalaadimine"
        vf = model.Vaidefail.get(file_id)
        if vf and vf.vaie_id == int(id):
            filename = vf.filename
            (mimetype, encoding) = mimetypes.guess_type(filename)
            return utils.download(vf.filedata, filename, mimetype)            
        else:
            raise NotFound(_("Dokumenti ei leitud"))
        
    def _delete(self, item):
        sooritaja = item.sooritaja
        if item.staatus == const.V_STAATUS_OTSUSTATUD:
            self.error(_("Vaie on juba otsustatud"))
            return
        elif item.staatus == const.V_STAATUS_ETTEPANDUD:
            self.error(_("Vaie on juba hinnatud"))                        
            return        
        elif item.staatus == const.V_STAATUS_OTSUSTAMISEL:
            self.error(_("Vaie on juba otsustamisel"))                        
            return        
        elif item.staatus == const.V_STAATUS_MENETLEMISEL or \
                sooritaja.hindamine_staatus != const.H_STAATUS_HINNATUD:
            # taastame vaidlustamiseelse olukorra
            sooritaja.hindamine_staatus = const.H_STAATUS_HINNATUD
            valimis = sooritaja.valimis
            for tos in sooritaja.sooritused:
                tos.hindamine_staatus = const.H_STAATUS_HINNATUD
                for holek in tos.hindamisolekud:
                    # leiame algse hindamistaseme
                    holek.hindamistase = holek.hindamiskogum.get_hindamistase(valimis, tos.toimumisaeg)
                    # aga kui on olemas III või eksperthindamine, siis arvestame seda
                    for h in holek.hindamised:
                        if not h.tyhistatud and h.liik in (const.HINDAJA3, const.HINDAJA4):
                            if h.liik > holek.hindamistase:
                                holek.hindamistase = h.liik
                        elif not h.tyhistatud and h.liik == const.HINDAJA5:
                            h.tyhistatud = True
                    holek.staatus = const.H_STAATUS_HINNATUD

        item.delete()
        model.Session.commit()
        self.success(_("Vaie on tühistatud!"))

    def update(self):
        """Vaide lehe tegevused: menetlusse võtmine jms
        """
        id = self.request.matchdict.get('id')
        op = self.request.params.get('op')
        sub = self._get_sub()
        if sub:
            # prepare_signature, finalize_signature, kontakt
            return eval('self._update_%s' % sub)(id)

        self.form = Form(self.request, schema=forms.ekk.muud.VaieForm)
        err = not self.form.validate()
        rc = None
        item = model.Vaie.get(id)

        if not err and item:
            try:
                if self.request.params.get('edastaavaldus'):
                    # edasta DVK-ga HMi ja saada kiri
                    rc = self._update_edastaavaldus(item)                
                elif self.request.params.get('menetlusse'):
                    # võtame vaide menetlusse ja saadame teated sooritajale ja ekspertidele
                    rc = self._update_menetlusse(item)
                elif self.request.params.get('votatagasi'):
                    # avalduse tagasi võtmine
                    rc = self._update_votatagasi(item)
                elif self.request.params.get('menetlussesooritajale'):
                    # saadame sooritajale veelkord teate vaide menetlusse võtmise kohta
                    self._saada_teade_sooritajale(item)
                elif self.request.params.get('arvuta'):
                    # arvutame menetluses oleva vaide menetlusjärgsed tulemused
                    rc = self._update_arvuta(item)
                elif self.request.params.get('eelnou'):
                    # koostame otsuse eelnõu PDFi
                    rc = self._update_eelnou(item)                
                elif self.request.params.get('edastaeelnou'):
                    # saadame eelnõu sooritajale 
                    r = self._update_edastaeelnou(item)
                elif self.request.params.get('otsustamisel') or op == 'otsustamisel':
                    # märgime ärakuulamine lõppenuks, vaie otsustamisele
                    rc = self._update_otsustamisel(item)
                elif self.request.params.get('otsus') or op == 'otsus':
                    # koostame otsuse PDFi
                    rc = self._update_otsus(item)                    
                elif self.request.params.get('upload'):
                    # laadime otsuse DDOCi üles
                    rc = self._update_upload(item)
                #elif self.request.params.get('edastaotsus'):
                #    # edasta otsus sooritajale ja teade korraldajatele
                #    rc = self._update_edastaotsus(item)
                elif self.request.params.get('otsussooritajale'):
                    # saadame veelkord otsuse sooritajale 
                    r = self._saada_otsus_sooritajale(item)
                    if r:
                        self._add_vaidelogi(item,
                                            model.Vaidelogi.TEGEVUS_EDASTA,
                                            tapsustus=r)
                elif self.request.params.get('lopeta'):
                    # lõpeta 
                    rc = self._update_lopeta(item)
                elif op == 'uuesti':
                    # võtame uuesti menetlusse
                    rc = self._update_uuesti(item)
                    
                if isinstance(rc, (HTTPFound, Response)):
                    return rc
            except ValidationError as e:
                self.form.errors = e.errors
                err = True

        if self.form.errors or err:
            model.Session.rollback()
            return self._error_update()
        model.Session.commit()
        return self._after_update(id)

    def _update_kontakt(self, id):
        """Kontaktandmete salvestamine
        """
        item = model.Vaie.get(id)
        self.form = Form(self.request, schema=forms.ekk.muud.VaieKontaktForm)
        if not self.form.validate():
            return self._error_update()
        item.otsus_epostiga = self.form.data.get('otsus_epostiga')
        kasutaja = item.sooritaja.kasutaja
        kasutaja.from_form(self.form.data, 'k_')
        model.Aadress.adr_from_form(kasutaja, self.form.data, 'a_')
        if item.otsus_epostiga and not kasutaja.epost:
            self.error(_("E-postiga otsuse saatmiseks palun sisestada e-posti aadress"))
            return self._error_update()

        self._save_vaidefail(item)
        model.Session.commit()
        return self._after_update(id)

    def _save_vaidefail(self, item):
        vfdel_id = self.form.data.get('vfdel_id')
        if vfdel_id:
            vf = model.Vaidefail.get(vfdel_id)
            if vf and vf.vaie_id == item.id:
                item.vaidefailid.remove(vf)
                vf.delete()
                
        vfail = self.form.data.get('vfail')
        if vfail != b'':
            filedata = vfail.value
            filename = vfail.filename
            if filedata:
                vf = None
                for vf in item.vaidefailid:
                    vf.filename = filename
                    vf.filedata = filedata
                    break
                if not vf:
                    vf = model.Vaidefail(vaie=item,
                                         filename=filename,
                                         filedata=filedata)
                    item.vaidefailid.append(vf)

    def _update_menetlusse(self, item):
        if item.staatus != const.V_STAATUS_ESITATUD:
            self.error(_("Vaide olek on juba: {s}").format(s=item.staatus_nimi))
            return 
        sooritaja = item.sooritaja

        # Süsteem omistab vaide oleku väärtuseks "menetluses".
        item.staatus = const.V_STAATUS_MENETLEMISEL
        if not item.vaide_nr:
            item.vaide_nr = item.id
        
        # muudame kõigi soorituste kõik hindamisolekud
        sooritaja.hindamine_staatus = const.H_STAATUS_POOLELI
        for tos in sooritaja.sooritused:
            tos.hindamine_staatus = const.H_STAATUS_POOLELI
            #tos.pallid = None
            for holek in tos.hindamisolekud:
                if not holek.hindamiskogum.arvutihinnatav:
                    holek.hindamistase = const.HINDAJA5
                holek.staatus = const.H_STAATUS_HINDAMATA
        
        self._add_vaidelogi(item, model.Vaidelogi.TEGEVUS_MENETLUSSE)
        model.Session.commit()

        # saadetakse teade sooritajale menetlusse võtmise kohta
        self._saada_teade_sooritajale(item)
        
        # otsime vastava aine hindamisjuhid ja -eksperdid ja saadame neile teate uue vaide kohta
        self._saada_teade_ekspertidele(item)

    def _arvuta(self, item):
        sooritaja = item.sooritaja
        if item.staatus > const.V_STAATUS_OTSUSTAMISEL:
            return _("Vaide olek on juba: {s}").format(s=item.staatus_nimi)
        elif item.staatus < const.V_STAATUS_ETTEPANDUD:
            return _("Vaide ettepanekut pole veel edastatud")
        elif sooritaja.vaie.ettepanek_dok is None:
            return _("Vaide ettepanekut ei ole veel koostatud")

        test = sooritaja.test
        resultentry = ResultEntry(self, const.SISESTUSVIIS_PALLID, test, None)
        for n, tos in enumerate(sooritaja.sooritused):
            resultentry.testiosa = tos.testiosa
            if tos.ylesanneteta_tulemus:
                tos.pallid = tos.pallid_peale_vaiet
            for holek in tos.hindamisolekud:
                hindamine = holek.get_hindamine(const.HINDAJA5)
                #if not hindamine:
                #    self.error(u_("Vaide korral eksperthindamist pole läbi viidud"))
                #    return
                if hindamine:
                    hindamine.staatus = const.H_STAATUS_HINNATUD
                    model.Session.flush()
                    resultentry.update_hindamisolek(sooritaja, tos, holek, force=True, is_update_sooritus=False)
            resultentry.update_sooritus(sooritaja, tos, is_update_sooritaja=False)
        resultentry.update_sooritaja(sooritaja)
        if sooritaja.hindamine_staatus == const.H_STAATUS_HINNATUD:
            if item.pallid_parast != sooritaja.pallid:
                return _("Arvutatud tulemus ({s1}) ei vasta ettepanekule ({s2}). Palun hindamisjuhil punktid uuesti salvestada ja vajadusel uus ettepanek koostada.").format(s1=self.h.fstr(sooritaja.pallid), s2=self.h.fstr(item.pallid_parast))
        
    def _update_arvuta(self, item):
        item.h_arvestada = True
        model.Session.flush()
        err = self._arvuta(item)
        h_staatus = item.sooritaja.hindamine_staatus
        
        # ei tohi arvutatud tulemusi avaldada enne otsust
        model.Session.rollback()

        if err:
            self.error(err)
        elif h_staatus != const.H_STAATUS_HINNATUD:
            self.error(_("Tulemusi ei saa veel arvutada"))
        else:
            self._add_vaidelogi(item, model.Vaidelogi.TEGEVUS_ARVUTUSED)
            model.Session.commit()
            self.success(_("Tulemused on arvutatud"))

    def _update_eelnou(self, item):
        item.h_arvestada = True
        item.eelnou_pohjendus = self.form.data.get('eelnou_pohjendus')
        item.arakuulamine_kuni = self.form.data.get('arakuulamine_kuni')
        errors = {}
        if not item.arakuulamine_kuni:
            errors['arakuulamine_kuni'] = _("Palun sisestada väärtus")
        elif item.arakuulamine_kuni < date.today():
            errors['arakuulamine_kuni'] = _("Ärakuulamise tähtaeg on minevikus")
        if errors:
            raise ValidationError(self, errors)
        model.Session.flush()
        
        err = self._arvuta(item)
        if err:
            self.error(err)
            return
        if item.pallid_parast is None:
            self.error(_("Tulemust pole arvutatud"))
            return
        if not item.ettepanek_dok:
            self.error(_("Ettepaneku dokument puudub"))
            return
        
        doc = VaideotsusDoc(self, item, None)
        data = doc.generate()
        if doc.error:
            self.error(doc.error)
            return

        item.eelnou_pdf = data

        self._add_vaidelogi(item, model.Vaidelogi.TEGEVUS_EELNOU)
        self._remove_otsus(item)
        model.Session.commit()
        self.success(_("Eelnõu on koostatud"))

    def _remove_otsus(self, item):
        "Otsuse kustutamine (nt kui võetakse uuesti menetlusse)"
        item.otsus_dok = item.otsus_pdok = item.otsus_ext = None
        item.allkirjad = 0
        for va in list(item.vaideallkirjad):
            va.delete()

    def _update_edastaeelnou(self, item):
        if item.eelnou_pdf is None:
            self.error(_("Eelnõu pole koostatud"))
            return

        if not item.arakuulamine_kuni:
            self.error(_("Ärakuulamise tähtaeg puudub"))
            return
        elif item.arakuulamine_kuni < date.today():
            self.error(_("Ärakuulamise tähtaeg on minevikus"))
            return
        
        kuhu = []
        
        r = self._saada_eelnou_sooritajale(item)
        if r:
            kuhu.append(r)
            self._add_vaidelogi(item,
                                model.Vaidelogi.TEGEVUS_EELNOU_EDASTA,
                                tapsustus=', '.join(kuhu))
            model.Session.commit()
        
    def _update_otsustamisel(self, item):
        if item.staatus != const.V_STAATUS_ETTEPANDUD:
            self.error(_("Vaide staatus on: {s}").format(s=item.staatus_nimi))
            return
        item.staatus = const.V_STAATUS_OTSUSTAMISEL
        self._add_vaidelogi(item, model.Vaidelogi.TEGEVUS_OTSUSTAMISEL)
        model.Session.commit()
        self.success('Ärakuulamine on lõppenud')

    def _update_otsus(self, item):
        err = self._arvuta(item)
        if err:
            self.error(err)
            return
        if item.pallid_parast is None:
            self.error(_("Tulemust pole arvutatud"))
            return
        if not item.ettepanek_dok:
            self.error(_("Ettepaneku dokument puudub"))
            return
        allkirjastajad, error = self._set_allkirjastajad(item)
        if error:
            self.error(error)
            return
        item.otsus_kp = self.form.data.get('otsus_kp')
        item.otsus_pohjendus = self.form.data.get('otsus_pohjendus')

        doc = VaideotsusDoc(self, item, allkirjastajad)
        data = doc.generate()
        if doc.error:
            self.error(doc.error)
            return

        item.otsus_pdf = data
        item.otsus_dok = item.otsus_pdok = item.otsus_ext = None
        item.allkirjad = 0
        self._add_vaidelogi(item, model.Vaidelogi.TEGEVUS_OTSUS)
        model.Session.commit()
        # saadame kirja esimesele allkirjastajale, kui see pole mina ise
        self._kirjuta_jargmisele(item)
        self.success(_("Otsus on koostatud"))

    def _update_upload(self, item):
        """Otsuse faili üles laadimine (kui käsitsi allkirjastati)
        """
        if item.staatus != const.V_STAATUS_OTSUSTAMISEL:
            self.error(_("Vaide olek on: {s}").format(s=item.staatus_nimi))
            return 

        f = self.request.params.get('otsus_dok')
        if f != b'':
            item.otsus_dok = f.value
            item.otsus_pdok = None
            if not item.otsus_ext:
                item.otsus_ext = f.filename.rsplit('.')[-1].lower()
            # leiame faili allkirjastajad
            signers = ddocs.list_signed(self, item.otsus_dok, item.otsus_ext)
            if signers is None:
                # ddoc faili ei saanud lugeda
                return
            # leiame seni teadaolevad allkirjastajad
            q = model.SessionR.query(model.Kasutaja.isikukood).\
                join(model.Vaidelogi.kasutaja).\
                filter(model.Vaidelogi.tegevus==model.Vaidelogi.TEGEVUS_ALLKIRI).\
                filter(model.Vaidelogi.vaie_id==item.id)
            old_signers = [r[0] for r in q.all()]
            # kui on mõni uus allkiri, siis lisame selle kohta märke allkirjastamise logisse
            for cert_cn in signers:
                isikukood = cert_cn.split(',')[-1]
                if isikukood not in old_signers:
                    k = model.Kasutaja.get_by_ik(isikukood)
                    if not k:
                        self.error(_("Allkirjastaja {s} ei ole EISi kasutaja").format(s=cert_cn))
                    else:
                        # märgime allkirjastatuks
                        found = False
                        for va in item.vaideallkirjad:
                            if va.kasutaja_id == k.id:
                                if not va.allkirjastatud:
                                    va.allkirjastatud = datetime.now()
                                found = True
                        if not found:
                            self.error(_("Otsuse on allkirjastanud {s}, kes ei kuulu selle dokumendi allkirjastamise järjekorda").format(s=k.nimi))
                        self._add_vaidelogi(item, model.Vaidelogi.TEGEVUS_ALLKIRI, k.id)

            item.allkirjad = len(signers)
            model.Session.commit()
            self.success(_("Fail on laaditud"))

            self._kirjuta_jargmisele(item)
        else:
            self.error(_("Palun laadi fail üles"))

    def _update_votatagasi(self, item):
        """Vaide märkimine otsustatuks koos mujalt salvestatud otsusega, esialgne tulemus taastatakse
        """
        old_staatus = item.staatus
        if item.staatus in (const.V_STAATUS_ESITAMATA, const.V_STAATUS_OTSUSTATUD):
            self.error(_("Ei saa tagasi võtta, sest vaide olek on: {s}").format(s=item.staatus_nimi))
            return 

        f = self.request.params.get('tagasivotmine_dok')
        if f != b'':
            item.tagasivotmine_dok = f.value
            item.tagasivotmine_ext = f.filename.rsplit('.')[-1].lower()
        else:
            self.error(_("Palun laadi fail üles"))
            return
        
        sooritaja = item.sooritaja
        if item.staatus >= const.V_STAATUS_MENETLEMISEL and \
                 sooritaja.hindamine_staatus != const.H_STAATUS_HINNATUD:
            # taastame vaidlustamiseelse olukorra
            sooritaja = item.sooritaja
            valimis = sooritaja.valimis
            sooritaja.hindamine_staatus = const.H_STAATUS_HINNATUD
            for tos in sooritaja.sooritused:
                tos.hindamine_staatus = const.H_STAATUS_HINNATUD
                for holek in tos.hindamisolekud:
                    # leiame algse hindamistaseme
                    holek.hindamistase = holek.hindamiskogum.get_hindamistase(valimis, tos.toimumisaeg)
                    # aga kui on olemas III või eksperthindamine, siis arvestame seda
                    for h in holek.hindamised:
                        if not h.tyhistatud and h.liik in (const.HINDAJA3, const.HINDAJA4):
                            if h.liik > holek.hindamistase:
                                holek.hindamistase = h.liik
                        elif not h.tyhistatud and h.liik == const.HINDAJA5:
                            h.tyhistatud = True
                    holek.staatus = const.H_STAATUS_HINNATUD

        item.staatus = const.V_STAATUS_TAGASIVOETUD
        item.pallid_parast = item.pallid_enne
        item.muutus = 0
        item.tunnistada = None
        if old_staatus == const.V_STAATUS_TAGASIVOETUD:
            tapsustus = 'avalduse asendamine'
        else:
            tapsustus = None
        self._add_vaidelogi(item,
                            model.Vaidelogi.TEGEVUS_TAGASIVOTMINE,
                            tapsustus=tapsustus)
        model.Session.commit()

        if old_staatus != const.V_STAATUS_TAGASIVOETUD:
            # saadetakse teade sooritajale menetluse tagasi võtmise kohta
            self._saada_tagasivotuteade_sooritajale(item)
            self.success(_("Vaie on tagasi võetud!"))
        else:
            self.success(_("Tagasivõtmise avaldus asendatud"))

    def _update_prepare_signature(self, id):
        """Allkirjastamise alustamine: brauserilt on saadud sert,
        selle kohta arvutatakse allkirjastatav räsi.
        """
        error = None
        vaie = model.Vaie.get(id)
        if vaie.staatus != const.V_STAATUS_OTSUSTAMISEL:
            error =  _("Vaide olek on juba: {s}").format(s=vaie.staatus_nimi)

        elif vaie.otsus_pdf is None:
            error = _("Otsust pole koostatud")

        elif vaie.otsus_pdok is not None and vaie.modified > datetime.now() - timedelta(minutes=2):
            error =  _("Allkirjastamine on juba pooleli")

        elif not self._kas_saan_allkirjastada(vaie):
            error = _("Praegu pole sinu kord allkirjastada")
            
        filedata = vaie.otsus_dok
        filename = vaie.otsus_ext
        if not filedata:
            filedata = vaie.otsus_pdf
            filename = 'otsus.pdf'

        filedata, res = ddocs.DdocS.prepare_signature(self, filedata, filename, error)
        if filedata:
            vaie.otsus_pdok = filedata
            model.Session.commit()
        return res
    
    def _update_finalize_signature(self, id):
        """Allkirjastamise lõpetamine: brauserilt on saadud allkiri,
        see lisatakse pooleli oleva DDOC-faili sisse.
        """
        vaie = model.Vaie.get(id)
        err = True
        signers = None
        if vaie.staatus != const.V_STAATUS_OTSUSTAMISEL:
            self.error(_("Vaide olek on juba: {s}").format(s=vaie.staatus_nimi))
        else:
            filedata, signers, dformat = ddocs.DdocS.finalize_signature(self, vaie.otsus_pdok)
            if filedata:
                # salvestame allkirjastatud faili
                vaie.otsus_dok = filedata
                vaie.otsus_ext = dformat
                self._add_vaidelogi(vaie, model.Vaidelogi.TEGEVUS_ALLKIRI)
                err = False

                # märgime allkirjastatuks
                for va in vaie.vaideallkirjad:
                    if va.kasutaja_id == self.c.user.id:
                        va.allkirjastatud = datetime.now()
                
            # pooleli allkirjastamise andmed teeme tühjaks
            vaie.otsus_pdok = None
            if not err:
                if not signers:
                    signers = ddocs.list_signed(self, vaie.otsus_dok, vaie.otsus_ext)
                vaie.allkirjad = len(signers or [])

        model.Session.commit()
        if not err:
            self._kirjuta_jargmisele(vaie)

        return self._after_update(id)
        
    def _update_lopeta(self, item):
        if item.staatus != const.V_STAATUS_OTSUSTAMISEL:
            self.error(_("Vaide olek on juba: {s}").format(s=item.staatus_nimi))
            return 
        if item.otsus_dok is None:
            self.error(_("Otsust pole"))
            return
        if not self._kas_allkirjastatud(item):
            self.error(_("Allkirjastamine on veel pooleli"))
            return
        
        sooritaja = item.sooritaja
        test = sooritaja.test

        # selgitame välja, kas tulemus on muutunud
        muutus = item.muutus 
        if not muutus and test.testiliik_kood == const.TESTILIIK_TASE:
            # Tasemeeksamitel tuleb uus tunnistus välja anda ka juhul, kui
            # tulemust muudetakse nii, et osaoskuse tulemus liigub ühest protsendivahemikust teise             
            for sooritus in sooritaja.sooritused:
                if sooritus.staatus != const.S_STAATUS_TEHTUD:
                    continue
                atos = None
                for atos in sooritus.alatestisooritused:
                    # alatestidega testiosa alatestisooritused
                    if atos.staatus != const.S_STAATUS_TEHTUD:
                        continue
                    protsent_enne = atos.pallid_enne_vaiet * 100. / atos.max_pallid
                    protsent_peale = atos.tulemus_protsent
                    if test.get_vahemik_by_protsent(protsent_enne)[0] != test.get_vahemik_by_protsent(protsent_peale)[0]:
                        muutus = True
                        break
                if not atos:
                    # alatestideta testiosa
                    protsent_enne = sooritus.pallid_enne_vaiet * 100. / sooritus.max_pallid
                    protsent_peale = sooritus.tulemus_protsent
                    if test.get_vahemik_by_protsent(protsent_enne)[0] != test.get_vahemik_by_protsent(protsent_peale)[0]:
                        muutus = True
                        break                    
                    
        if muutus:
            # kui otsusega palle muudeti, siis tuleb märkida tunnistuse uuendamise lipp
            vaarib_tunnistust = not test.lavi_pr or sooritaja.tulemus_piisav

            # otsime tunnistused (eesti keel teise keelena korral võib 2 tunnistust olla)
            omab_tunnistust = False
            for tunnistus in model.Tunnistus.query.\
                join(model.Tunnistus.testitunnistused).\
                filter(model.Testitunnistus.sooritaja_id==sooritaja.id).\
                filter(model.Tunnistus.staatus>=const.N_STAATUS_KEHTIV).\
                all():
                tunnistus.uuendada = True
                omab_tunnistust = True

            # teeme vaidele märke tunnistuse uuendamiseks
            if omab_tunnistust and vaarib_tunnistust:
                item.tunnistada = const.U_STAATUS_UUENDADA
            elif not omab_tunnistust and vaarib_tunnistust:
                item.tunnistada = const.U_STAATUS_VALJASTADA
            elif omab_tunnistust and not vaarib_tunnistust:
                item.tunnistada = const.U_STAATUS_TYHISTADA
            else:
                item.tunnistada = None

            if item.tunnistada:
                # kui tunnistust tuleb muuta, siis saadame kirja korraldajatele
                kellele = self._saada_muutus_korraldajatele(item)
                if kellele:
                    self._add_vaidelogi(item,
                                        model.Vaidelogi.TEGEVUS_EDASTA,
                                        tapsustus=', '.join(kellele))

        item.staatus = const.V_STAATUS_OTSUSTATUD
        self._add_vaidelogi(item, model.Vaidelogi.TEGEVUS_LOPETA)
        model.Session.commit()
        self.success(_("Vaidemenetlus on lõpetatud"))

    def _update_uuesti(self, item):
        if item.staatus not in (const.V_STAATUS_OTSUSTATUD, const.V_STAATUS_TAGASIVOETUD):
            self.error(_("Vaide olek on juba: {s}").format(s=item.staatus_nimi))
            return 
        item.staatus = const.V_STAATUS_ESITATUD
        self._remove_otsus(item)
        
        return self._update_menetlusse(item)


    ######################### kirjade saatmine
    
    def _saada_tagasivotuteade_sooritajale(self, item):
        """Vaidlustajale saadetakse teade (kinnitus vaide tagasi võtmise kohta) 
        """
        sooritaja = item.sooritaja
        kasutaja = sooritaja.kasutaja
        test = sooritaja.testimiskord.test
        to = kasutaja.epost
        if to:
            data = {'isik_nimi': kasutaja.nimi,
                    'test_nimi': test.nimi,
                    'user_nimi': self.c.user.fullname,
                    }
            subject, body = self.render_mail('mail/vaidemenetlus.tagasivotmine.sooritajale.mako', data)
            body = Mailer.replace_newline(body)
            if not Mailer(self).send(to, subject, body):
                self.notice(_("Vaide tagasi võtmise teade on saadetud eksaminandile."))
                log.debug(_("Kiri saadetud sooritajale {s}").format(s=to))
                kiri = model.Kiri(tyyp=model.Kiri.TYYP_MUU,
                                  sisu=body,
                                  teema=subject,
                                  teatekanal=const.TEATEKANAL_EPOST)
                model.Kirjasaaja(kiri=kiri, kasutaja_id=kasutaja.id, epost=to)
                model.Sooritajakiri(sooritaja=sooritaja, kiri=kiri)
                return to

    def _saada_teade_sooritajale(self, item):
        """Vaidlustajale saadetakse teade (kinnitus vaide menetlusse võtmise kohta) 
        """
        sooritaja = item.sooritaja
        kasutaja = sooritaja.kasutaja
        test = sooritaja.testimiskord.test
        to = kasutaja.epost
        if to:
            data = {'isik_nimi': kasutaja.nimi,
                    'test_nimi': test.nimi,
                    'user_nimi': self.c.user.fullname,
                    }
            subject, body = self.render_mail('mail/vaidemenetlus.sooritajale.mako', data)
            body = Mailer.replace_newline(body)
            if not Mailer(self).send(to, subject, body):
                self.notice(_("Menetlusse võtmise teade on saadetud eksaminandile."))
                log.debug(_("Kiri saadetud sooritajale {s}").format(s=to))
                kiri = model.Kiri(tyyp=model.Kiri.TYYP_MUU,
                                  sisu=body,
                                  teema=subject,
                                  teatekanal=const.TEATEKANAL_EPOST)
                model.Kirjasaaja(kiri=kiri, kasutaja_id=kasutaja.id, epost=to)
                model.Sooritajakiri(sooritaja=sooritaja, kiri=kiri)                
                return to
                
    def _saada_teade_ekspertidele(self, item):
        """Vaide aine hindamisjuhtidele ja -ekspertidele saadetakse
        teade uue vaide menetlusse võtmise kohta
        """
        sooritaja = item.sooritaja
        kasutaja = sooritaja.kasutaja
        test = sooritaja.testimiskord.test

        # saadame kirja antud testimiskorra ekspertrühma liikmetele (bugzilla 747)
        q = (model.SessionR.query(model.Kasutaja.id,
                                 model.Kasutaja.epost,
                                 model.Kasutaja.nimi)
             .distinct()
             .filter(model.Kasutaja.epost!=None)
             .filter(model.Kasutaja.epost!='')
             .join(model.Kasutaja.labiviijad)
             .filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAMISEKSPERT)
             .join(model.Labiviija.toimumisaeg)
             .filter(model.Toimumisaeg.testimiskord_id==sooritaja.testimiskord_id))
             
        li_epost = []
        li_nimi = []
        kasutajad = [(k_id, epost, nimi) for (k_id, epost, nimi) in q.all()]
        li_epost = [r[1] for r in kasutajad]
        li_nimi = [r[2] for r in kasutajad]
        if len(li_epost):
            to = li_epost
            data = {'isik_nimi': kasutaja.nimi,
                    'test_nimi': test.nimi,
                    'user_nimi': self.c.user.fullname,
                    }
            subject, body = self.render_mail('mail/vaidemenetlus.hindamisjuhile.mako', data)
            body = Mailer.replace_newline(body)
            if not Mailer(self).send(to, subject, body):
                self.notice(_("Menetlusse võtmise teade on saadetud hindamisjuhtidele ja -ekspertidele ({s})").format(s=', '.join(li_nimi)))
                log.debug(_("Kiri saadetud hindamisjuhtidele ja -ekspertidele {s}").format(s=to))
                kiri = model.Kiri(tyyp=model.Kiri.TYYP_VAIDEMENETLUS,
                                  sisu=body,
                                  teema=subject,
                                  teatekanal=const.TEATEKANAL_EPOST)
                model.Sooritajakiri(sooritaja=sooritaja, kiri=kiri)
                for k_id, epost, nimi in kasutajad:
                    model.Kirjasaaja(kiri=kiri, kasutaja_id=k_id, epost=epost)
                return to

    def _q_allkirjastajad(self, testiliik_kood, jarjekorras):
        "Leitakse allkirjastajate andmed"
        # leiame need, kes on kasutajarolli järgi määratud allkirjastama
        today = date.today()
        grupid = (const.GRUPP_VAIDEKOM_ESIMEES,
                  const.GRUPP_VAIDEKOM_SEKRETAR,
                  const.GRUPP_VAIDEKOM)
        q = (model.SessionR.query(model.Kasutaja.nimi,
                                 model.Kasutaja.id,
                                 model.Kasutajaroll.allkiri_jrk,
                                 model.Kasutajaroll.allkiri_tiitel1,
                                 model.Kasutajaroll.allkiri_tiitel2)
            .join(model.Kasutaja.kasutajarollid)
            .filter(model.Kasutajaroll.kasutajagrupp_id.in_(grupid))
            .filter(model.Kasutajaroll.testiliik_kood==testiliik_kood)
            .filter(model.Kasutajaroll.kehtib_alates<=today)
            .filter(model.Kasutajaroll.kehtib_kuni>=today)
            )
        if jarjekorras:
            # otsime ainult neid, kes saavad otsuseid allkirjastada
            q = q.filter(model.Kasutajaroll.allkiri_jrk!=None)
        q = q.order_by(model.Kasutajaroll.allkiri_jrk)
        return q

    def _leia_tiitel(self, testiliik_kood):
        "Leitakse jooksva kasutaja tiitel kirja jalusesse panekuks"
        q = self._q_allkirjastajad(testiliik_kood, False)
        q = q.filter(model.Kasutaja.id==self.c.user.id)
        for nimi, k_id, jrk, tiitel1, tiitel2 in q.all():
            tiitel = (tiitel1 or '') + '\n' + (tiitel2 or '')
            return nimi, tiitel
        
    def _set_allkirjastajad(self, item):
        "Vaideotsuse genereerimisel luuakse allkirjastajate kirjed"
        # eemaldame igaks juhuks senised allkirjastajate kirjed
        for va in list(item.vaideallkirjad):
            va.delete()
        # leiame need, kes on kasutajarolli järgi määratud allkirjastama
        test = item.sooritaja.test
        testiliik_kood = test.testiliik_kood
        q = self._q_allkirjastajad(testiliik_kood, True)
        
        testiliik_nimi = test.testiliik_nimi
        uus_jrk = 1
        error = None
        data = []
        for nimi, k_id, jrk, tiitel1, tiitel2 in q.all():
            if jrk < uus_jrk:
                error = _('Testiliigi "{liik}" {n}. allkirjastajaid on määratud liiga palju').format(liik=testiliik_nimi, n=jrk)
                break
            elif jrk > uus_jrk:
                error = _('Testiliigi "{liik}" {n}. allkirjastaja on määramata').format(liik=testiliik_nimi, n=uus_jrk)
                break
            else:
                uus_jrk = jrk + 1
                data.append((nimi, tiitel1, tiitel2))
                va = model.Vaideallkiri(kasutaja_id=k_id, jrk=jrk)
                item.vaideallkirjad.append(va)
        if not data:
            error = _('Testiliigi "{liik}" allkirjastajad on määramata').format(liik=testiliik_nimi)
        return data, error
    
    def _kas_allkirjastatud(self, item):
        """Kas kõik vajalikud allkirjad on olemas
        """
        for va in item.vaideallkirjad:
            if not va.allkirjastatud:
                return False
        return True

    def _kas_saan_allkirjastada(self, item):
        """Kontrollitakse, kas jooksev isik võib praegu allkirjastada
        """
        allkirjad = list(item.vaideallkirjad)
        # leiame esimese allkirjastaja kirje, kes pole veel allkirjastanud
        for va in allkirjad:
            if not va.allkirjastatud:
                # kas on sama isik?
                return va.kasutaja_id == self.c.user.id
    
    def _kirjuta_jargmisele(self, item):
        """Leitakse allkirjastamise järjekorras järgmine ja saadetakse kiri
        """
        kasutaja = None
        for va in item.vaideallkirjad:
            if not va.allkirjastatud:
                kasutaja = va.kasutaja
                break
        sooritaja = item.sooritaja
        if kasutaja and kasutaja.id != self.c.user.id:
            epost = kasutaja.epost
            nimi = kasutaja.nimi
            k_id = kasutaja.id
            if not epost:
                self.error(_("Vaidekomisjoni liikme {s} allkiri puudub, aga EIS ei saa talle selle kohta kirja saata, sest me ei tea tema e-posti aadressi").format(s=nimi))
                return
            data = {'isik_nimi': nimi,
                    'vaide_nr': item.vaide_nr,
                    'vaide_url': self.url('muud_edit_vaie', id=item.id, pw_url=True),
                    }
            subject, body = self.render_mail('mail/vaideotsus.allkirjastada.mako', data)

            body = Mailer.replace_newline(body)
            if not Mailer(self).send(epost, subject, body):
                buf = _("Teade on saadetud järgmisele allkirjastajale {s} ({email})").format(s=nimi, email=epost)
                self.notice(buf)
                log.debug(buf)
                kiri = model.Kiri(tyyp=model.Kiri.TYYP_MUU,
                                  sisu=body,
                                  teema=subject,
                                  teatekanal=const.TEATEKANAL_EPOST)
                model.Sooritajakiri(sooritaja=sooritaja, kiri=kiri)
                model.Kirjasaaja(kiri=kiri, kasutaja_id=k_id, epost=epost)
                model.Session.commit()
    
    def _saada_eelnou_sooritajale(self, item):
        """Sooritajale saadetakse otsuse eelnõu
        """
        sooritaja = item.sooritaja
        kasutaja = sooritaja.kasutaja
        test = sooritaja.testimiskord.test            
        r = self._leia_tiitel(test.testiliik_kood)
        if not r:
            self.error(_("Kasutajal {nimi} pole vaidekomisjoni rolli ja seetõttu ei saa eelnõud saata")\
                       .format(nimi=self.c.user.fullname, testiliik=test.testiliik_nimi))
            return
        eelnou_saatja, eelnou_saatja_tiitel = r
        to = kasutaja.epost
        if to:
            data = {'arakuulamine_kuni': item.arakuulamine_kuni.strftime('%d.%m.%Y'),
                    'eelnou_saatja': eelnou_saatja,
                    'eelnou_saatja_tiitel': eelnou_saatja_tiitel,
                    }
            if test.testiliik_kood in (const.TESTILIIK_RV, const.TESTILIIK_RIIGIEKSAM, const.TESTILIIK_POHIKOOL):
                template = 'mail/vaideeelnou.sooritajale.r.mako'
            else:
                template = 'mail/vaideeelnou.sooritajale.te.mako'
            subject, body = self.render_mail(template, data)

            filename = 'vaide-eelnou.pdf'
            filedata = item.eelnou_pdf
            attachments = [(filename, filedata)]

            body = Mailer.replace_newline(body)
            if not Mailer(self).send(to, subject, body, attachments):
                self.notice(_("Eelnõu on saadetud e-postiga eksaminandile. "))
                log.debug(_("Kiri saadetud sooritajale {s}").format(s=to))
                kiri = model.Kiri(tyyp=model.Kiri.TYYP_MUU,
                                  sisu=body,
                                  teema=subject,
                                  teatekanal=const.TEATEKANAL_EPOST)
                kiri.filename = filename
                kiri.filedata = filedata
                model.Kirjasaaja(kiri=kiri, kasutaja_id=kasutaja.id, epost=to)
                model.Sooritajakiri(sooritaja=sooritaja, kiri=kiri)

                return to
        else:
            self.notice(_("Eksaminandile ei saa teadet saata, sest tal pole e-posti aadressi"))
            log.debug(_("Eksaminandile ei saa teadet saata, sest tal pole e-posti aadressi"))
    
    def _saada_otsus_sooritajale(self, item):
        """Sooritajale saadetakse otsus vaide kohta
        """
        sooritaja = item.sooritaja
        kasutaja = sooritaja.kasutaja
        test = sooritaja.testimiskord.test            
        to = kasutaja.epost
        if to:
            data = {'isik_nimi': kasutaja.nimi,
                    'test_nimi': test.nimi,
                    'user_nimi': self.c.user.fullname,
                    }
            subject, body = self.render_mail('mail/vaideotsus.sooritajale.mako', data)
            filename = 'vaideotsus.%s' % item.otsus_ext
            filedata = item.otsus_dok
            attachments = [(filename, filedata)]

            body = Mailer.replace_newline(body)
            if not Mailer(self).send(to, subject, body, attachments):
                self.notice(_("Otsus on saadetud e-postiga eksaminandile. "))
                log.debug(_("Kiri saadetud sooritajale {s}").format(s=to))
                kiri = model.Kiri(tyyp=model.Kiri.TYYP_MUU,
                                  sisu=body,
                                  teema=subject,
                                  teatekanal=const.TEATEKANAL_EPOST)
                kiri.filename = filename
                kiri.filedata = filedata
                model.Kirjasaaja(kiri=kiri, kasutaja_id=kasutaja.id, epost=to)
                model.Sooritajakiri(sooritaja=sooritaja, kiri=kiri)
                return to
        else:
            self.notice(_("Eksaminandile ei saa teadet saata, sest tal pole e-posti aadressi"))
            log.debug(_("Eksaminandil kasutaja.id={n} pole eposti").format(n=kasutaja.id))

    def _saada_muutus_korraldajatele(self, item):
        """Saadame kirja korraldajatele, et tunnistus uuesti teha
        """
        sooritaja = item.sooritaja
        kasutaja = sooritaja.kasutaja
        test = sooritaja.testimiskord.test            

        q = (model.SessionR.query(model.Kasutaja.id,
                                 model.Kasutaja.epost)
             .filter(model.Kasutaja.epost!=None)
             .filter(model.Kasutaja.kasutajarollid.any(
                 sa.and_(model.Kasutajaroll.kasutajagrupp_id==const.GRUPP_KORRALDUS,
                         sa.or_(model.Kasutajaroll.testiliik_kood==None,
                                model.Kasutajaroll.testiliik_kood==test.testiliik_kood),
                         model.Kasutajaroll.kehtib_alates<=datetime.now(),
                         model.Kasutajaroll.kehtib_kuni>=datetime.now())))
             )
        kasutajad = [(k_id, epost) for (k_id, epost) in q.all()]
        li_epost = [r[1] for r in kasutajad]
        if len(li_epost):
            to = li_epost
            
            data = {'isik_nimi': kasutaja.nimi,
                    'test_nimi': test.nimi,
                    'testimiskord_tahis': sooritaja.testimiskord.tahised,
                    'user_nimi': self.c.user.fullname,
                    }
            subject, body = self.render_mail('mail/vaideotsus.korraldajale.mako', data)
            body = Mailer.replace_newline(body)            
            if not Mailer(self).send(to, subject, body):
                self.notice(_("Teade hindepallide muutmise kohta on saadetud korraldajatele ({s}). ").format(s=', '.join(to)))
                log.debug(_("Teade hindepallide muutmise kohta on saadetud korraldajatele: {s}").format(s=to))
                kiri = model.Kiri(tyyp=model.Kiri.TYYP_MUU,
                                  sisu=body,
                                  teema=subject,
                                  teatekanal=const.TEATEKANAL_EPOST)
                model.Sooritajakiri(sooritaja=sooritaja, kiri=kiri)
                for k_id, epost in kasutajad:
                    model.Kirjasaaja(kiri=kiri, kasutaja_id=k_id, epost=epost)
                return to
        else:
            self.notice(_("Korraldajatele ei saa teadet saata, sest pole korraldajate e-posti aadresse"))                

    def _add_vaidelogi(self, vaie, tegevus, kasutaja_id=None, tapsustus=None):
        if not kasutaja_id:
            kasutaja_id = self.c.user.id
        if tapsustus and len(tapsustus) > 256:
            tapsustus = tapsustus[:252] + '...'
        rcd = model.Vaidelogi(tegevus=tegevus, kasutaja_id=kasutaja_id, vaie=vaie, tapsustus=tapsustus)

    def _perm_params(self):
        if None not in self.lubatud_testiliigid:
            if self.c.test:
                if self.c.test.testiliik_kood not in self.lubatud_testiliigid:
                    return False
        
    def __before__(self):
        pbit = self._is_modify() and const.BT_UPDATE or const.BT_INDEX
        kasutaja = self.c.user.get_kasutaja()
        if kasutaja:
            self.lubatud_testiliigid = kasutaja.get_testiliigid('vaided', pbit)
        else:
            # autentimata kasutaja, ei saa ligi
            self.lubatud_testiliigid = []
        id = self.request.matchdict.get('id')
        if id:
            self.c.item = model.Vaie.get(id)
            self.c.sooritaja = self.c.item and self.c.item.sooritaja
            self.c.test = self.c.sooritaja and self.c.sooritaja.test
            self.c.kasutaja = self.c.sooritaja and self.c.sooritaja.kasutaja
            if self._perm_params() == False:
                self.c.can_edit = False
            else:
                self.c.can_edit = self.c.user.has_permission('vaided', const.BT_UPDATE)
            
    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        if not self.has_errors() and not self.has_success():
            self.success()
        if self._index_after_create:
            return self._redirect('index')
        else:
            return self._redirect('edit', id)
