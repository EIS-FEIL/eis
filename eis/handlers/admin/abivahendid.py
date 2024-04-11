from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class AbivahendidController(BaseResourceController):
    _permission = 'klassifikaatorid'
    _MODEL = model.Abivahend
    _EDIT_TEMPLATE = 'admin/abivahend.mako'
    _INDEX_TEMPLATE = 'admin/abivahendid.mako'
    _LIST_TEMPLATE = 'admin/abivahendid_list.mako'
    _DEFAULT_SORT = 'abivahend.jrk'
    _actions = 'index,new,create,edit,update,delete,show'
    _index_after_create = True
    _no_search_default = True

    @property
    def _ITEM_FORM(self):
        if self.c.lang:
            return forms.admin.TranAbivahendForm
        else:
            return forms.admin.AbivahendForm
    
    def _update(self, item, lang=None):
        super()._update(item, self.c.lang)

    def _error_update(self):
        extra_info = self._edit_d()
        if isinstance(extra_info, (HTTPFound, Response)):
            return extra_info    
        html = self.form.render(self._EDIT_TEMPLATE, extra_info=extra_info)
        return Response(html)
        
    def _show_vahend(self, id):
        "Abivahendi kuvamine nii, nagu lahendaja näeb"
        self.c.item = model.Abivahend.get(id)
        template = '/avalik/lahendamine/abivahend.mako'
        return self.render_to_response(template)

    def __before__(self):
        c = self.c
        c.lang = self.params_lang()
        if c.lang == const.LANG_ET:
            c.lang = ''
        super().__before__()
