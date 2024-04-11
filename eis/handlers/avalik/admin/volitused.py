from eis.lib.baseresource import *
from eis.lib.xtee import ehis
log = logging.getLogger(__name__)
_ = i18n._

class VolitusedController(BaseResourceController):
    _permission = 'paroolid'
    _MODEL = model.Kasutaja
    _SEARCH_FORM = forms.avalik.admin.VolitusForm
    _ITEM_FORM = forms.avalik.admin.VolitusForm
    _INDEX_TEMPLATE = 'avalik/admin/volitused.otsing.mako' # otsinguvormi mall
    _LIST_TEMPLATE = 'avalik/admin/volitused.mako'
    _EDIT_TEMPLATE = 'avalik/admin/volitused.mako'
    _get_is_readonly = False
    
    def _search(self, q):
        """Isikukoodi küsimise vormi kuvamine
        või isikukoodi järgi isiku otsimine
        """
        self.c.item = self._give_kasutaja()

    def _give_kasutaja(self):
        # leiame kasutaja, kelle andmete vaatamise õigust jagame
        self.c.isikukood = self.form.data.get('isikukood')        
        if self.c.isikukood:
            kasutaja = None
            usp = eis.forms.validators.IsikukoodP(self.c.isikukood)
            if usp.valid:
                kasutaja = usp.get(model.Kasutaja, write=True)
                if not kasutaja and usp.isikukood:
                    opilane = model.Opilane.get_by_ik(usp.isikukood)
                    if opilane:
                        kasutaja = opilane.give_kasutaja()
                        model.Session.commit()
                if not kasutaja and self.request.is_ext() and usp.isikukood_ee:
                    # otsime RRist...
                    kasutaja = xtee.set_rr_pohiandmed(self, None, usp.isikukood_ee)
                    if kasutaja:
                        model.Session.commit()
                elif not kasutaja:
                    self.error(_("Antud isikukoodiga kasutajat ei leitud"))
            else:
                self.error(_("Vigane isikukood"))
            return kasutaja
        return None
    
    def _showlist(self):
        template = self.c.item and self._LIST_TEMPLATE or self._INDEX_TEMPLATE
        assert template is not None, 'Mall puudub'
        return self.render_to_response(template)

    def delete(self):
        id = self.request.matchdict.get('id')
        item = model.Volitus.get(id)
        if not item.tyhistatud:
            item.tyhistatud = datetime.now()
            item.tyhistaja_kasutaja_id = self.c.user.id
            model.Session.commit()
            self.success()
        return HTTPFound(location=self.url('admin_edit_volitus', id=item.volitatu_kasutaja_id))

    def _update(self, item):
        kasutaja = self._give_kasutaja()
        if kasutaja and kasutaja.id == item.id:
            self.error(_("Kasutajale endale pole enda andmete vaatamiseks vaja volitust anda"))
        elif kasutaja:
            opilane = self._uuenda_opilane(kasutaja)
            if not opilane:
                self.error(_("Valitud isik ei ole õpilane"))
            elif opilane.koht_id != self.c.user.koht_id:
                self.error(_("Valitud isik õpib teises koolis"))
            else:
                kehtib_kuni = self.form.data.get('kehtib_kuni') or const.MAX_DATE
                dt_kehtib_kuni = datetime.combine(kehtib_kuni, time(0,0))
                qv = (model.Volitus.query
                      .filter(model.Volitus.volitatu_kasutaja_id==item.id)
                      .filter(model.Volitus.opilane_kasutaja_id==kasutaja.id)
                      .filter(model.Volitus.tyhistatud==None)
                      .filter(model.Volitus.kehtib_kuni >= kehtib_kuni))
                if qv.count() > 0:
                    self.error(_("Volitus juba kehtib"))
                else:
                    model.Volitus(volitatu_kasutaja_id=item.id,
                                  opilane_kasutaja_id=kasutaja.id,
                                  andja_kasutaja_id=self.c.user.id,
                                  kehtib_alates=datetime.now(),
                                  kehtib_kuni=kehtib_kuni)

    def _uuenda_opilane(self, kasutaja):
        isikukood = kasutaja.isikukood
        if isikukood:
            err = ehis.uuenda_opilased(self, [isikukood])
            if err:
                self.error(err)
                return False
            model.Session.commit()
            opilane = model.Opilane.get_by_ik(isikukood)
            return opilane
