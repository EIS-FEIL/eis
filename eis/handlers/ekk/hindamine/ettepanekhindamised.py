from eis.lib.baseresource import *
_ = i18n._
from eis.lib.block import BlockController
from eis.lib.resultentry import ResultEntry

from .eksperthindamised import EksperthindamisedController

class EttepanekhindamisedController(EksperthindamisedController):
    """Hindamisjuht sisestab vaide korral hindamisel punktide ettepanekud ühe ülesande küsimuste kohta
    """
    _permission = 'eksperthindamine'
    _EDIT_TEMPLATE = 'ekk/hindamine/ettepanek.hindamine.mako'
    _ITEM_FORM = forms.avalik.hindamine.KHindamineForm

    def _get_ylesanded(self):
        c = self.c
        c.testiylesanded_id = [c.testiylesanne.id]

    def _update(self, item):
        if not self.c.olen_hindamisjuht:
            self.error(_("Kasutaja pole hindamisjuht"))
            return self._redirect('show')

        hindamine = self._give_hindamine()
        if not hindamine:
            self.error(_("Tööd ei saa enam hinnata"))
            return self._redirect('edit')
        
        self._save_hindamine(hindamine, False, False)
        return self._after_update()

    def _after_update(self):
        url = self.url('hindamine_edit_ettepanek', 
                       toimumisaeg_id=self.c.toimumisaeg.id, 
                       id=self.c.sooritus.id)
        return HTTPFound(location=url)

    def _get_tab_urls(self):
        c = self.c
        h = self.h
        def f_submit_url(ty_id):
            return h.url('hindamine_ettepanek_hindamine',
                         hindamiskogum_id=c.hindamiskogum.id, 
                         toimumisaeg_id=c.toimumisaeg.id,
                         sooritus_id=c.sooritus.id, id=ty_id)

        c.f_submit_url = f_submit_url

    def _edit_kokku(self, id):
        # sooritus.ylesanneteta_tulemus=true korral testiosa kogupallide sisestamine 
        return self.render_to_response('ekk/hindamine/ettepanek.ylesanneteta_kokku.mako')

    def _update_kokku(self, item):
        # sooritus.ylesanneteta_tulemus=true korral testiosa kogupallide salvestamine
        c = self.c
        if c.sooritus.ylesanneteta_tulemus and c.olen_hindamisjuht:
            # ylesanneteta_tulemus
            self.form = Form(self.request, schema=self._ITEM_FORM)
            if self.form.validate():
                c.sooritus.pallid_peale_vaiet = self.form.data.get('kokku_pallid')
                c.sooritus.hindamine_staatus = const.H_STAATUS_HINNATUD
                for holek in c.sooritus.hindamisolekud:
                    hindamine = holek.get_hindamine(const.HINDAJA5)
                    if hindamine:
                        hindamine.staatus = const.H_STAATUS_HINNATUD
                model.Session.commit()

        return HTTPFound(location=self.url('hindamine_edit_ettepanek', 
                                           toimumisaeg_id=c.toimumisaeg.id, 
                                           id=c.sooritus.id))

    def __before__(self):
        c = self.c
        super().__before__()
        c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        c.testiosa = c.toimumisaeg.testiosa
        c.test = c.testiosa.test
        c.ettepanek = True

        ty_id = self.request.matchdict.get('id') or self.request.matchdict.get('ty_id')
        # showtask korral on ty_id, mitte id
        c.testiylesanne = model.Testiylesanne.get(ty_id)
        c.ylesandevastus = c.sooritus.get_ylesandevastus(c.testiylesanne.id)
        c.vy = c.ylesandevastus and c.ylesandevastus.valitudylesanne
        # c.ylesandevastus ei pruugi olla siis, kui on c.sooritus.ylesanneteta_tulemus
        if c.testiosa.lotv:
            c.hindamiskogum = c.vy.hindamiskogum
        else:
            c.hindamiskogum = c.testiylesanne.hindamiskogum
        
    def _kas_ekspert(self):
        c = self.c
        c.sooritaja = c.sooritus.sooritaja
        vaie = c.sooritaja.vaie
        if vaie and not vaie.otsus_dok and \
               vaie.staatus in (const.V_STAATUS_MENETLEMISEL, const.V_STAATUS_ETTEPANDUD):
            c.olen_hindamisjuht = c.user.has_group(const.GRUPP_T_HINDAMISJUHT, c.test) \
                or c.user.has_group(const.GRUPP_HINDAMISJUHT, aine_kood=c.test.aine_kood)
    
    def _perm_params(self):
        if self.c.is_edit and not self.c.olen_hindamisjuht:
            log.debug(_(u"Kasutaja pole hindamisjuht"))
            return False

        test = self.c.testiosa.test
        return {'aine': test.aine_kood,
                'testiliik': test.testiliik_kood,
                }
