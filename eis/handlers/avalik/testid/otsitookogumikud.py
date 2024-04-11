from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController

log = logging.getLogger(__name__)

class OtsitookogumikudController(BaseResourceController):
    "Ylesannete otsing minu töökogumikest"
    _permission = 'testid'
    _MODEL = model.Tookogumik
    _INDEX_TEMPLATE = 'avalik/testid/otsitookogumikud.mako'
    _LIST_TEMPLATE = 'avalik/testid/otsitookogumikud_list.mako'
    _SHOW_TEMPLATE = 'avalik/testid/otsitookogumikud.tookogumik.mako'
    _SEARCH_FORM = forms.avalik.tookogumikud.OtsingForm 
    _DEFAULT_SORT = 'tookogumik.nimi' # vaikimisi sortimine
    _log_params_never = True # et saaks readonly ylesanded.py transaktsioonist kutsuda
    _actions = 'index' # võimalikud tegevused
    
    def _query(self):
        q = (model.SessionR.query(model.Tookogumik)
             .filter(model.Tookogumik.kasutaja_id==self.c.user.id)
             )
        return q
    
    def _search_default(self, q):
        """Otsingu tingimuste seadmine siis, kui otsing toimub 
        kohe otsinguvormi avamisel ja kasutaja pole veel saanud 
        otsingutingimusi valida.
        """
        return self._search(q)

    def _search(self, q):
        """Otsinguvormi päringu koostamine ning 
        otsitingimuste meelde jätmine c sees.
        """
        c = self.c
        c.opt_tookogumik = [(tk.id, tk.nimi) for tk in q.order_by(model.Tookogumik.nimi)]
        if not c.tookogumik_id and c.opt_tookogumik:
            c.tookogumik_id = c.opt_tookogumik[0][0]
        if c.tookogumik_id:
            q = q.filter(model.Tookogumik.id==c.tookogumik_id)
        return q

    def _get_current_upath(self):
        # anname upath ette, et leitaks parameetrid ka siis,
        # kui request on tehtud Ylesanded kontrollerile
        return self.h.url_current()
       
    def __before__(self):
        """Väärtustame self.c.test testiga
        """
        c = self.c
        c.testiruum_id = self.request.matchdict.get('testiruum_id')
        c.test_id = self.request.matchdict.get('test_id')
        c.test = model.Test.get(c.test_id)
        if c.testiruum_id:
            testiruum = model.Testiruum.get(c.testiruum_id)
            c.nimekiri = testiruum and testiruum.nimekiri

        BaseResourceController.__before__(self)
