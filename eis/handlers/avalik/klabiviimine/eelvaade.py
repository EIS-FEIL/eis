from eis.lib.baseresource import *
from eis.handlers.ekk.testid import eelvaade

log = logging.getLogger(__name__)

class EelvaadeController(eelvaade.EelvaadeController):
    """Testi sooritamise eelvaade testi administraatorile
    """
    _permission = 'testiadmin'    
    _EDIT_TEMPLATE = 'avalik/klabiviimine/eelvaade.mako'
    _actions = 'index,new,create,show,update,edit,download,delete' # võimalikud tegevused

    def _q_komplektid(self):
        "Kasutatavate komplektide päring"
        toimumisaeg_id = self._get_toimumisaeg().id
        q = (model.SessionR.query(model.Komplekt.id, model.Komplekt.tahis)
             .filter(model.Komplekt.staatus==const.K_STAATUS_KINNITATUD)
             .join((model.Toimumisaeg_komplekt,
                    sa.and_(model.Toimumisaeg_komplekt.komplekt_id==model.Komplekt.id,
                            model.Toimumisaeg_komplekt.toimumisaeg_id==toimumisaeg_id)))
             )
        return q
    
    def _url_out(self):
        "URL, mida kasutatakse eelvaatest väljumisel"
        c = self.c
        return self.url('klabiviimine_edit_toimumisaeg', id=c.testiruum.id)

    def _get_toimumisaeg(self):
        c = self.c
        return c.toimumisaeg
        
    def __before__(self):       
        c = self.c
        c.testiruum_id = self.request.matchdict.get('testiruum_id')
        c.testiruum = model.Testiruum.get(c.testiruum_id)
        c.toimumisaeg = c.testiruum.testikoht.toimumisaeg
        c.avalik = True
        eelvaade.EelvaadeController.__before__(self)
        c.testiosa = c.toimumisaeg.testiosa
        c.testiosa_id = c.testiosa.id
            
    def _perm_params(self):
        if not self.c.toimumisaeg.eelvaade_admin:
            # administraatoril pole lubatud eelvaadet vaadata
            return False
        q = (model.SessionR.query(sa.func.count(model.Sooritus.id))
             .filter_by(testiruum_id=self.c.testiruum_id)
             .filter(model.Sooritus.staatus.in_((const.S_STAATUS_POOLELI,
                                                 const.S_STAATUS_TEHTUD,
                                                 const.S_STAATUS_KATKESTATUD)))
             )
        if q.scalar() == 0:
            # administraator ei või eelvaadet vaadata enne, kui mõni on alustanud sooritamist
            return False
        # kontrollida testi läbiviimisõigus selles kohas
        return {'obj':self.c.testiruum}
