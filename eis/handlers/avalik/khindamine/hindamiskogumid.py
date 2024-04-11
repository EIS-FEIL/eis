from eis.lib.baseresource import *
_ = i18n._

log = logging.getLogger(__name__)

class HindamiskogumidController(BaseResourceController):
    """Kirjalik hindamine - otsinguvorm
    """
    _permission = 'khindamine'
    _MODEL = model.Labiviija
    _INDEX_TEMPLATE = 'avalik/khindamine/hindamiskogumid.mako'
    _LIST_TEMPLATE = 'avalik/khindamine/hindamiskogumid_list.mako'
    _DEFAULT_SORT = 'hindamiskogum.id'
    _SEARCH_FORM = forms.avalik.hindamine.OtsingForm 
    _actions = 'index,update'
    
    def _query(self):
        # Nimistus näidatakse kehtivad ja järgmistele tingimustele vastavad testihindaja kirjed:
        # - kasutaja on märgitud hindajaks
        # - testi toimumisaja andmetes on märge, et on lubatud testi tulemuste sisestamine hindajate poolt,
        # - toimumisaja tulemused ei ole märgitud kinnitamisel olevateks või kinnitatuteks

        q = (model.SessionR.query(model.Labiviija,
                                 model.Hindamiskogum,
                                 model.Toimumisaeg,
                                 model.Koht.nimi,
                                 model.Testiruum.tahis,
                                 model.Testiruum.id)
             .filter(model.Labiviija.kasutaja_id==self.c.user.id)
             .filter(model.Labiviija.staatus!=const.L_STAATUS_KEHTETU)
             .join(model.Labiviija.toimumisaeg)
             .join(model.Toimumisaeg.testiosa)
             .join(model.Labiviija.hindamiskogum)
             .join(model.Toimumisaeg.testimiskord)
             .filter(model.Testimiskord.tulemus_kinnitatud==False)
             .filter(model.Toimumisaeg.on_hindamisprotokollid==1)
             .filter(model.Labiviija.liik<=const.HINDAJA3)
             .join(model.Testiosa.test)
             .outerjoin(model.Labiviija.testiruum)
             .outerjoin(model.Testiruum.testikoht)
             .outerjoin(model.Testikoht.koht)
             )
        return q

    def _search_default(self, q):
        return self._search(q)

    def _search(self, q):
        c = self.c
        if c.test_id:
            q_test = q = q.filter(model.Testiosa.test_id==int(c.test_id))
        if c.aine:
            q = q.filter(model.Test.aine_kood==c.aine)
        if c.testiosa_tahis:
            q = q.filter(model.Testiosa.tahis==c.testiosa_tahis)
        if c.vastvorm:
            q = q.filter(model.Testiosa.vastvorm_kood==c.vastvorm)
        if c.alates:
            q = q.filter(model.Toimumisaeg.kuni>=c.alates)
        if c.kuni:
            q = q.filter(model.Toimumisaeg.alates<=c.kuni) 
        if c.testsessioon_id:
            q = q.filter(model.Testimiskord.testsessioon_id==c.testsessioon_id)
        if c.lang:
            q = q.filter(model.Labiviija.lang==c.lang)
        if c.t_nimi:
            q = q.filter(model.Test.nimi.ilike('%' + c.t_nimi + '%'))
        if c.hinnatud == 't':
            # ainult ära hinnatud:
            # kõik mulle määratud hindamised on kinnitatud
            # ja planeeritud hindamiste arv on täis või rohkem hinnatavaid töid pole
            Maaramata = _filter_maaramata_search()
            q = (q.filter(model.Labiviija.hinnatud_toode_arv>=model.Labiviija.toode_arv)
                 .filter(sa.or_(model.Labiviija.planeeritud_toode_arv<=model.Labiviija.hinnatud_toode_arv,
                                ~ sa.exists().where(Maaramata))
                                )
                 )

        elif not c.hinnatud:
            # ainult pooleliolevad:
            # mulle määratud tööde seas on veel kinnitamata hindamisi
            # või leidub määramata töid, mida saan hindamisele võtta
            Maaramata = _filter_maaramata_search()
            q = (q.filter(sa.or_(
                model.Labiviija.hinnatud_toode_arv<model.Labiviija.toode_arv,
                sa.and_(sa.exists().where(Maaramata),
                        sa.or_(model.Labiviija.planeeritud_toode_arv==None,
                               model.Labiviija.planeeritud_toode_arv>model.Labiviija.toode_arv)
                        )
                )))
        if c.test_id and q.count() == 0:
            # kui testi ID on antud, aga tulemusi pole, siis selgitatakse,
            # miks see test ei vasta tingimustele
            other_result = q_test.count() > 0
            self._explain_test(other_result, q_test)
            # kuvatakse tulemused ainult testi ID järgi, muid otsingutingimusi arvestamata
            q = q_test            

        c.header = self._prepare_header()
        c.prepare_item = self._prepare_item

        self._get_opt()
        return q

    def _explain_test(self, other_result, q_test):
        c = self.c
        errors = []

        def join_ja(li):
            if len(li) > 1:
                return ', '.join(li[:-1]) + _(" ja ") + li[-1]
            elif len(li) == 1:
                return li[-1]
            else:
                return ''

        def check_perm(q, test):
            ferrors = []
            q1 = (q.join(model.Test.nimekirjad)
                  .filter(model.Test.opetajale_peidus==False)
                  .filter(model.Nimekiri.testimiskord_id==None)
                  .join(model.Nimekiri.testiruumid)
                  )
            
            q = q.join(model.Test.testimiskorrad)
            if q.count() == 0:
                ferrors.append(_("Testi pole tsentraalselt korraldatud."))
            if not ferrors:
                q = q.filter(model.Testimiskord.tulemus_kinnitatud==False)
                if q.count() == 0:
                    ferrors.append(_("Testi tulemused on juba kinnitatud."))
            if not ferrors:
                q = (q.join(model.Testimiskord.toimumisajad)
                     .filter(model.Toimumisaeg.on_hindamisprotokollid==1))
                if q.count() == 0:
                    ferrors.append(_("Toimumisajal pole hindamisprotokolle."))
            if not ferrors:
                q = (q.join(model.Toimumisaeg.labiviijad)
                     .filter(model.Labiviija.kasutaja_id==c.user.id)
                     .filter(model.Labiviija.liik!=None))
                if q.count() == 0:
                    ferrors.append(_("Kasutaja pole selle testi hindajaks määratud."))
                else:
                    q = q.filter(model.Labiviija.liik<=const.HINDAJA3)
                    if q.count() == 0:
                        ferrors.append(_("III hindamine toimub siseveebis, mitte avalikus vaates."))
                    else:
                        q = q.filter(model.Labiviija.staatus!=const.L_STAATUS_KEHTETU)
                        if q.count() == 0:
                            ferrors.append(_("Läbiviijaks määramine on muudetud kehtetuks."))

            # kas on ise korraldatud test?
            q1r = q1.filter(model.Nimekiri.esitaja_kasutaja_id==self.c.user.id)
            if q1r.count() > 0:
                url = self.url('rhindamised', test_id=test.id)
                ferrors.append(_('Ise korraldatud testi hindamine toimub <a href="{url}">minu korraldatud testide</a> menüüs.').format(url=url))
                
            q1m = q1.join((model.Labiviija,
                    sa.and_(model.Labiviija.testiruum_id==model.Testiruum.id,
                            model.Labiviija.kasutaja_id==self.c.user.id,
                            model.Labiviija.kasutajagrupp_id==const.GRUPP_HINDAJA_K)))
            if q1m.count() > 0:
                url = self.url('muudhindamised', test_id=test.id)
                ferrors.append(_('Teiste läbiviijate poolt korraldatud testi hindamine toimub <a href="{url}">muude testide</a> menüüs.').format(url=url))                
             
                            
            return ferrors
            
        def check_filter(q, test):
            # otsingutingimuste kontroll
            ferrors = []
            if c.aine:
                if test.aine_kood != c.aine:
                    ferrors.append(_("õppeaine"))
            if c.testiosa_tahis:
                q1 = q.filter(model.Testiosa.test_id==test.id)
                if q1.count() == 0:
                    ferrors.append(_("testiosa tähis"))
            if c.vastvorm:
                q1 = q.filter(model.Testiosa.vastvorm_kood==c.vastvorm)
                if q1.count() == 0:
                    ferrors.append(_("vastamise vorm"))
            if c.alates or c.kuni:
                q1 = q
                if c.alates:
                    q1 = q1.filter(model.Toimumisaeg.kuni>=c.alates)
                if c.kuni:
                    q1 = q1.filter(model.Toimumisaeg.alates<=c.kuni)
                if q1.count() == 0:
                    ferrors.append(_("toimumise algusaeg"))
            if c.testsessioon_id:
                q1 = q.filter(model.Testimiskord.testsessioon_id==c.testsessioon_id)
                if q1.count() == 0:
                    ferrors.append(_("testsessioon"))
            if c.lang:
                q1 = q.filter(model.Labiviija.lang==c.lang)
                if q1.count() == 0:
                    ferrors.append(_("keel"))
            if c.t_nimi:
                q1 = q.filter(model.Test.nimi.ilike('%' + c.t_nimi + '%'))
                if q1.count() == 0:
                    ferrors.append(_("testi nimetus"))
            if ferrors:
                return _("Testil on erinev {omadused}.").format(omadused=join_ja(ferrors))

        def check_hinnatud(q):
            ferrors = []
            if c.hinnatud == 't':
                # ainult ära hinnatud:
                # kõik mulle määratud hindamised on kinnitatud
                # ja planeeritud hindamiste arv on täis või rohkem hinnatavaid töid pole
                Maaramata = _filter_maaramata_search()
                q1 = (q.filter(model.Labiviija.hinnatud_toode_arv>=model.Labiviija.toode_arv)
                     .filter(sa.or_(model.Labiviija.planeeritud_toode_arv<=model.Labiviija.hinnatud_toode_arv,
                                    ~ sa.exists().where(Maaramata))
                                    )
                     )
                if q1.count() == 0:
                    ferrors.append(_("Kõik tööd pole hinnatud."))
            elif not c.hinnatud:
                # ainult pooleliolevad:
                # mulle määratud tööde seas on veel kinnitamata hindamisi
                # või leidub määramata töid, mida saan hindamisele võtta
                Maaramata = _filter_maaramata_search()
                q1 = (q.filter(sa.or_(
                    model.Labiviija.hinnatud_toode_arv<model.Labiviija.toode_arv,
                    sa.and_(sa.exists().where(Maaramata),
                            sa.or_(model.Labiviija.planeeritud_toode_arv==None,
                                   model.Labiviija.planeeritud_toode_arv>model.Labiviija.toode_arv)
                            )
                    )))
                if q1.count() == 0:
                    ferrors.append(_("Testis pole hindamata töid."))
            return ferrors
        
        q = model.SessionR.query(model.Test).filter_by(id=c.test_id)
        test = q.first()
        if test:
            # test on olemas
            if other_result:
                # test on kättesaadav, aga ei vasta otsingutingimustele
                err = check_filter(q_test, test)
                if err:
                    errors.append(err)
                errors.extend(check_hinnatud(q_test))
            else:
                errors.extend(check_perm(q, test))

            if errors:
                if other_result:
                    err = _("Kuvatakse test {id}, aga see ei vasta otsingutingimustele.").format(id=test.id)
                else:
                    err = _("Test {id} ei vasta otsingutingimustele.").format(id=test.id)
                msg = err + ' ' + ' '.join(errors)
                self.warning(msg)
   
    def _get_opt(self):
        c = self.c
        q = (model.SessionR.query(model.Test.aine_kood).distinct()
             .join(model.Test.testiosad)
             .join(model.Testiosa.toimumisajad)
             .join(model.Toimumisaeg.labiviijad)
             .filter(model.Labiviija.kasutaja_id==c.user.id)
             .filter(model.Labiviija.liik<=const.HINDAJA3)             
             )
        minu = [r[0] for r in q.all()]
        c.opt_aine = [r for r in c.opt.klread_kood('AINE') if r[0] in minu]

        q = (model.SessionR.query(model.Labiviija.lang).distinct()
             .filter(model.Labiviija.kasutaja_id==c.user.id)
             .filter(model.Labiviija.liik<=const.HINDAJA3)                          
             )
        minu = [r[0] for r in q.all()]
        c.opt_soorkeel = [r for r in c.opt.SOORKEEL if r[0] in minu]


    def _prepare_header(self):
        header = [('hindamiskogum.tahis', _("Hindamiskogum"), 'chk'),
                  ('test.id', _("Testi ID")),
                  ('test.nimi', _("Test")),
                  ('labiviija.liik', _("Hindamise liik")),
                  ('labiviija.lang', _("Keel")),
                  ('koht.nimi,testiruum.tahis', _("Suulise testi soorituskoht")),
                  (None, _("Alustamata hindamised"), 'alustamata'),
                  (None, _("Pooleli hindamised"), 'pooleli'),
                  (None, _("Kinnitatud hindamised"), 'kinnitatud'),
                  ]
        return header
    
    def _prepare_item(self, rcd, on_markus=False):
        lv, hk, ta, k_nimi, tr_tahis, tr_id = rcd
        testiosa = ta.testiosa
        test = testiosa.test
        h = self.h
        skoht = '%s %s' % (k_nimi or '', tr_tahis or '')
        item = [hk and hk.tahis,
                test.id,
                test.nimi,
                lv.liik_nimi,
                lv.lang_nimi,
                skoht,
                None,
                ]

        harv = HindamisteArv(lv, ta)
        s_alustamata = harv.alustamata
        lv_pooleli = harv.lv_pooleli + harv.lv_valmis
        lv_hinnatud = harv.lv_hinnatud

        if s_alustamata:
            badge = 'danger' # punane
        elif lv_pooleli:
            badge = 'warning' # kollane
        elif lv_hinnatud:
            badge = 'success' # roheline
        else:
            badge = 'secondary' # hall

        item.extend([s_alustamata,
                     lv_pooleli,
                     lv_hinnatud,
                     badge])
        return item
    
    def __before__(self):
        toimumisaeg_id = self.request.matchdict.get('toimumisaeg_id')
        if toimumisaeg_id:
            self.c.toimumisaeg = model.Toimumisaeg.get(toimumisaeg_id)

    def _has_permission(self):
        if not self.c.toimumisaeg:
            # loetelu kuvamine
            return True

        self.c.hindaja = model.Labiviija.get_hindaja_by_user(self.c.toimumisaeg.id,
                                                             user=self.c.user)
        return self.c.hindaja is not None

