# -*- coding: utf-8 -*- 

from eis.lib.baseresource import *
from eis.lib.basegrid import *
_ = i18n._

log = logging.getLogger(__name__)

class SisufailController(BaseResourceController):
    """Ülesande sisu"""

    _permission = 'ylesanded'
    _MODEL = model.Sisuobjekt
    _actions = 'show,download,delete'

    def delete(self):
        """DELETE /admin_ITEMS/id: Delete an existing item"""
        parent_id = self.c.item.parent_id
        if self.c.item.sisuplokk_id:
            after_delete = 'ylesanne_edit_sisuplokk'
            ylesanne_id = self.c.item.sisuplokk.ylesanne_id
        else:
            after_delete = 'ylesanded_failid'
            ylesanne_id = None
        self.c.item.delete()
        self.success(_("Andmed on kustutatud"))
        model.Session.commit()
        if ylesanne_id:
            return HTTPFound(location=self.url(after_delete, id=parent_id, ylesanne_id=ylesanne_id))
        else:
            return HTTPFound(location=self.url(after_delete, id=parent_id))

    def _download(self, id, format):
        """Näita faili"""
        item = self.c.item
        if not item:
            raise NotFound('Kirjet ei leitud')
        lang = self.params_lang()        

        item_tr = item.tran(lang)
        filepath = item_tr.path_for_response
        last_modified = item_tr.modified

        return utils.cache_download(self.request,
                                    filepath,
                                    item.filename, 
                                    item.mimetype,
                                    inline=True,
                                    last_modified=last_modified)

    def __before__(self):
        obj_id = self.request.matchdict.get('id')
        self.c.item = self._MODEL.get(obj_id)

    def _perm_params(self):
        return {'obj':self.c.item and self.c.item.sisuplokk.ylesanne or None}
