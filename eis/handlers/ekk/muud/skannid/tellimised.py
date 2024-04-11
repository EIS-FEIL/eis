from eis.lib.baseresource import *
from eis.lib.pdf.skannidtellimised import SkannidTellimisedDoc

log = logging.getLogger(__name__)

class TellimisedController(BaseResourceController):
    """Tööga tutvumise tellimused
    """
    _permission = 'skannid'
    _MODEL = model.Sooritus
    _INDEX_TEMPLATE = 'ekk/muud/skannid.tellimised.mako'
    _EDIT_TEMPLATE = 'ekk/muud/skannid.tellimine.mako' 
    _LIST_TEMPLATE = 'ekk/muud/skannid.tellimised_list.mako'

    _SEARCH_FORM = forms.ekk.muud.SkannidTellimisedForm 
    _ITEM_FORM = forms.ekk.muud.SkannidTellimineUusForm
    _DEFAULT_SORT = '-sooritus.id'

    _ignore_default_params = ['pdf', 'csv']
    
    def _query(self):
        self.c.prepare_item = self._prepare_item
        self.c.prepare_header = self._prepare_header
        q = (model.SessionR.query(model.Sooritus, 
                                 model.Sooritaja, 
                                 model.Kasutaja,
                                 model.Test,
                                 model.Testimiskord)
             .join(model.Sooritus.sooritaja)
             .join(model.Sooritaja.testimiskord)
             .join(model.Sooritaja.test)
             .join(model.Sooritaja.kasutaja)
             .outerjoin(model.Sooritus.testiprotokoll)
             )
        return q

    def _search_default(self, q):
        return None

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.sessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==self.c.sessioon_id)
        if self.c.test_id:
            q = q.filter(model.Sooritaja.test_id==self.c.test_id)
        if self.c.isikukood:
            usp = validators.IsikukoodP(self.c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))                                    
        if self.c.eesnimi:
            q = q.filter(model.Sooritaja.eesnimi.ilike(self.c.eesnimi))
        if self.c.perenimi:
            q = q.filter(model.Sooritaja.perenimi.ilike(self.c.perenimi))

        q = q.filter(model.Sooritus.tutv_esit_aeg!=None)
        if self.c.alates:
            q = q.filter(model.Sooritus.tutv_esit_aeg>=self.c.alates)
        if self.c.kuni:
            q = q.filter(model.Sooritus.tutv_esit_aeg<self.c.kuni+timedelta(1))

        if self.c.valjaotsitud and not self.c.valjaotsimata:
            q = q.filter(model.Sooritus.valjaotsitud==True)
        elif self.c.valjaotsimata and not self.c.valjaotsitud:
            q = q.filter(sa.or_(model.Sooritus.valjaotsitud==False,
                                model.Sooritus.valjaotsitud==None))

        if self.c.laaditud and not self.c.laadimata:
            q = q.filter(sa.exists().where(model.Skannfail.sooritus_id==model.Sooritus.id))
        elif self.c.laadimata and not self.c.laaditud:
            q = q.filter(~ sa.exists().where(model.Skannfail.sooritus_id==model.Sooritus.id))

        if self.c.aine:
            q = q.filter(model.Test.aine_kood==self.c.aine)

        liigid = self.c.user.get_testiliigid(self._permission)
        if None not in liigid:
            q = q.filter(model.Test.testiliik_kood.in_(liigid))

        if self.c.pdf:
            return self._index_pdf(q)
        if self.c.csv:
            return self._index_csv(q)
        return q

    def _index_pdf(self, q):
        q = self._order(q)
        header, items = self._prepare_items(q)
        doc = SkannidTellimisedDoc(header, items)
        data = doc.generate()
        filename = 'tellimised.pdf'
        mimetype = const.CONTENT_TYPE_PDF
        return utils.download(data, filename, mimetype)

    def _index_csv(self, q):
        header, items = self._prepare_items(q)
        data = self._csv_data(header, items)
        data = utils.encode_ansi(data)
        filename = 'tellimised.csv'
        return utils.download(data, filename, const.CONTENT_TYPE_CSV)

    def _prepare_header(self):
        header = [('test.nimi', 'Test'),
                  ('test.id', 'Testi tähis'),
                  ('testimiskord.tahis', 'Testimiskord'),
                  ('testiprotokoll.tahised', 'Protokollirühm'),
                  ('sooritus.tahised', 'Testitöö'),
                  ('kasutaja.isikukood', 'Isikukood'),
                  ('sooritaja.perenimi,sooritaja.eesnimi', 'Nimi'),
                  ('sooritus.tutv_esit_aeg', 'Esitamise aeg'),
                  #('sooritus.soovib_p', 'Soovib Haridus- ja Noorteametis tutvuda'),
                  #('sooritus.soovib_skanni', 'Soovib skannitud koopiat'),
                  ]
        return header
    
    def _prepare_items(self, q):
        header = self._prepare_header()
        items = [self._prepare_item(rcd) for rcd in q.all()]
        return header, items

    def _prepare_item(self, rcd):
        "Loetelu kirje vormistamine CSV ja PDF jaoks"
        
        sooritus, sooritaja, k, test, tkord = rcd
        ta = sooritus.toimumisaeg
        tahised = sooritus.tahised
        tpr = sooritus.testiprotokoll
        h = self.h
        item = [test.nimi,
                str(test.id),
                tkord and tkord.tahis or '',
                tpr and tpr.tahised or '',
                tahised,
                k.isikukood,
                sooritaja.nimi,
                h.str_from_date(sooritus.tutv_esit_aeg) or '',
                ]
        return item
    
    def new(self, format='html'):
        """Uue vaide alustamise vormi kuvamine.
        Kasutaja peab sisestama vaidlustava sooritaja isikukoodi.
        """
        if self.request.params.get('isikukood'):
            self._new_item()
        return self.render_to_response('/ekk/muud/skannid.tellimine.mako')

    def _new_item(self):
        """Otsitakse antud isikukoodiga sooritaja andmed
        """
        self.form = Form(self.request, schema=forms.ekk.muud.SkannidTellimineUusOtsiForm)
        if self.form.validate():
            self.c.isikukood = self.form.data.get('isikukood')
            self.c.kasutaja = model.Kasutaja.get_by_ik(self.c.isikukood)
            if not self.c.kasutaja:
                self.error('Isik pole eksameid sooritanud')
            else:
                self._get_opt()
        return self.response_dict

    def _get_opt(self):
        dt = date.today()
        q = (model.SessionR.query(model.Sooritus.id, model.Toimumisaeg.tahised, model.Test.nimi)
             .join(model.Sooritus.sooritaja)
             .filter(model.Sooritaja.kasutaja_id==self.c.kasutaja.id)
             .join(model.Sooritaja.testimiskord)
             .filter(model.Testimiskord.tutv_taotlus_alates <= dt)
             .filter(sa.or_(model.Testimiskord.tutv_taotlus_kuni==None,
                            model.Testimiskord.tutv_taotlus_kuni>=dt))
             .filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
             .join(model.Sooritaja.test)
             .join(model.Sooritus.testiosa)
             .filter(model.Testiosa.vastvorm_kood==const.VASTVORM_KP)
             .join(model.Testimiskord.toimumisajad)
             .filter(model.Toimumisaeg.testiosa_id==model.Testiosa.id)
             )
        self.c.opt_sooritus = [(s_id, '%s %s' % (tahised, nimi)) for (s_id, tahised, nimi) in q.all()]
        if not len(self.c.opt_sooritus):
            self.error('Isikul ei ole eksamitöid, millega tutvumise taotlust saab praegu esitada')
        self.c.esitamisaeg = date.today()

    def _create_index(self):
        "Väljaotsitud vaiete märkimine"
        valitud_id = self.request.params.getall('s_id')
        endised_id = self.request.params.getall('endine_id')

        uued_id = set(valitud_id) - set(endised_id)
        if len(uued_id):
            for vaie_id in uued_id:
                model.Sooritus.get(vaie_id).valjaotsitud = True

        eemaldatud_id = set(endised_id) - set(valitud_id)
        if len(eemaldatud_id):
            for vaie_id in eemaldatud_id:
                model.Sooritus.get(vaie_id).valjaotsitud = False

        model.Session.commit()
        return HTTPFound(location=self.request.params.get('list_url'))

    def create(self):
        """Uue tellimise loomine
        On sisestatud sooritaja isikukood ja valitud test.
        """
        if self.request.params.get('sub') == 'index':
            return self._create_index()
        
        if self.request.params.get('otsi'):
            # otsitakse isik
            self._new_item()
            if self.form.errors:
                # isiku otsimine ei õnnestunud
                return Response(self.form.render('/ekk/muud/skannid.tellimine.mako',
                                                 extra_info=self.response_dict))
            # kuvatakse isiku testi valimise vorm
            return self.new()

        else:
            # salvestatakse isiku taotlus
            self.form = Form(self.request, schema=self._ITEM_FORM)
            if not self.form.validate():
                # taotluse andmete sisestamise viga
                kasutaja_id = self.request.params.get('kasutaja_id')
                self.c.kasutaja = kasutaja_id and model.Kasutaja.get(kasutaja_id)
                if self.c.kasutaja:
                    self._get_opt()
                return Response(self.form.render('/ekk/muud/skannid.tellimine.mako',
                                                 extra_info=self._new_item()))

        item = self._create()
        if isinstance(item, Response):
            return item
        if self.has_errors():
            return self._redirect('new')
        # uus vaie on loodud
        model.Session.commit()
        return self._redirect(action='edit', id=item.id)

    def _create(self, **kw):
        sooritus = model.Sooritus.get(self.form.data.get('sooritus_id'))
        sooritaja = sooritus.sooritaja

        if sooritaja.staatus != const.S_STAATUS_TEHTUD:
            self.error('Sooritus pole tehtud')
            self._new_item()
            return self.new()

        if not sooritus.tutv_esit_aeg:
            sooritus.tutv_esit_aeg = date.today()

        sooritus.soovib_skanni = self.form.data.get('soovib_skanni') and True or False
        epost = self.form.data.get('k_epost')
        if epost:
            sooritaja.kasutaja.epost = epost
        model.Session.commit()
        self.c.is_saved = True
        return self.render_to_response(self._EDIT_TEMPLATE)

    def _edit(self, item):
        self.c.kasutaja = item.sooritaja.kasutaja

    def _download(self, id, format):
        """Näita faili"""
        item = self._MODEL.get(id)
        sf = item and item.skannfail
        if not sf:
            raise NotFound('Ei leitud')
    
        filedata, filename = sf.filedata, sf.filename
        mimetype = const.CONTENT_TYPE_PDF

        if not filedata:
            raise NotFound('Dokumenti ei leitud')
        return utils.download(filedata, filename, mimetype)
