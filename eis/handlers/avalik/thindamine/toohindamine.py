# -*- coding: utf-8 -*- 
from eis.lib.baseresource import *
from eis.lib.resultentry import ResultEntry
from eis.handlers.avalik.khindamine.rhindamised import get_rhindamiste_arvud
_ = i18n._
from eis.handlers.avalik.khindamine.hkhindamine import HkhindamineController

import logging
log = logging.getLogger(__name__)

class ToohindamineController(HkhindamineController):
    """Labiviija hindab lahendaja kirjalikku lahendust.
    """
    _permission = 'thindamine'
    _INDEX_TEMPLATE = 'avalik/thindamine/toohindamine.mako'

    def _get_ylesanded(self):
        c = self.c
        komplektis_ty_id = [ty.id for ty in c.testiosa.testiylesanded if not ty.arvutihinnatav]
        if c.ignore_ty_id:
            # jätame välja need testiylesanded, mida ei ole vaja hindajale kuvada
            komplektis_ty_id = [ty_id for ty_id in komplektis_ty_id \
                                if ty_id not in c.ignore_ty_id]

        if c.test.on_jagatudtoo:
            li = []
            # jätame välja need testiylesanded, mida lahendaja pole kinnitanud
            for ty_id in komplektis_ty_id:
                yv = self._get_ylesandevastus(ty_id)
                if yv:
                    li.append(ty_id)
            komplektis_ty_id = li
            
        c.testiylesanded_id = komplektis_ty_id           

    def _set_etest_unresponded(self):
        # e-testi korral: leitakse ülesanded, mis tuleb hindamiselt välja jätta, kuna pole käsitsi hinnatavaid vastuseid
        c = self.c
        resultentry = ResultEntry(self, const.SISESTUSVIIS_PALLID, c.test, c.testiosa)
        c.ignore_ty_id = []
        for holek in c.sooritus.hindamisolekud:
            hkogum = holek.hindamiskogum
            if holek.staatus and hkogum:
                # kui on ilma hindamiskogumita yhe ylesande kaupa hindamine, siis anname ty_id
                ty_id = c.vy and c.vy.testiylesanne_id or None
                li = resultentry.unresponded_zero(c.sooritus, c.hindamine, holek, hkogum, ty_id)
                c.ignore_ty_id.extend(li)

    def _get_tab_urls(self):
        c = self.c
        handler = self
        # vasakul poolel ylesande avamise (GET) või hindamise salvestamise (POST) URL
        def f_submit_url(ty_id):
            # hindamiskogumis teise ylesande ettevõtmine ilma salvestamiseta
            if ty_id:
                return handler.url('test_sooritus_hindamine', test_id=c.test.id, testiruum_id=c.testiruum_id, sooritus_id=c.sooritus.id, id=ty_id)                
            else:
                return handler.url('test_sooritus_hindamised', test_id=c.test.id, testiruum_id=c.testiruum_id, sooritus_id=c.sooritus.id)                
        c.f_submit_url = f_submit_url

        get_tab_urls(self, self.c)

    def _redirect_to_index(self, is_json):
        c = self.c
        url = self.url('test_toohindamised', test_id=c.test.id, testiruum_id=c.testiruum.id)
        if is_json:
            return Response(json_body={'redirect': url})
        else:
            return HTTPFound(location=url)

    def _redirect_new(self):
        # võetakse järgmine töö hindamiseks
        c = self.c
        holek, error = new_hindamine(self, c.test, c.testiruum, c.hindaja)
        if error:
            self.warning(error)
        if holek:
            # on töö, mida hinnata, suundume tööle
            return self._redirect('index', sooritus_id=holek.sooritus_id)        
        else:
            return self._redirect_to_index(True)

    def _ty_edit(self, ty_id):
        res = super()._ty_edit(ty_id)
        # lisame sooritajate valiku
        if self.c.vy:
            self._get_opt_sooritused()
        return res
    
    def _give_hindaja(self):
        c = self.c
        grupp_id = const.GRUPP_HINDAJA_K
        liik = const.HINDAJA1
        kasutaja_id = c.user.id
        q = (model.Session.query(model.Labiviija)
             .filter_by(testiruum_id=c.testiruum.id)
             .filter_by(kasutajagrupp_id=grupp_id)
             .filter_by(liik=liik)
             .filter_by(kasutaja_id=kasutaja_id)
             )
        hindaja = q.first()
        if not hindaja:
            hindaja = model.Labiviija(kasutaja_id=kasutaja_id,
                                      testikoht_id=c.testiruum.testikoht_id,
                                      testiruum_id=c.testiruum.id,
                                      liik=liik,
                                      kasutajagrupp_id=grupp_id,
                                      toode_arv=0,
                                      hinnatud_toode_arv=0,
                                      tasu_toode_arv=0)
            model.Session.flush()
        return hindaja

    def _give_hindamine(self):
        c = self.c
        if not c.hindaja:
            c.hindaja = self._give_hindaja()
        liik = const.HINDAJA1
        holek = c.sooritus.give_hindamisolek(c.hindamiskogum)
        user_id = c.hindaja.kasutaja_id
        eityhista = c.action == 'edit'
        c.hindamine = holek.give_hindamine(liik, hindaja_kasutaja_id=user_id, labiviija_id=c.hindaja.id, eityhista=eityhista, unikaalne=False)
        if not c.hindamine:
            h = holek.get_hindamine(liik)
            k = h and h.hindaja_kasutaja
            if k:
                self.error(_("Tööd hindab juba {s}").format(s=k.nimi))
                return
        c.hindamine.hindaja_kasutaja_id = user_id
        c.hindamine.labiviija = c.hindaja
        model.Session.flush()
        c.hindaja.calc_toode_arv()
        return c.hindamine

    def _save_hindamine(self, hindamine):
        c = self.c
        holek = hindamine.hindamisolek
        self._set_hindamine_komplekt(hindamine, holek)
            
        hindamine.hindaja_kasutaja_id = c.user.id
        hindamine.ksm_naeb_hindaja = self.form.data['ksm_naeb_hindaja']
        hindamine.ksm_naeb_sooritaja = self.form.data['ksm_naeb_sooritaja']        

        viis = const.SISESTUSVIIS_PALLID
        resultentry = ResultEntry(self, viis, c.test, c.testiosa, c.test.on_jagatudtoo)
        resultentry.on_hindamiskogumita = True
        c.sooritus.hindamiskogumita = True
        prefix = ''
        lopeta = None # kui on võimalik, siis hindamine ikkagi kinnitatakse
        sooritaja = c.sooritus.sooritaja
        resultentry.save_ty_hindamine(sooritaja, self.form.data, lopeta, prefix, c.sooritus, holek, c.testiosa, hindamine, None, False)

        if resultentry.errors:
            err = self._desc_errors(resultentry.errors)
            raise ValidationError(self, resultentry.errors, message=err)

        model.Session.commit()

    def _set_hindamine_komplekt(self, hindamine, komplekt):
        # hindamiskogumita hindmaisel ei ole hindamise kirje kyljes komplekti
        pass

    def _get_opt_sooritused(self):
        # sooritaja valikvälja valikud
        # otsitakse selle ylesande kõik sooritused, mida ma saan hinnata
        c = self.c
        q = (model.Session.query(model.Sooritus.id,
                                 model.Sooritaja.eesnimi,
                                 model.Sooritaja.perenimi,
                                 model.Ylesandehinne.pallid,
                                 model.Ylesandehinne.probleem_varv)
             .join(model.Sooritus.sooritaja)
             .filter(model.Sooritus.testiruum_id==c.testiruum.id)
             .join((model.Ylesandevastus,
                    model.Ylesandevastus.sooritus_id==model.Sooritus.id))
             .filter(model.Ylesandevastus.mittekasitsi==False)
             .outerjoin(model.Ylesandevastus.ylesandehinded)
             .outerjoin(model.Ylesandehinne.hindamine)
             .filter(sa.or_(model.Hindamine.id==None,
                            sa.and_(model.Hindamine.hindaja_kasutaja_id==c.user.id,
                                    model.Hindamine.tyhistatud==False)))
             .filter(model.Ylesandevastus.valitudylesanne_id==c.vy.id)
             )
        
        if c.test.on_jagatudtoo:
            q = (q.filter(model.Ylesandevastus.muudetav==False)
                 .filter(model.Ylesandevastus.kehtiv==True)
                 )
        else:
            q = q.filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
        q = q.order_by(model.Sooritaja.eesnimi,
                       model.Sooritaja.perenimi)
        #model.log_query(q)
        c.opt_sooritused = []
        for s_id, fn, ln, p, color in q.all():
            label = f'{fn} {ln}'
            if p:
                label += ' (%sp)' % self.h.fstr(p)
            if color:
                attrs = {'style': f'background-color:{color};'}
            else:
                attrs = {}
            c.opt_sooritused.append((s_id, label, attrs))
        
    def _get_ylesandevastus(self, ty_id, komplekt_id=None):
        c = self.c
        if c.test.on_jagatudtoo:
            muudetav = False
        else:
            muudetav = None
        return self.c.sooritus.getq_ylesandevastus(ty_id, komplekt_id, muudetav=muudetav)

    def _is_next(self, sooritus):
        # kas on veel töid saadaval ja on vaja järgmise töö nuppu
        c = self.c
        check_s_id = sooritus.id
        next_holek, next_error = new_hindamine(self, c.test, c.testiruum, c.hindaja, check_s_id)        
        return next_holek is not None

    def _get_hindamiste_arvud(self):
        c = self.c
        c.alustamata, c.cnt_pooleli, c.cnt_hinnatud = get_rhindamiste_arvud(c.testiruum.id, None)
    
    def __before__(self):
        c = self.c
        sooritus_id = self.request.matchdict.get('sooritus_id')
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
        if c.hindaja:
            # kui on määratud kindlaid ylesandeid hindama, siis ei või töökaupa hinnata
            for ly in c.hindaja.labiviijaylesanded:
                return False

        nimekiri = c.testiruum.nimekiri
        if not nimekiri:
            return False
        if self.c.test.opetajale_peidus:
            return False
        return {'obj':nimekiri}

    def _has_permission(self):
        return BaseController._has_permission(self)
        
