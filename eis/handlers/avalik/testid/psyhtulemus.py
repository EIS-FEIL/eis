from eis.lib.baseresource import *
from eis.lib.feedbackreport import FeedbackReport
log = logging.getLogger(__name__)
_ = i18n._

class PsyhtulemusController(BaseResourceController):
    "Koolipsyhholoogi õpilaste tulemused"
    _permission = 'koolipsyh'
    _MODEL = model.Sooritus
    _EDIT_TEMPLATE = 'avalik/psyhtulemused/psyhtulemus.mako'
    _get_is_readonly = False
    _actions = 'download,show,edit' # võimalikud tegevused
    
    def _show(self, item):
        c = self.c
        c.sooritus = item
        sooritaja = item.sooritaja
        c.test = sooritaja.test
        c.test_id = sooritaja.test_id
        c.testiruum_id = item.testiruum_id
        c.kasutaja = sooritaja.kasutaja
        c.nimekiri = sooritaja.nimekiri
        fr = FeedbackReport.init_opetaja(self, c.test, sooritaja.lang, sooritaja.kursus_kood)
        if fr:
            err, c.tagasiside_html = fr.generate(sooritaja)
            if err:
                self.error(err)
        
    def _download(self, id, format=None):
        """Näita faili"""
        item = model.Sooritus.get(id)
        if not item:
            raise NotFound(_('Kirjet {s} ei leitud').format(s=id))        
        sooritaja = item.sooritaja
        test = sooritaja.test
        if sooritaja.esitaja_kasutaja_id != self.c.user.id or \
           item.staatus != const.S_STAATUS_TEHTUD or \
           test.testiliik_kood != const.TESTILIIK_KOOLIPSYH:
            if not self.c.app_ekk:
                raise NotFound(_('Ei saa kuvada'))

        fr = FeedbackReport.init_opetaja(self, test, sooritaja.lang, sooritaja.kursus_kood)
        if fr:
            if format == 'xls':
                filedata = fr.generate_xls(sooritaja)
                return utils.download_xls_file(filedata, 'tagasiside.xlsx')
            else:
                filedata = fr.generate_pdf(sooritaja)
                return utils.download(filedata, 'tagasiside.pdf', const.CONTENT_TYPE_PDF)
