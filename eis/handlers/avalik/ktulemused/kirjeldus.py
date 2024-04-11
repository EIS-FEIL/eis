from eis.lib.baseresource import *
from .feedbackbase import FeedbackBaseController
_ = i18n._

log = logging.getLogger(__name__)

class KirjeldusController(FeedbackBaseController, BaseResourceController):
    "Testi kirjeldus"
    _permission = 'avalikadmin,testiadmin,aineopetaja'
    _INDEX_TEMPLATE = 'avalik/ktulemused/kirjeldus.mako'
    _actions = 'index,download'

    def _search(self, q):
        c = self.c
        res = self._get_tagasiside(0, [], [], c.kursus)
        if c.pdf or c.xls:
            return res
        elif res:
            c.tagasiside_html = res
        else:
            url = self.url('ktulemused_osalejad', test_id=c.test.id, testimiskord_id=c.testimiskord.id, kursus=c.kursus)
            return HTTPFound(location=url)

    def _get_fr(self, test, lang, kursus):
        fr = eis.lib.feedbackreport.FeedbackReport.init_kirjeldus(self, test, lang, kursus)
        return fr
                   
    def _perm_params(self):
        c = self.c
        if not c.testimiskord.koondtulemus_avaldet:
            return False
        return {'test': c.test}
