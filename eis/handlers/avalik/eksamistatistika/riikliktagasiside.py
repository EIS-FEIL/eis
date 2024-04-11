from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class RiikliktagasisideController(BaseResourceController):
    """Eksamite tulemuste statistika
    """
    _permission = 'lahendamine'
    _ITEM_TEMPLATE = 'avalik/eksamistatistika/riikliktagasiside.mako'
    _authorize = False
    _actions = 'show'
    # kas testimiskorrad peavad olema avalikus vaates avaldatud
    avalik = True
    
    def show(self):
        """PDF-raport"""
        c = self.c
        c.aasta = aasta = self.request.matchdict['aasta']
        test_id = self.request.matchdict['test_id']
        c.kursus = kursus = self.request.matchdict['kursus'] or None
        _format = self.request.params.get('pdf') and 'pdf' or 'html'
        
        c.test = test = model.Test.get(test_id)
        data = None
        if test:
            aasta = int(aasta)
            raport = model.Statistikaraport.get_raport(test_id, kursus, aasta, _format)
            if raport and (raport.avalik or not self.avalik):
                data = raport.filedata
        if not data:
            self.error(_("Raportit ei leitud"))
        elif _format == 'html':
            self.c.tagasiside_html = data.decode('utf-8')
        else:
            filename = raport.filename
            mimetype = raport.mimetype
            return utils.download(data, filename, mimetype)

        return self.render_to_response(self._ITEM_TEMPLATE)
                
