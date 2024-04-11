"Testi ülesande hindamisjuhendi ja hindamisjuhi küsimuste näitamine kirjalikule hindajale"

from eis.lib.baseresource import *
_ = i18n._
from .hkhindamine import get_tab_urls
log = logging.getLogger(__name__)

class HindamiskysimusedController(BaseResourceController):
    _permission = 'khindamine'
    _EDIT_TEMPLATE = 'avalik/khindamine/hindamiskysimus.mako'
    _INDEX_TEMPLATE = 'avalik/khindamine/hindamine_r.hindamiskysimused.mako'
    _MODEL = model.Hindamiskysimus
    _actions = 'index,new,create' 

    def _index_d(self):
        self._get_tab_urls()        
        return self.response_dict

    def _get_tab_urls(self):
        get_tab_urls(self, self.c)
    
    def create(self):
        """Hindamiskysimuse salvestamine
        """
        c = self.c
        kysimus = self.request.params.get('kysimus')
        if kysimus:
            item = model.Hindamiskysimus(kysimus=kysimus,
                                        kysija_kasutaja_id=c.user.id,
                                        ylesanne_id=c.ylesanne.id,
                                        kysimisaeg=datetime.now())
            model.Session.commit()
            kysimus_hindamisjuhile(self, item, c.test, c.toimumisaeg)
        return self._redirect(action='index', indlg=c.indlg)

    def __before__(self):
        c = self.c
        vy_id = self.request.matchdict.get('vy_id')
        c.vy = model.Valitudylesanne.get(vy_id)
        c.ylesanne = c.vy.ylesanne
        
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        testiosa = c.toimumisaeg.testiosa
        c.test = testiosa.test
        if testiosa.lotv:
            c.hindamiskogum = c.vy.hindamiskogum
        else:
            c.hindamiskogum = c.vy.testiylesanne.hindamiskogum
        c.lang = self.params_lang()
        c.indlg = self.request.params.get('indlg')

    def _has_permission(self):
        # suulise hindamise korral on antud c.testiruum
        # kirjaliku hindamise korral on antud c.toimumisaeg
        c = self.c
        hk_id = c.hindamiskogum.id
        c.hindaja = c.toimumisaeg.get_hindaja(c.user.id, hindamiskogum_id=hk_id)
        return self.c.hindaja is not None

def kysimus_hindamisjuhile(handler, item, test, toimumisaeg):
    """Hindamisjuhile saadetakse teade, et esitati uus kysimus
    """
    today = date.today()
    q = (model.Session.query(model.Kasutaja.id,
                             model.Kasutaja.epost,
                             model.Kasutaja.nimi)
         .filter(model.Kasutaja.epost!=None)
         .filter(model.Kasutaja.epost!='')
         .join(model.Testiisik.kasutaja)
         .filter(model.Testiisik.kasutajagrupp_id==const.GRUPP_T_HINDAMISJUHT)
         .filter(model.Testiisik.test_id==test.id)
         .filter(model.Testiisik.kehtib_alates<=today)
         .filter(model.Testiisik.kehtib_kuni>=today)
         )
    li_epost = []
    li_nimi = []
    kasutajad = list(q.all())
    li_epost = [r[1] for r in kasutajad]
    li_nimi = [r[2] for r in kasutajad]
    if len(li_epost):
        to = li_epost
        data = {'test_nimi': test.nimi,
                'user_nimi': handler.c.user.fullname,
                'ta_tahised': toimumisaeg.tahised,
                'kysimus': item
                }
        subject, body = handler.render_mail('mail/hindamiskysimus.hindamisjuhile.mako', data)
        body = Mailer.replace_newline(body)
        if not Mailer(handler).send(to, subject, body):
            kiri = model.Kiri(tyyp=model.Kiri.TYYP_MUU,
                              sisu=body,
                              teema=subject,
                              teatekanal=const.TEATEKANAL_EPOST)
            for k_id, epost, nimi in kasutajad:
                model.Kirjasaaja(kiri=kiri, kasutaja_id=k_id, epost=epost)
            model.Session.commit()
