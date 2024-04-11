from eis.lib.baseresource import *
from eis.lib.basegrid import BaseGridController
log = logging.getLogger(__name__)

class MaaramisedController(BaseResourceController):
    _permission = 'nousolekud'
    _MODEL = model.Labiviija
    _SEARCH_FORM = forms.avalik.admin.MaaramisedForm
    _INDEX_TEMPLATE = '/avalik/nousolekud/maaramised.mako' 
    _LIST_TEMPLATE = '/avalik/nousolekud/maaramised_list.mako'
    _DEFAULT_SORT = '-toimumisaeg.alates'

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        if self.c.testsessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==int(self.c.testsessioon_id))
        if self.c.alates:
            q = q.filter(model.Toimumisaeg.kuni >= self.c.alates)
        if self.c.kuni:
            q = q.filter(model.Toimumisaeg.alates <= self.c.kuni)
        return q

    def _query(self):
        dd = date.today()
        q = model.SessionR.query(model.Labiviija).\
            filter(model.Labiviija.kasutajagrupp_id != const.GRUPP_HIND_INT).\
            filter_by(kasutaja_id=self.c.kasutaja.id).\
            join(model.Labiviija.toimumisaeg)
        return q
        
    def __before__(self):
        self.c.kasutaja = self.c.user.get_kasutaja()