def get_tab_urls(handler, c):
    h = handler.h
        
    # paremal poolel ylesandega seotud sakkide andmed
    def f_r_tabs_data(vy, ylesanne, indlg):
        data = []
        indlg = indlg and 1 or None
        if c.r_tab == 'juhend' or ylesanne.on_hindamisjuhend:
            url = handler.url('test_hindamine_juhendid', test_id=c.test.id, testiruum_id=c.testiruum_id, vy_id=vy.id, lang=c.lang, indlg=indlg)
            label = _("Hindamisjuhend")
            if ylesanne.hindamisjuhist_muudetud():
               label = label + ' ' + h.mdi_icon('mdi-flag')
            data.append(('juhend', url, label))

        url = handler.url('test_hindamine_edit_lahendamine', test_id=c.test.id, testiruum_id=c.testiruum_id, vy_id=vy.id, id=vy.ylesanne_id, lang=c.lang, correct=1, indlg=indlg)
        data.append(('correct', url, _("Õige vastus")))      

        url = handler.url('test_hindamine_edit_lahendamine', test_id=c.test.id, testiruum_id=c.testiruum_id, vy_id=vy.id, id=vy.ylesanne_id, lang=c.lang, indlg=indlg)
        data.append(('lahendamine', url, _("Lahendaja vaade")))
        return data
    
    c.f_r_tabs_data = f_r_tabs_data
    if c.vy:
        c.r_tabs_data = f_r_tabs_data(c.vy, c.vy.ylesanne, c.indlg)


