from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class ProtokollidController(BaseResourceController):
    """Tähelepanu vajavad hindamisprotokollid
    """
    _permission = 'hindamisanalyys'
    _MODEL = model.Hindamisprotokoll
    _INDEX_TEMPLATE = 'ekk/hindamine/analyys.protokollid.mako'
    _LIST_TEMPLATE = 'ekk/hindamine/analyys.protokollid_list.mako'
    _DEFAULT_SORT = 'testiprotokoll.tahised,hindamisprotokoll.liik' # vaikimisi sortimine

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.hindamiskogum_id:
            q = q.join(model.Sisestuskogum.hindamiskogumid).\
                filter(model.Hindamiskogum.id==int(self.c.hindamiskogum_id))

        if self.c.csv:
            return self._index_csv(q)
        return q

    def _query(self):
        q = model.SessionR.query(model.Hindamisprotokoll,
                                model.Testiprotokoll.tahised,
                                model.Sisestuskogum,
                                model.Koht.nimi)
        q = q.join(model.Hindamisprotokoll.testiprotokoll).\
            join(model.Testiprotokoll.testipakett).\
            join(model.Testipakett.testikoht).\
            outerjoin(model.Hindamisprotokoll.sisestuskogum).\
            join(model.Testikoht.koht).\
            filter(model.Testikoht.toimumisaeg_id==self.c.toimumisaeg.id).\
            filter(model.Hindamisprotokoll.staatus != const.H_STAATUS_HINNATUD).\
            filter(model.Hindamisprotokoll.tehtud_toodearv>0)
        
        return q

    def _prepare_header(self):
        header = [_("Soorituskoht"),
                  _("Protokollirühm"),
                  _("Sisestuskogum"),
                  _("Hindamise liik"),
                  _("Olek"),
                  _("I sisestus"),
                  _("II sisestus"),
                  ]
        return header
    
    def _prepare_item(self, rcd, n):
        hpr, tpr_tahised, skogum, koht_nimi = rcd 
        item = [koht_nimi,
                tpr_tahised,
                '%s %s' % (skogum.tahis, skogum.nimi),
                hpr.liik_nimi,
                hpr.staatus_nimi,
                hpr.staatus1_nimi,
                hpr.staatus2_nimi,
                ]
        return item

    def __before__(self):
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        self.c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        self.c.test = self.c.toimumisaeg.testimiskord.test
        
    def _perm_params(self):
        return {'obj': self.c.test}
        
