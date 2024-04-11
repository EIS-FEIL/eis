# Helifailide kontroll, ES-3580

from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class HelifailidController(BaseResourceController):
    _permission = 'korraldamine'
    _MODEL = model.Testikoht
    _INDEX_TEMPLATE = '/ekk/korraldamine/helifailid.mako' 
    _LIST_TEMPLATE = '/ekk/korraldamine/helifailid_list.mako'
    _DEFAULT_SORT = 'sooritus.tahised'
    _ignore_default_params = ['pdf','csv']
    _UNIQUE_SORT = 'sooritaja.id'
    
    def _query(self):
        q = (model.Session.query(model.Sooritus.tahised,
                                 model.Sooritaja.eesnimi,
                                 model.Sooritaja.perenimi,
                                 model.Kasutaja.isikukood,
                                 model.Sooritus.staatus,
                                 model.Koht.nimi,
                                 model.Sooritus.algus,
                                 model.Helivastusfail.kestus,
                                 model.Helivastusfail.filesize,
                                 model.Helivastusfail.created,
                                 model.Helivastusfail.valjast,
                                 model.Testiylesanne.tahis,
                                 )
             .join(model.Sooritus.sooritaja)
             .join(model.Sooritaja.kasutaja)
             .join(model.Sooritus.testikoht)
             .join(model.Testikoht.koht)
             .filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id)
             .outerjoin(model.Sooritus.helivastused)
             .outerjoin(model.Helivastus.testiylesanne)
             .outerjoin(model.Helivastus.helivastusfail)
             )
        return q

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        if self.c.testikoht_id:
            q = q.filter(model.Sooritus.testikoht_id==self.c.testikoht_id)

        if self.c.csv:
            return self._index_csv(q)
        self.c.prepare_header = self._prepare_header
        self.c.prepare_item = self._prepare_item
        self.c.opt_testikoht = self.c.toimumisaeg.get_testikohad_opt()
        return q

    def _order(self, q, sort=None):
        """Otsingu sorteerimine.
        """
        sort = sort or self.request.params.get('sort') or self._DEFAULT_SORT
        # kui on PDFi väljastamine, siis peab
        # alati olema sortimine piirkonna järgi
        if self.request.params.get('pdf'):
            if not sort.startswith('piirkond.nimi'):
                sort = 'piirkond.nimi,'+sort
        return BaseResourceController._order(self, q, sort)

    def _showlist(self):
        """Otsingu tulemuste kuvamine.
        """
        if self.request.params.get('pdf'):
            data, filename = self._render_pdf()
            mimetype = const.CONTENT_TYPE_PDF
            return utils.download(data, filename, mimetype)            

        if self.request.params.get('partial'):
            return self.render_to_response(self._LIST_TEMPLATE)
        else:
            return self.render_to_response(self._INDEX_TEMPLATE)

    def _prepare_header(self):
        "Loetelu päis"
        return (('sooritus.tahised', _("Töö kood")),
                ('sooritaja.eesnimi', _("Eesnimi")),
                ('sooritaja.perenimi', _("Perekonnanimi")),
                ('kasutaja.isikukood', self.request.is_ext() and _("Isikukood") or _("Kasutajatunnus")),
                ('sooritus.staatus', _("Testiosa soorituse olek")),
                ('koht.nimi', _("Soorituskoht")),
                ('sooritus.algus', _("Kuupäev")),
                ('helivastusfail.kestus', _("Faili kestus")),
                ('helivastusfail.filesize', _("Faili suurus")),
                ('helivastusfail.valjast', _("Fail salvestatud EISis")),
                ('helivastusfail.valjast', _("Fail laaditud üles")),
                ('helivastusfail.created', _("Faili salvestamise aeg")),
                )

    def _prepare_item(self, rcd, n=None):
        "Loetelu rida"
        tahised, eesnimi, perenimi, ik, staatus, k_nimi, algus, kestus, filesize, created, valjast, ty_tahis = rcd
        return [tahised,
                eesnimi,
                perenimi,
                ik,
                self.c.opt.S_STAATUS.get(staatus),
                k_nimi,
                self.h.str_from_date(algus),
                self.h.str_from_time_sec(kestus),
                self.h.filesize(filesize),
                valjast == False and _("Jah") or '',
                valjast == True and _("Jah") or '',
                self.h.str_from_datetime(created),
                ]

    def __before__(self):
        self.c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        self.c.testiosa = self.c.toimumisaeg.testiosa
        self.c.test = self.c.testiosa.test
