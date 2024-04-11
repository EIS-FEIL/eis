# -*- coding: utf-8 -*- 

from eis.lib.base import *
_ = i18n._
import eis.lib.html_export as html_export

log = logging.getLogger(__name__)

class ExportController(BaseController):
    """Testi ülesannete eksport.
    """
    _permission = 'ekk-testid'

    def show(self):
        test_id = self.request.matchdict.get('test_id')
        komplekt_id = self.request.matchdict.get('komplekt_id')
        test = model.Test.get(test_id)
        komplekt = model.Komplekt.get(komplekt_id)
        komplektivalik = komplekt.komplektivalik
        if komplektivalik.testiosa.test != test:
            return 'Vale komplekt'
        #self.c.block_correct = True
        lang = self.params_lang()
        format = self.request.matchdict.get('format')
        if format == 'qti':
            return ''
            #data = qti_export.export_zip(item, lang)
            #_download_headers('application/zip', 'ylesanne.zip', data)
            #return data
        elif format == 'html':
            data = html_export.export_test_html(komplekt, lang, self)
            return Response(data)
        elif format == 'zip':
            data = html_export.export_test_zip(komplekt, lang, self)
            return utils.download(data, 'test.zip', 'application/zip')
        else:
            return ''
        
    def __before__(self):
        self.c.item = model.Test.get(self.request.matchdict.get('test_id'))

    def _perm_params(self):
        return {'obj':self.c.item}
