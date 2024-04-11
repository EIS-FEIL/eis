from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class VastajadController(BaseResourceController):

    _MODEL = model.Sooritus
    _INDEX_TEMPLATE = 'avalik/shindamine/vastajad.mako' 
    _LIST_TEMPLATE = 'avalik/shindamine/vastajad_list.mako'
    _DEFAULT_SORT = 'kasutaja.nimi'
    #_ITEM_FORM = forms.avalik.admin.KSooritajadForm

    def _search(self, q):
        if self.c.testiprotokoll_id:
            q = q.filter(model.Sooritus.testiprotokoll_id==self.c.testiprotokoll_id)
        return q

    def _query(self):
        q = (model.Session.query(model.Sooritus, model.Hindamisolek)
             .filter(model.Sooritus.testiruum_id==self.c.testiruum.id)
             .join(model.Sooritus.sooritaja)
             .join(model.Sooritaja.kasutaja)
             .join(model.Sooritus.hindamisolekud)
             )

        if not self.c.eksam_kaib:
            # kui eksam enam ei käi, siis näitame ainult neid sooritusi,
            # mille hindamine pole veel läbi 
            q = q.filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
        else:
            q = q.filter(model.Sooritus.staatus>=const.S_STAATUS_REGATUD)
            
        if self.c.labiviija.liik == const.HINDAJA3:
            # kui on kolmas hindamine, siis näitame ainult neid sooritusi,
            # mis on hindajale suunatud
            q = q.filter(model.Hindamisolek.hindamised.any(\
                model.Hindamine.labiviija_id==self.c.labiviija.id))
            
        # suulisel testil peaks olema üksainus hindamiskogum
        # aga kui on mitu, siis kuvame need, muidu ei saa kasutaja aru,
        # miks sama sooritaja on mitme rea peal
        cnt_hk = len([hk for hk in self.c.toimumisaeg.testiosa.hindamiskogumid if hk.staatus])
        self.c.show_hindamiskogum = cnt_hk > 1

        return q
       
    def __before__(self):
        self.c.testiruum = model.Testiruum.get(self.request.matchdict.get('testiruum_id'))
        testikoht = self.c.testiruum.testikoht
        self.c.toimumisaeg = testikoht.toimumisaeg

        # eksam käib siis, kui toimumisprotokoll on kinnitamata
        self.c.eksam_kaib = False
        for tpakett in testikoht.testipaketid:
            toimumisprotokoll = tpakett.toimumisprotokoll
            if not toimumisprotokoll or toimumisprotokoll.staatus == const.B_STAATUS_KEHTIV:
                self.c.eksam_kaib = True
                break

        # leitakse kasutaja roll selles testiruumis
        self.c.labiviija = model.Labiviija.get_hindaja(self.c.toimumisaeg.id,
                                                       self.c.user.id,
                                                       testiruum_id=self.c.testiruum.id,
                                                       kehtiv=True)
        if not self.c.labiviija:# and not self.c.eksam_kaib:
            # hilisem läbiviija ei pruugi olla selle kohaga seotud
            self.c.labiviija = model.Labiviija.get_hindaja(self.c.toimumisaeg.id,
                                                           self.c.user.id,
                                                           testiruum_id=None,
                                                           kehtiv=True)

    def _has_permission(self):
        return self.c.labiviija is not None

