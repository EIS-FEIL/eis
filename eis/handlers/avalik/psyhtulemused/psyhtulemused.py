import pickle
from eis.lib.baseresource import *

log = logging.getLogger(__name__)

class PsyhtulemusedController(BaseResourceController):
    "Koolipsyhholoogi õpilaste tulemused"
    # loetelu ainult, sooritaja tulemuste kuvamine vt testid/psyhtulemus.py
    _permission = 'koolipsyh'
    _MODEL = model.Sooritus
    _SEARCH_FORM = forms.avalik.testid.PsyhtulemusedForm
    _INDEX_TEMPLATE = 'avalik/psyhtulemused/psyhtulemused.mako'
    _LIST_TEMPLATE = 'avalik/psyhtulemused/psyhtulemused_list.mako'
    _DEFAULT_SORT = '-sooritaja.id' # vaikimisi sortimine

    def _query(self):
        q = (model.Session.query(model.Sooritus)
             .join(model.Sooritus.sooritaja)
             .filter(model.Sooritaja.esitaja_kasutaja_id==self.c.user.id)
             .join(model.Sooritaja.test)
             .filter(model.Test.testiliik_kood==const.TESTILIIK_KOOLIPSYH)
             .join(model.Sooritaja.kasutaja)
             )
        #model.log_query(q)
        return q

    def _search_default(self, q):
        pass

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        if not q:
            return None
        if c.isikukood:
            q = q.filter(eis.forms.validators.IsikukoodP(c.isikukood)
                         .filter(model.Kasutaja))
        return q
