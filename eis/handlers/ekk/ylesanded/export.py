# -*- coding: utf-8 -*- 

from eis.lib.base import *
_ = i18n._
import eis.lib.qti_export as qti_export
import eis.lib.html_export as html_export
import eis.lib.raw_export as raw_export

log = logging.getLogger(__name__)

class ExportController(BaseController):
    """Ülesannete eksport.
    """
    _permission = 'ylesanded'
    _get_is_readonly = False    

    def show(self):
        id = self.request.matchdict.get('id')
        item = model.Ylesanne.get(id)
        format = self.request.matchdict.get('format')
        lang = self.params_lang()

        if format == 'qti':
            try:
                filedata = qti_export.export_zip(item, lang)
            except Exception as ex:
                self._error(ex, 'QTI export')
                self.error(_("Selle ülesande QTI eksportimine ei õnnestu"))
                return HTTPFound(location=self.url('ylesanded_edit_sisu', id=id, lang=lang))
            filename = 'ylesanne%s_qti.zip' % item.id
            mimetype = 'application/zip'
            return utils.download(filedata, filename, mimetype)

        elif format == 'html':
            filedata = html_export.export_html(item, lang, self)
            filename = 'ylesanne%s.html' % item.id
            mimetype = 'text/html'
            return Response(filedata)

        elif format == 'zip':
            filedata = html_export.export_zip(item, lang, self)
            filename = 'ylesanne%s_html.zip' % item.id
            mimetype = 'application/zip'
            return utils.download(filedata, filename, mimetype)

        elif format == 'raw':
            filedata = raw_export.export(item)
            filename = 'ylesanne%s.raw' % item.id
            mimetype = 'application/binary'
            return utils.download(filedata, filename, mimetype)

        else:
            raise NotFound(_("Formaadis {s} eksportimist ei toimu").format(s=format))

    def __before__(self):
        self.c.ylesanne = model.Ylesanne.get(self.request.matchdict.get('id'))

    def _perm_params(self):
        return {'obj':self.c.ylesanne}
