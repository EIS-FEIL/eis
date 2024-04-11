from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class SkannfailController(BaseResourceController):
    """Eksamitööga tutvumise taotluse esitamine
    """
    _permission = 'sooritamine'
    _MODEL = model.Sooritus
    _actions = 'download'
    
    def _download(self, id, format=None):
        """Näita faili"""
        item = self._MODEL.get(id)
        if not item:
            raise NotFound('Ei leitud')
        if not self.c.user.get_kasutaja().on_volitatud(item.sooritaja.kasutaja_id):
            raise NotFound('Ei leitud')            

        sf = item.skannfail
        if not item:
            raise NotFound('Dokumenti ei leitud')

        filename = sf.filename
        filedata = sf.filedata
        mimetype = sf.mimetype

        if not filedata:
            raise NotFound('Dokumenti ei leitud')
        return utils.download(filedata, filename, mimetype)
