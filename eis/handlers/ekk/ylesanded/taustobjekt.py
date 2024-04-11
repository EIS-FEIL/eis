from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class TaustobjektController(BaseResourceController):
    """Uue faili salvestamine"""

    _permission = 'ylesanded'
    _MODEL = model.Taustobjekt
    _actions = 'create,update'

    def _create(self, **kw):
        block = model.Sisuplokk.get(self.c.sisuplokk_id)
        item = block.taustobjekt
        if not item:
            item = model.Taustobjekt(sisuplokk_id=block.id)
        return self._update(item)

    def _update(self, item):
        lang = self.params_lang() or None
        value = self.request.params.get('file')
        res = {}
        if value != None and value != b'' and value.file:
            tr_item = lang and item.give_tran(lang) or item
            tr_item.from_form_value('filedata', value)
            model.Session.flush()
            if not lang:
                self._uniq_filename(item)

            model.Session.commit()
            res['obj_id'] = item.id
            res['filename'] = item.filename
        else:
            res['error'] = _("Fail puudub")
        return Response(json_body=res)

    def _uniq_filename(self, item):
        # kontrollime, et failinimi on ylesande piires unikaalne, 
        # et sellele saaks images/filename kaudu viidata
        filename = item.filename
        li = filename.rsplit('.', 1)
        if len(li) == 1:
            basename = filename
            ext = ''
        else:
            basename, ext = li
            ext = '.' + ext
            
        q = (model.Session.query(model.Sisuobjekt.filename)
             .join(model.Sisuobjekt.sisuplokk)
             .filter(model.Sisuplokk.ylesanne_id==self.c.ylesanne.id)
             .filter(model.Sisuobjekt.id != item.id))
        filenames = [s for s, in q.all()]
        if filename in filenames:
            for n in range(1000):
                filename = '%s%s%s' % (basename, n, ext)
                if filename not in filenames:
                    item.filename = filename
                    break
 
    def __before__(self):
        ylesanne_id = self.request.matchdict.get('ylesanne_id')
        self.c.ylesanne = model.Ylesanne.get(ylesanne_id)
        self.c.sisuplokk_id = self.request.matchdict.get('sisuplokk_id')
        self.c.sisuplokk = model.Sisuplokk.get(self.c.sisuplokk_id)
        obj_id = self.request.matchdict.get('id')
        if obj_id:
            self.c.item = model.Sisuobjekt.get(obj_id)

    def _perm_params(self):
        return {'obj':self.c.ylesanne}
