# -*- coding: utf-8 -*- 

from eis.lib.base import *
_ = i18n._
from eis.lib.importpackage import ImportException
from eis.lib.qti_import import QtiImportPackage
from eis.lib.raw_import import RawImportPackage
from eis.lib.csv_import import CsvImportPackage
from eis.lib.gift_import import GiftImportPackage

log = logging.getLogger(__name__)

# QTI nimeruumid
IMSCP = "{http://www.imsglobal.org/xsd/imscp_v1p1}"
IMSMD = "{http://www.imsglobal.org/xsd/imsmd_v1p2}"
XSI = "{http://www.w3.org/2001/XMLSchema-instance}"
IMSQTI = "{http://www.imsglobal.org/xsd/imsqti_v2p0}"    

class ImportController(BaseController):
    """QTI import.
    """
    _permission = 'ylesanded'

    def index(self):
        return self.render_to_response('ekk/ylesanded/import.mako')

    def create(self):
        c = self.c
        err = None
        
        self.form = Form(self.request, schema=forms.ekk.ylesanded.ImportForm)
        if not self.form.validate():
            err = _("Midagi on valesti")
        else:
            filedata = self.request.params.get('f_filedata')
            if filedata == b'':
                err = _("Fail puudub")

        if err:
            self.error(err)
            return self._redirect('index')
        else:
            try:
                if self._run_import(filedata):
                    self.success(_("Import õnnestus!"))
            except ImportException as ex:
                self.error(ex.message)
            return self.index()

    def _run_import(self, filedata):
        c = self.c
        fn = filedata.filename                                
        c.ext = ext = fn.rsplit('.', 1)[-1].lower()
        if ext == 'raw':
            imp = RawImportPackage(None, filedata)
        elif ext == 'zip':
            imp = QtiImportPackage(None, filedata)
        elif ext == 'gift':
            # Moodle Gift
            c.aine = self.request.params.get('aine')
            c.lang = self.params_lang()                
            imp = GiftImportPackage(None, filedata, c.aine, c.lang)
        elif ext == 'csv':
            c.aine = self.request.params.get('aine')
            c.lang = self.params_lang()
            c.utf8 = self.request.params.get('utf8')
            encoding = c.utf8 and 'utf-8' or None
            
            # loeme pildifailid
            imgobjs = {}
            for files in self.form.data['files']:
                li = files['filedata']
                if isinstance(li, cgi.FieldStorage):
                    li = [li]
                for fstorage in li:
                    # filedata on fstorage.value
                    img_fn = _fn_local(fstorage.filename)
                    imgobjs[img_fn] = fstorage

            log.debug(imgobjs)
            imp = CsvImportPackage(None, filedata, c.aine, c.lang, imgobjs=imgobjs, encoding=encoding)
        else:
            self.error(_("Tundmatu failitüüp {s}").format(s=ext))
            imp = None
        if imp:
            imp.handler = self
            c.messages = imp.messages
            if not imp.is_error and imp.items:
                model.Session.flush()
                imp.after_import()
                c.items = imp.items
                model.Session.commit()
                return True
        
def _fn_local(fnPath):
    """
    Rajast eraldatakse failinimi.
    """
    pos = max(fnPath.rfind('\\'), fnPath.rfind('/'))
    if pos > -1:
        return fnPath[pos + 1:]
    else:
        return fnPath

