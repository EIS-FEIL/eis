# -*- coding: utf-8 -*- 
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class OppekavadController(BaseResourceController):
    _permission = 'kasutajad'
    _INDEX_TEMPLATE = '/admin/koht.oppekavad.mako'
    _EDIT_TEMPLATE = '/admin/koht.oppekava.mako' 
    _MODEL = model.Koolioppekava
    _ITEM_FORM = forms.admin.OppekavaForm
    
    def index(self):
        self.c.item = self.c.koht
        return self.render_to_response(self._INDEX_TEMPLATE)
    
    def _create(self):
        "Õppekava lisamine"
        oppetase_kood = self.form.data['oppetase_kood']
        kavatase_kood = self.form.data['kavatase_kood']
        q = (model.Koolioppekava.query
             .filter_by(koht_id=self.c.koht.id)
             .filter_by(oppetase_kood=oppetase_kood)
             .filter_by(kavatase_kood=kavatase_kood))
        if q.count() > 0:
            self.error(_("Selline tase on juba olemas"))
        else:
            item = model.Koolioppekava(koht_id=self.c.koht.id,
                                       oppetase_kood=oppetase_kood,
                                       kavatase_kood=kavatase_kood,
                                       on_ehisest=False)
            return item

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """        
        if not self.has_errors():
            self.success()
        return self._redirect('index')
    
    def delete(self):
        row_id = self.request.matchdict.get('id')
        item = model.Koolioppekava.get(row_id)
        if item.on_ehisest==False:
            BaseResourceController._delete(self, item)
        return self._redirect('index')
    
    def __before__(self):
        self.c.koht = model.Koht.get(self.request.matchdict.get('koht_id'))
