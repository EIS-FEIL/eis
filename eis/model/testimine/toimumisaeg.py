"Testi andmemudel"
from eis.model.entityhelper import *
from eis.model.kasutaja import Kasutaja, Kasutajapiirkond, Profiil, Aineprofiil, Ainelabiviija
from eis.model.koht import Koht, Piirkond
from eis.model.test import Test, Testiosa, Testitase, Komplekt, Hindamiskogum, Alatest
_ = usersession._

class Toimumisaeg(EntityHelper, Base):
    """Testiosa toimumisaeg. Igal testimiskorral on iga testiosa jaoks oma toimumisaeg
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tahised = Column(String(32), nullable=False) # testi, testiosa ja testimiskorra tähised, kriips vahel
    alates = Column(Date) # toimumise ajavahemiku algus
    kuni = Column(Date) # toimumise ajavahemiku lõpp
    testimiskord_id = Column(Integer, ForeignKey('testimiskord.id'), index=True, nullable=False) # viide testimiskorrale
    testimiskord = relationship('Testimiskord', foreign_keys=testimiskord_id, back_populates='toimumisajad')
    testiosa_id = Column(Integer, ForeignKey('testiosa.id'), index=True, nullable=False) # viide testiosale
    testiosa = relationship('Testiosa', foreign_keys=testiosa_id)
    #testiosa = relationship('Testiosa', foreign_keys=testiosa_id, back_populates='toimumisajad')
    
    # kontroll ja hindamine
    vaatleja_maaraja = Column(Boolean) # kas eksamikeskus määrab vaatleja
    hindaja1_maaraja = Column(Integer) # hindaja1 määraja: eksamikeskus/soorituskoht/ei 
    hindaja1_maaraja_valim = Column(Integer) # valimi hindaja1 määraja: eksamikeskus/soorituskoht/ei 
    hindaja2_maaraja = Column(Integer) # hindaja2 määraja: ekk/koht/ei (suulise testi korral või kahekordse mitte-paarishindamisega kirjaliku testi korral)
    hindaja2_maaraja_valim = Column(Integer) # valimi hindaja2 määraja: ekk/koht/ei (suulise testi korral või kahekordse mitte-paarishindamisega kirjaliku testi korral)    
    intervjueerija_maaraja = Column(Integer) # kas eksamikeskus määrab intervjueerija (suulise testi korral)
    admin_maaraja = Column(Boolean) # kas on vaja testi administraatorit; p-testi korral pole vaja; e-testi korral on administraatorit vaja parajasti siis, kui on kirjalik test
    admin_teade = Column(Boolean) # kas saata testi administraatorile administraatoriks määramisel teade
    vaatleja_koolituskp = Column(Date) # kuupäev, millest varasem koolitus ei tule vaatleja puhul kõne alla
    hindaja_koolituskp = Column(Date) # kuupäev, millest varasem koolitus ei tule hindaja puhul kõne alla
    intervjueerija_koolituskp = Column(Date) # kuupäev, millest varasem koolitus ei tule intervjueerija puhul kõne alla
    verif = Column(String(1)) # verifitseerimine: V=const.VERIF_VERIFF - Veriff; P=const.VERIF_PROCTORIO - Proctorio
    verif_param = Column(String(500)) # Proctorio seaded (Proctorio korral); Veriffi integratsiooni ID konfis (Veriffi korral)
    verif_seb = Column(Boolean) # kas on kasutusel Safe Exam Browser (SEB)
    seb_konf = deferred(Column('seb_konf', LargeBinary)) # SEB konfifail XML kujul
    on_arvuti_reg = Column(Boolean) # kas sooritajate arvutite registreerimine on nõutav
    on_reg_test = Column(Boolean) # kas teistel sama testimiskorra toimumisaegadel samasse ruumi tehtud arvutite registreeringud kehtivad ka sellel toimumisajal
    kahekordne_sisestamine = Column(Boolean, sa.DefaultClause('1')) # kas on kahekordne sisestamine (enamasti on, aga eeltestide korral sisestatakse ühekordselt, kuna tulemusi on vaja vaid statistika jaoks)
    esimees_maaraja = Column(Boolean) # kas eksamikomisjoni esimehe määramine on kohustuslik
    esimees_koolituskp = Column(Date) # kuupäev, millest varasem koolitus ei tule komisjoni esimehe puhul kõne alla (TE,SE eksami korral)
    komisjoniliige_maaraja = Column(Boolean) # kas eksamikomisjoni liikme määramine on kohustuslik
    komisjoniliige_koolituskp = Column(Date) # kuupäev, millest varasem koolitus ei tule komisjoni liikme puhul kõne alla (TE,SE eksami korral)
    komisjon_maaramise_tahtaeg = Column(Date) # komisjoni esimehe ja liikmete määramise tähtaeg
    konsultant_koolituskp = Column(Date) # kuupäev, millest varasem koolitus ei tule konsultandi puhul kõne alla (konsultatsiooni korral)
    reg_labiviijaks = Column(Boolean) # kas läbiviijaks registreerimine on avatud
    hindaja_kaskkirikpv = Column(Date) # varaseim lubatud kuupäev, millal hindajad on käskkirja lisatud; kui puudub, siis ei ole hindajate käskkirja lisamine nõutav
    intervjueerija_kaskkirikpv = Column(Date) # varaseim lubatud kuupäev, millal intervjueerijad on käskkirja lisatud; kui puudub, siis ei ole intervjueerijate käskkirja lisamine nõutav    
    ruumide_jaotus = Column(Boolean) # kas on lubatud soorituskohtades ruume määrata
    ruum_voib_korduda = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas ruumi saab samal toimumispäeval kasutada sama toimumisaja mitme testiruumina
    ruum_noutud = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas korraldamisel peab määrama päris ruumi (või võib kasutada määramata ruumi)
    labiviijate_jaotus = Column(Boolean) # kas on lubatud soorituskohtades läbiviijaid määrata    
    kohad_avalikud = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas sooritajatele võib neile määratud soorituskohad avaldada (eesti.ee portaalis või soorituskohateateid saates)
    kohad_kinnitatud = Column(Boolean) # kas soorituskohtade andmed on kinnitatud (kui on kinnitatud, siis ei saa sooritajaid testimiskorrale suunata ja testiosa tähise muutmine ei too kaasa toimumisaja tähise muutmist)
    hinnete_sisestus = Column(Boolean) # kas hindajad saavad tulemusi sisestada
    oma_prk_hindamine = Column(Boolean) # kas hindaja saab hinnata ainult oma piirkonna õpilasi (või ka muid)
    oma_kooli_hindamine = Column(Boolean) # kas hindaja saab ka oma kooli töid hinnata (või ainult muude koolide õpilaste töid)
    sama_kooli_hinnatavaid = Column(Integer) # ühest koolist hinnatavate õpilaste max arv
    hindamise_algus = Column(DateTime) # hetk, millest varem ei saa hinnata
    hindamise_luba = Column(Boolean, sa.DefaultClause('1'), nullable=False) # kas hindajad võivad hinnata
    hindamise_tahtaeg = Column(Date) # hindamise tähtaeg
    protok_ryhma_suurus = Column(Integer) # sooritajaid protokollis
    samaaegseid_vastajaid = Column(Integer) # samaaegsete vastajate lubatud max arv
    tulemus_kinnitatud = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas tulemused on kinnitatud
    aja_jargi_alustatav = Column(Boolean, sa.DefaultClause('0'), nullable=False) # true - registreeritud olekus sooritajad saavad automaatselt lahendamist alustada peale algusaja saabumist, administraator ei pea selleks andma alustamise luba; false - lahendamist võib alustada siis, kui testi administraator annab sooritajale alustamise loa
    algusaja_kontroll = Column(Boolean, sa.DefaultClause('0'), nullable=False) # true - alustamise luba ei võimalda alustada sooritamist enne sooritamise kellaaega; false - alustamise loa olemasolul on võimalik sooritada ka enne alguse kellaaega
    kell_valik = Column(Boolean, sa.DefaultClause('0'), nullable=False) # true - soorituskohale saab valida ainult toimumisaja seadetes kirjeldatud kellaaja; false - soorituskohale saab kellaaja vabalt sisestada
    jatk_voimalik = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas testi administraator saab lubada sooritajal jätkata sooritamist peale seda, kui ta on sooritamise juba lõpetanud
    keel_admin = Column(Boolean) # kas testi administraator saab sooritaja soorituskeelt muuta
    eelvaade_admin = Column(Boolean) # kas testi administraator saab testi eelvaadet vaadata
    prot_admin = Column(Integer, sa.DefaultClause('1'), nullable=False) # kas testi administraator saab toimumise protokolli sisestada/kinnitada: 0=const.PROT_NULL - ei saa; 1=const.PROT_SISEST - saab sisestada, mitte kinnitada; 2=const.PROT_KINNIT - saab sisestada ja kinnitada
    prot_eikinnitata = Column(Boolean) # kui True, siis toimumise protokolle soorituskohtades ei kinnitata
    nimi_jrk = Column(Boolean) # kas PDF protokollides (üleandmisprotokollides, toimumisprotokollides, hindamisprotokollides) järjestada sooritajad nime järgi (kui ei, siis järjestatakse töö koodi järgi)
    
    # logistika
    valjastusymbrikuliigid = relationship('Valjastusymbrikuliik', order_by='Valjastusymbrikuliik.tahis', back_populates='toimumisaeg')
    valjastuskoti_maht = Column(Integer) # mitu testitööd mahub ühte kotti

    tagastusymbrikuliigid = relationship('Tagastusymbrikuliik', order_by='Tagastusymbrikuliik.tahis', back_populates='toimumisaeg')
    tagastuskoti_maht = Column(Integer) # mitu testitööd mahub ühte kotti

    # ülesandekomplektid
    komplektid = relationship('Komplekt', secondary='toimumisaeg_komplekt') # komplektid, mida antud toimumisajal kasutatakse
    #komplektid = relationship('Komplekt', secondary='toimumisaeg_komplekt', back_populates='toimumisajad') # komplektid, mida antud toimumisajal kasutatakse
    komplekt_valitav = Column(Boolean) # kas sooritaja saab ise komplekti valida (või valib süsteem juhuslikult)
    komplekt_valitav_y1 = Column(Boolean) # kui sooritaja saab komplekti valida, siis kas valida saab ainult iga komplekti esimese ülesande juures (või võib ka mujal valida)
    
    # töötasud
    vaatleja_tasu = Column(Float) # vaatleja töötasu
    vaatleja_lisatasu = Column(Float) # läbiviija lisatasu, mida makstakse vaatlejatele, komisjoniliikmetele ja komisjoniesimeestele üleajalise töö eest
    komisjoniliige_tasu = Column(Float) # eksamikomisjoni liikme tasu
    esimees_tasu = Column(Float) # eksamikomisjoni esimehe tasu
    konsultant_tasu = Column(Float) # konsultandi tasu (konsultatsiooni toimumisaja korral)
    admin_tasu = Column(Float) # testi administraatori tasu
    
    labiviijad = relationship('Labiviija', back_populates='toimumisaeg')
    testikohad = relationship('Testikoht', order_by='Testikoht.tahis', back_populates='toimumisaeg')
    sooritused = relationship('Sooritus', back_populates='toimumisaeg')
    on_kogused = Column(Integer, sa.DefaultClause('0'), nullable=False) # kas ümbrike ja kottide kogused on arvutatud
    on_ymbrikud = Column(Integer, sa.DefaultClause('0'), nullable=False) # kas ümbrike ja kottide kirjed on loodud
    on_hindamisprotokollid = Column(Integer, sa.DefaultClause('0'), nullable=False) # kas hindamisprotokollid ja muud hindamiseks vajalikud kirjed on loodud

    nousolekud = relationship('Nousolek', back_populates='toimumisaeg')

    arvutusprotsessid = relationship('Arvutusprotsess', order_by=sa.desc(sa.text('Arvutusprotsess.id')), back_populates='toimumisaeg')
    kysimusestatistikad = relationship('Kysimusestatistika', back_populates='toimumisaeg') # küsimuste statistika antud toimumisajal

    hindajad_seq = Column(Integer, sa.DefaultClause('0'), nullable=False) # toimumisaja hindajate tähiste sekvents
    labiviijad_seq = Column(Integer, sa.DefaultClause('0'), nullable=False) # toimumisaja läbiviijate tähiste sekvents
    testikohad_seq = Column(Integer, sa.DefaultClause('0'), nullable=False) # toimumisaja testikohtade tähiste sekvents
    toimumispaevad = relationship('Toimumispaev', order_by='Toimumispaev.seq', back_populates='toimumisaeg')
    __table_args__ = (
        sa.UniqueConstraint('tahised'),
        )
    _parent_key = 'testimiskord_id'
    
    @property
    def on_ruumiprotokoll(self):
        """Kas igas testiruumis on oma toimumise protokoll või on testikoha peale üks.
        Üldjuhul on tesitkoha kohta üks protokoll,
        ainult SE ja TE eksamite puhul on igal testiruumil oma protokoll.
        Vastavalt on ka komisjoni esimees kas igas testiruumis eraldi või testikoha peale üks.
        """
        return self.testimiskord.on_ruumiprotokoll

    @property
    def on_paketid(self):
        "Kas kasutatakse testipakette, st kas on p-test"
        return self.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP)
    
    @property
    def on_veriff(self):
        return self.verif == const.VERIF_VERIFF

    @property
    def on_proctorio(self):
        return self.verif == const.VERIF_PROCTORIO

    @property
    def on_hindamise_luba(self):
        "Kas hindajad võivad hinnata"
        return self.hindamise_luba and \
            (not self.hindamise_algus or self.hindamise_algus < datetime.now())
    
    def muu_koha_hindamine(self, valim, liik=None):
        "Kas koolis määratakse teiste koolide õpilaste tööde hindajad?"
        if valim:
            if liik == const.HINDAJA1:
                rc = self.hindaja1_maaraja_valim == const.MAARAJA_MUUKOHT
            elif liik == const.HINDAJA2:
                rc = self.hindaja2_maaraja_valim == const.MAARAJA_MUUKOHT
            else:
                rc = self.hindaja1_maaraja_valim == const.MAARAJA_MUUKOHT or \
                     self.hindaja2_maaraja_valim == const.MAARAJA_MUUKOHT
        else:
            if liik == const.HINDAJA1:
                rc = self.hindaja1_maaraja == const.MAARAJA_MUUKOHT
            elif liik == const.HINDAJA2:
                rc = self.hindaja2_maaraja == const.MAARAJA_MUUKOHT
            else:
                rc = self.hindaja1_maaraja == const.MAARAJA_MUUKOHT or \
                     self.hindaja2_maaraja == const.MAARAJA_MUUKOHT
        return rc

    def koolis_hindamine(self, valim, liik=None):
        "Kas koolis määratakse oma õpilaste tööde hindajad?"
        if valim:
            if liik == const.HINDAJA1:
                rc = self.hindaja1_maaraja_valim == const.MAARAJA_KOHT
            elif liik == const.HINDAJA2:
                rc = self.hindaja2_maaraja_valim == const.MAARAJA_KOHT
            else:
                rc = self.hindaja1_maaraja_valim == const.MAARAJA_KOHT or \
                     self.hindaja2_maaraja_valim == const.MAARAJA_KOHT
        else:
            if liik == const.HINDAJA1:
                rc = self.hindaja1_maaraja == const.MAARAJA_KOHT
            elif liik == const.HINDAJA2:
                rc = self.hindaja2_maaraja == const.MAARAJA_KOHT
            else:
                rc = self.hindaja1_maaraja == const.MAARAJA_KOHT or \
                     self.hindaja2_maaraja == const.MAARAJA_KOHT
        return rc

    def delete_subitems(self):    
        self.komplektid = []
        self.delete_subrecords(['valjastusymbrikuliigid',
                                'tagastusymbrikuliigid',
                                'testikohad',
                                'toimumispaevad',
                                #'alatestikorrad',
                                ])

    def set_tahised(self):
        from .testimiskord import Testimiskord

        testimiskord = self.testimiskord or Testimiskord.get(self.testimiskord_id)
        testiosa = self.testiosa or Testiosa.get(self.testiosa_id)
        test = testiosa.test
        self.tahised = '%s-%s-%s' % (test.id, testiosa.tahis, testimiskord.tahis)

        for tkoht in self.testikohad:
            tkoht.set_tahised()

    @property
    def millal(self):
        buf = ''
        if self.alates:
            buf = self.alates.strftime('%d.%m.%Y')
            if self.kuni:
                kuni = self.kuni.strftime('%d.%m.%Y')
                if kuni != buf:
                    buf += '–' + kuni
        return buf

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .testimiskord import Testimiskord

        testimiskord = self.testimiskord or self.testimiskord_id and Testimiskord.get(self.testimiskord_id)
        if testimiskord:
            testimiskord.logi('Toimumisaeg %s (%s) %s' % (self.id, self.tahised, liik), vanad_andmed, uued_andmed, logitase)

    def copy(self):
        cp = EntityHelper.copy(self)
        self.copy_subrecords(cp, ['toimumispaevad',
                                  'tagastusymbrikuliigid',
                                  'valjastusymbrikuliigid',
                                  ])
        for k in self.komplektid:
            cp.komplektid.append(k)
        return cp

    @classmethod
    def get_opt(cls, testsessioon_id, vastvorm_kood=None, test_id=None, testimiskord_id=None, keeletase=None, testiliik_kood=None, testiliigid_kood=None, testsessioonid_id=None):
        """Leitakse kõigi testide toimumisajad antud testsessioonis
        """
        from .testimiskord import Testimiskord
        if not (testsessioon_id or testsessioonid_id):
            return []
        q = SessionR.query(Toimumisaeg.id,
                          Toimumisaeg.tahised,
                          Toimumisaeg.alates, 
                          Test.nimi)
        q = (q.join(Toimumisaeg.testimiskord)
             .join(Testimiskord.test)
             .join(Toimumisaeg.testiosa)
             .filter(Test.testityyp==const.TESTITYYP_EKK)
             )
        if testsessioon_id:
            q = q.filter(Testimiskord.testsessioon_id==testsessioon_id)
        else:
            q = q.filter(Testimiskord.testsessioon_id.in_(testsessioonid_id))

        if vastvorm_kood:
            q = q.filter(Testiosa.vastvorm_kood==vastvorm_kood)
        if test_id:
            q = q.filter(Testiosa.test_id==int(test_id))
        elif keeletase:
            q = q.filter(Test.testitasemed.any(Testitase.keeletase_kood==keeletase))
        if testimiskord_id:
            q = q.filter(Toimumisaeg.testimiskord_id==testimiskord_id)

        if testiliik_kood:
            q = q.filter(Test.testiliik_kood==testiliik_kood)
        elif testiliigid_kood:
            q = q.filter(Test.testiliik_kood.in_(testiliigid_kood))
            
        items = q.order_by(Test.nimi).all()
        return [(ta_id, '%s %s %s' % (nimi, tahised, str_from_date(ta_alates))) \
                    for (ta_id, tahised, ta_alates, nimi) in items]

    def get_sooritused(self, kasutaja_id=None, koht_id=None, ruum_id=None):
        """Leitakse soorituse kirjed
        Vajalik EKK testide korral
        """
        from eis.model.testimine import Sooritus, Sooritaja
        q = Sooritus.query.filter_by(toimumisaeg_id=self.id)
        if koht_id:
            q = q.filter_by(koht_id=koht_id)
        if ruum_id:
            q = q.filter_by(ruum_id=ruum_id)
        if kasutaja_id:
            q = q.join(Sooritus.sooritaja).\
                filter(Sooritaja.kasutaja_id==int(kasutaja_id))
        return q.all()

    def update_komplektid(self, komplektid_id):
        # komplektid_id on list komplektide id-dest
        li = [Komplekt.get(rcd_id) for rcd_id in komplektid_id]
        for rcd in li:
            if rcd not in self.komplektid:
                self.komplektid.append(rcd)
        for rcd in self.komplektid:
            if rcd not in li:
                self.komplektid.remove(rcd)

    def give_testikoht(self, koht_id):
        """Luuakse antud toimumisaega ja kohta siduv testikoht
        Seda tohib enne commitit üheainsa korra kasutada, muidu ei leita
        äsja lisatud kirjet.
        """
        from eis.model.testimine import Testikoht
        ta_id = self.id
        if ta_id:
            q = (Testikoht.query
                 .filter_by(toimumisaeg_id=ta_id)
                 .filter_by(koht_id=koht_id))
            testikoht = q.first()
        else:
            testikoht = None
        if testikoht is None:
            testikoht = Testikoht(toimumisaeg_id=ta_id,
                                  koht_id=koht_id,
                                  testiosa=self.testiosa,
                                  staatus=const.B_STAATUS_KEHTIV)
            if not ta_id:
                testikoht.toimumisaeg = self
        return testikoht

    def get_toimumispaevad_opt(self, kell=False, valim=None):
        li = []
        for tpv in self.toimumispaevad:
            if valim and tpv.valim == False:
                # ei ole valimile lubatud päev
                continue
            if kell:
                title = str_from_datetime(tpv.aeg)
                if tpv.lopp:
                    if tpv.lopp.date() == tpv.aeg.date():
                        title += ' - ' + str_from_time(tpv.lopp)
                    else:
                        title += ' - ' + str_from_datetime(tpv.lopp)
            else:
                title = str_from_date(tpv.aeg)
                if tpv.lopp and tpv.lopp.date() != tpv.aeg.date():
                    title += ' - ' + str_from_date(tpv.lopp)
                    
            li.append((tpv.id, title))
        return li

    def get_testikohad_opt(self, piirkond_id=None):
        from eis.model.testimine import Testikoht
        q = (SessionR.query(Testikoht, Koht)
             .filter(Testikoht.toimumisaeg_id==self.id)
             .join(Testikoht.koht))
        if piirkond_id:
            f = []
            prk = Piirkond.get(piirkond_id)
            for prk_id in prk.get_alamad_id():
                f.append(Koht.piirkond_id==prk_id)
            q = q.filter(sa.or_(*f))
        q = q.order_by(Koht.nimi)
        li = [(tk.id, '%s %s' % (tk.tahis, k.nimi)) for (tk, k) in q.all()]
        return li

    def get_testikoht_id(self, testikoht2_id):
        "Leitakse teise toimumisaja testikohaga samas kohas asuv selle toimumisaja testikoht"
        from eis.model.testimine import Testikoht
        if testikoht2_id:
            Testikoht2 = sa.orm.aliased(Testikoht)
            q = (SessionR.query(Testikoht.id)
                 .filter(Testikoht.toimumisaeg_id==self.id)
                 .join((Testikoht2, Testikoht2.id==testikoht2_id))
                 .filter(Testikoht.koht_id==Testikoht2.koht_id))
            for testikoht_id, in q.all():
                return testikoht_id
    
    def get_piirkonnad_opt(self):
        from eis.model.testimine import Testikoht
        q = SessionR.query(Piirkond.id, Piirkond.nimi).\
            join(Piirkond.kohad).\
            join(Koht.testikohad).\
            filter(Testikoht.toimumisaeg_id==self.id).\
            distinct().\
            order_by(Piirkond.nimi)
        li = [(r_id, r_nimi) for (r_id, r_nimi) in q.all()]
        return li

    def get_nousolek(self, kasutaja_id):
        from eis.model.testimine import Nousolek
        return Nousolek.query.filter_by(toimumisaeg_id=self.id).\
            filter_by(kasutaja_id=kasutaja_id).\
            first()

    def give_nousolek(self, kasutaja_id):
        from eis.model.testimine import Nousolek
        rcd = self.get_nousolek(kasutaja_id)
        if not rcd:
            rcd = Nousolek(toimumisaeg_id=self.id,
                           kasutaja_id=kasutaja_id)
        return rcd

    def get_labiviijad(self, kasutaja_id):
        from eis.model.testimine import Labiviija
        q = Labiviija.query.filter_by(toimumisaeg_id=self.id).\
            filter_by(kasutaja_id=kasutaja_id)
        return q.all()

    def get_labiviijagrupid_opt(self, koolis=None):
        li = []
        testiosa = self.testiosa
        on_suuline = testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP)
        if testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE):
            li.append((const.GRUPP_T_ADMIN, _("Testi administraator")))
        if koolis:
            # ainult kooli poolt määratavad rollid, aga mitte kirjalikud hindajad
            if self.hindaja1_maaraja == const.MAARAJA_KOHT and on_suuline:
                li.append((const.GRUPP_HINDAJA_S, _("1. hindaja")))
            if self.hindaja2_maaraja == const.MAARAJA_KOHT and on_suuline:
                li.append((const.GRUPP_HINDAJA_S2, _("2. hindaja")))
            if self.intervjueerija_maaraja == const.MAARAJA_KOHT:
                li.append((const.GRUPP_INTERVJUU, _("Intervjueerija")))        
        else:
            # kõik toimumisajal kasutusel olevad rollid
            if self.vaatleja_maaraja:
                li.append((const.GRUPP_VAATLEJA, _("Vaatleja")))
            if self.hindaja1_maaraja and on_suuline:
                li.append((const.GRUPP_HINDAJA_S, _("1. hindaja")))
            if self.hindaja2_maaraja and on_suuline:
                li.append((const.GRUPP_HINDAJA_S2, _("2. hindaja")))
            # kui koolis=False, siis mitte kirjalikud hindajad
            if koolis is None:
                if self.hindaja1_maaraja and not on_suuline:
                    li.append((const.GRUPP_HINDAJA_K, _("Hindaja")))
                if self.hindaja1_maaraja_valim and not on_suuline:
                    li.append((const.GRUPP_HINDAJA_K, _("Hindaja (valim)")))            
            if self.intervjueerija_maaraja:
                li.append((const.GRUPP_INTERVJUU, _("Intervjueerija")))
                
        li.append((const.GRUPP_KOMISJON_ESIMEES, _("Komisjoni esimees")))
        li.append((const.GRUPP_KOMISJON, _("Komisjoniliige")))
        return li
    
    def get_hindaja(self, kasutaja_id, liik=None, lang=None, hindamiskogum_id=None):
        for rcd in self.labiviijad:
            if rcd.kasutaja_id == kasutaja_id and \
                    rcd.hindamiskogum_id == hindamiskogum_id and \
                    rcd.liik:
                if not liik or rcd.liik == liik:
                    if not lang or rcd.lang == lang:
                        return rcd

    def get_hindaja_by_q(self, kasutaja_id, liik=None, lang=None, hindamiskogum_id=None):
        from eis.model.testimine import Labiviija
        q = (Labiviija.query
             .filter(Labiviija.kasutaja_id==kasutaja_id)
             .filter(Labiviija.hindamiskogum_id==hindamiskogum_id)
             )
        if liik:
            q = q.filter(Labiviija.liik==liik)
        if lang:
            q = q.filter(Labiviija.lang==lang)
        return q.first()

    def get_valik_q(self, grupp_id, on_piirkond=True, lang=None, join_ainelabiviija=False, kasutaja_id=None, on_kaskkiri=True, on_koolitus=True):
        """Võimalike läbiviijate päringu koostamine
        """

        toimumisaeg = self
        testimiskord = toimumisaeg.testimiskord
        test = testimiskord.test
        aine_kood = test.aine_kood

        # keeled, mis peavad profiilis olema
        if lang and isinstance(lang, list):
            # keeled on ette antud
            keeled = lang
        elif lang:
            # keel on ette antud
            keeled = [lang]
        else:
            # kontrollitakse kõiki testimiskorra keeli
            #keeled = testimiskord.get_keeled()
            keeled = []

        vastvorm = toimumisaeg.testiosa.vastvorm_kood

        if join_ainelabiviija:
            q = SessionR.query(Kasutaja, Ainelabiviija.tahis)
        else:
            # otsitakse kasutajaid, kes on potentsiaalsed testide läbiviijad
            q = SessionR.query(Kasutaja)

        if kasutaja_id:
            # päring konkreetse kasutaja kohta
            q = q.filter(Kasutaja.id==kasutaja_id)
            
        if grupp_id not in (const.GRUPP_KOMISJON, const.GRUPP_KOMISJON_ESIMEES) or test.on_tseis:
            # kui pole TE ega SE liiki test, siis ei ole komisjoni liikmel vaja profiili
            # muidu peab olema läbiviija profiil
            q = q.filter(Kasutaja.on_labiviija==True).\
                join(Kasutaja.profiil)

            if join_ainelabiviija:
                q = q.outerjoin((Ainelabiviija,
                                 sa.and_(Ainelabiviija.profiil_id==Profiil.id,
                                         Ainelabiviija.aine_kood==aine_kood)))

        if on_piirkond:
            piirkonnad = toimumisaeg.testimiskord.piirkonnad
            if len(piirkonnad):
                # kontrollime, et antud piirkond sobib 
                piirkonnad_id = set()
                for piirkond in piirkonnad:
                    p_id = piirkond.get_ylemad_id()
                    piirkonnad_id = piirkonnad_id.union(p_id)
                q = q.filter(Kasutaja.kasutajapiirkonnad.any(\
                    Kasutajapiirkond.piirkond_id.in_(piirkonnad_id)))
        
        # kontrollime, et antud roll sobib
        if grupp_id == const.GRUPP_VAATLEJA:
            q = q.filter(Profiil.on_vaatleja==True)
            for lang in keeled:
                q = q.filter(Profiil.v_skeeled.like('%' + lang + '%'))
            if on_koolitus and toimumisaeg.vaatleja_koolituskp:
                q = q.filter(Profiil.v_koolitusaeg>=toimumisaeg.vaatleja_koolituskp)
            if on_kaskkiri and toimumisaeg.hindaja_kaskkirikpv:
                q = q.filter(Profiil.v_kaskkirikpv>=toimumisaeg.hindaja_kaskkirikpv)
                
        elif grupp_id == const.GRUPP_T_ADMIN:
            q = q.filter(Profiil.on_testiadmin==True)
        elif grupp_id in (const.GRUPP_KOMISJON, const.GRUPP_KOMISJON_ESIMEES) and not test.on_tseis:
            # komisjoniliikmel ei pea profiili olema, va TE ja SE liiki testides
            pass
        else:
            # hindaja või intervjueerija või TE/SE komisjoniliige või konsultant
            if grupp_id == const.GRUPP_HINDAJA_S2:
                # aineprofiili tabelis on kõigi suuliste hindajate kohta üks grupp
                grupp_id = const.GRUPP_HINDAJA_S
            q = q.join(Kasutaja.aineprofiilid).\
                filter(Aineprofiil.aine_kood==aine_kood)

            # kui testil on keeletase, siis peab profiil olema antud taseme kohta (SE, TE)
            keeletase_kood = test.keeletase_kood
            if keeletase_kood:
                q = q.filter(Aineprofiil.keeletase_kood==keeletase_kood)
                
            if grupp_id == const.GRUPP_KOMISJON:
                # komisjoni liikmena saab tegutseda ka komisjoni esimehe koolituse läbinu
                grupid_id = (const.GRUPP_KOMISJON, 
                             const.GRUPP_KOMISJON_ESIMEES,
                             )
                q = q.filter(Aineprofiil.kasutajagrupp_id.in_(grupid_id))
            else:
                q = q.filter(Aineprofiil.kasutajagrupp_id==grupp_id)

            if grupp_id == const.GRUPP_HINDAJA_K:
                # kui on hindaja või intervjueerija, siis kontrollime,
                # et suudab antud keeles hinnata ja intervjueerida
                for lang in keeled:
                    q = q.filter(Profiil.k_skeeled.like('%' + lang + '%'))

            elif grupp_id in (const.GRUPP_HINDAJA_S, const.GRUPP_INTERVJUU):
                # kui on hindaja või intervjueerija, siis kontrollime,
                # et suudab antud keeles hinnata ja intervjueerida
                for lang in keeled:
                    q = q.filter(Profiil.s_skeeled.like('%' + lang + '%'))                        

            if on_koolitus:
                if grupp_id == const.GRUPP_INTERVJUU:
                    koolituskpv = toimumisaeg.intervjueerija_koolituskp
                elif grupp_id == const.GRUPP_KONSULTANT:
                    koolituskpv = toimumisaeg.konsultant_koolituskp
                elif grupp_id == const.GRUPP_KOMISJON:
                    koolituskpv = toimumisaeg.komisjoniliige_koolituskp
                elif grupp_id == const.GRUPP_KOMISJON_ESIMEES:
                    koolituskpv = toimumisaeg.esimees_koolituskp
                else:
                    koolituskpv = toimumisaeg.hindaja_koolituskp
                if koolituskpv:
                    q = q.filter(Aineprofiil.koolitusaeg>=koolituskpv)

            if on_kaskkiri:
                if grupp_id == const.GRUPP_INTERVJUU:
                    if toimumisaeg.intervjueerija_kaskkirikpv:
                        q = q.filter(Aineprofiil.kaskkirikpv>=toimumisaeg.intervjueerija_kaskkirikpv)
                else:
                    if toimumisaeg.hindaja_kaskkirikpv:
                        q = q.filter(Aineprofiil.kaskkirikpv>=toimumisaeg.hindaja_kaskkirikpv)                

        return q

    def _get_sooritajatearv_q(self, testikoht_id=None, testiruum_id=None, staatus=None, lang=None, group_lang=False, hindamiskogum_id=None, valimis=None):
        # kui testikoht_id==0, siis leitakse kohatute sooritajate arvud
        # kui testikoht_id==None, siis leitakse sooritajate koguarvud
        # kui testiruum_id==None, siis leitakse testikoha koguarvud
        from eis.model.testimine import Sooritus, Sooritaja, Hindamisolek
        if group_lang:
            q = SessionR.query(sa.func.count(Sooritus.id), Sooritaja.lang)
        else:
            q = SessionR.query(sa.func.count(Sooritus.id))            

        q = q.join(Sooritus.sooritaja)

        if testiruum_id:
            # testiruumi andmed
            q = q.filter(Sooritus.testiruum_id==testiruum_id)
        elif testikoht_id:
            # testikoha koguandmed
            q = q.filter(Sooritus.testikoht_id==testikoht_id)
        elif testikoht_id == 0:
            # kohatute sooritajate andmed
            q = (q.filter(Sooritus.toimumisaeg_id==self.id)
                 .filter(Sooritus.testikoht_id==None)
                 )
        else:
            q = q.filter(Sooritus.toimumisaeg_id==self.id)

        if staatus:
            q = q.filter(Sooritus.staatus==staatus)
        else:
            q = (q.filter(Sooritus.staatus>const.S_STAATUS_REGAMATA)
                 .filter(Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
                 )
        if lang:
            q = q.filter(Sooritaja.lang==lang)
        if valimis is not None:
            q = q.filter(Sooritaja.valimis==valimis)
        if group_lang:
            q = q.group_by(Sooritaja.lang)

        if hindamiskogum_id:
            q = q.filter(sa.exists().where(
                sa.and_(Sooritus.id==Hindamisolek.sooritus_id,
                        Hindamisolek.hindamiskogum_id==hindamiskogum_id,
                        Hindamisolek.mittekasitsi==False,
                        Hindamisolek.puudus==False)
                ))
        else:
            # peab olema mõni hindamisolek, millest ei puudunud
            # või ei ole yhti hindamisolekut
            q = q.filter(sa.or_(
                sa.exists().where(sa.and_(Hindamisolek.sooritus_id==Sooritus.id,
                                          Hindamisolek.puudus==False)),
                ~ sa.exists().where(Hindamisolek.sooritus_id==Sooritus.id))
                         )
        return q

    def get_sooritajatearvud(self, testikoht_id=None, testiruum_id=None, staatus=None, hindamiskogum_id=None, valimis=None):
        q = self._get_sooritajatearv_q(testikoht_id,
                                       testiruum_id,
                                       staatus,
                                       group_lang=True,
                                       hindamiskogum_id=hindamiskogum_id,
                                       valimis=valimis)
        di = {}
        total = 0
        for rcd in q.all():
            total += rcd[0]
            di[rcd.lang] = rcd[0]
        di['total'] = total
        return di

    def get_sooritajatearv(self, testikoht_id=None, testiruum_id=None, staatus=None, lang=None, valimis=None):
        q = self._get_sooritajatearv_q(testikoht_id, testiruum_id, staatus, lang, valimis=valimis)
        return q.scalar()

    def get_kysimusestatistika(self, kysimus_id, vy_id):
        from eis.model.testimine import Kysimusestatistika
        q = (Session.query(Kysimusestatistika)
             .filter_by(toimumisaeg_id=self.id)
             .filter_by(kysimus_id=kysimus_id)
             .filter_by(valitudylesanne_id=vy_id) # võib NULL olla
             )
        return q.first()

    def give_kysimusestatistika(self, kysimus_id, vy_id):
        from eis.model.testimine import Kysimusestatistika

        rcd = self.get_kysimusestatistika(kysimus_id, vy_id)
        if not rcd:
            rcd = Kysimusestatistika(testiosa=self.testiosa,
                                     toimumisaeg=self,
                                     tkorraga=True,
                                     valitudylesanne_id=vy_id,
                                     kysimus_id=kysimus_id)
            self.kysimusestatistikad.append(rcd)
        return rcd
                
    def update_aeg(self):
        """Toimumise ajast sõltuvate teiste väljade muutmine,
        seda on vaja teha peale toimumise aja muutmist 
        või teiste väljade lisamist.
        """
        # koht peab saama ise kella valida antud kuupäeval
        sql = """UPDATE testiruum 
            SET algus=toimumispaev.aeg
            FROM toimumispaev
            WHERE testiruum.toimumispaev_id=toimumispaev.id
            AND toimumispaev.toimumisaeg_id=:toimumisaeg_id
            AND (testiruum.algus IS NULL OR date(testiruum.algus) != date(toimumispaev.aeg))"""
        params = {'toimumisaeg_id': self.id}
        Session.execute(sa.text(sql), params)

        sql = """UPDATE testikoht 
            SET alates=(SELECT MIN(testiruum.algus) FROM testiruum 
                        WHERE testiruum.testikoht_id=testikoht.id)
            WHERE testikoht.toimumisaeg_id=:toimumisaeg_id"""
        params = {'toimumisaeg_id': self.id}
        Session.execute(sa.text(sql), params)

        sql = """UPDATE sooritus 
            SET kavaaeg=testiruum.algus
            FROM testiruum
            WHERE testiruum.id=sooritus.testiruum_id
            AND sooritus.toimumisaeg_id=:toimumisaeg_id
            AND (kavaaeg IS NULL OR date(kavaaeg) != date(testiruum.algus))"""
        params = {'toimumisaeg_id': self.id}
        Session.execute(sa.text(sql), params)

    def update_hindamisolekud(self, kogumid_id=None):
        """Hindamisolekute uuendamine juhuks, kui hindamiskogumite andmeid on vahepeal muudetud.
        Kasutada enne tulemuste arvutamist või koguste arvutamist.
        """
        from eis.model.testimine.hindamisolek import Hindamisolek
        from eis.model.testimine.sooritus import Sooritus
        from eis.model.testimine.sooritaja import Sooritaja

        testiosa = self.testiosa or Testiosa.get(self.testiosa_id)

        sql = """
        INSERT INTO hindamisolek (created,modified,creator,modifier, 
                                  sooritus_id, hindamiskogum_id, 
                                  hindamisprobleem)
        SELECT :now,:now,:userid,:userid,tos.id, hkogum.id,
               (CASE hkogum.arvutihinnatav WHEN true THEN 0 ELSE %d END)
        FROM sooritus tos, hindamiskogum hkogum,sooritaja j
        WHERE tos.toimumisaeg_id=:toimumisaeg_id
        AND hkogum.testiosa_id=:testiosa_id
        AND NOT EXISTS 
        (SELECT * FROM hindamisolek 
         WHERE sooritus_id=tos.id AND hindamiskogum_id=hkogum.id)
        AND hkogum.staatus=%d
        AND j.id=tos.sooritaja_id
        AND COALESCE(j.kursus_kood,'0')=COALESCE(hkogum.kursus_kood,'0')
        """ % (const.H_PROBLEEM_SISESTAMATA, const.B_STAATUS_KEHTIV)

        params = {'now': datetime.now(),
                  'userid': usersession.get_userid(),
                  'toimumisaeg_id': self.id,
                  'testiosa_id': testiosa.id,
                  }
        Session.execute(sa.text(sql), params)

        vastvorm_e = (const.VASTVORM_KE,
                      const.VASTVORM_SE,
                      const.VASTVORM_I,
                      const.VASTVORM_SH)
        if testiosa.vastvorm_kood in vastvorm_e:
            # muudame hindamistaseme 0-ks nendes hindamisolekutes,
            # millele vastavad hindamiskogumid on arvutihinnatavad
            sql = """UPDATE hindamisolek SET hindamistase=0, hindamisprobleem=0
            FROM sooritus tos, hindamiskogum 
            WHERE tos.id=hindamisolek.sooritus_id
            AND tos.toimumisaeg_id=:toimumisaeg_id
            AND hindamiskogum.id=hindamisolek.hindamiskogum_id
            AND hindamiskogum.arvutihinnatav=true"""
            params = {'toimumisaeg_id': self.id}
            Session.execute(sa.text(sql), params)

            # lisame komplekti nendele uutele hindamisolekutele,
            # mis on loodud peale testi toimumist

            # alatestideta testiosas on ainult üks komplektivalik 
            subsql = """SELECT min(ho2.komplekt_id) FROM hindamisolek ho2
                WHERE ho2.sooritus_id=hindamisolek.sooritus_id
                AND ho2.komplekt_id IS NOT NULL
                """

            # alatestidega testiosas peame vaatama,
            # kas et hindamisolek oleks samast komplektivalikust
            if testiosa.on_alatestid:
                subsql += """AND EXISTS (SELECT a.id FROM alatest a
                JOIN testiylesanne ty ON ty.alatest_id=a.id
                 AND ty.hindamiskogum_id=hindamisolek.hindamiskogum_id
                JOIN alatest a2 ON a2.komplektivalik_id=a.komplektivalik_id
                JOIN testiylesanne ty2 ON ty2.alatest_id=a2.id
                 AND ty2.hindamiskogum_id=ho2.hindamiskogum_id
                WHERE a.testiosa_id=:testiosa_id) """
                params['testiosa_id'] = testiosa.id
                
            sql = """UPDATE hindamisolek SET komplekt_id=(%s)
                FROM sooritus s
                WHERE s.id=hindamisolek.sooritus_id
                AND s.toimumisaeg_id=:toimumisaeg_id
                AND hindamisolek.komplekt_id IS NULL""" % (subsql)

            Session.execute(sa.text(sql), params)
                
        # muudame õigeks hindamistaseme nendes hindamisolekutes,
        # mis ei peaks olema arvutihinnatavad 
        # ja kus seni ei ole kolmanda hindamise vajaduseni jõutud
        # NB! hindamisprobleemi väärtust siin ei muudeta
        if testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP) \
               and not testiosa.test.on_tseis:
            if self.hindaja1_maaraja and self.hindaja2_maaraja:
                hindamistase = const.HINDAJA2
            else:
                hindamistase = const.HINDAJA1
            sql = """UPDATE hindamisolek SET hindamistase=:hindamistase
                     FROM sooritus
                     WHERE sooritus.id=hindamisolek.sooritus_id
                     AND sooritus.toimumisaeg_id=:toimumisaeg_id
                     AND hindamisolek.hindamistase < 3"""
            params = {'toimumisaeg_id': self.id, 
                      'hindamistase': hindamistase,
                      }
        else:
            sql = """UPDATE hindamisolek 
            SET hindamistase=(CASE
                              WHEN hindamiskogum.kahekordne_hindamine and not sooritaja.valimis THEN 2
                              WHEN hindamiskogum.kahekordne_hindamine_valim and sooritaja.valimis THEN 2
                              ELSE 1
                              END)
            FROM sooritus, hindamiskogum, sooritaja
            WHERE sooritus.id=hindamisolek.sooritus_id
            AND sooritus.toimumisaeg_id=:toimumisaeg_id
            AND sooritaja.id=sooritus.sooritaja_id
            AND hindamiskogum.id=hindamisolek.hindamiskogum_id
            AND hindamiskogum.arvutihinnatav=false
            AND hindamisolek.hindamistase < 3"""
            params = {'toimumisaeg_id': self.id}
        Session.execute(sa.text(sql), params)
            
        # eemaldame mitteaktiivsete hindamiskogumite hindamisolekud,
        # kui neid peaks varem olema tekkinud
        q = (Session.query(Hindamisolek)
             .join((Sooritus, Sooritus.id==Hindamisolek.sooritus_id))
             .filter(Sooritus.staatus!=const.S_STAATUS_TEHTUD)
             .filter(Sooritus.toimumisaeg_id==self.id)
             .join((Hindamiskogum, Hindamiskogum.id==Hindamisolek.hindamiskogum_id))
             .filter(Hindamiskogum.staatus==const.B_STAATUS_KEHTETU)
             .filter(Hindamiskogum.testiosa_id==self.testiosa_id)
             )
        for rcd in q.all():
            rcd.delete()

        # eemaldame teiste kursuste hindamisolekud
        q = Session.query(Hindamisolek).\
            join((Sooritus, Hindamisolek.sooritus_id==Sooritus.id)).\
            filter(Sooritus.toimumisaeg_id==self.id).\
            join((Hindamiskogum, Hindamiskogum.id==Hindamisolek.hindamiskogum_id)).\
            join(Sooritus.sooritaja).\
            filter(Sooritaja.kursus_kood!=Hindamiskogum.kursus_kood).\
            filter(Hindamiskogum.testiosa_id==self.testiosa_id)
        for rcd in q.all():
            rcd.delete()
        #log_query(q)

        self.give_alatestisooritused()

    def give_alatestisooritused(self):
        "Loome alatestisooritused"
        from eis.model.eksam import Alatestisooritus
        from eis.model.testimine import Sooritus, Sooritaja
        creator = usersession.get_userid()
        bindparam = sa.sql.expression.bindparam
        q = (Session.query(sa.func.current_timestamp(),
                           sa.func.current_timestamp(),
                           bindparam('creator', creator),
                           bindparam('modifier', creator),
                           bindparam('staatus', const.S_STAATUS_ALUSTAMATA),
                           Sooritus.id,
                           Alatest.id)
             .filter(Sooritus.toimumisaeg_id==self.id)
             .filter(Sooritus.staatus.in_((const.S_STAATUS_ALUSTAMATA,
                                           const.S_STAATUS_REGATUD)))
             .join((Alatest, Alatest.testiosa_id==self.testiosa_id))
             .filter(~ sa.exists().where(
                 sa.and_(Sooritus.id==Alatestisooritus.sooritus_id,
                         Alatestisooritus.alatest_id==Alatest.id))
                     )
             .order_by(Sooritus.id, Alatest.id)
             )
        #log_query(q)
        fields = (Alatestisooritus.created,
                  Alatestisooritus.modified,
                  Alatestisooritus.creator,
                  Alatestisooritus.modifier,
                  Alatestisooritus.staatus,
                  Alatestisooritus.sooritus_id,
                  Alatestisooritus.alatest_id)
        stmt = Alatestisooritus.__table__.insert().from_select(fields, q)
        Session.execute(stmt)
        Session.flush()

        # vabastame kirjalikust alatestist tasemeeksami yle 65a vabastusega sooritajad
        if self.testiosa.test.testiliik_kood == const.TESTILIIK_TASE:
            q = (Session.query(Alatestisooritus)
                 .filter(Alatestisooritus.staatus==const.S_STAATUS_ALUSTAMATA)
                 .join((Sooritus, Alatestisooritus.sooritus_id==Sooritus.id))
                 .filter(Sooritus.toimumisaeg_id==self.id)
                 .join(Sooritus.sooritaja)
                 .filter(Sooritaja.vabastet_kirjalikust==True)
                 .join((Alatest, Alatestisooritus.alatest_id==Alatest.id))
                 .filter(Alatest.alatest_kood==const.ALATEST_RK_KIRJUTAMINE)
                 )
            for atos in q.all():
                atos.staatus = const.S_STAATUS_VABASTATUD

class TempToimumisaeg(object):
    testiosa_id = None
    kahekordne_sisestamine = False
    eelvaade_admin = None
    on_veriff = False
    on_proctorio = False
    
    def __init__(self, testiosa_id=None):
        self.testiosa_id = testiosa_id

    @property
    def testiosa(self):
        if self.testiosa_id:
            return Testiosa.get(self.testiosa_id)
