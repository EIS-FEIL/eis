# -*- coding: utf-8 -*- 
import os.path

from eis.lib.base import *
_ = i18n._
from eis.lib.block import BlockController

log = logging.getLogger(__name__)

class FailidController(BaseController):
    _permission = 'ylesanded'

    def files(self):
        """Näitame faili, mille leiame nime järgi ülesandefailide seast
        """
        ylesanne_id = self.request.matchdict.get('ylesanne_id')
        filename = self.request.matchdict.get('filename')
        item = model.Ylesandefail.get_by_item(ylesanne_id, filename)
        if not item:
            log.info('Ei leitud ylesandefaili, ylesanne_id=%s, %s' % (ylesanne_id, filename))
            raise NotFound('Kirjet ei leitud')            
        filedata = item.filedata
        filename = item.filename
        mimetype = item.mimetype

        return utils.download(filedata, filename, mimetype)

    def __before__(self):
        self.c.ylesanne = model.Ylesanne.get(self.request.matchdict.get('id'))

    def _perm_params(self):
        return {'obj':self.c.ylesanne}
