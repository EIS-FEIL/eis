"Testikorralduse andmemudel"

from eis.model.entityhelper import *
from eis.model.kasutaja import Kasutaja, Kasutajagrupp_oigus
from eis.model.test import Test
from .toimumisaeg import Toimumisaeg
from .labiviija import Labiviija
           
class Testiruum(EntityHelper, Base):
    """Testi sooritamise ruum
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tahis = Column(String(10), nullable=False) # testiruumi tähis, unikaalne testikoha piires
    markus = Column(Text) # märkus
    ruum_id = Column(Integer, ForeignKey('ruum.id'), index=True) # viide ruumile soorituskohas (kui ruum on määramata või ajutine, siis väärtus puudub)
    ruum = relationship('Ruum', foreign_keys=ruum_id, back_populates='testiruumid')
    toimumispaev_id = Column(Integer, ForeignKey('toimumispaev.id'), index=True) # päev, millal toimub
    toimumispaev = relationship('Toimumispaev', foreign_keys=toimumispaev_id, back_populates='testiruumid')
    algus = Column(DateTime) # toimumispäeva kuupäev + suulise testi korral soorituskohas valitud kell
    alustamise_lopp = Column(DateTime) # kellaaeg, millest varem peab sooritamist alustama (kutseeksami korral, kui aja_jargi_alustatav=True)
    lopp = Column(DateTime) # kellaaeg, millal hiljemalt peab sooritamine lõppema (isegi, kui piiraeg ei ole täis)
    aja_jargi_alustatav = Column(Boolean, sa.DefaultClause('0'), nullable=False) # true - lahendamist võib alustada peale algusaega; false - lahendamist võib alustada siis, kui testi administraator annab sooritajale alustamise loa (testimiskorrata testi korral)
    algusaja_kontroll = Column(Boolean, sa.DefaultClause('0'), nullable=False) # true - alustamise luba ei võimalda alustada sooritamist enne sooritamise kellaaega; false - alustamise loa olemasolul on võimalik sooritada ka enne alguse kellaaega (testimiskorrata testi korral)
    kohti = Column(Integer) # kohtade arv 
    testikoht_id = Column(Integer, ForeignKey('testikoht.id'), index=True, nullable=False) # viide testikohale
    testikoht = relationship('Testikoht', foreign_keys=testikoht_id, back_populates='testiruumid')
    labiviijad = relationship('Labiviija', back_populates='testiruum') 
    parool = Column(String(10)) # sooritajate arvutite registreerimise parool
    on_arvuti_reg = Column(Boolean) #  kas sooritajate arvutite registreerimine on nõutav (kutseeksami korral)
    arvuti_reg = Column(Integer, sa.DefaultClause('0'), nullable=False) # sooritajate arvutite registreerimine: 0=const.ARVUTI_REG_POLE - ei ole vajalik; 1=const.ARVUTI_REG_ON - on käimas; 2=const.ARVUTI_REG_LUKUS - on lõppenud
    #url_key = Column(String(32)) # EISi testisoorituse URLi osa, mida teab ainult SEB (et välistada ilma SEBita lahendamine)
    #seb_konf = deferred(Column('seb_konf', LargeBinary)) # testiruumi SEB konfifail krüpteeritud kujul    
    testiarvutid = relationship('Testiarvuti', order_by='Testiarvuti.id', back_populates='testiruum')
    sooritused = relationship('Sooritus', order_by='Sooritus.tahis', back_populates='testiruum')
    testiprotokollid = relationship('Testiprotokoll', order_by='Testiprotokoll.tahis', back_populates='testiruum')    
    toimumisprotokollid = relationship('Toimumisprotokoll', back_populates='testiruum')
    ruumifailid = relationship('Ruumifail', order_by='Ruumifail.id', back_populates='testiruum')
    bron_arv = Column(Integer, sa.DefaultClause('0'), nullable=False) # ruumi suunatud või ruumi valinud sooritajate arv, sh pooleli regamised
    sooritajate_arv = Column(Integer, sa.DefaultClause('0'), nullable=False) # regatud sooritajate arv ruumis
    valimis_arv = Column(Integer, sa.DefaultClause('0'), nullable=False) # valimis olevate regatud sooritajate arv ruumis    
    nimekiri_id = Column(Integer, ForeignKey('nimekiri.id'), index=True) # avaliku vaate testi korral viide nimekirjale
    nimekiri = relationship('Nimekiri', foreign_keys=nimekiri_id, back_populates='testiruumid')    

    _parent_key = 'testikoht_id'
    valjastusymbrikud = relationship('Valjastusymbrik', back_populates='testiruum')
    testipaketid = relationship('Testipakett', back_populates='testiruum') # ruumiga on paketid seotud ainult juhul, kui Toimumisaeg.on_ruumiprotokoll
    __table_args__ = (
        sa.UniqueConstraint('testikoht_id','tahis'),
        sa.UniqueConstraint('testikoht_id','nimekiri_id'), # avaliku vaate korral on iga nimekirja jaoks üks testiruum
        )

    def muuda_algus(self, uus_algus):
        # muudame ruumi ja selle kõigi sooritajate ajad
        vana_algus = self.algus
        self.algus = uus_algus
        testiosa = self.testikoht.testiosa
        for tpr in self.testiprotokollid:
            if not uus_algus:
                tpr.algus = None
            elif tpr.algus and tpr.algus.date() != uus_algus.date():
                tpr.algus = datetime.combine(uus_algus, tpr.algus.time())
        for tos in self.sooritused:
            if not uus_algus:
                tos.kavaaeg = None
            else:
                if testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_KP) \
                  or not tos.kavaaeg or vana_algus.hour == 0:
                    #.sooritaja alustab ruumi alguse ajal
                    tpr = tos.testiprotokoll
                    tos.kavaaeg = tpr and tpr.algus or uus_algus
                else:
                    # suulise testi sooritajal on isiklik algusaeg,
                    # mis jääb sama palju nihkesse ruumi aja suhtes kui varem
                    kavaaeg = uus_algus + (tos.kavaaeg - vana_algus)
                    # igaks juhuks kontrollime, et algus jääb sama kpv sisse
                    if kavaaeg.date() > uus_algus.date():
                        kavaaeg = uus_algus
                    tos.kavaaeg = kavaaeg
            if testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
                tos.algus = tos.kavaaeg

    def gen_tahis(self, tkoht=None):
        """Genereeritakse toimumisaja piires unikaalne tähis
        """
        from .testikoht import Testikoht

        if not self.tahis:
            if not tkoht:
                tkoht = self.testikoht or Testikoht.get(self.testikoht_id)
            for n in range(1,1000):
                tahis = '%02d' % n
                found = False
                for rcd in tkoht.testiruumid:
                    if rcd.tahis == tahis:
                        found = True
                        break

                if not found:
                    self.tahis = tahis
                    break

    def get_sooritajatearvud(self):
        from .testikoht import Testikoht
        testikoht = self.testikoht or Testikoht.get(self.testikoht_id)        
        ta = testikoht.toimumisaeg
        if ta:
            return ta.get_sooritajatearvud(self.testikoht_id, testiruum_id=self.id)

    def get_labiviija(self, kasutajagrupp_id=None, kasutaja_id=None, hindamiskogum_id=None):
        for rcd in self.labiviijad:
            if (not kasutajagrupp_id or \
                isinstance(kasutajagrupp_id, (list, tuple)) and rcd.kasutajagrupp_id in kasutajagrupp_id or \
                rcd.kasutajagrupp_id == kasutajagrupp_id) \
                and \
                (not kasutaja_id or kasutaja_id == rcd.kasutaja_id) \
                and \
                (not hindamiskogum_id or hindamiskogum_id == rcd.hindamiskogum_id):
                return rcd

    def create_labiviija(self, kasutajagrupp_id):
        from .testikoht import Testikoht
        testikoht = self.testikoht or Testikoht.get(self.testikoht_id)
        toimumisaeg = testikoht.toimumisaeg or Toimumisaeg.get(testikoht.toimumisaeg_id)        
        rcd = Labiviija(toimumisaeg=toimumisaeg,
                        testikoht=testikoht,
                        testiruum=self,
                        kasutajagrupp_id=kasutajagrupp_id,
                        staatus=const.L_STAATUS_MAARAMATA)
        if kasutajagrupp_id == const.GRUPP_HINDAJA_S:
            rcd.liik = const.HINDAJA1
        elif kasutajagrupp_id == const.GRUPP_HINDAJA_S2:
            rcd.liik = const.HINDAJA2
        if rcd.liik:
            # on hindaja (peab pärast ka hindamiskogumi määrama)
            rcd.toode_arv = rcd.hinnatud_toode_arv = rcd.tasu_toode_arv = 0
        return rcd

    def give_labiviija(self, kasutajagrupp_id, required, allowed=None, hindamiskogum_id=None):
        """Leitakse antud rollis läbiviija kirje.
        Kui seda rolli on vaja ja seda pole, siis luuakse.
        Kui roll pole lubatud, aga see on olemas, siis märgitakse kehtetuks.
        """
        rcd = self.get_labiviija(kasutajagrupp_id=kasutajagrupp_id, hindamiskogum_id=hindamiskogum_id)
        if required:
            if not rcd:
                rcd = self.create_labiviija(kasutajagrupp_id)
                rcd.hindamiskogum_id = hindamiskogum_id
        elif not allowed:
            if rcd:
                # eemaldame kõik selle grupiga läbiviijad
                for rcd in self.labiviijad:
                    if rcd.kasutajagrupp_id == kasutajagrupp_id and \
                        (not hindamiskogum_id or hindamiskogum_id == rcd.hindamiskogum_id):
                        if not (rcd.kasutaja_id or rcd.kasutaja):
                            # kasutajat pole veel määratud
                            rcd.delete()
                        else:
                            rcd.staatus = const.L_STAATUS_KEHTETU
                rcd = None
        return rcd
            
    def give_labiviijad(self, testikoht=None):
        from .testikoht import Testikoht
        if not testikoht:
            testikoht = self.testikoht or Testikoht.get(self.testikoht_id)
        toimumisaeg = testikoht.toimumisaeg or Toimumisaeg.get(testikoht.toimumisaeg_id)
        testiosa = toimumisaeg.testiosa
        test = toimumisaeg.testimiskord.test
        if test.testityyp == const.TESTITYYP_KONS:
            self.give_labiviija(const.GRUPP_KONSULTANT, True)
            return

        self.give_labiviija(const.GRUPP_VAATLEJA, toimumisaeg.vaatleja_maaraja)
        
        if testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP):
            for hkogum in testiosa.hindamiskogumid:
                # ES-1746 - võime eeldada, et suulises testiosas on täpselt 1 hindamiskogum
                if not hkogum.staatus:
                    # hindamiskogum pole aktiivne, läbiviijaid pole vaja
                    on_hindaja1 = on_hindaja2 = False
                elif testiosa.vastvorm_kood == const.VASTVORM_SP:
                    # SP: kui hindaja on määratud, siis on alati seotud testiruumiga 
                    on_hindaja1 = toimumisaeg.hindaja1_maaraja
                    on_hindaja2 = toimumisaeg.hindaja2_maaraja
                else:
                    # SH: ainult soorituskohas määratud hindajad on seotud testiruumiga
                    on_hindaja1 = toimumisaeg.hindaja1_maaraja == const.MAARAJA_KOHT
                    on_hindaja2 = toimumisaeg.hindaja2_maaraja == const.MAARAJA_KOHT
                        
                self.give_labiviija(const.GRUPP_HINDAJA_S, on_hindaja1, hindamiskogum_id=hkogum.id)
                self.give_labiviija(const.GRUPP_HINDAJA_S2, on_hindaja2, hindamiskogum_id=hkogum.id)
        else:
            # kirjalikel testidel ei ole hindajad kunagi testiruumiga seotud
            self.give_labiviija(const.GRUPP_HINDAJA_S, False)
            self.give_labiviija(const.GRUPP_HINDAJA_S2, False)
            
        if testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP, const.VASTVORM_I):
            self.give_labiviija(const.GRUPP_INTERVJUU, toimumisaeg.intervjueerija_maaraja)
        else:
            self.give_labiviija(const.GRUPP_INTERVJUU, False)
            
        self.give_labiviija(const.GRUPP_T_ADMIN, toimumisaeg.admin_maaraja)        

        if toimumisaeg.esimees_maaraja:
            # peab olema määratud esimees
            if toimumisaeg.on_ruumiprotokoll:
                # SE ja TE eksamite korral on igas ruumis oma esimees
                self.give_labiviija(const.GRUPP_KOMISJON_ESIMEES, toimumisaeg.esimees_maaraja, True)
            else:
                rcd = testikoht.get_labiviija(const.GRUPP_KOMISJON_ESIMEES)
                if not rcd:
                    rcd = testikoht.create_labiviija(const.GRUPP_KOMISJON_ESIMEES)

        if toimumisaeg.komisjoniliige_maaraja:
            # peab olema määratud komisjoniliige
            if toimumisaeg.on_ruumiprotokoll:
                # SE ja TE eksamite korral on igas ruumis oma esimees
                self.give_labiviija(const.GRUPP_KOMISJON, toimumisaeg.komisjoniliige_maaraja, True)
            else:
                rcd = testikoht.get_labiviija(const.GRUPP_KOMISJON)
                if not rcd:
                    rcd = testikoht.create_labiviija(const.GRUPP_KOMISJON)

    def opt_labiviijad(self, grupp_id, lisatud_labiviijad_id=[], hindamiskogum_id=None, liik=None):
        "Suulise testi hindajate ja intervjueerijate valik"
        # EH-354: lubame valida kõigi antud testikoha hindajate seast, ei pea olema õigesse ruumi määratud
        q_k = (SessionR.query(Labiviija.kasutaja_id, Labiviija.tahis, Kasutaja.nimi)
                .distinct()
                .filter(Labiviija.testikoht_id==self.testikoht_id)
                .filter(Labiviija.kasutajagrupp_id==grupp_id)  
                .join(Labiviija.kasutaja)
                .order_by(Labiviija.tahis))
        opt_lv = list()
        for k_id, lv_tahis, k_nimi in q_k.all():
            lv_id = None
            q_r = (SessionR.query(Labiviija.id)
                   .filter(Labiviija.kasutajagrupp_id==grupp_id)
                   .filter(Labiviija.testiruum_id==self.id)
                   .filter(Labiviija.kasutaja_id==k_id)
                   .order_by(Labiviija.id))
            if hindamiskogum_id and hindamiskogum_id != '0':
                q_r = q_r.filter(Labiviija.hindamiskogum_id==hindamiskogum_id)
            if liik:
                q_r = q_r.filter(Labiviija.liik==liik)

            for r_id, in q_r.all():
                lv_id = r_id
                break
            if not lv_id:
                # negatiivne id tähendab, et läbiviija kirjet ei ole veel
                lv_id = 0 - k_id
            elif lisatud_labiviijad_id and lv_id in lisatud_labiviijad_id:
                # kui on lisatud_labiviijad_id sees, siis on kirje äsja loodud
                lv_id = 0 - k_id               
            opt_lv.append((lv_id, '%s %s' % (lv_tahis, k_nimi)))
        return opt_lv

    def opt_te_labiviijad(self, grupp_id, lisatud_labiviijad_id=None, hindamiskogum_id=None, liik=None):
        "Tasemeeksami hindajate valik"
        return self.testikoht.opt_te_labiviijad(grupp_id, lisatud_labiviijad_id, testiruum_id=self.id, hindamiskogum_id=hindamiskogum_id, liik=liik)
        
    @property
    def vabukohti(self):
        if self.sooritajate_arv is None:
            self.sooritajate_arv = 0
        if self.kohti is not None:
            return self.kohti - self.sooritajate_arv

    def set_sooritajate_arv(self):
        from eis.model.testimine.sooritus import Sooritus
        from eis.model.testimine.sooritaja import Sooritaja
        assert self.id, 'flush puudub'

        # kohta suunatud või koha valinud sooritajate arv, sh pooleli regamised
        q = (Session.query(sa.func.count(Sooritus.id))
             .filter(Sooritus.testiruum_id==self.id)
             )
        self.bron_arv = q.scalar()

        # regatud sooritajate arv
        q = (q.filter(Sooritus.staatus>=const.S_STAATUS_TASUMATA)
             .filter(Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
             )
        self.sooritajate_arv = q.scalar()

        # regatud valimi sooritajate arv
        q = (q.join(Sooritus.sooritaja)
             .filter(Sooritaja.valimis==True)
             )
        self.valimis_arv = q.scalar()
        return self.sooritajate_arv
   
    def give_valjastusymbrik(self, valjastusymbrikuliik_id, testipakett_id, kursus):
        for ymbrik in self.valjastusymbrikud:
            if ymbrik.valjastusymbrikuliik_id == valjastusymbrikuliik_id and \
                    ymbrik.testipakett_id == testipakett_id and \
                    ymbrik.kursus_kood == kursus:
                return ymbrik
            
        from .valjastusymbrik import Valjastusymbrik
        ymbrik = Valjastusymbrik(valjastusymbrikuliik_id=valjastusymbrikuliik_id,
                                 testipakett_id=testipakett_id,
                                 kursus_kood=kursus)
        self.valjastusymbrikud.append(ymbrik)
        return ymbrik

    def fix_toimumispaev(self):
        "Kas ruumi toimumispäev on muutmatult paika pandud"
        from eis.model.testimine.sooritus import Sooritus        
        q = (SessionR.query(sa.func.count(Sooritus.id))
             .filter(Sooritus.testiruum_id==self.id)
             .filter(Sooritus.reg_toimumispaev_id!=None)
             .filter(Sooritus.reg_toimumispaev_id==self.toimumispaev_id)
             )
        return q.scalar() > 0

    @property
    def valim_lubatud(self):
        "Kas ruumi aeg sobib valimi sooritajatele"
        tpv = self.toimumispaev
        return not (tpv and tpv.valim == False)

    def get_other_in_tk(self, testimiskord_id, tr_id=None):
        "Leitakse sama ruumi teised testiruumid samal testimiskorral"
        from .testikoht import Testikoht
        if not self.ruum_id:
            # määramata ruumiga testiruum
            return []
        q = (SessionR.query(Testiruum.id)
             .filter(Testiruum.ruum_id==self.ruum_id)
             .filter(Testiruum.id!=self.id)
             .join(Testiruum.testikoht)
             .join(Testikoht.toimumisaeg)
             .filter(Toimumisaeg.testimiskord_id==testimiskord_id)
             )
        if tr_id:
            q = q.filter(Testiruum.id==tr_id)
        return [tr_id for tr_id, in q.order_by(Testiruum.id).all()]
    
    def delete_subitems(self):    
        self.delete_subrecords(['testiarvutid',
                                'labiviijad',
                                'testiprotokollid',
                                'valjastusymbrikud',
                                'testipaketid',
                                'ruumifailid',
                                'toimumisprotokollid',
                                ])

    def has_permission(self, permission, perm_bit, user=None):
        """Kontrollitakse jooksva kasutaja õigust 
        antud tegevusele antud testikohas.
        """
        if not user:
            user = usersession.get_user()
        if not user:
            return False

        testikoht = self.testikoht
        test = testikoht.testiosa.test
        koht = testikoht.koht
        
        if user.app_name == const.APP_EKK:
            # eksamikeskuse vaate õiguste kontroll
            kasutaja = user.get_kasutaja()
            if not kasutaja:
                return False
            piirkond_id = koht.piirkond_id
            rc = kasutaja.has_permission(permission, 
                                         perm_bit,
                                         koht_id=const.KOHT_EKK,
                                         piirkond_id=piirkond_id,
                                         aine_kood=test.aine_kood, 
                                         testiliigid=[test.testiliik_kood])
            return rc
        else:
            # avaliku vaate kasutaja
            if user.has_permission('avtugi', perm_bit):
                return True            

            if permission in ('omanimekirjad','testiadmin','thindamine'):
                # avalikus vaates testiga seotud andmete vaatamine
                # kui pole testimiskorraga test, siis piisab nimekirja õigusest
                nimekiri = self.nimekiri
                if nimekiri and nimekiri.has_permission(permission, perm_bit, user):
                    return True
                if test.avaldamistase in (const.AVALIK_OPETAJAD, const.AVALIK_MAARATUD):
                    # kontrollime avaldamise ajavahemikku
                    dt = date.today()
                    if test.avalik_alates and test.avalik_alates > dt or \
                           test.avalik_kuni and test.avalik_kuni < dt:
                        # pole enam avalik test
                        log.info('Test %s pole enam avalik' % test.id)
                        return False

            # kas kasutaja on antud testikohas sellises rollis läbiviija,
            # millel on niisugune õigus olemas
            q = SessionR.query(Labiviija.id, Kasutajagrupp_oigus.bitimask).\
                filter(Labiviija.testiruum_id==self.id).\
                filter(Labiviija.kasutaja_id==user.id).\
                join((Kasutajagrupp_oigus, 
                      Kasutajagrupp_oigus.kasutajagrupp_id==Labiviija.kasutajagrupp_id)).\
                filter(Kasutajagrupp_oigus.nimi==permission)

            for rcd in q.all():
                lv_id, bitimask = rcd
                if bitimask & perm_bit == perm_bit:
                    return True

            if koht.has_permission('avalikadmin', perm_bit, user):
                return True

            # kui testi liik on tasemeeksam ja kasutaja on intervjueerija, 
            # siis on tal komisjoni esimehe õigus
            if test.testiliik_kood == const.TESTILIIK_TASE:
                otsigrupp_id = const.GRUPP_INTERVJUU
                on_grupp = SessionR.query(Labiviija.id).\
                           filter(Labiviija.testiruum_id==self.id).\
                           filter(Labiviija.kasutaja_id==user.id).\
                           filter(Labiviija.kasutajagrupp_id==otsigrupp_id).\
                           first()
                if on_grupp:
                    q = SessionR.query(Kasutajagrupp_oigus.bitimask).\
                        filter(Kasutajagrupp_oigus.kasutajagrupp_id==const.GRUPP_KOMISJON_ESIMEES).\
                        filter(Kasutajagrupp_oigus.nimi==permission)
                    for bitimask, in q.all():
                        if bitimask & perm_bit == perm_bit:
                            return True