def _filter_maaramata(toimumisaeg_id, hk_id, hliik, lang, valimis, hindaja_id, is_q, is_p):
    # tööde otsing, mis on hindajale määramata

    # kontrollitakse hindamise olemasolu liigi järgi
    # paarishindamisega kogumi korral ei tohi ka paarishindaja olla määratud
    if is_q:
        f_hliik = sa.or_(model.Hindamine.liik==hliik,
                         sa.and_(valimis==False,
                                 model.Hindamiskogum.kahekordne_hindamine==True,
                                 model.Hindamiskogum.paarishindamine==True,
                                 model.Hindamine.liik.in_((const.HINDAJA1, const.HINDAJA2))),
                         sa.and_(valimis==True,
                                 model.Hindamiskogum.kahekordne_hindamine_valim==True,
                                 model.Hindamiskogum.paarishindamine==True,
                                 model.Hindamine.liik.in_((const.HINDAJA1, const.HINDAJA2)))
                         )
    elif is_p:
        f_hliik = model.Hindamine.liik.in_((const.HINDAJA1, const.HINDAJA2))
    else:
        f_hliik = model.Hindamine.liik==hliik

    flt = sa.and_(
        model.Hindamisolek.hindamiskogum_id==hk_id,
        model.Hindamisolek.staatus!=const.H_STAATUS_HINNATUD,
        model.Hindamisolek.hindamisprobleem!=const.H_PROBLEEM_TOOPUUDU,
        model.Sooritus.toimumisaeg_id==toimumisaeg_id,
        model.Sooritus.staatus==const.S_STAATUS_TEHTUD,
        model.Sooritaja.valimis==valimis,
        ~ model.Hindamisolek.hindamised.any(sa.and_(
            model.Hindamine.staatus!=const.H_STAATUS_LYKATUD,
            model.Hindamine.tyhistatud==False,
            f_hliik))
        )

    # suuline (hindajaga) testiosas saab hinnata ainult neid, kelle protokoll on kinnitatud ES-3717
    if is_q:
        flt = sa.and_(flt,
                      sa.or_(model.Testiosa.vastvorm_kood != const.VASTVORM_SH,
                             sa.exists().where(sa.and_(
                                 model.Toimumisprotokoll.id==model.Sooritus.toimumisprotokoll_id,
                                 model.Toimumisprotokoll.staatus.in_(
                                     (const.B_STAATUS_KINNITATUD, const.B_STAATUS_EKK_KINNITATUD))
                             )))
                      )
    else:
        qv = (model.SessionR.query(model.Testiosa.vastvorm_kood)
          .join(model.Toimumisaeg.testiosa)
          .filter(model.Toimumisaeg.id==toimumisaeg_id))
        vastvorm = qv.scalar()
        if vastvorm == const.VASTVORM_SH:
            flt = sa.and_(flt,
                          sa.exists().where(sa.and_(
                              model.Toimumisprotokoll.id==model.Sooritus.toimumisprotokoll_id,
                              model.Toimumisprotokoll.staatus.in_(
                                  (const.B_STAATUS_KINNITATUD, const.B_STAATUS_EKK_KINNITATUD))
                        )))
        
    if is_q:
        # suulise testi hindajal ei ole keelt
        flt = sa.and_(flt, sa.or_(lang==None, model.Sooritaja.lang==lang))
    elif lang:
        flt = sa.and_(flt, model.Sooritaja.lang==lang)

    # jätame välja need tööd, mille olen tagasi lykanud ja ei taha rohkem hinnata
    flt = sa.and_(flt,
                  ~ model.Hindamisolek.hindamised.any(sa.and_(
                      model.Hindamine.staatus==const.H_STAATUS_LYKATUD,
                      model.Hindamine.labiviija_id==hindaja_id))
                  )

    if hliik in (const.HINDAJA1, const.HINDAJA2):
        flt = sa.and_(flt, model.Hindamisolek.hindamistase.in_((const.HINDAJA1, const.HINDAJA2)))
    elif hliik == const.HINDAJA3:
        flt = sa.and_(flt, model.Hindamisolek.hindamistase == hliik)
    else:
        # hliik on model.Labiviija.liik
        flt = sa.and_(flt,
                      sa.or_(model.Hindamisolek.hindamistase==hliik,
                             sa.and_(hliik.in_((const.HINDAJA1, const.HINDAJA2)),
                                     model.Hindamisolek.hindamistase.in_((const.HINDAJA1, const.HINDAJA2)))
                             )
                      )
    return flt

