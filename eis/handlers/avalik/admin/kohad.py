# -*- coding: utf-8 -*- 
from eis.lib.baseresource import *
_ = i18n._
from eis.handlers.admin import kohad
log = logging.getLogger(__name__)

class KohadController(kohad.KohadController):
    "Soorituskoha andmete vaatamine/muutmine soorituskoha administraatori poolt"

    _permission = 'avalikadmin'
    _EDIT_TEMPLATE = 'avalik/admin/koht.mako'
    
    def index(self):
        # soorituskoha otsingut ei ole, 
        # suunatakse kohe kasutaja soorituskoha lehele
        return self._redirect('show', id=self.c.user.koht_id)

    def _show_d(self):
        id = self.c.user.koht_id
        self.c.item = self._MODEL.get(id)
        self._show(self.c.item)
        return self.response_dict

    def __before__(self):
        koht_id = self.request.matchdict.get('id')
        if koht_id:
            if int(koht_id) != self.c.user.koht_id:
                raise NotAuthorizedException('avaleht', message=_("Puudub ligipääsuõigus"))            
            item = model.Koht.get(koht_id)
            self.c.can_edit = item.haldusoigus

    def _update(self, item, lang=None):
        # omistame vormilt saadud andmed
        if item.haldusoigus:
            item.from_form(self.form.data, self._PREFIX, lang=lang)
            item.set_name()
            model.Aadress.adr_from_form(item, self.form.data, 'a_')        
            
    def _has_permission(self):
        if not self.c.can_edit:
            action = self.c.action
            if action in ('edit', 'update','delete','create'):
                return False
        return BaseController._has_permission(self)
