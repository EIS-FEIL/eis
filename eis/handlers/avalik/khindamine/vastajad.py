import random
from eis.lib.baseresource import *
_ = i18n._
from eis.lib.resultentry import ResultEntry
log = logging.getLogger(__name__)
from .hindamiskogumid import HindamisteArv

class VastajadController(BaseResourceController):
    """Hindamiskogumi soorituste näitamine
    """
    _permission = 'khindamine'
    _MODEL = model.Sooritus
    _INDEX_TEMPLATE = 'avalik/khindamine/vastajad.mako'
    _LIST_TEMPLATE = 'avalik/khindamine/vastajad_list.mako'
    _DEFAULT_SORT = '-hindamine.on_probleem,sooritus.id'
    _actions = 'index,create' 
    
    def _query(self):
        """Mulle suunatud või pooleli hindamiste loetelu
        """
        q = (model.SessionR.query(model.Sooritus, model.Hindamisolek, model.Hindamine)
             .filter(model.Sooritus.toimumisaeg_id==self.c.toimumisaeg.id)
             .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
             .join(model.Sooritus.sooritaja)
             .join(model.Sooritus.hindamisolekud)
             .filter(model.Hindamisolek.hindamiskogum_id==self.c.hindamiskogum.id)
             .filter(model.Hindamisolek.puudus==False)
             .filter(model.Hindamisolek.hindamisprobleem!=const.H_PROBLEEM_TOOPUUDU)
             .filter(model.Hindamisolek.mittekasitsi==False)
             )
        return q 

    def _search_default(self, q):
        self.c.staatus = const.H_STAATUS_POOLELI
        return self._search(q)

    def _search(self, q):
        c = self.c
        q = q.outerjoin((model.Hindamine,
                         sa.and_(model.Hindamisolek.id==model.Hindamine.hindamisolek_id,
                                 model.Hindamine.labiviija_id==c.hindaja.id,
                                 model.Hindamine.tyhistatud==False,
                                 model.Hindamine.sisestus==1)
                         ))
            
        # teeme päringu valitud staatuse järgi
        H_STAATUS_POOLELI_VALMIS = 3
        if c.staatus == '':
            if c.cnt_pooleli:
                c.staatus = const.H_STAATUS_POOLELI
            elif c.cnt_valmis:
                c.staatus = H_STAATUS_POOLELI_VALMIS
            elif c.cnt_hindamata:
                c.staatus = const.H_STAATUS_HINDAMATA
            else:
                c.staatus = const.H_STAATUS_HINNATUD
        else:
            c.staatus = int(c.staatus)

        staatus = c.staatus
        if staatus == H_STAATUS_POOLELI_VALMIS:
            staatus = const.H_STAATUS_POOLELI
            sisestatud = True
        elif staatus == const.H_STAATUS_POOLELI:
            sisestatud = False
        else:
            sisestatud = None

        if staatus == const.H_STAATUS_HINDAMATA and c.testiosa.vastvorm_kood == const.VASTVORM_SH:
            # arvestada ainult neid sooritajaid, kelle protokoll on kinnitatud ES-3717
            q = q.filter(sa.exists().where(sa.and_(
                          model.Toimumisprotokoll.id==model.Sooritus.toimumisprotokoll_id,
                          model.Toimumisprotokoll.staatus.in_(
                              (const.B_STAATUS_KINNITATUD, const.B_STAATUS_EKK_KINNITATUD))
                          )))
            
        # leiame alustamata tööde arvu, sh määramata saadaval tööd
        harv = HindamisteArv(c.hindaja, c.toimumisaeg)
        c.alustamata = harv.alustamata
        maaramata = harv.maaramata
        c.cnt_hindamata = harv.lv_hindamata_maaratud
        c.cnt_pooleli = harv.lv_pooleli
        c.cnt_valmis = harv.lv_valmis
        c.cnt_hinnatud = harv.lv_hinnatud

        lopetamata = c.cnt_hindamata + c.cnt_pooleli

        if lopetamata and c.cnt_valmis:
            self.error(_("Hindamine on lõpetamata! Hindamata on {n1} tööd, kinnitamata {n2} tööd.").format(n1=lopetamata, n2=c.cnt_valmis))
        elif lopetamata:
            self.error(_("Hindamine on lõpetamata! Hindamata on {n1} tööd.").format(n1=lopetamata))
        elif c.cnt_valmis:
            self.error(_("Hindamine on lõpetamata! Kinnitamata on {n1} tööd.").format(n1=c.cnt_valmis))                
        elif c.cnt_hinnatud and not c.alustamata and maaramata and c.hindaja.planeeritud_toode_arv:
            self.success(_("Selles hindamiskogumis on sulle planeeritud arv töid hinnatud ja kinnitatud."))
        elif c.cnt_hinnatud and not c.alustamata:
            self.success(_("Selles hindamiskogumis on kõik tööd hinnatud ja kinnitatud."))
            

        if staatus == const.H_STAATUS_HINDAMATA and harv.paariline_id:
            # hindamata tööd võivad olla ka ainult paarilisel
            Hindamine2 = sa.orm.aliased(model.Hindamine)
            q = q.filter(sa.or_(model.Hindamine.staatus==const.H_STAATUS_HINDAMATA,
                                sa.and_(model.Hindamine.id==None,
                                        sa.exists().where(sa.and_(
                                            Hindamine2.hindamisolek_id==model.Hindamisolek.id,
                                            Hindamine2.labiviija_id==harv.paariline_id,
                                            Hindamine2.tyhistatud==False)
                                                          )
                                        )
                                )
                         )
        else:
            q = q.filter(model.Hindamine.staatus==staatus)
        if sisestatud is not None:
            q = q.filter(model.Hindamine.sisestatud==sisestatud)

        testimiskord = c.toimumisaeg.testimiskord
        c.sisestus_isikukoodiga = testimiskord.sisestus_isikukoodiga
   
        c.header = self._prepare_header()
        c.prepare_item = self._prepare_item        
        self._list_ylesanded()

        c.opt_hkogumid = self._get_opt_hkogumid()
        return q

    def _get_opt_hkogumid(self):
        "Leitakse sama toimumisaja muud hindamiskogumid, mille hindaja ma olen"
        c = self.c
        vastvorm_k = (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I, const.VASTVORM_KP)
        q = (model.SessionR.query(model.Labiviija.id,
                                 model.Toimumisaeg.id,
                                 model.Hindamiskogum.tahis)
             .filter(model.Labiviija.kasutaja_id==c.hindaja.kasutaja_id)
             .join(model.Labiviija.toimumisaeg)
             .filter(model.Toimumisaeg.testimiskord_id==c.toimumisaeg.testimiskord_id)
             .join(model.Toimumisaeg.testiosa)
             .filter(model.Testiosa.vastvorm_kood.in_(vastvorm_k))
             .join(model.Labiviija.hindamiskogum)
             .filter(model.Toimumisaeg.on_hindamisprotokollid==1)
             .filter(model.Labiviija.liik<=const.HINDAJA3)
             .order_by(model.Hindamiskogum.tahis)
             )
        li = []
        for lv_id, ta_id, label in q.all():
            if lv_id != c.hindaja.id:
                href = self.h.url_current(hindaja_id=lv_id, toimumisaeg_id=ta_id)
            else:
                href = ''
            li.append([lv_id, label, href])
        return li

    def _list_ylesanded(self):
        if not self.c.hindamiskogum:
            return
        q = (model.SessionR.query(model.Testiylesanne.alatest_seq,
                                 model.Testiylesanne.seq,
                                 model.Valitudylesanne)
             .join(model.Valitudylesanne.testiylesanne)
             .join(model.Valitudylesanne.komplekt)
             .join(model.Komplekt.toimumisajad)
             .filter(model.Toimumisaeg.id==self.c.toimumisaeg.id)
             )
        if self.c.toimumisaeg.testiosa.lotv:
            q = q.filter(model.Valitudylesanne.hindamiskogum_id==self.c.hindamiskogum.id)
        else:
            q = q.filter(model.Testiylesanne.hindamiskogum_id==self.c.hindamiskogum.id)
        
        q = q.order_by(model.Testiylesanne.alatest_seq,
                       model.Testiylesanne.seq,
                       model.Valitudylesanne.seq)
        self.c.items_ylesanded = q.all()
        self._get_tab_urls()

    def _get_tab_urls(self):
        # funktsioon, mis genereerib lingi ylesandele
        from .hkhindamine import get_tab_urls
        get_tab_urls(self, self.c)

    def _prepare_header(self):
        max_p = self.h.fstr(self.c.hindamiskogum.max_pallid)
        header = [('sooritus.tahis', _("Testitöö kood")),
                  ('hindamine.pallid', _("Punktid (max {p})").format(p=max_p)),
                  ]
        if self.c.staatus == const.H_STAATUS_POOLELI:
            header.extend([('hindamine.on_probleem', _("Probleem")),
                           ('hindamine.probleem_sisu', _("Probleemi sisu")),
                           ])
        return header
    
    def _prepare_item(self, rcd):
        tos, holek, hindamine = rcd

        if self.c.sisestus_isikukoodiga:
            k = tos.sooritaja.kasutaja
            ik = k.isikukood
            too = f'{tos.tahised} {ik}'
        else:
            too = tos.tahised
        pallid = hindamine and self.h.fstr(hindamine.pallid) or None
        item = [too,
                pallid]
        return item
    
    def create(self):
        c = self.c
        if self.request.params.get('sub') == 'hinda':
            # Kasutaja soovib hakata uut tööd hindama
            holek, error = new_hindamine(self, c.toimumisaeg, c.testiosa, c.hindamiskogum, c.hindaja)
            if error:
                self.error(error)
            if holek:
                return self._redirect_hinda(holek.sooritus_id)
            else:
                return self._redirect('index')
        else:
            return self._create_kinnita()

    def _redirect_hinda(self, sooritus_id):
        "Algab hindamine"
        c = self.c
        partial = self.request.params.get('partial') or None                
        if c.testiosa.vastvorm_kood == const.VASTVORM_SH:
            url = self.url('shindamine_hindamised', 
                           hindaja_id=c.hindaja.id, 
                           sooritus_id=sooritus_id)
        else:
            url = self.url('khindamine_hkhindamised', 
                           toimumisaeg_id=c.toimumisaeg.id, 
                           hindaja_id=c.hindaja.id, 
                           sooritus_id=sooritus_id,
                           partial=partial)
        return HTTPFound(location=url)

    def _create_kinnita(self):
        """Kasutaja linnutas pooleli hindamisega tööd ja soovib nende hindamise kinnitada
        """
        c = self.c
        cnt = 0
        for h_id in self.request.params.getall('hindamine_id'):
            hindamine = model.Hindamine.get(h_id)
            if hindamine:
                hindaja_kasutaja_id = hindamine.hindaja_kasutaja_id
                user_id = self.c.user.id
                assert hindaja_kasutaja_id == user_id, _("Vale kasutaja")
                if hindamine.staatus == const.H_STAATUS_POOLELI and hindamine.sisestatud:
                    hindamine.staatus = const.H_STAATUS_HINNATUD
                    rs = ResultEntry(self, const.SISESTUSVIIS_PALLID, c.test, c.testiosa)
                    holek = hindamine.hindamisolek
                    sooritus = holek.sooritus
                    rs.update_hindamisolek(sooritus.sooritaja, sooritus, holek)
                    cnt += 1
        if cnt:
            model.Session.commit()
            c.hindaja.calc_toode_arv()
            model.Session.commit()
            self.success(_("Kinnitatud {n} hindamist").format(n=cnt))
            
        return self._redirect('index')

    def __before__(self):
        c = self.c
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)
        c.testimiskord = c.toimumisaeg.testimiskord
        hindaja_id = self.request.matchdict.get('hindaja_id')
        c.hindaja = model.Labiviija.get(hindaja_id)
        c.hindamiskogum = c.hindaja and c.hindaja.hindamiskogum
        c.testiosa = c.toimumisaeg.testiosa
        c.test = c.testiosa.test
        
    def _has_permission(self):
        c = self.c
        return c.hindaja and c.hindaja.kasutaja_id == c.user.id

