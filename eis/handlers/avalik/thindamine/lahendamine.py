"Testi ülesande sisu näitamine kirjalikule hindajale"

from eis.lib.baseresource import *
_ = i18n._
from .toohindamine import get_tab_urls
from eis.handlers.avalik.lahendamine import lahendamine
log = logging.getLogger(__name__)

class LahendamineController(lahendamine.LahendamineController):
    _permission = 'omanimekirjad'
    _EDIT_TEMPLATE = 'avalik/khindamine/hindamine_r.lahendamine.mako'     
    _actions = 'edit,update,show'

    def edit(self):
        c = self.c
        get_tab_urls(self, c)
        if self.request.params.get('correct'):
            # õige vastuse sakk
            c.show_correct = True
            c.read_only = True
        else:
            # ei tee õige vastuse nuppu, kuna õige vastus on eraldi sakis
            c.prepare_correct = True
            c.btn_correct = False
        return super().edit()

    def _edittask_bcorrect(self):
        # kas kuvada õige vastuse nupp
        # bcorrect on False, kuna õige vastus on eraldi sakis
        return False
       
    def __before__(self):
        c = self.c
        vy_id = self.request.matchdict.get('vy_id')
        c.vy = model.Valitudylesanne.get(vy_id)
        id = self.request.matchdict.get('id')
        c.ylesanne = model.Ylesanne.get(id)
        c.lang = self.params_lang()
        c.indlg = self.request.params.get('indlg')
        c.testiruum_id = self.request.matchdict.get('testiruum_id')
        test_id = self.request.matchdict.get('test_id')
        c.test = model.Test.get(test_id)

    def _check_status(self, item):
        # hindaja peab ylesandele ligi saama
        return True
