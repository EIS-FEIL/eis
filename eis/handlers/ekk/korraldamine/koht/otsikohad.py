from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class OtsikohadController(BaseResourceController):
    """Soorituskoha otsimine dialoogiaknas, et sinna ümber suunata
    """
    _permission = 'korraldamine'
    _MODEL = model.Testiruum
    _INDEX_TEMPLATE = 'ekk/korraldamine/koht.otsikohad.mako'
    _DEFAULT_SORT = 'koht.nimi' # vaikimisi sortimine
    _no_paginate = True

    def _index_handle_params(self, q, has_params, default_params):
        # yle kirjutatud selleks, et vormi meetod poleks GET

        self.form = Form(self.request, schema=self._SEARCH_FORM)
        if has_params and self.form.validate():
            # kopeerime parameetrid self.c sisse
            # kui parameetrid olid kasutaja poolt, siis jätame need meelde ka
            self._copy_search_params(self.form.data, save=True)

        if default_params:
            # taaskasutame varasemast meelde jäetud parameetreid
            self._copy_search_params(default_params)                            

        if not self.form.errors:
            # saame teha tavalise otsingu
            try:
                # koostame päringu vastavalt sisendparameetritele
                q = self._search(q)                
            except ValidationError as e:
                self.form.errors = e.errors

        if self.form.errors:                        
            # sisendparameetrid ei valideeru
            template = self.request.params.get('partial') and self._LIST_TEMPLATE or self._INDEX_TEMPLATE
            extra_info = self._index_d()
            if isinstance(extra_info, (HTTPFound, Response)):
                return extra_info    
            html = self.form.render(template, extra_info=extra_info)            
            return Response(html)
        else:
            return q

    def _query(self):
        # leiame suunatavate arvu seniste ruumide kaupa
        sooritused_id = self.request.params.getall('sooritus_id')
        qr = (model.Session.query(model.Sooritus.testiruum_id,
                                  sa.func.count(model.Sooritus.id))
              .filter(model.Sooritus.id.in_(sooritused_id))
              .group_by(model.Sooritus.testiruum_id)
              )
        self.c.suunatavad = dict()
        for tr_id, cnt in qr.all():
            self.c.suunatavad[tr_id] = cnt

        # koostame uute ruumide otsimise päringu
        q = (model.Session.query(model.Testiruum, model.Koht, model.Ruum)
             .join(model.Testiruum.testikoht)
             .join(model.Testikoht.koht)
             .outerjoin(model.Testiruum.ruum)
             .outerjoin(model.Koht.aadress)
             .filter(model.Testikoht.toimumisaeg_id==self.c.toimumisaeg.id)
             )
        if self.c.testikoht and self.c.toimumisaeg.ruum_noutud:
            # kui ruum on nõutud, siis sama soorituskoha sees sooritajate
            # suunamisel ei paku valikusse määramata ruumi
            q = q.filter(sa.or_(model.Testikoht.id!=self.c.testikoht.id,
                                model.Testiruum.ruum_id!=None))
        return q

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.tkoht_id:
            q = q.filter(model.Testiruum.testikoht_id==int(self.c.tkoht_id)) 
        if self.c.vabukohti:
            q = q.filter(model.Testiruum.kohti>=model.Testiruum.sooritajate_arv+int(self.c.vabukohti))
        if self.c.piirkond_id:
            piirkonnad_id = model.Piirkond.get(self.c.piirkond_id).get_alamad_id()
            q = q.filter(model.Koht.piirkond_id.in_(piirkonnad_id))
        if self.c.maakond_kood:
            tase, kood = self.c.maakond_kood.split('.')
            q = q.filter(model.Aadress.kood1==kood)
        return q

    def _search_default(self, q):
        # dialoogiakna avamisel pakume vaikimisi võimalust
        # soorituskoha siseselt ruumi vahetada

        if self.c.testikoht:
            q = q.filter(model.Testiruum.testikoht_id==self.c.testikoht.id)
            self.c.show_tpr = True
            return self._search(q)
            
    # def _get_arvud(self):
    #     li = list(map(int, self.request.params.getall('sooritus_id')))
    #     q = (model.Session.query(sa.func.count(model.Sooritaja.id))
    #          .join(model.Sooritaja.sooritused)
    #          .filter(model.Sooritus.id.in_(li))
    #          .filter(model.Sooritaja.valimis==True))
    #     self.c.suunatavate_arv = len(li)
    #     self.c.suunatavate_arv_valim = q.scalar()
        
    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        self.c.testikoht_id = int(self.request.matchdict.get('testikoht_id'))
        if self.c.testikoht_id:
            self.c.testikoht = model.Testikoht.get(self.c.testikoht_id)

    def _perm_params(self):
        if self.c.testikoht:
            return {'obj':self.c.testikoht}

