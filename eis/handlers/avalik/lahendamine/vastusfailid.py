# -*- coding: utf-8 -*- 

import os.path
import urllib.request, urllib.parse, urllib.error

from eis.lib.baseresource import *
from eis.s3file import s3file_get

_ = i18n._
from eis.lib.block import BlockController

log = logging.getLogger(__name__)

class VastusfailidController(BaseController):
    _authorize = False
    _actions = 'download'

    def download(self):
        ks_id = self.request.matchdict.get('id')
        yv_id = self.request.matchdict.get('uuid')
        format = self.request.matchdict.get('format')
        fileversion = self.request.matchdict.get('fileversion')
        if fileversion:
            filedata = self._get_filedata_s3(ks_id, fileversion, format)
        else:
            filedata = self._get_filedata_ks(ks_id, yv_id)

        if not filedata:
            return utils.download('Kirjet ei leitud', 'err.txt', 'text/plain')

        # päris failinime ei või hindajale kuvada, sest lahendaja võis sinna panna oma nime
        filename = 'ks%s.%s' % (ks_id, format)
        mimetype = model.guess_mimetype(filename)
        model.Session.rollback()
        return utils.download(filedata, filename, mimetype)
            
    def _get_filedata_ks(self, ks_id, yv_id):
        q = (model.Session.query(model.Kvsisu)
             .join(model.Kvsisu.kysimusevastus)
             .join(model.Kysimusevastus.ylesandevastus)
             .filter(model.Kvsisu.id==ks_id)
             .filter(model.Ylesandevastus.id==yv_id)
             .filter(model.Ylesandevastus.sooritus_id==None)
             )
        item = q.first()
        return item and item.filedata

    def _get_filedata_s3(self, ks_id, fileversion, format):
        ks = NewItem(id=ks_id, fileversion=fileversion, format=format)
        return s3file_get('kvsisu', ks)
