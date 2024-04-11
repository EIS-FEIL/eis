from eis.lib.baseresource import *
_ = i18n._
from eis.lib.basegrid import BaseGridController

log = logging.getLogger(__name__)

class RuumidController(BaseResourceController):
    _permission = 'kohad'
    _MODEL = model.Ruum
    _ITEM_FORM = forms.admin.RuumidForm
    _INDEX_TEMPLATE = 'admin/ruumid.mako' # otsinguvormi mall
    _EDIT_TEMPLATE = 'admin/ruumid.mako' # muutmisvormi mall
    #_LIST_TEMPLATE = '/admin/ruumid.mako'
    
    def _create(self):
        self.c.koht.from_form(self.form.data, self._PREFIX)
        ruumid = self.form.data['r']

        class RuumGridController(BaseGridController):
            def can_delete(self, rcd):
                return not rcd.in_use
            
        RuumGridController(self.c.koht.ruumid, model.Ruum).save(ruumid)
        self.c.koht.update_testiruumid()
        for r in self.c.koht.ruumid:
            r.update_testiruumid()
        return self.c.koht

    def _after_update(self, id):
        """Mida teha peale õnnestunud salvestamist
        """
        self.success()
        return HTTPFound(location=self.url('admin_koht_ruumid', koht_id=self.c.koht.id))

    def _perm_obj(self):
        return {'piirkond_id':self.c.koht.piirkond_id}

    def __before__(self):
        self.c.koht = model.Koht.get(self.request.matchdict.get('koht_id'))
        self.c.can_edit = self.c.user.has_permission('kohad', const.BT_UPDATE, piirkond_id=self.c.koht.piirkond_id)
        if not self.c.can_edit:
            self.c.is_edit = False