def _filter_maaramata_search():
    flt = _filter_maaramata(model.Labiviija.toimumisaeg_id,
                            model.Labiviija.hindamiskogum_id,
                            model.Labiviija.liik,
                            model.Labiviija.lang,
                            model.Labiviija.valimis,
                            model.Labiviija.id,
                            True,
                            None)
    flt = sa.and_(
        flt,
        model.Sooritus.id==model.Hindamisolek.sooritus_id,
        model.Sooritaja.id==model.Sooritus.sooritaja_id,
        model.Sooritaja.valimis==model.Labiviija.valimis,
        sa.or_(
            model.Labiviija.testikoht_id==None,
            sa.and_(model.Labiviija.muu_koha_hindamine==None,
                    model.Sooritus.testikoht_id==model.Labiviija.testikoht_id),
            sa.and_(model.Labiviija.muu_koha_hindamine==False,
                    model.Sooritus.testikoht_id==model.Labiviija.testikoht_id),
            sa.and_(model.Labiviija.muu_koha_hindamine==True,
                    model.Sooritus.testikoht_id!=model.Labiviija.testikoht_id)
        ))
    return flt

class HindamisteArv:
    "Leitakse läbiviija alustamata määratud, pooleli ja hinnatud tööde arv"

    def __init__(self, lv, ta):
        self.lv = lv
        self.ta = ta
        self.paariline_id = self._get_paariline_id()
        
         # läbiviija pooleli ja hinnatud tööd
        q = (model.SessionR.query(sa.func.count(model.Hindamine.id))
             .filter(model.Hindamine.labiviija_id==lv.id)
             .filter(model.Hindamine.tyhistatud==False)
             .filter(model.Hindamine.sisestus==1)
             .join(model.Hindamine.hindamisolek)
             .join(model.Hindamisolek.sooritus)
             .filter(model.Sooritus.staatus < const.S_STAATUS_EEMALDATUD)
             .filter(model.Hindamisolek.hindamisprobleem!=const.H_PROBLEEM_TOOPUUDU)
             .filter(model.Hindamisolek.mittekasitsi==False))

        # minule määratud alustamata tööd, ei arvesta paarishindaja alustatud töid
        lv_hindamata = q.filter(model.Hindamine.staatus==const.H_STAATUS_HINDAMATA).scalar()

        # paarishindajale määratud tööd, mida mina pole veel alustanud
        lv_hindamata_p = self._get_alustamata_p()

        self.lv_hindamata = lv_hindamata + lv_hindamata_p
        # kui on ainult 1 hindaja, siis hiljem lisatakse määramata tööd ka lv_hindamata sisse
        # jätame meelde, kui palju on hindajale määratud hindamata töid
        self.lv_hindamata_maaratud = self.lv_hindamata
        
        # minu pooleli hindamised
        q1 = (q.filter(model.Hindamine.staatus==const.H_STAATUS_POOLELI)
              .filter(model.Hindamine.sisestatud==False))
        self.lv_pooleli = q1.scalar()

        # minu kinnitamiseks valmis hindamised
        q1 = (q.filter(model.Hindamine.staatus==const.H_STAATUS_POOLELI)
              .filter(model.Hindamine.sisestatud==True))
        self.lv_valmis = q1.scalar()

        # minu kinnitatud hindamised
        q1 = q.filter(model.Hindamine.staatus==const.H_STAATUS_HINNATUD)
        self.lv_hinnatud = q1.scalar()

        # määramata (saadaval) tööde arv
        self.maaramata = self._get_maaramata()

        # alustamata tööde arv koos jagamise infoga (võib olla tekst)
        self.alustamata = self._get_alustamata()

    def _get_alustamata_p(self):
        "Leitakse paarilise poolt alustatud hindamised, mis pole veel mulle määratud"
        if not self.paariline_id:
            return 0
        else:
             Hindamine2 = sa.orm.aliased(model.Hindamine)
             q = (model.SessionR.query(sa.func.count(model.Hindamine.id))
                  .filter(model.Hindamine.labiviija_id==self.paariline_id)
                  .filter(model.Hindamine.tyhistatud==False)
                  .filter(model.Hindamine.sisestus==1)
                  .join(model.Hindamine.hindamisolek)
                  .join(model.Hindamisolek.sooritus)
                  .filter(model.Sooritus.staatus < const.S_STAATUS_EEMALDATUD)
                  .filter(model.Hindamisolek.hindamisprobleem!=const.H_PROBLEEM_TOOPUUDU)                  
                  .filter(model.Hindamisolek.mittekasitsi==False)
                  .filter(~ sa.exists().where(sa.and_(
                      Hindamine2.hindamisolek_id==model.Hindamine.hindamisolek_id,
                      Hindamine2.labiviija_id==self.lv.id)))
                  )
             return q.scalar()
        
    def _get_maaramata(self):
        "Leitakse hindamata ja hindajale määramata tööde arv (mis on hindajale saadaval)"
        lv = self.lv
        ta = self.ta
        if lv.liik == const.HINDAJA3:
            # kolmandale hindajale määratakse tööd, ise ei saa määramata töid võtta
            return 0
        flt = _filter_maaramata(lv.toimumisaeg_id, lv.hindamiskogum_id, lv.liik, lv.lang, lv.valimis, lv.id, False, self.paariline_id)
        q = (model.SessionR.query(sa.func.count(model.Hindamisolek.id))
             .join(model.Hindamisolek.sooritus)
             .join(model.Sooritus.sooritaja)
             .filter(flt))

        if lv.testikoht_id:
            # soorituskohas määratud hindaja
            if ta.muu_koha_hindamine(lv.valimis, lv.liik):
                q = q.filter(model.Sooritus.testikoht_id!=lv.testikoht_id)
            else:
                q = q.filter(model.Sooritus.testikoht_id==lv.testikoht_id)

        if len(lv.labiviijaklassid):
            # hindaja on määratud kindlate klasside jaoks
            q = q.filter(sa.exists().where(
                sa.and_(model.Labiviijaklass.labiviija_id==lv.id,
                        sa.func.coalesce(model.Labiviijaklass.klass,'')==sa.func.coalesce(model.Sooritaja.klass,''),
                        sa.func.coalesce(model.Labiviijaklass.paralleel,'')==sa.func.coalesce(model.Sooritaja.paralleel,'')
                        )
                ))

        return q.scalar()

    def _get_hindajatearv(self):
        "Leiame kõigi hindajate arvu, kelle vahel alustamata hindamised jagatakse"
        lv = self.lv
        q = (model.SessionR.query(sa.func.count(model.Labiviija.id))
             .filter(model.Labiviija.toimumisaeg_id==lv.toimumisaeg_id)
             .filter(model.Labiviija.liik==lv.liik)
             .filter(model.Labiviija.hindamiskogum_id==lv.hindamiskogum_id)
             .filter(model.Labiviija.testikoht_id==lv.testikoht_id)
             .filter(model.Labiviija.lang==lv.lang)
             .filter(model.Labiviija.valimis==lv.valimis)
             )
        return q.scalar()

    def _get_alustamata(self):
        "Leitakse alustamata tööde arv, sh määramata (kuid saadaval) ja määratud tööd"
        lv = self.lv
        ta = self.ta
        planeeritud_arv = lv.planeeritud_toode_arv

        if planeeritud_arv is not None:
            # sooritajale on planeeritud kindel arv töid
            alustamata_arv = planeeritud_arv - self.lv_hinnatud - self.lv_pooleli - self.lv_valmis
            if self.lv_hindamata > alustamata_arv:
                # mulle määratud alustamata töid on rohkem kui planeeritud
                alustamata_arv = self.lv_hindamata
            else:
                # mulle on vaja veel töid määrata
                veel_maarata = alustamata_arv - self.lv_hindamata
                alustamata_arv = self.lv_hindamata + min(veel_maarata, self.maaramata)
            alustamata = alustamata_arv
        else:
            # sooritajale pole planeeritud tööde arvu
            jagamiseks = ''
            if self.maaramata:
                # leidub töid, millele pole hindajat määratud
                hindajate_arv = self._get_hindajatearv()
                if hindajate_arv == 1:
                    # olen ise ainuke hindaja
                    self.lv_hindamata += self.maaramata
                    self.maaramata = 0
                else:
                    # tööd jagatakse hindajate vahel
                    jagamiseks = _("{n1} ({n2} hindajat)").format(n1=self.maaramata, n2=hindajate_arv)
            if self.lv_hindamata and jagamiseks:
                alustamata = f'{jagamiseks} + {self.lv_hindamata}'
            elif self.lv_hindamata:
                alustamata = self.lv_hindamata
            else:
                alustamata = jagamiseks
        return alustamata

    def _get_paariline_id(self):
        "Leiame paarishindaja ID"
        lv = self.lv
        paariline_id = None
        if lv.on_paaris:
            # määratud mulle või paariline on juba hindama asunud
            paariline_id = lv.hindaja1_id
            if not paariline_id or paariline_id == lv.id:
                for phindaja in lv.paarishindajad:
                    if phindaja.id != lv.id:
                        paariline_id = phindaja.id
                        break
        return paariline_id

