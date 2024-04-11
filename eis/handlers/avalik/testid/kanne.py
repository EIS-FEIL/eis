from eis.lib.baseresource import *
import eis.handlers.ekk.otsingud.kohateated as kt
_ = i18n._
log = logging.getLogger(__name__)

class KanneController(BaseResourceController):
    """Registreerimisnimekirja kande vaatamine"""
    _permission = 'omanimekirjad'
    _MODEL = model.Sooritaja
    _EDIT_TEMPLATE = 'avalik/testid/nimekiri.kanne.mako' 
    _ITEM_FORM = forms.avalik.testid.KanneForm
    _actions = 'show,update,edit,delete'

    def _delete(self, item):
        if item.muutmatu:
            self.error(_("Seda registreeringut ei saa enam tühistada"))
            return self._redirect('show', id=item.id)            
        elif item.staatus >= const.S_STAATUS_POOLELI:
            self.error(_('Sooritamist on alustatud, ei saa enam tühistada'))
            return self._redirect('show', id=item.id)
        else:
            item.logi_pohjus = self.request.params.get('pohjus')            
            kt.send_tyhteade(self, item.kasutaja, item)            
            item.tyhista()
            model.Session.flush()
            item.delete()
            model.Session.commit()
            self.success(_('Registreering on tühistatud!'))

    def __before__(self):
        self.c.test_id = self.request.matchdict.get('test_id')
        self.c.test = model.Test.get(self.c.test_id)
        self.c.testiruum_id = self.request.matchdict.get('testiruum_id')
        nimekiri_id = self.request.matchdict.get('nimekiri_id')
        self.c.nimekiri = model.Nimekiri.get(nimekiri_id)
        sooritaja_id = self.request.matchdict.get('id')
        self.c.sooritaja = model.Sooritaja.get(sooritaja_id)
        
    def _perm_params(self):
        return {'obj':self.c.nimekiri}