def new_hindamine(handler, toimumisaeg, testiosa, hindamiskogum, hindaja, check_s_id=None):
    """Alustatakse uue töö hindamist.
    E-testi hindamise korral valib süsteem hinnatava töö.
    P-testi hindamimise korral peab HTTP parameetrites olema hinnatava töö tähis
    check_s_id - praegu hinnatava soorituse ID juhul, kui eesmärk on vaadata, kas saadaval on veel töid peale selle;
                 kui on antud, siis otsitakse ka hindajal juba pooleli olevate hindamiste seast
    """
    rc = True
    tahis = None # töö tähis p-testi korral
    error = None
    holek = None # valitava töö hindamisoleku kirje
    
    on_ptest = False
    if testiosa.vastvorm_kood == const.VASTVORM_KP:
        sk = hindamiskogum.sisestuskogum
        on_ptest = not (sk and sk.on_skannimine)

    # kontrollime, et planeeritud tööde arv poleks täis
    if hindaja and hindaja.planeeritud_toode_arv:
        # planeeritud tööde arv on määratud
        if hindaja.toode_arv and hindaja.toode_arv >= hindaja.planeeritud_toode_arv:
            error = _("Planeeritud tööde arv on täis")
            rc = False

    if hindaja and hindaja.testikoht_id and \
           toimumisaeg.muu_koha_hindamine(hindaja.valimis, hindaja.liik):
        # soorituskoha määratud hindaja hindab teiste soorituskohtade töid
        # sama palju, kui on oma soorituskohas sooritajaid
        q1 = (model.SessionR.query(sa.func.count(model.Sooritus.id))
              .filter(model.Sooritus.testikoht_id==hindaja.testikoht_id)
              .join(model.Sooritus.sooritaja)
              .filter(model.Sooritaja.valimis==hindaja.valimis)
              .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD))
        koha_sooritajate_arv = q1.scalar()
        q2 = (model.SessionR.query(sa.func.sum(model.Labiviija.toode_arv))
              .filter(model.Labiviija.testikoht_id==hindaja.testikoht_id)
              .filter(model.Labiviija.kasutajagrupp_id==hindaja.kasutajagrupp_id)
              .filter(model.Labiviija.liik==hindaja.liik)
              .filter(model.Labiviija.hindamiskogum_id==hindaja.hindamiskogum_id))
        koha_toode_arv = q2.scalar() or 0
        if koha_toode_arv >= koha_sooritajate_arv:
            if not koha_sooritajate_arv:
                error = _("Minu koolis pole keegi testi sooritanud, seetõttu ei saa veel hinnata")
            else:
                error = _("Koolis on testi praeguseks teinud {n} sooritajat ning kool on juba sama palju töid hindamiseks saanud, uusi töid hindamisele ei saa võtta").format(n=koha_sooritajate_arv)
            rc = False
    
    if rc:
        # otsime uut hinnatavat tööd
        params = handler.request.params
        if on_ptest:
            # p-testi e-hindamine
            # kasutaja on sisestanud töö tähise, mis tal paberil ees on
            holek, error = _choose_p_next(handler, toimumisaeg, hindamiskogum, hindaja, None, params)
        else:
            # e-testi või skannitud p-testi e-hindamine
            # süsteem valib ise töö
            holek, error = _choose_e_next(handler, toimumisaeg, testiosa, hindamiskogum, hindaja, check_s_id)
            if not holek:
                error = _("Pole enam ühtki tööd, mida valitud rollis hinnata saaks")

        if holek and not handler.c.app_ekk and not check_s_id:
            # on töö, mida hinnata, suundume tööle
            # märgime töö selle hindaja hindamisele
            liik = hindaja and hindaja.liik or const.HINDAJA1
            hindamine = holek.give_hindamine(liik, hindaja_kasutaja_id=handler.c.user.id)
            hindamine.hindaja_kasutaja_id = handler.c.user.id
            hindamine.labiviija = hindaja

            # kui oli vana hindamine, mis oli tagasi lükatud, siis märgime sellele uue hindamise
            if hindamine.staatus != const.H_STAATUS_LYKATUD:
                qv = (model.Hindamine.query
                      .filter(model.Hindamine.hindamisolek_id==holek.id)
                      .filter(model.Hindamine.liik==liik)
                      .filter(model.Hindamine.staatus==const.H_STAATUS_LYKATUD)
                      .filter(model.Hindamine.uus_hindamine_id==None)
                      )
                for vana_hindamine in qv.all():
                    vana_hindamine.uus_hindamine = hindamine
                    vana_hindamine.staatus = const.H_STAATUS_SUUNATUD
                    vana_hindamine.tyhistatud = True                
                    break

            model.Session.commit()

    return holek, error

