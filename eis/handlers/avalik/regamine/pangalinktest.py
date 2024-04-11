# Pangalingi testimine
# https://eis.ekk.edu.ee/eis/admin/pangalinktestid

from eis.lib.base import *
from eis.lib.pangalink import Pangalink
from .pangalink import PangalinkController
log = logging.getLogger(__name__)
_ = i18n._
class PangalinkTestController(PangalinkController):
    _actions = 'index,new,returned'
    
    def index(self):
        # https://eis.ekk.edu.ee/ekk/admin/pangalinktestid
        if not self.c.user.is_authenticated:
            raise NotAuthorizedException('login')
        if not self.c.user.get_kasutaja().on_kehtiv_roll(const.GRUPP_ADMIN):
            raise NotAuthorizedException('avaleht')            
        self.c.tasumata = 0.01
        self.c.pangad = Pangalink.get_list()
        self.c.kasutaja = self.c.user.get_kasutaja()
        return self.render_to_response('avalik/regamine/pangalink_test.mako')

    def _get_ret_url(self):
        tasu = .01
        mille_eest = 'Pangalingi testimine ÕÄÖÜ'
        ret_url = self.url('admin_return_pangalinktest', 
                           pank_id=self.c.pank_id,
                           pw_url=True)
        return tasu, mille_eest, ret_url

    def _set_paid(self, makse):
        self._show_msg('1') # makse on sooritatud
        
    def _after_return(self, sooritaja_id):
        return self._redirect('index')
