from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController
from eis.lib.xtee import ehis

log = logging.getLogger(__name__)

class KohalogidController(BaseResourceController):
    _permission = 'kohad'
    _MODEL = model.Kohalogi
    _SEARCH_FORM = forms.admin.KohalogiForm
    _INDEX_TEMPLATE = 'admin/kohalogi.mako' # otsinguvormi mall
    _LIST_TEMPLATE = '/admin/kohalogi_list.mako'
    _DEFAULT_SORT = '-kohalogi.id'
    
    def _query(self):
        q = model.SessionR.query(model.Kohalogi, 
                                model.Koht.nimi,
                                model.Kasutaja.nimi)
        q = q.join(model.Kohalogi.koht).\
            join(model.Kohalogi.kasutaja)

        self.c.opt_allikas = [(model.Kohalogi.ALLIKAS_EKK, _("Eksamikeskus")),
                              (model.Kohalogi.ALLIKAS_SK, _("Soorituskoht")),
                              (model.Kohalogi.ALLIKAS_EHIS, _("EHIS")),
                              ]
        return q

    def _search_default(self, q):
        self.c.alates = date.today()
        return self._search(q)

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.koht_id:
            q = q.filter(model.Kohalogi.koht_id == self.c.koht_id)
        if self.c.koht_nimi:
            q = q.filter(model.Koht.koolinimed.any(\
                    model.Koolinimi.nimi.ilike(self.c.koht_nimi)))
        if self.c.alates:
            q = q.filter(model.Kohalogi.modified >= self.c.alates)
        if self.c.kuni:
            q = q.filter(model.Kohalogi.modified <= self.c.kuni)
        if self.c.allikas:
            q = q.filter(model.Kohalogi.allikas == self.c.allikas)
        if self.c.muutja_nimi:
            q = q.filter(model.Kasutaja.nimi.ilike(self.c.muutja_nimi))
        return q
   
