from eis.lib.baseresource import *
from .laadimine import send_skann_epost
log = logging.getLogger(__name__)

class ToolaadimineController(BaseResourceController):
    """Skannitud testitöö PDFi laadimine andmebaasi
    """
    _permission = 'skannid'
    _MODEL = model.Sooritus

    def _update(self, item):
        value = self.request.params.get('file')
        res = {}
        if value != None and value != b'' and value.file:
            fname = _fn_local(value.filename)
            sf = item.skannfail
            if not sf:
                sf = model.Skannfail(sooritus_id=item.id)
            sf.filename = fname
            sf.filedata = value.value
            model.Session.commit()
            msg, err = send_skann_epost(self, item, sf)
            res['filename'] = fname
            res['msg'] = msg
            res['error'] = err
        return Response(json_body=res)

def _fn_local(fnPath):
    """
    Rajast eraldatakse failinimi.
    """
    pos = max(fnPath.rfind('\\'), fnPath.rfind('/'))
    if pos > -1:
        return fnPath[pos + 1:]
    else:
        return fnPath
        
