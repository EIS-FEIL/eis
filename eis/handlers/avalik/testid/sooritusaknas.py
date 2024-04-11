from eis.lib.baseresource import *
from eis.handlers.avalik.sooritamine import sooritus
from eis.lib.feedbackreport import FeedbackReport
import logging
log = logging.getLogger(__name__)
_ = i18n._
class SooritusaknasController(sooritus.SooritusController):
    """Õpetaja vaatab lahendaja lahendust.
    """
    _permission = 'omanimekirjad'
    _EDIT_TEMPLATE = 'avalik/testid/sooritusaknas.mako'
    _actions = 'show,download' # võimalikud tegevused
    _actionstask = 'showtask,correct,showtool'
    
    def new(self):
        raise Exception(_('Vale tegevus'))

    def _show(self, item):
        # item on None
        c = self.c
        c.on_sooritusaknas = True
        c.read_only = True
        self._generate(None)        

        # staatilisi plokke välja ei jäeta (ES-2210)
        
        c.show_tulemus = True
        ty_id = self.request.params.get('ty_id')
        if ty_id:
            c.ty_id = int(ty_id)
        c.grupp_id = self.request.params.get('grupp_id')
        return sooritus.SooritusController._show(self, item)

    def _download(self, id, format=None):
        """Näita faili"""
        res = self._generate(format)
        if res:
            return res
        else:
            raise NotFound('Faili ei leitud')

    def _generate(self, format):
        c = self.c
        fr = FeedbackReport.init_opetaja(self, c.test, c.sooritaja.lang, c.sooritaja.kursus_kood)
        if fr:
            if format == 'pdf':
                filedata = fr.generate_pdf(c.sooritaja)
                return utils.download(filedata, 'tagasiside.pdf', const.CONTENT_TYPE_PDF)
            elif format == 'xls':
                filedata = fr.generate_xls(c.sooritaja)
                return utils.download_xls_file(filedata, 'tagasiside.xlsx')
            else:
                err, c.tagasiside_html = fr.generate(c.sooritaja)
                if err:
                    self.error(err)

    def _has_permission(self):
        return BaseResourceController._has_permission(self)

    def _perm_params(self):
        c = self.c
        c.sooritus = model.Sooritus.get(self.request.matchdict.get('id'))
        c.sooritaja = c.sooritus.sooritaja
        c.test_id = c.sooritaja.test_id
        c.test = c.sooritaja.test
        c.testiosa = c.sooritus.testiosa
        c.testiosa_id = c.testiosa.id
        nimekiri = c.sooritaja.nimekiri
        if not nimekiri:
            return False
        c.testiruum_id = self.request.matchdict.get('testiruum_id')
        c.testiruum = model.Testiruum.get(c.testiruum_id)
        return {'obj':nimekiri}
