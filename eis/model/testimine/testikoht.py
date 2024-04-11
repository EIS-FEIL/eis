"Testikorralduse andmemudel"

from eis.model.entityhelper import *
from eis.model.kasutaja import Kasutaja, Kasutajakoht, Kasutajapiirkond, Kasutajagrupp_oigus, Pedagoog, Ainelabiviija
from eis.model.test import Test
from eis.model.koht import Koht, Ruum
from eis.lib.helpers import str_from_datetime
_ = usersession._
from .toimumisaeg import Toimumisaeg
from .testiruum import Testiruum
from .testipakett import Testipakett
from .testiprotokoll import Testiprotokoll
from .labiviija import Labiviija
      
class Testikoht(EntityHelper, Base): 
    """Testikoht, testi sooritamise koht ehk soorituskoht
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tahis = Column(String(3)) # testikoha tähis, unikaalne toimumisaja piires (testimiskorraga testi korral)
    tahised = Column(String(36)) # testi, testiosa, testimiskorra ja testikoha tähised, kriips vahel (testimiskorraga testi korral)
    testiosa_id = Column(Integer, ForeignKey('testiosa.id'), index=True, nullable=False) # viide testiosale
    testiosa = relationship('Testiosa', foreign_keys=testiosa_id)
    #testiosa = relationship('Testiosa', foreign_keys=testiosa_id, back_populates='testikohad')
    toimumisaeg_id = Column(Integer, ForeignKey('toimumisaeg.id'), index=True) # viide toimumisajale (puudub avaliku vaate testi korral)
    toimumisaeg = relationship('Toimumisaeg', foreign_keys=toimumisaeg_id, back_populates='testikohad')
    koht_id = Column(Integer, ForeignKey('koht.id'), index=True) # viide soorituskohale (kui avaliku testi koostaja pole pedagoog, siis võib NULL olla)
    koht = relationship('Koht', foreign_keys=koht_id, back_populates='testikohad')
    alates = Column(DateTime) # algus
    staatus = Column(Integer, sa.DefaultClause('1'), nullable=False) # olek: 0=const.B_STAATUS_KEHTETU - kehtetu; 1=const.B_STAATUS_KEHTIV - kehtiv
    testiruumid = relationship('Testiruum', order_by='Testiruum.tahis', back_populates='testikoht') 
    sooritused = relationship('Sooritus', order_by='Sooritus.tahis', back_populates='testikoht')
    labiviijad = relationship('Labiviija', back_populates='testikoht')
    testipaketid = relationship('Testipakett', back_populates='testikoht')    
    toimumisprotokollid = relationship('Toimumisprotokoll', back_populates='testikoht')
    sooritused_seq = Column(Integer, sa.DefaultClause('0'), nullable=False) # testikoha soorituste tähiste sekvents
    markus = Column(Text) # märkused
    koolinimi_id = Column(Integer, ForeignKey('koolinimi.id'), index=True) # viide testi sooritamise ajal kehtinud koha nime kirjele
    koolinimi = relationship('Koolinimi')
    koht_aadress_kood1 = Column(String(4)) # koha maakonna kood testi sooritamise ajal (statistika jaoks)
    koht_aadress_kood2 = Column(String(4)) # koha omavalitsuse kood testi sooritamise ajal (statistika jaoks)
    koht_piirkond_id = Column(Integer, ForeignKey('piirkond.id'), index=True) # koha piirkond testi sooritamise ajal (statistika jaoks)
    koht_piirkond = relationship('Piirkond')
    meeldetuletus = Column(DateTime) # viimase korraldamise meeldetuletuse saatmise aeg
    
    __table_args__ = (
        sa.UniqueConstraint('tahised'),
        )
    
    @classmethod
    def give_testikoht(cls, koht_id, testiosa_id, toimumisaeg_id=None):
        """Luuakse antud testi ja kohta siduv testikoht.
        Kui toimumisaeg_id==None, siis on tegu avaliku testiga.
        """
        q = Testikoht.query.\
            filter(Testikoht.testiosa_id==testiosa_id).\
            filter(Testikoht.toimumisaeg_id==toimumisaeg_id).\
            filter(Testikoht.koht_id==koht_id)
        testikoht = q.first()

        if testikoht is None:
            testikoht = Testikoht(toimumisaeg_id=toimumisaeg_id,
                                  testiosa_id=testiosa_id,
                                  koht_id=koht_id,
                                  staatus=const.B_STAATUS_KEHTIV)
        return testikoht

    @property
    def testipaketid_sorted(self):
        "Testipaketid keele järgi sorditult"
        return sorted(self.testipaketid, key=lambda r: lang_sort(r.lang))

    @property
    def millal(self):
        li = [tr.algus for tr in self.testiruumid if tr.algus]
        if li:
            alates = min(li)
            kuni = max(li)
        else:
            alates = kuni = None
        if alates:
            alates = alates.strftime('%d.%m.%Y')
            kuni = kuni.strftime('%d.%m.%Y')
            if alates != kuni:
                buf = '%s-%s' % (alates, kuni)
            else:
                buf = alates
        elif self.toimumisaeg:
            buf = self.toimumisaeg.millal
        else:
            buf = None
        return buf

    def gen_tahis(self):
        """Genereeritakse toimumisaja piires unikaalne tähis
        """
        if not self.tahis:
            ta = self.toimumisaeg or self.toimumisaeg_id and Toimumisaeg.get(self.toimumisaeg_id)
            if not ta:
                # pole testimiskorraga test
                self.tahis = self.koht_id
            else:
                ta.testikohad_seq += 1
                self.tahis = '%03d' % ta.testikohad_seq
                self.set_tahised()

    def set_tahised(self):
        ta = self.toimumisaeg or self.toimumisaeg_id and Toimumisaeg.get(self.toimumisaeg_id)
        self.tahised = '%s-%s' % (ta.tahised, self.tahis)
        for pakett in self.testipaketid:
            for tpr in pakett.testiprotokollid:
                tpr.set_tahised()

    def gen_testiruum_tahis(self):
        for n in range(1,1000):
            tahis = '%d' % n
            found = False
            for rcd in self.testiruumid:
                if rcd.tahis == tahis:
                    found = True
                    break

            if not found:
                return tahis

    def reset_testiprotokollid(self, sailitakoodid=False):
        """Tühjaks jäänud protokollirühmad eemaldatakse,
        alles jäävad protokollirühmad tähistatakse uuesti.
        """
        from .sooritus import Sooritus
        from .sooritaja import Sooritaja
        log.debug('RESET tpr tkoht=%s' % (self.id))

        # leiame sooritajad, kelle soorituskeel on muutunud ja kes tuleb teise paketti tõsta
        q = (Session.query(Sooritus)
             .filter(Sooritus.testikoht==self)
             .join(Sooritus.sooritaja)
             .join(Sooritus.testiprotokoll)
             .join(Testiprotokoll.testipakett)
             .filter(Testipakett.lang!=Sooritaja.lang))
        for tos in q.all():
            tos.suuna(tos.testikoht, tos.testiruum)            

        # ilma protokollirühmata sooritused pannakse protokollrühma
        q = (Session.query(Sooritus)
             .filter(Sooritus.testikoht==self)
             .filter(Sooritus.testiprotokoll_id==None)
             .order_by(Sooritus.tahis))
        for tos in q.all():
            tos.suuna(tos.testikoht, tos.testiruum)            
            
        Session.flush()
        
        testiruumid = list(self.testiruumid)
        # eemaldame tühjad protokollid
        deleted_tpr = []
        for tr in testiruumid:
            log.debug('testiruum %s' % (tr.id))
            tr.set_sooritajate_arv()

            for tpr in list(tr.testiprotokollid):
                if tpr.soorituste_arv == 0:
                    deleted_tpr.append(tpr)
                    tpr.delete()

        if sailitakoodid:
            # jätame kõik protokollide koodid alles - võib jääda auke
            return
        
        # loendame protokollid uuesti, alustades 1-st
        # tähise muutmisel lisame algul märgi '#', hiljem korjame selle ära,
        # kuna tpr.tahised on unikaalne
        cnt = 0

        tpaketid = [r for r in self.testipaketid_sorted] + [None]
        for tpakett in tpaketid:
            for tr in testiruumid:
                for tpr in tr.testiprotokollid:
                    if tpr in deleted_tpr:
                        continue
                    if tpr.testipakett == tpakett:
                        cnt += 1
                        tpr.tahis = '%02d' % (cnt)
                        tahised = '%s-%s' % (self.tahised, tpr.tahis)
                        if tahised != tpr.tahised:
                            tpr.tahised = '%s#' % tahised
                            tpr.flush()
                        log.debug('tahised=%s' % tpr.tahised)
                
        for tr in testiruumid:
            for tpr in tr.testiprotokollid:
                if tpr in deleted_tpr:
                    continue
                if tpr.tahised.endswith('#'):
                    tpr.tahised = tpr.tahised[:-1]


    def give_testiprotokoll(self, testiruum, testipakett, tahis):
        vale_r_tpr = None
        for tr in self.testiruumid:
            for tpr in tr.testiprotokollid:
                if tpr.tahis == tahis:
                    if tr == testiruum:
                        # leitud
                        return tpr
                    # sama tähis, vale ruum
                    vale_r_tpr = tpr

        # ei leitud protokolli, mis oleks õiges ruumis ja õige tähisega
        if vale_r_tpr:
            # leiti protokoll õige tähisega, aga vales ruumis
            vale_r_tpr.tahis = ''
            vale_r_tpr.tahised = ''
            Session.flush()
        # teeme uue protokolli
        rcd = Testiprotokoll(tahis=tahis,
                             tahised='%s-%s' % (self.tahised, tahis),
                             testiruum=testiruum,
                             testipakett=testipakett)
        Session.flush()
        if vale_r_tpr:
            vale_r_tpr.gen_tahis()
            Session.flush()
        return rcd
                    
    def get_sooritajatearv(self, lang=None, kursus=None, tehtud=None, valimis=None):
        from .sooritus import Sooritus
        from .sooritaja import Sooritaja

        q = (Sooritus.query
             .filter_by(testikoht_id=self.id)
             .filter(Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
             .join(Sooritus.sooritaja))
        if tehtud:
            q = q.filter(Sooritus.staatus==const.S_STAATUS_TEHTUD)
        else:
            q = q.filter(Sooritus.staatus>const.S_STAATUS_REGAMATA)
        if lang:
            q = q.filter(Sooritaja.lang==lang)
        if kursus:
            q = q.filter(Sooritaja.kursus_kood==kursus)
        if valimis is not None:
            q = q.filter(Sooritaja.valimis==valimis)
        return q.count()

    def get_sooritajatearvud(self):
        return self.toimumisaeg.get_sooritajatearvud(self.id)

    def give_testiruum(self, ruum_id=None, tahis=None, toimumispaev_id=None, valimis=None):
        tahisega = None
        for rcd in self.testiruumid:
            if tahis and tahis == rcd.tahis:
                tahisega = rcd
            if not ruum_id or rcd.ruum_id == ruum_id:
                if not tahis or tahis == rcd.tahis:
                    if valimis and not rcd.valim_lubatud:
                        # ei ole valimi sooritajale lubatud päev
                        continue
                    if not toimumispaev_id or toimumispaev_id == rcd.toimumispaev_id:
                        # kirje leitud
                        return rcd
        if tahisega:
            # tähis on juba kasutusel
            tahis = None
        rcd = Testiruum(ruum_id=ruum_id,
                        toimumispaev_id=toimumispaev_id,
                        testikoht=self,
                        tahis=tahis)
        self.set_testiruum(rcd)
        return rcd
    
    def set_testiruum(self, testiruum):
        """Seatakse testiruumi kirje andmed
        """
        testiruum.gen_tahis()
        
        toimumisaeg = self.toimumisaeg or \
            self.toimumisaeg_id and Toimumisaeg.get(self.toimumisaeg_id)

        if toimumisaeg:
            # eksamikeskuse test
            testiosa = toimumisaeg.testiosa
            vastvorm_kood = testiosa.vastvorm_kood
        else:
            # avalik test
            vastvorm_kood = const.VASTVORM_KE

        ruum = testiruum.ruum or testiruum.ruum_id and Ruum.get(testiruum.ruum_id)
        if vastvorm_kood in (const.VASTVORM_SE, const.VASTVORM_SH, const.VASTVORM_SP, const.VASTVORM_I):
            # suulise testi korral ruumi kohtade arvu ei arvesta
            kohti = None
        elif ruum:
            if vastvorm_kood == const.VASTVORM_KP:
                kohti = ruum.ptestikohti
            else:
                kohti = ruum.etestikohti

        else:
            koht = self.koht or Koht.get(self.koht_id)
            if koht:
                if vastvorm_kood == const.VASTVORM_KP:
                    kohti = koht.ptestikohti
                else:
                    kohti = koht.etestikohti
            else:
                # avaliku kasutaja avalik test, millel pole kohta
                kohti = None
        testiruum.kohti = kohti
        
        # leiame toimumisaja esimese toimumispäeva
        if toimumisaeg:
            if not testiruum.toimumispaev_id:
                for tp in toimumisaeg.toimumispaevad:
                    testiruum.toimumispaev_id = tp.id
                    testiruum.algus = tp.aeg
                    testiruum.lopp = tp.lopp
                    break
            elif not testiruum.algus:
                for tp in toimumisaeg.toimumispaevad:
                    if tp.id == testiruum.toimumispaev_id:
                        testiruum.algus = tp.aeg
                        testiruum.lopp = tp.lopp                        
                        break

        li = [tr.algus for tr in self.testiruumid if tr.algus]
        self.alates = li and min(li) or None
        return testiruum

    def get_testiruumid_opt(self, maaramata=True):
        li = []
        for rcd in self.testiruumid:
            ruum = rcd.ruum
            if not ruum and maaramata == False:
                # mitte arvestada määramata ruumiga testiruume
                continue
            r_tahis = ruum and _("ruum {s}").format(s=ruum.tahis) or _("määramata ruum")
            if rcd.algus:
                algus = ' (%s)' % str_from_datetime(rcd.algus, hour0=False)
            else:
                algus = ''
            label = f"{rcd.tahis or ''}, {r_tahis} {algus}"
            li.append((rcd.id, label))
        return li

    def opt_te_labiviijad(self, grupp_id, lisatud_labiviijad_id=None, testiruum_id=None, hindamiskogum_id=None, liik=None):
        "Tasemeeksami hindajate valik"
        q_k = self.get_valik_q(grupp_id, on_piirkond=False, on_kasutamata=False, join_ainelabiviija=True).\
              order_by(Ainelabiviija.tahis)
        opt_lv = list()
        for k, lv_tahis in q_k.all():
            q_r = (SessionR.query(Labiviija.id)
                   .filter(Labiviija.kasutajagrupp_id==grupp_id)
                   .filter(Labiviija.toimumisaeg_id==self.toimumisaeg_id)
                   .filter(Labiviija.testiruum_id==testiruum_id)
                   .filter(Labiviija.kasutaja_id==k.id))
            if hindamiskogum_id and hindamiskogum_id != '0':
                q_r = q_r.filter(Labiviija.hindamiskogum_id==hindamiskogum_id)
            if liik:
                q_r = q_r.filter(Labiviija.liik==liik)
            try:
                lv_id, = q_r.first()
            except:
                lv_id = None
            if not lv_id:
                # negatiivne id tähendab, et läbiviija kirjet ei ole veel
                lv_id = 0 - k.id
            elif lisatud_labiviijad_id and lv_id in lisatud_labiviijad_id:
                # kui on lisatud_labiviijad_id sees, siis on kirje äsja loodud
                lv_id = 0 - k.id               
            opt_lv.append((lv_id, '%s %s' % (lv_tahis, k.nimi)))
        return opt_lv

    def delete_subitems(self):
        # eemaldame testikoha läbiviijad (ruumide läbiviijad eemaldatakse koos ruumidega)
        for lv in self.labiviijad:
            if not lv.testiruum_id:
                lv.delete()
        self.delete_subrecords(['testiruumid',
                                'testipaketid',
                                'toimumisprotokollid',
                                ])

    def may_be_deleted(self):
        if len(self.sooritused):
            return False
        for rcd in self.labiviijad:
            if rcd.kasutaja_id:
                return False
        return True

    def get_testipakett(self, lang, testiruum=None):
        for rcd in self.testipaketid:
            if rcd.lang == lang and rcd.testiruum == testiruum:
                return rcd

    def give_testipakett(self, lang, testiruum=None):
        rcd = self.get_testipakett(lang, testiruum)
        if not rcd:
            rcd = Testipakett(testiruum=testiruum,
                              testikoht=self,
                              lang=lang)
        return rcd

    def get_toimumisprotokoll(self, lang, testiruum_id):
        from .toimumisprotokoll import Toimumisprotokoll

        toimumisaeg = self.toimumisaeg
        testimiskord = toimumisaeg.testimiskord
        on_testikohakaupa = not testimiskord.prot_tulemusega
        on_ruumikaupa = toimumisaeg.on_ruumiprotokoll
        
        q = Session.query(Toimumisprotokoll)
        if on_ruumikaupa:
            q = q.filter_by(testiruum_id=testiruum_id).filter_by(lang=lang)
        elif on_testikohakaupa:
            q = q.filter_by(testikoht_id=self.id).filter_by(lang=lang)
        else:
            q = (q.filter_by(testiruum_id=None)
                 .filter_by(testimiskord_id=testimiskord.id)
                 .filter_by(koht_id=self.koht_id)
                 )
        return q.first()

    def get_kiirvalik_q(self, grupp_id, on_kasutamata=True, lang=None, on_kaskkiri=True):
        """Eelistatud läbiviijate päringu koostamine
        (ainult nendest, kes on antud soorituskohaga seotud)
        """
        q = self.get_valik_q(grupp_id, on_piirkond=False, on_kasutamata=on_kasutamata, lang=lang, on_kaskkiri=on_kaskkiri)
        if q:
            q = q.join(Kasutaja.kasutajakohad).\
                filter(Kasutajakoht.koht_id==self.koht_id)
        return q

    def get_valik_q(self, grupp_id, on_piirkond=True, on_kasutamata=True, lang=None, join_ainelabiviija=False, hkogum_id=None, on_kaskkiri=True):
        """Võimalike läbiviijate päringu koostamine
        """
        q = self.toimumisaeg.get_valik_q(grupp_id,
                                         on_piirkond=False,
                                         lang=lang,
                                         join_ainelabiviija=join_ainelabiviija,
                                         on_kaskkiri=on_kaskkiri)
        koht = self.koht
        if on_piirkond:
            if koht.piirkond:
                # kontrollime, et antud piirkond sobib 
                piirkonnad_id = koht.piirkond.get_ylemad_id()
                q = q.filter(sa.or_(Kasutaja.kasutajapiirkonnad.any(Kasutajapiirkond.piirkond_id.in_(piirkonnad_id)),
                                    Kasutaja.kasutajakohad.any(Kasutajakoht.koht_id==koht.id)))
            else:
                q = q.filter(Kasutaja.kasutajakohad.any(Kasutajakoht.koht_id==koht.id))
        # kontrollime, et antud roll sobib
        if grupp_id == const.GRUPP_VAATLEJA:
            # vaatleja ei tohi samas koolis ise töötada, kus ta vaatleb
            q = q.filter(~ Kasutaja.pedagoogid.any(Pedagoog.koht_id==koht.id))

        return q

    def get_labiviijad_opt(self, grupp_id, on_kasutamata=True, lang=None):
        """Võimalike läbiviijate loetelu
        """
        q = self.get_kiirvalik_q(grupp_id, on_kasutamata=on_kasutamata, lang=lang)
        if q:
            li = [(o.id, o.nimi) for o in q.order_by(Kasutaja.nimi).all()]            
            return li
        else:
            return []

    def get_labiviija(self, kasutajagrupp_id):
        """Leitakse testikoha läbiviija, kes pole ruumiga seotud
        (see peab olema komisjoni esimees või liige)
        """
        for rcd in self.labiviijad:
            if rcd.testiruum == None:
                if kasutajagrupp_id == rcd.kasutajagrupp_id:
                    return rcd

    def create_labiviija(self, kasutajagrupp_id):
        """Tehakse testikoha läbiviija, kes pole ruumiga seotud
        """
        assert kasutajagrupp_id in (const.GRUPP_KOMISJON_ESIMEES, 
                                    const.GRUPP_KOMISJON), \
            'Ruumita saab olla ainult komisjoni liige või esimees'
        toimumisaeg = self.toimumisaeg or Toimumisaeg.get(self.toimumisaeg_id)        
        rcd = Labiviija(toimumisaeg=toimumisaeg,
                        testikoht=self,
                        testiruum=None,
                        kasutajagrupp_id=kasutajagrupp_id,
                        staatus=const.L_STAATUS_MAARAMATA)
        return rcd

    def has_permission(self, permission, perm_bit, user=None):
        """Kontrollitakse jooksva kasutaja õigust 
        antud tegevusele antud testikohas.
        """
        if not user:
            user = usersession.get_user()
        if not user:
            return False

        if user.app_name == const.APP_EKK:
            # eksamikeskuse vaate õiguste kontroll
            kasutaja = user.get_kasutaja()
            if not kasutaja:
                return False
            test = self.testiosa.test
            if test.testityyp == const.TESTITYYP_AVALIK:
                rc = test.has_permission(permission, perm_bit, user)
            else:
                koht = self.koht
                piirkond_id = koht and koht.piirkond_id or None
                rc = kasutaja.has_permission(permission, 
                                            perm_bit,
                                            koht_id=const.KOHT_EKK,
                                            piirkond_id=piirkond_id,
                                            aine_kood=test.aine_kood, 
                                            testiliigid=[test.testiliik_kood])
            return rc
        else:
            # avalikus vaates õiguste kontroll
            # kas kasutaja on antud testikohas sellises rollis läbiviija,
            # millel on niisugune õigus olemas
            q = SessionR.query(Labiviija.id, Kasutajagrupp_oigus.bitimask).\
                filter(Labiviija.testikoht_id==self.id).\
                filter(Labiviija.kasutaja_id==user.id).\
                join((Kasutajagrupp_oigus, 
                      Kasutajagrupp_oigus.kasutajagrupp_id==Labiviija.kasutajagrupp_id)).\
                filter(Kasutajagrupp_oigus.nimi==permission)
            for rcd in q.all():
                lv_id, bitimask = rcd
                if bitimask & perm_bit == perm_bit:
                    return True

            return self.koht.has_permission('avalikadmin', perm_bit, user)