def _choose_p_next(handler, toimumisaeg, hindamiskogum, hindaja, next_tahis, params):
    """Võetakse järgmine p-töö, mida hinnata
    """
    holek = error = None
    tahised = next_tahis or params.get('tahised')
    sisestus_isikukoodiga = toimumisaeg.testimiskord.sisestus_isikukoodiga
    isikukood = sisestus_isikukoodiga and params.get('isikukood')
    if not tahised and not isikukood:
        if not sisestus_isikukoodiga:
            error = _("Palun sisesta testitöö tähis")
        else:
            error = _("Palun sisesta testitöö tähis või isikukood")
    else:
        q = (model.Sooritus.query
             .filter(model.Sooritus.toimumisaeg_id==toimumisaeg.id)
             .join(model.Sooritus.sooritaja)
             .filter(model.Sooritaja.valimis==hindaja.valimis)
             )
        if tahised:
            q = q.filter(model.Sooritus.tahised==tahised)
        else:
            q = q.join(model.Sooritaja.kasutaja)
            usp = validators.IsikukoodP(isikukood)
            q = q.filter(usp.filter(model.Kasutaja))
        tos = q.first()
        sooritaja = tos and tos.sooritaja
        if not tos:
            if tahised:
                error = _("Tähisega {s} sooritust ei leitud").format(s=tahised)
            else:
                error = _("Isikukoodiga {s} sooritust ei leitud").format(s=isikukood)

        elif hindaja.testikoht_id and hindaja.testikoht_id != tos.testikoht_id and not toimumisaeg.muu_koha_hindamine(hindaja.valimis, hindaja.liik):
            # saab ainult oma soorituskoha töid hinnata                    
            error = _("Sooritus {s} on teisest soorituskohast").format(s=tos.tahised)
        elif hindaja.testikoht_id and hindaja.testikoht_id == tos.testikoht_id and toimumisaeg.muu_koha_hindamine(hindaja.valimis, hindaja.liik):
            # saab ainult muu soorituskoha töid hinnata                    
            error = _("Oma soorituskoha sooritajaid ei või hinnata")
        elif not sooritaja.valimis and hindaja.valimis:
            error = _("Sooritus {s} on väljaspool valimit").format(s=tos.tahised)
        elif sooritaja.valimis and not hindaja.valimis:
            error = _("Sooritus {s} on valimis").format(s=tos.tahised)            
        elif hindaja.lang != tos.sooritaja.lang:
            error = _("Soorituse {s} keel ({lang}) ei vasta hindaja rollile").format(s=tos.tahised, lang=tos.sooritaja.lang_nimi)
        elif tos.staatus != const.S_STAATUS_TEHTUD:
            error = _("Sooritus {s1} on olekus {s2}").format(s1=tos.tahised, s2=tos.staatus_nimi)
        elif toimumisaeg.oma_prk_hindamine and \
                tos.testikoht.koht.piirkond_id not in hindaja.kasutaja.get_kasutaja_piirkonnad_id():
            error = _("Sooritus {s} on teisest piirkonnast, mida pole lubatud hinnata").format(s=tos.tahised)
        else:
            holek = tos.give_hindamisolek(hindamiskogum)

            # kontrollida, et sellel tööl peab olema minu liiki hindamine
            if hindaja.liik > holek.hindamistase:
                error = _("Testitöö {s1} ei vaja hindamist {s2}").format(s1=tos.tahised, s2=hindaja.liik)
                holek = None
            else:
                # kontrollida, et sellel tööl ei oleks minu liigile vastavat hindamist
                hindamine = holek.get_hindamine(hindaja.liik)
                if hindamine and hindamine.labiviija_id and hindamine.labiviija != hindaja:
                    error = _("Testitööl {s} on juba hindaja").format(s=tos.tahised)
                    holek = None
    return holek, error
        
