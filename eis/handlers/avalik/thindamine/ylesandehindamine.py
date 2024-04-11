from eis.lib.baseresource import *
_ = i18n._
from .toohindamine import ToohindamineController, get_tab_urls
import logging
log = logging.getLogger(__name__)

class YlesandehindamineController(ToohindamineController):
    """Labiviija hindab ülesannete kaupa
    """
    _permission = 'thindamine'
    _MODEL = model.Sooritus
    _INDEX_TEMPLATE = 'avalik/thindamine/ylesandehindamine.mako'
    
    def index(self):
        c = self.c
        sooritus_id, error = _choose_e_next(self, c.test, c.testiruum, c.hindaja, c.vy)
        if error:
            self.error(error)
        if sooritus_id:
            # leiti uus töö, mida hinnata
            ty_id = c.vy.testiylesanne_id
            return self._redirect('edit', id=sooritus_id)
        else:
            # hinnatavaid töid rohkem pole
            return self._redirect_to_index(False)

    def edit(self):
        d = self._edit_d()
        if isinstance(d, dict):
            if not self.request.params.get('partial'):
                template = self._INDEX_TEMPLATE
            else:
                template = self._EDIT_TEMPLATE
            return self.render_to_response(template)
        else:
            return d

    def _edit(self, item):
        # get_opt_sooritused() tehakse toohindamine.ty_edit() sees
        ty_id = self.c.vy.testiylesanne_id
        return self._ty_edit(ty_id)

    def _get_ylesanded(self):
        c = self.c
        c.testiylesanded_id = [c.vy.testiylesanne_id]

    def _get_tab_urls(self):
        c = self.c
        handler = self
        # vasakul poolel ylesande avamise (GET) või hindamise salvestamise (POST) URL
        def f_submit_url(ty_id):
            # hindamiskogumis teise ylesande ettevõtmine ilma salvestamiseta
            return handler.url('test_ylesanne_hindamine', test_id=c.test.id, testiruum_id=c.testiruum_id, id=c.sooritus.id, vy_id=c.vy.id)                

        c.f_submit_url = f_submit_url

        get_tab_urls(self, self.c)
        
    def _redirect_to_index(self, is_json):
        c = self.c
        url = self.url('test_ylesandehindamised', test_id=c.test.id, testiruum_id=c.testiruum.id)
        if is_json:
            return Response(json_body={'redirect': url})        
        else:
            return HTTPFound(location=url)

    def _redirect_new(self):
        # võetakse järgmine töö hindamiseks
        c = self.c
        sooritus_id, error = new_hindamine(self, c.test, c.testiruum, c.hindaja, c.vy)
        if error:
            self.warning(error)
        if sooritus_id:
            # on töö, mida hinnata, suundume tööle
            return self._redirect('edit', id=sooritus_id)
        else:
            return self._redirect_to_index(True)

    def _is_next(self, sooritus):
        # kas on veel töid saadaval ja on vaja järgmise töö nuppu
        c = self.c
        check_s_id = sooritus.id
        next_id, next_error = new_hindamine(self, c.test, c.testiruum, c.hindaja, c.vy, check_s_id)
        return next_id is not None

    def _after_update(self, op):
        if op == 'jargminetoo':
            # võetakse järgmine töö ette
            response = self._redirect_new()
            if response:
                return response
        else:
            next_tos_id = self._get_next_tos(op)
            if next_tos_id:
                # on antud järgmine töö (ylesandehindamine.py)
                url = self.url_current('edit', id=next_tos_id)
                return HTTPFound(location=url)

        # loetellu
        return self._redirect_to_index(True)
        
    def __before__(self):
        c = self.c
        vy_id = self.request.matchdict.get('vy_id')
        c.vy = model.Valitudylesanne.get(vy_id)
        
        sooritus_id = self.request.matchdict.get('id')
        if sooritus_id:
            c.sooritus = model.Sooritus.get(sooritus_id)
            
        c.testiruum_id = self.request.matchdict.get('testiruum_id')
        c.testiruum = model.Testiruum.get(c.testiruum_id)
        c.testikoht = c.testiruum.testikoht
        c.test_id = self.request.matchdict.get('test_id')
        c.test = model.Test.get(c.test_id)
        c.hindaja = c.testiruum.get_labiviija(const.GRUPP_HINDAJA_K, c.user.id)
        c.testiosa = c.testikoht.testiosa
        
    def _perm_params(self):
        c = self.c
        if c.sooritus and \
               (c.sooritus.testiruum_id != c.testiruum.id or \
                c.sooritus.testiosa_id != c.testikoht.testiosa_id):
            return False
        nimekiri = c.testiruum.nimekiri
        if not nimekiri:
            return False
        if self.c.test.opetajale_peidus:
            return False
        return {'obj':nimekiri}
       
