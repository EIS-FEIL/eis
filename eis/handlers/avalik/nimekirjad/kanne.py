from eis.lib.baseresource import *
import eis.handlers.ekk.otsingud.kohateated as kt
_ = i18n._

log = logging.getLogger(__name__)

class KanneController(BaseResourceController):
    """Registreerimisnimekirja kande vaatamine"""
    _permission = 'nimekirjad'
    _MODEL = model.Sooritaja
    _EDIT_TEMPLATE = 'avalik/nimekirjad/kanne.mako' 
    _ITEM_FORM = forms.avalik.testid.KanneForm
    _actions = 'edit,show,update,delete'

    def _delete(self, item):
        staatus = item.staatus
        if item.muutmatu:
            self.error(_("Seda registreeringut ei saa enam tühistada"))
            return self._redirect('show', id=item.id)            
        elif staatus >= const.S_STAATUS_POOLELI:
            self.error(_('Sooritamist on alustatud, ei saa enam tühistada'))
            return self._redirect('show', id=item.id)
        else:
            koht_id = self.c.user.koht_id
            testiliik = item.test.testiliik_kood
            if not item.kool_voib_tyhistada(koht_id, testiliik):
                self.error(_("Kool ei saa seda registreeringut tühistada"))
                return self._redirect('show', id=item.id)                

            item.logi_pohjus = self.request.params.get('pohjus')            
            kt.send_tyhteade(self, item.kasutaja, item)            
            item.tyhista()
            if staatus == const.S_STAATUS_REGAMATA:
                model.Session.flush()
                item.delete()
            model.Session.commit()
            self.success(_('Registreering on tühistatud!'))

    def _after_delete(self, parent_id=None):
        url = self.h.url('nimekirjad_testimiskord_korrasooritajad', testimiskord_id=self.c.testimiskord_id)
        return HTTPFound(location=url)
            
    def __before__(self):
        c = self.c
        c.testimiskord_id = self.request.matchdict.get('testimiskord_id')
        c.testimiskord = model.Testimiskord.get(c.testimiskord_id)
        id = self.request.matchdict.get('id')
        c.item = model.Sooritaja.get(id)
        
    def _has_permission(self):
        rc = super()._has_permission()
        if rc:
            # lisaks testimiskorra õigusele kontrollime, et on oma kooli õpilane
            perm_bit = self._get_perm_bit()            
            rc = self.c.user.has_permission('regikuitk', perm_bit, self.c.item)
        return rc
        
    def _perm_params(self):
        return {'obj':self.c.testimiskord}


