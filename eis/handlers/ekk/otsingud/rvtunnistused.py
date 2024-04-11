from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class RvtunnistusedController(BaseResourceController):
    """Rahvusvaheliste eksamite tunnistuste otsimine
    """
    _permission = 'aruanded-rvtunnistused'
    _MODEL = model.Rvsooritaja
    _INDEX_TEMPLATE = 'ekk/otsingud/rvtunnistused.mako'
    _LIST_TEMPLATE = 'ekk/otsingud/rvtunnistused_list.mako'
    _EDIT_TEMPLATE = 'ekk/otsingud/rvtunnistus.mako'
    _DEFAULT_SORT = 'rvsooritaja.id'
    _SEARCH_FORM = forms.ekk.otsingud.RvtunnistusedForm
    _ignore_default_params = ['xls']    

    def _query(self):
        q = model.Session.query(model.Rvsooritaja,
                                model.Rveksam,
                                model.Tunnistus,
                                model.Kasutaja.isikukood,
                                model.Sooritaja.test_id)
        q = (q.join(model.Rvsooritaja.rveksam)
             .join(model.Rvsooritaja.tunnistus)
             .join(model.Tunnistus.kasutaja)
             .outerjoin((model.Sooritaja, model.Rvsooritaja.sooritaja_id==model.Sooritaja.id))
             )
        return q
    
    def _search_default(self, q):
        return None

    def _search(self, q):
        if self.c.rveksam_id:
            q = q.filter(model.Rvsooritaja.rveksam_id==self.c.rveksam_id)
        if self.c.aine:
            q = q.filter(model.Rveksam.aine_kood==self.c.aine)
        if self.c.isikukood:
            usp = validators.IsikukoodP(self.c.isikukood)
            q = q.filter(usp.filter(model.Kasutaja))
        if self.c.alates:
            q = q.filter(model.Tunnistus.valjastamisaeg>=self.c.alates)
        if self.c.kuni:
            q = q.filter(model.Tunnistus.valjastamisaeg<=self.c.kuni)
        if self.c.sis_alates:
            q = q.filter(model.Rvsooritaja.created>=self.c.sis_alates)
        if self.c.sis_kuni:
            q = q.filter(model.Rvsooritaja.created<=self.c.sis_kuni)

        if self.request.params.get('xls'):
            return self._index_xls(q, 'rvtunnistused.xlsx')

        return q

    def _prepare_header(self):
        """Päringutulemuste paigutamine väljastamiseks sobivale kujule"""
        header = [('rveksam.nimi', _("Tunnistus")),
                  ('tunnistus.tunnistusenr', _("Tunnistuse nr")),
                  ('tunnistus.valjastamisaeg', _("Väljastamisaeg")),
                  ('rvsooritaja.kehtib_kuni', _("Kehtib kuni")),
                  ('kasutaja.isikukood', _("Isikukood")),
                  ('tunnistus.eesnimi', _("Eesnimi")),
                  ('tunnistus.perenimi', _("Perekonnanimi")),
                  ('rvsooritaja.keeletase_kood', _("Tase")),
                  ('sooritaja.test_id', _("Testi ID")),
                  ]
        return header

    def _prepare_item(self, rcd, n=None):
        rvsooritaja, rveksam, tunnistus, kasutaja_ik, test_id = rcd
        item = [rveksam.nimi,
                tunnistus.tunnistusenr,
                self.h.str_from_date(tunnistus.valjastamisaeg),
                self.h.str_from_date(rvsooritaja.kehtib_kuni),
                kasutaja_ik,
                tunnistus.eesnimi,
                tunnistus.perenimi,
                rvsooritaja.keeletase_kood,
                test_id,
                ]
        return item
