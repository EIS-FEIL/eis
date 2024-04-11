from eis.lib.baseresource import *
_ = i18n._
from eis.lib.blockview import BlockView
from eis.lib.resultentry import ResultEntry

from .eksperthindamised import EksperthindamisedController

class EttepanekvastusedController(EksperthindamisedController):
    """Hindamisjuht sisestab vaide korral hindamisel punktide ettepanekud ühe ülesande küsimuste kohta
    """
    _permission = 'eksperthindamine'
    _MODEL = model.Testiylesanne
    _EDIT_TEMPLATE = 'ekk/hindamine/ettepanek.vastused.mako'
    _ITEM_FORM = forms.avalik.hindamine.KHindamineForm

    def _show(self, item):
        self.c.show_tulemus = True
        self.c.prepare_correct = True
        self.c.btn_correct = True
        self.c.read_only = True

        self.c.testiosa = self.c.sooritus.testiosa
        self.c.sisestus = 1
        
        self.c.holek = self.c.sooritus.get_hindamisolek(self.c.hindamiskogum)
        self.c.hindamine = self.c.holek.get_hindamine(const.HINDAJA5)
        self.c.assessment_entry = BlockView.assessment_entry
        self.c.komplekt = self.c.holek.komplekt


    def _edit(self, item):
        self.c.testiosa = self.c.sooritus.testiosa
        self.c.sisestus = 1
        self.c.holek = self.c.sooritus.get_hindamisolek(self.c.hindamiskogum)
        self.c.hindamine = self._give_hindamine(self.c.holek)
        self.c.assessment_entry = BlockView.assessment_entry
        self.c.komplekt = self.c.holek.komplekt

    def _update(self, item):
        if not self.c.olen_hindamisjuht:
            self.error(_("Kasutaja pole hindamisjuht"))
            return self._redirect('show')
    
        lopeta = True
        test = self.c.testiosa.test
        resultentry = ResultEntry(self, None, test, self.c.testiosa)
        resultentry.ekspert_ettepanek = True
        sooritaja = self.c.sooritus.sooritaja

        compare2 = self.c.sisestus != 'p' and self.c.kahekordne_sisestamine

        # yhe hindamiskogumi hinnete salvestamine (kõik sooritused)
        hindamiskogum = self.c.hindamiskogum

        # leitakse soorituse hindamisoleku kirje antud hindamiskogumi kohta
        holek = self.c.sooritus.give_hindamisolek(hindamiskogum)
        rcd = self.form.data['hk'][0].get('hmine')
        if rcd:
            # rcd on yhe soorituse yhe hindamiskogumi yhele hindamisele vastav kirje
            # leitakse hindamisolekule vastav hindamise kirje antud sisestuse kohta
            hindamine = self._give_hindamine(holek)

            # vastuste salvestamine
            resultentry.save_hindamine(sooritaja, rcd, False, 'hk-0.hmine', self.c.sooritus, holek, self.c.testiosa, hindamine, None, False, self.c.testiylesanne.id)
            
            if not hindamine.sisestaja_kasutaja_id:
                hindamine.sisestaja_kasutaja_id = self.c.user.id

        if resultentry.errors:
            raise ValidationError(self, resultentry.errors)

        if resultentry.error_lopeta:
            # sisestamise lõpetamist takistav viga
            self.error(resultentry.error_lopeta)
            lopeta = False

        model.Session.commit()
        self._calc_sooritaja_pallid()

        return HTTPFound(location=self.url('hindamine_edit_ettepanek', 
                                           toimumisaeg_id=self.c.toimumisaeg.id, 
                                           id=self.c.sooritus.id))

    def _give_hindamine(self, holek):
        hindamine = holek.give_hindamine(const.HINDAJA5)
        hindamine.komplekt = holek.komplekt
        hindamine.flush()
        return hindamine

    def __before__(self):
        c = self.c
        c.sooritus = model.Sooritus.get(self.request.matchdict.get('sooritus_id'))
        c.sooritaja = c.sooritus.sooritaja
        c.testiylesanne = model.Testiylesanne.get(self.request.matchdict.get('id'))
        c.hindamiskogum = c.testiylesanne.hindamiskogum
        assert not c.hindamiskogum.on_hindamisprotokoll, _("Pole vastuste sisestamisega hindamiskogum")
        c.hindamine_liik = const.HINDAJA5
        c.toimumisaeg = model.Toimumisaeg.get(self.request.matchdict.get('toimumisaeg_id'))
        c.testiosa = c.toimumisaeg.testiosa
        c.test = c.testiosa.test
        c.ettepanek = True
        c.kahekordne_sisestamine = c.toimumisaeg.kahekordne_sisestamine

        if c.sooritaja.vaie and \
               c.sooritaja.vaie.staatus in (const.V_STAATUS_MENETLEMISEL, const.V_STAATUS_ETTEPANDUD) and \
               not c.sooritaja.vaie.otsus_dok:
            c.olen_hindamisjuht = c.user.has_group(const.GRUPP_T_HINDAMISJUHT, c.test) \
                or c.user.has_group(const.GRUPP_HINDAMISJUHT, aine_kood=c.test.aine_kood)
            
    def _perm_params(self):
        if self.c.is_edit and not self.c.olen_hindamisjuht:
            return False

        test = self.c.test
        return {'aine': test.aine_kood,
                'testiliik': test.testiliik_kood,
                }

    def _calc_sooritaja_pallid(self):
        # leiame testi kogutulemuse
        sooritaja_pallid = 0
        for tos in self.c.sooritaja.sooritused:
            sooritus_pallid = 0
            if tos.staatus == const.S_STAATUS_TEHTUD:
                for holek in tos.hindamisolekud:
                    hindamine = holek.get_hindamine(const.HINDAJA5)
                    if hindamine:
                        hk_pallid = hindamine.pallid or 0
                        if holek.hindamiskogum.arvutus_kood == const.ARVUTUS_SUMMA:
                            hk_pallid *= 2
                    else:
                        hk_pallid = holek.pallid or 0
                    sooritus_pallid += hk_pallid
            sooritaja_pallid += sooritus_pallid

        # lõpptulemus on ümardatud
        sooritaja_pallid = round(sooritaja_pallid)

        # võrdleme senisega
        vaie = self.c.sooritaja.vaie
        if sooritaja_pallid != vaie.pallid_parast:
            # midagi on muudetud
            if vaie.ettepanek_dok:
                # ettepanek on juba olemas
                self.notice(_("Senine ettepaneku dokument tühistati, kuna selle sisu on muudetud"))
                vaie.ettepanek_dok = None
                vaie.ettepanek_pdok = None
            vaie.pallid_parast = sooritaja_pallid
            vaie.muutus = vaie.pallid_parast - vaie.pallid_enne
            vaie.ettepanek_pohjendus = None

        model.Session.commit()
