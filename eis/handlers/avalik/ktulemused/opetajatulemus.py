from eis.lib.baseresource import *
_ = i18n._
from eis.lib.feedbackreport import FeedbackReport
from .opilasetulemus import OpilasetulemusController

log = logging.getLogger(__name__)

class OpetajatulemusController(OpilasetulemusController):

    _permission = 'avalikadmin,testiadmin'
    _MODEL = model.Sooritaja
    _EDIT_TEMPLATE = 'avalik/ktulemused/opetajatulemus.mako'

    def _show(self, item):
        super()._show(item)

        c = self.c
        if not c.tagasiside_html:
            # kui õpetaja tagasiside puudub, siis minnakse õpilase tagasiside lehele
            # enne kontrollime, kas õpilase tagasiside on õpetajale lubatud
            lang = item.lang
            kursus = item.kursus_kood
            has_opilane = c.FeedbackReport.init_opilane(self, c.test, lang, kursus, check=True, opetajale=True)
            if has_opilane:
                url = self.url('ktulemused_opilasetulemus', test_id=c.test.id, testimiskord_id=c.testimiskord.id, id=c.sooritaja.id, kursus=c.kursus or '')
                raise HTTPFound(location=url)
        
    def _get_fr(self, test, lang, kursus):
        fr = FeedbackReport.init_opetaja(self, test, lang, kursus)
        return fr
