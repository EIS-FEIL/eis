# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
from eis.lib.basegrid import *
from eis.lib.feedbackreport import FeedbackReport

log = logging.getLogger(__name__)

class ProfiililehtController(BaseResourceController):
    "Õpilase tagasiside genereerimine"
    _permission = 'omanimekirjad'
    _MODEL = model.Sooritus
    _get_is_readonly = False
   
    def _show(self, item):
        # koostatakse c.tagasiside_html
        self._generate(item.sooritaja, None)

    def _download(self, id, format=None):
        """Näita faili"""
        sooritus = model.Sooritus.get(id)
        if sooritus:
            return self._generate(sooritus.sooritaja, format)
        raise NotFound('Faili ei leitud')

    def _generate(self, sooritaja, format):
        fr = FeedbackReport.init_opetaja(self, sooritaja.test, sooritaja.lang, sooritaja.kursus_kood)
        if fr:
            if format == 'pdf':
                filedata = fr.generate_pdf(sooritaja)
                return utils.download(filedata, 'tagasiside.pdf', const.CONTENT_TYPE_PDF)
            elif format == 'xls':
                filedata = fr.generate_xls(sooritaja)
                return utils.download_xls_file(filedata, 'tagasiside.xlsx')
            else:
                err, self.c.tagasiside_html = fr.generate(sooritaja)
                if err:
                    self.error(err)
                    
    def __before__(self):
        c = self.c
        c.testiruum_id = self.request.matchdict.get('testiruum_id')
        sooritus_id = self.request.matchdict.get('id')
        if sooritus_id:
            c.sooritus = c.item = model.Sooritus.get(sooritus_id)
            c.sooritaja = c.sooritus.sooritaja
            c.test = c.sooritaja.test
            c.test_id = c.sooritaja.test_id
            c.testiruum_id = c.sooritus.testiruum_id
            c.kasutaja = c.sooritaja.kasutaja
            kasutaja_id = c.sooritaja.kasutaja_id

    def _perm_params(self):
        testiruum = model.Testiruum.get(self.c.testiruum_id)
        nimekiri = testiruum.nimekiri
        if not nimekiri:
            return False
        return {'obj':nimekiri}
