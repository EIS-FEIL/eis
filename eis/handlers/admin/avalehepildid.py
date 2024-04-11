from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class AvalehepildidController(BaseResourceController):

    _permission = 'olulineinfo'
    _ITEM_FORM = forms.admin.AvalehepiltForm
    _INDEX_TEMPLATE = 'admin/avalehepildid.mako'
    _EDIT_TEMPLATE = 'admin/avalehepilt.mako'
    _MODEL = model.Avalehepilt
    _actions = 'index,edit,update'
    _index_after_create = True
    
    def _search_default(self, q):
        return self._search(q)
    
    def _search(self, q):
        c = self.c
        # praegu kehtiv pilt
        c.item = model.Avalehepilt.get_kehtiv()
        
        # tulevikus kehtivad pildid (välja arvatud vaikimisi ja jooksev pilt)
        today = date.today()
        q = (model.Session.query(model.Avalehepilt)
             .filter(model.Avalehepilt.kuni >= today)
             .filter(model.Avalehepilt.id != model.Avalehepilt.DEFAULT_ID)
             )
        if c.item:
            q = q.filter(model.Avalehepilt.id != c.item.id)
        q = q.order_by(model.Avalehepilt.alates)
        return q

    def _edit(self, item):    
        q = (model.Session.query(model.Avalehepilt)
             .order_by(model.Avalehepilt.id))
        self.c.items = [r for r in q.all()]

    def _update(self, item, lang=None):
        # omistame vormilt saadud andmed
        item.from_form(self.form.data, self._PREFIX, lang=lang)
        if not item.kuni:
            # ainult vaikimisi pildil võib lõpukpv puududa
            item.kuni = const.MAX_DATE

        if item.id != model.Avalehepilt.DEFAULT_ID:
            # kas mõni pilt teine kehtib samal ajal
            q = (model.Session.query(sa.func.count(model.Avalehepilt.id))
                .filter(model.Avalehepilt.id!=item.id)
                .filter(model.Avalehepilt.id!=model.Avalehepilt.DEFAULT_ID)
                .filter(model.Avalehepilt.alates <= item.kuni)
                .filter(model.Avalehepilt.kuni >= item.alates)
                )
            cnt = q.scalar()
            if cnt:
                raise ValidationError(self, {}, message=_("Antud ajavahemikul on vähemalt üks päev, mis kattub mõne teise pildi ajavahemikuga"))
        
    def _update_file(self, id):
        # pildifaili salvestamine
        item = model.Avalehepilt.get(id)
        value = self.request.params.get('file')
        res = {}
        rc = False
        if value != None and value != b'' and value.file:
            stream = value.file
            item.from_form_value('filedata', value)
            model.Session.flush()
            try:
                item.set_image_size(None, stream, item.filename)
            except IOError as e:
                res['error'] = _("Pole pildifail")
            else:
                model.Session.commit()
                rc = True
                res['href'] = self.url('avalehepilt', format=item.fileext, id=item.id, v=item.fileversion)                
                
        return Response(json_body=res)
        