def new_hindamine(handler, test, testiruum, hindaja, check_s_id=None):
    """Leitakse uus töö, mida hinnata
    """
    rc = True
    holek = None # valitava töö hindamisoleku kirje
    error = None
    
    # kontrollime, et planeeritud tööde arv poleks täis
    if hindaja and hindaja.planeeritud_toode_arv:
        # planeeritud tööde arv on määratud
        if hindaja.toode_arv and hindaja.toode_arv >= hindaja.planeeritud_toode_arv:
            error = _("Planeeritud tööde arv on täis")
            rc = False
    if rc:
        # otsime uut hinnatavat tööd
        params = handler.request.params
        holek, error = _choose_e_next(handler, test, testiruum, hindaja, check_s_id)
    return holek, error

def _choose_e_next(handler, test, testiruum, hindaja, check_s_id):
    """Otsitakse järgmine e-töö, mida hinnata
    """
    holek = error = None
    # võtame suvalise töö, millel pole hindamise kirjet
    q = (model.Hindamisolek.query
         .filter(model.Hindamisolek.hindamiskogum_id==None)
         .filter(model.Hindamisolek.mittekasitsi==False)
         .join(model.Hindamisolek.sooritus)
         .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
         .filter(model.Sooritus.hindamine_staatus!=const.H_STAATUS_HINNATUD)
         .filter(model.Sooritus.testiruum_id==testiruum.id)
         )
    if hindaja.lang:
        q = (q.join(model.Sooritus.sooritaja)
             .filter(model.Sooritaja.lang==hindaja.lang))

    if check_s_id:
        # jätame välja jooksva töö, kui eesmärk on vaadata, kas saadaval on veel töid
        q = q.filter(model.Sooritus.id != check_s_id)

    # jätame välja tööd, millel on hindamine olemas
    q2 = q.filter(~ model.Hindamisolek.hindamised.any(
        model.Hindamine.staatus!=const.H_STAATUS_LYKATUD))

    holek = q2.first()
    if not holek:
        # kui alustamata hindamisi pole, siis otsime mõne minu pooleli hindamise
        q3 = q.filter(model.Hindamisolek.hindamised.any(
            sa.and_(model.Hindamine.staatus!=const.H_STAATUS_LYKATUD,
                    model.Hindamine.labiviija_id==hindaja.id)
            ))
        holek = q3.first()

    if not holek:
        cnt = q.count()
        model.log_query(q)
        if cnt:
            error = _("Hindamata on veel {n} tööd, kuid nende hindamist on juba keegi teine alustanud").format(n=cnt)
        else:
            error = _("Hindamata töid rohkem ei ole")
    return holek, error
