from eis.lib.baseresource import *
_ = i18n._

class EttepanekeksperdidController(BaseResourceController):
    """Ühe soorituse vaiet hindavate ekspertide valik ekspertrühmast
    """
    _permission = 'eksperthindamine'
    _MODEL = model.Sooritus
    _EDIT_TEMPLATE = 'ekk/hindamine/ettepanek.eksperdid.mako'

    def _new_d(self):
        self.c.eksperthindajad = model.Labiviija.query.\
            filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAMISEKSPERT).\
            filter(model.Labiviija.toimumisaeg_id==self.c.sooritus.toimumisaeg_id).\
            all()
        q = model.SessionR.query(model.Labivaatus.ekspert_labiviija_id).\
             distinct().\
             join(model.Labivaatus.hindamine).\
             join(model.Hindamine.hindamisolek).\
             filter(model.Hindamisolek.sooritus_id==self.c.sooritus.id)
        self.c.kasutusel = [lv_id for lv_id, in q.all()]
        return self.response_dict

    def create(self):
        if not self.c.olen_hindamisjuht:
            self.error(_("Kasutaja pole hindamisjuht"))
            return self._redirect('show')

        labiviijad_id = list(map(int, self.request.params.getall('lv_id')))
        for holek in self.c.sooritus.hindamisolekud:
            hindamine = holek.give_hindamine(const.HINDAJA5, labivaatus5=False)
            hk_labivaadanud = []
            for r in hindamine.labivaatused:
                if r.ekspert_labiviija_id in labiviijad_id:
                    hk_labivaadanud.append(r.ekspert_labiviija_id)
                    #labiviijad_id.remove(r.ekspert_labiviija_id)
                else:
                    # kustutame läbivaatuse, kui läbivaataja pole enam
                    # ekspertrühma liige ja pole läbivaatust lõpetanud
                    r.delete()
            for lv_id in labiviijad_id:
                if lv_id not in hk_labivaadanud:
                    hindamine.give_labivaatus(lv_id)

        # jätame meelde, kes on praegu aktiivne
        eksperthindajad = model.Labiviija.query.\
            filter(model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAMISEKSPERT).\
            filter(model.Labiviija.toimumisaeg_id==self.c.sooritus.toimumisaeg_id).\
            all()
        for lv in eksperthindajad:
            lv.aktiivne = lv.id in labiviijad_id

        model.Session.commit()

        return HTTPFound(location=self.url('hindamine_edit_ettepanek', 
                                           toimumisaeg_id=self.c.sooritus.toimumisaeg_id, 
                                           id=self.c.sooritus.id))


    def __before__(self):
        c = self.c
        c.sooritus = model.Sooritus.get(self.request.matchdict.get('sooritus_id'))
        c.sooritaja = c.sooritus.sooritaja
        c.testiosa = c.sooritus.testiosa
        c.test = c.sooritaja.test
        if c.sooritaja.vaie and \
               c.sooritaja.vaie.staatus in (const.V_STAATUS_MENETLEMISEL, const.V_STAATUS_ETTEPANDUD) and \
               not c.sooritaja.vaie.otsus_dok:
            c.olen_hindamisjuht = c.user.has_group(const.GRUPP_T_HINDAMISJUHT, c.test) \
                or c.user.has_group(const.GRUPP_HINDAMISJUHT, aine_kood=c.test.aine_kood)

    def _perm_params(self):
        c = self.c
        if c.is_edit and not c.olen_hindamisjuht:
            return False
        
        return {'aine': c.test.aine_kood,
                'testiliik': c.test.testiliik_kood,
                }
