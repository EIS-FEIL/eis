"Küsimuse hindamismaatriksi täiendamine sooritajate antud vastustega"
from eis.lib.baseresource import *
_ = i18n._
from eis.handlers.ekk.hindamine.analyysmaatriksid import AnalyysmaatriksidController as amxController
log = logging.getLogger(__name__)

class AnalyysmaatriksidController(amxController):
    _permission = 'ekk-testid'

    _MODEL = model.Hindamismaatriks

    def _set_list_url(self):
        c = self.c
        c.is_sp_analysis = True
        c.is_edit = False

        c.hm_list_url = self.url_current('index', test_id=c.test.id, kysimus_id=c.kysimus.id, maatriks=c.maatriks, prefix=c.prefix)
   

    def _has_permission(self):
        # leitakse, kas on õigus antud tegevusele,
        # ning seatakse c.can_edit_hm - kas on muutmisõigus

        perm = self._permission
        test = self.c.test
        can_show = self.c.user.has_permission(perm, const.BT_SHOW, obj=test)
        can_edit_hm = self._can_edit_hm(self.c.user, test, self.c.kysimus)

        self.c.can_edit_hm = can_edit_hm
        if self._is_modify():
            return can_edit_hm
        else:
            return can_show

    def _perm_params(self):
        return {'obj': self.c.test}
    
    def _can_edit_hm(self, user, test, kysimus):
        perm = 'vastusteanalyys'
        can_show = user.has_permission(perm, const.BT_SHOW, obj=test)
        can_edit_hm = False
        if user.has_permission(perm, const.BT_UPDATE, obj=test):
            # kasutajal on rolli kaudu yldine muutmise õigus
            can_edit_hm = True
        elif can_show:
            # kui kasutajal on testi koostaja grupp
            # ja samal ajal ylesande koostaja grupp,
            # siis ta võib maatriksit muuta
            if user.has_group(const.GRUPP_T_KOOSTAJA, test):
                ylesanne = kysimus.sisuplokk.ylesanne
                if user.has_group(const.GRUPP_Y_KOOSTAJA, ylesanne):
                    can_edit_hm = True
        return can_edit_hm
    
    def __before__(self):
        c = self.c
        c.test_id = self.request.matchdict.get('test_id')
        c.test = model.Test.get(c.test_id)
        kysimus_id = self.request.matchdict.get('kysimus_id')
        c.kysimus = model.Kysimus.get(kysimus_id)
        c.maatriks = self.request.params.get('maatriks') or 1
        c.prefix = self.request.params.get('prefix')