def new_hindamine(handler, test, testiruum, hindaja, vy, check_s_id=None):
    """Leitakse uus töö, mida hinnata
    """
    rc = True
    sooritus_id = error = None
    # kontrollime, et planeeritud tööde arv poleks täis
    if hindaja and hindaja.planeeritud_toode_arv:
        # planeeritud tööde arv on määratud
        if hindaja.toode_arv and hindaja.toode_arv >= hindaja.planeeritud_toode_arv:
            error = _("Planeeritud tööde arv on täis")
            rc = False
    
    if rc:
        # otsime uut hinnatavat tööd
        holek = None # valitava töö hindamisoleku kirje
        params = handler.request.params
        sooritus_id, error = _choose_e_next(handler, test, testiruum, hindaja, vy, check_s_id)
    return sooritus_id, error

def _choose_e_next(handler, test, testiruum, hindaja, vy, check_s_id=None):
    """Otsitakse järgmine e-töö, mida hinnata
    """
    sooritus_id = error = None
    # võtame suvalise töö, millel pole antud ylesanne hinnatud
    q = (model.Session.query(model.Sooritus.id)
         .filter(model.Sooritus.testiruum_id==testiruum.id)
         .join((model.Ylesandevastus,
                model.Ylesandevastus.sooritus_id==model.Sooritus.id))
         .filter(model.Ylesandevastus.mittekasitsi==False)
         .filter(model.Ylesandevastus.valitudylesanne_id==vy.id)
         )
    if test.on_jagatudtoo:
        q = (q.filter(model.Ylesandevastus.muudetav==False)
             .filter(model.Ylesandevastus.kehtiv==True)
             )
    else:
        q = q.filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)

    if hindaja and hindaja.lang:
        q = (q.join(model.Sooritus.sooritaja)
             .filter(model.Sooritaja.lang==hindaja.lang))

    if check_s_id:
        # jätame välja jooksva töö, kui eesmärk on vaadata, kas saadaval on veel töid
        q = q.filter(model.Sooritus.id != check_s_id)

    # jätame esialgu välja tööd, millel on hindamine olemas
    q2 = (q.filter(model.Sooritus.hindamine_staatus!=const.H_STAATUS_HINNATUD)
          .filter(model.Ylesandevastus.pallid==None)
          .filter(~ model.Ylesandevastus.ylesandehinded.any())
          )
    r = q2.first()
    sooritus_id = r and r[0] or None

    if not sooritus_id and hindaja:
        # otsime mõne minu pooleli jäänud hindamise
        q3 = (q.join(model.Ylesandevastus.ylesandehinded)
              .join(model.Ylesandehinne.hindamine)
              .filter(model.Hindamine.staatus!=const.H_STAATUS_LYKATUD)
              .filter(model.Hindamine.labiviija_id==hindaja.id)
              .filter(model.Sooritus.hindamine_staatus!=const.H_STAATUS_HINNATUD)
              .filter(model.Ylesandevastus.pallid==None)
              )
        r = q3.first()
        sooritus_id = r and r[0] or None

    if not sooritus_id and hindaja:
        # otsime lõpetamata hindamisi, mis pole minu hindamisel
        q4 = (q.filter(model.Sooritus.hindamine_staatus!=const.H_STAATUS_HINNATUD)
              .filter(model.Ylesandevastus.pallid==None)
              .filter(~ sa.exists().where(sa.and_(
                  model.Ylesandevastus.id==model.Ylesandehinne.ylesandevastus_id,
                  model.Ylesandehinne.hindamine_id==model.Hindamine.id,
                  model.Hindamine.staatus!=const.H_STAATUS_LYKATUD,
                  model.Hindamine.labiviija_id==hindaja.id)))
                  )
        cnt = q4.count()
        if cnt:
            error = _("Hindamata on veel {n} tööd, kuid nende hindamist on juba keegi teine alustanud").format(n=cnt)
        else:
            error = _("Hindamata töid rohkem ei ole")

    if not sooritus_id and hindaja:
        # kui alustamata hindamisi pole, siis otsime mõne minu tehtud hindamise
        q = (q.join(model.Ylesandevastus.ylesandehinded)
             .join(model.Ylesandehinne.hindamine)
             .filter(model.Hindamine.staatus!=const.H_STAATUS_LYKATUD)
             .filter(model.Hindamine.labiviija_id==hindaja.id)
             )
        r = q.first()
        sooritus_id = r and r[0] or None

    return sooritus_id, error
