# -*- coding: utf-8 -*- 
from eis.lib.baseresource import *
from eis.lib.basegrid import *
_ = i18n._
log = logging.getLogger(__name__)

class RvtunnistusedController(BaseResourceController):
    "Rahvusvaheliste eksamite tunnistused"
    _permission = 'avalikadmin'
    _MODEL = model.Rvsooritaja
    _SEARCH_FORM = forms.avalik.admin.RvtunnistusedForm
    _INDEX_TEMPLATE = 'avalik/rvtunnistused/rvtunnistused.mako'
    _LIST_TEMPLATE = 'avalik/rvtunnistused/rvtunnistused_list.mako'
    _EDIT_TEMPLATE = 'avalik/rvtunnistused/rvtunnistus.mako'
    _DEFAULT_SORT = 'kasutaja.perenimi,kasutaja.eesnimi' # vaikimisi sortimine
    _perm_koht = True
    
    def _query(self):
        q = model.Session.query(model.Rvsooritaja,
                                model.Rveksam,
                                model.Tunnistus,
                                model.Kasutaja.isikukood,
                                model.Opilane)
        q = q.join(model.Rvsooritaja.rveksam).\
            join(model.Rvsooritaja.tunnistus).\
            join(model.Tunnistus.kasutaja)
        q = q.join((model.Opilane,
                    model.Opilane.kasutaja_id==model.Tunnistus.kasutaja_id))
        q = q.filter(model.Opilane.koht_id==self.c.user.koht_id).\
            filter(model.Opilane.on_lopetanud==False)
        return q

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if not q:
            return None
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

        if self.c.klass:
            q = q.filter(model.Opilane.klass==self.c.klass)
        if self.c.paralleel:
            q = q.filter(model.Opilane.paralleel==self.c.paralleel.upper())
        return q

    def _edit(self, item):
        kasutaja = item.tunnistus.kasutaja
        opilane = kasutaja.opilane
        if not opilane or opilane.koht_id != self.c.user.koht_id:
            self.error(_('Ei ole oma kooli õpilase tunnistus'))
            raise self._redirect('index')
            