def _choose_e_next(handler, toimumisaeg, testiosa, hindamiskogum, hindaja, check_s_id=None):
    """Otsitakse järgmine e-töö, mida hinnata
    """
    holek = error = None
    paariline = hindaja and (hindaja.hindaja1 or hindaja.get_hindaja2())
    if paariline:
        # otsime tööd, mida paariline on hinnanud, aga mina mitte
        q = (model.Hindamisolek.query
             .filter(model.Hindamisolek.hindamised.any(
                sa.and_(model.Hindamine.labiviija_id==paariline.id,
                        ~ model.Hindamine.staatus.in_((const.H_STAATUS_SUUNATUD,const.H_STAATUS_LYKATUD)),
                        model.Hindamine.tyhistatud==False)
                 ))
             .filter(~ model.Hindamisolek.hindamised.any(
                model.Hindamine.hindaja_kasutaja_id==hindaja.kasutaja_id))
             .filter(model.Hindamisolek.hindamisprobleem!=const.H_PROBLEEM_TOOPUUDU)
             )
        if check_s_id:
            q = q.filter(model.Hindamisolek.sooritus_id != check_s_id)
        holek = q.first()
        
    if not holek:
        # otsime mulle suunatud hindamata tööde seast
        q = (model.Hindamisolek.query
             .join(model.Hindamisolek.sooritus)
             .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
             .filter(model.Sooritus.toimumisaeg_id==toimumisaeg.id)
             .filter(model.Hindamisolek.hindamiskogum_id==hindamiskogum.id)
             .join(model.Hindamisolek.hindamised)
             .filter(model.Hindamine.labiviija_id==hindaja.id)
             .filter(model.Hindamine.staatus==const.H_STAATUS_HINDAMATA)
             .filter(model.Hindamine.tyhistatud==False)
             .filter(model.Hindamisolek.hindamisprobleem!=const.H_PROBLEEM_TOOPUUDU)             
             )
        if check_s_id:
            q = q.filter(model.Hindamisolek.sooritus_id != check_s_id)        
        holek = q.first()

    liik = hindaja and hindaja.liik or const.HINDAJA1
    valimis = hindaja and hindaja.valimis or False
    if not holek:
        # võtame suvalise töö, millel pole hindamise kirjet
        q = (model.Hindamisolek.query
             .join(model.Hindamisolek.sooritus)
             .filter(model.Sooritus.staatus==const.S_STAATUS_TEHTUD)
             .filter(model.Sooritus.toimumisaeg_id==toimumisaeg.id)
             .join(model.Sooritus.sooritaja)
             .filter(model.Sooritaja.lang==hindaja.lang)
             .filter(model.Sooritaja.valimis==valimis)
             .filter(model.Hindamisolek.hindamiskogum_id==hindamiskogum.id)
             .filter(model.Hindamisolek.puudus==False)
             .filter(model.Hindamisolek.mittekasitsi==False)
             .filter(model.Hindamisolek.hindamisprobleem!=const.H_PROBLEEM_TOOPUUDU)
             .filter(model.Hindamisolek.staatus!=const.H_STAATUS_HINNATUD)
             )
        if liik in (const.HINDAJA1, const.HINDAJA2):
            q = q.filter(model.Hindamisolek.hindamistase.in_((const.HINDAJA1, const.HINDAJA2)))
        else:
            q = q.filter(model.Hindamisolek.hindamistase==liik)

        # jätame välja tööd, mida sama hindaja on juba hinnanud mõnes teises rollis (mõne muu hindamise liigiga)
        q = q.filter(~ model.Hindamisolek.hindamised.any(
            model.Hindamine.hindaja_kasutaja_id==hindaja.kasutaja_id))
        if liik == const.HINDAJA3:
            if handler.request.is_ext():
                # III hindajale jagatakse tööd korraldaja poolt, ise ei võta
                return holek, error
            # ATSis saavad III hindajad ise töid võtta
            # kus on peetud vajalikuks III hindamist, kuid hindajat veel pole määratud
            q = q.filter(
                 sa.and_(model.Hindamisolek.hindamisprobleem==const.H_PROBLEEM_SISESTAMATA,
                         model.Hindamisolek.hindamistase==const.HINDAJA3,
                         ~ model.Hindamisolek.hindamised.any(sa.and_(
                             model.Hindamine.liik==const.HINDAJA3,
                             model.Hindamine.staatus!=const.H_STAATUS_LYKATUD,
                             model.Hindamine.labiviija_id!=None))
                         )
                 )
        elif not valimis and hindamiskogum.kahekordne_hindamine and not hindamiskogum.paarishindamine or \
                 valimis and hindamiskogum.kahekordne_hindamine_valim and not hindamiskogum.paarishindamine:
            # jätame välja tööd, millel on sama liiki hindamine olemas
            q = q.filter(~ model.Hindamisolek.hindamised.any(
                sa.and_(model.Hindamine.liik==liik,
                        ~ model.Hindamine.staatus.in_((const.H_STAATUS_LYKATUD, const.H_STAATUS_SUUNATUD))))
                         )
        else:
            # jätame välja tööd, millel on hindamine olemas
            q = q.filter(~ model.Hindamisolek.hindamised.any(
                  ~ model.Hindamine.staatus.in_((const.H_STAATUS_LYKATUD, const.H_STAATUS_SUUNATUD))))

        if hindaja.testikoht_id:
            # soorituskoha poolt määratud hindaja
            if toimumisaeg.muu_koha_hindamine(hindaja.valimis, hindaja.liik):
                # hindab ainult teiste soorituskohtade töid
                q = q.filter(model.Sooritus.testikoht_id!=hindaja.testikoht_id)
            else:
                # saab ainult oma soorituskoha töid hinnata
                q = q.filter(model.Sooritus.testikoht_id==hindaja.testikoht_id)

                if len(hindaja.labiviijaklassid):
                    # hindaja on määratud kindlate klasside jaoks
                    q = q.filter(sa.exists().where(
                        sa.and_(model.Labiviijaklass.labiviija_id==hindaja.id,
                                sa.func.coalesce(model.Labiviijaklass.klass,'')==sa.func.coalesce(model.Sooritaja.klass,''),
                                sa.func.coalesce(model.Labiviijaklass.paralleel,'')==sa.func.coalesce(model.Sooritaja.paralleel,'')
                                )
                        ))

        if toimumisaeg.oma_prk_hindamine:
            lubatud_piirkonnad_id = hindaja.kasutaja.get_kasutaja_piirkonnad_id()
            if not lubatud_piirkonnad_id:
                error = _("Lubatud on hinnata ainult oma piirkonnas, aga hindajale ei ole piirkondi märgitud")
            q = (q.join(model.Sooritus.testikoht)
                 .join(model.Testikoht.koht)
                 .filter(model.Koht.piirkond_id.in_(lubatud_piirkonnad_id))
                 )
        if check_s_id:
            q = q.filter(model.Hindamisolek.sooritus_id != check_s_id)

        # jätame välja need tööd, mille olen ise tagasi lykanud
        q = q.filter(~ model.Hindamisolek.hindamised.any(
            sa.and_(model.Hindamine.staatus==const.H_STAATUS_LYKATUD,
                    model.Hindamine.labiviija_id==hindaja.id))
                     )

        queries = [q]
        if testiosa.vastvorm_kood == const.VASTVORM_SH:
            # arvestada ainult neid sooritajaid, kelle protokoll on kinnitatud ES-3717
            q = q.filter(sa.exists().where(sa.and_(
                          model.Toimumisprotokoll.id==model.Sooritus.toimumisprotokoll_id,
                          model.Toimumisprotokoll.staatus.in_(
                              (const.B_STAATUS_KINNITATUD, const.B_STAATUS_EKK_KINNITATUD))
                          )))
            
            # jätame tahapoole need tööd, mida on vastatud koos sellise sooritajaga, keda hindab keegi teine
            Helivastus2 = sa.orm.aliased(model.Helivastus)
            Hindamisolek2 = sa.orm.aliased(model.Hindamisolek)
            Hindamine2 = sa.orm.aliased(model.Hindamine)
            q2 = q.filter(~ sa.exists().where(
                sa.and_(model.Helivastus.sooritus_id==model.Sooritus.id,
                        model.Helivastus.helivastusfail_id==Helivastus2.helivastusfail_id,
                        Helivastus2.sooritus_id==Hindamisolek2.sooritus_id,
                        Hindamisolek2.id==Hindamine2.hindamisolek_id,
                        Hindamisolek2.hindamiskogum_id==hindaja.hindamiskogum_id,
                        Hindamine2.liik==liik,
                        ~ Hindamine2.staatus.in_((const.H_STAATUS_LYKATUD, const.H_STAATUS_SUUNATUD)),
                        Hindamine2.labiviija_id!=hindaja.id)
                ))
            queries.insert(0, q2)

        for q in queries:
            # valime juhusliku kirje esimese 8 seast, et vähendada tõenäosust,
            # et teine hindaja võtab samal sekundil sama töö 
            for holek in q.limit(8).all():
                if random.random() < .21:
                    break

    return holek, error
