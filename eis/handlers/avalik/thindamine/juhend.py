# -*- coding: utf-8 -*- 
"Testi ülesande hindamisjuhendi ja hindamisjuhi küsimuste näitamine kirjalikule hindajale"

from eis.lib.baseresource import *
_ = i18n._
from .toohindamine import get_tab_urls
log = logging.getLogger(__name__)

class JuhendController(BaseResourceController):
    _permission = 'omanimekirjad'
    #_get_is_readonly = False
    _actions = 'index,downloadfile'
    _INDEX_TEMPLATE = 'avalik/khindamine/hindamine_r.juhend.mako'     

    def _index_d(self):
        get_tab_urls(self, self.c)
        return self.response_dict

    # def download(self):
    #     """Näita faili
    #     """
    #     id = self.request.matchdict.get('id')
    #     ylesandefail_id = self.request.params.get('ylesandefail_id')
    #     format = self.request.matchdict.get('format')
    #     item = model.Hindamisobjekt.get(ylesandefail_id)
    #     if not item:
    #         raise NotFound('Kirjet ei leitud')
    #     assert item.ylesanne_id == c.vy.ylesanne_id, _("Vale ülesanne")
    #     return utils.download(item.filedata, item.filename, item.mimetype)

    def downloadfile(self):
        """Näita faili
        """
        ylesandefail_id = self.request.matchdict.get('file_id')
        format = self.request.matchdict.get('format')
        item = model.Hindamisobjekt.get(ylesandefail_id)
        if not item:
            raise NotFound('Kirjet ei leitud')
        assert item.ylesanne_id == self.c.vy.ylesanne_id, _("Vale ülesanne")
        return utils.download(item.filedata, item.filename, item.mimetype)

    def __before__(self):
        id = self.request.matchdict.get('vy_id')
        c = self.c
        c.vy = model.Valitudylesanne.get(id)
        c.ylesanne = c.vy.ylesanne
        c.lang = self.params_lang()
        c.indlg = self.request.params.get('indlg')
        c.testiruum_id = self.request.matchdict.get('testiruum_id')
        test_id = self.request.matchdict.get('test_id')
        c.test = model.Test.get(test_id)
