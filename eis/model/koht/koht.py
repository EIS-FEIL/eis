from eis.model.entityhelper import *
from eis.model.klassifikaator import Klrida
from .aadress import Aadress

class Koht(EntityHelper, Base):
    """Soorituskoht
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    nimi = Column(String(100)) # nimi
    piirkond_id = Column(Integer, ForeignKey('piirkond.id'), index=True) # viide piirkonnale, millesse antud soorituskoht kuulub
    piirkond = relationship('Piirkond', foreign_keys=piirkond_id, back_populates='kohad')
    haldusoigus = Column(Boolean) # kas soorituskoht võib ise oma andmeid hallata või mitte
    riik_kood = Column(String(3)) # riigi 3-kohaline ISO kood
    ruumidearv = Column(Integer) # ruumide arv
    ptestikohti = Column(Integer) # kohti p-testi sooritajatele
    etestikohti = Column(Integer) # kohti e-testi sooritajatele
    ruumid = relationship('Ruum', order_by='Ruum.tahis', back_populates='koht') # ruumid
    testikohad = relationship('Testikoht', back_populates='koht') # testikohad
    valitsus_tasekood = Column(String(6)) # viide maakonnale või linnale, mida antud koht valitseb (maa- või omavalitsuse korral); viitab tabeli Aadresskomponent kirjele ja on kujul "tase.kood"
    on_soorituskoht = Column(Boolean) # kas koht on EISi põhisüsteemis kasutusel
    on_plangikoht = Column(Boolean) # kas koht on plankide moodulis kasutusel
    staatus = Column(Integer, nullable=False) # olek: 1=const.B_STAATUS_KEHTIV - koht on kuskil kasutusel; 0=const.B_STAATUS_KEHTETU - koht pole kasutusel
    kool_regnr = Column(String(8)) # õppeasutuse registreerimisnumber, kui soorituskoht asub mõnes õppeasutuses
    kool_id = Column(Integer) # õppeasutuse ID EHISes
    koolityyp_kood = Column(String(20)) # kooliliikide klassifikaator EHISes, EISi klassifikaator KOOLITYYP
    alamliik_kood = Column(String(25)) # koolide alamliikide klassifikaator EHISes
    omandivorm_kood = Column(String(25)) # omandivorm
    diplomiseeria = Column(String(2)) # diplomi seeria teine täht; kui on kaks tähte, siis väljastab kool kaht erinevat seeriat (kõrgharidust andva õppeasutuse korral, kasutatakse plankide moodulis)
    aadress_id = Column(Integer, ForeignKey('aadress.id'), index=True) # viide aadressile
    aadress = relationship('Aadress', foreign_keys=aadress_id)
    postiindeks = Column(String(5)) # postiindeks
    normimata = Column(String(200)) # normaliseerimata aadress - vabatekstiliselt sisestatud aadressi lõpp, mida ei olnud võimalik sisestada ADSi komponentide klassifikaatori abil
    klassi_kompl_arv = Column(Integer) # klassikomplektide arv
    opilased_arv = Column(Integer) # õpilaste arv
    ehis_seisuga = Column(DateTime) # viimane EHISes uuendamise aeg
    telefon = Column(String(50)) # kooli telefon
    epost = Column(String(100)) # kooli e-posti aadress
    varustus = Column(Text) # koolis oleva varustuse vabatekstiline kirjeldus
    pedagoogid = relationship('Pedagoog', back_populates='koht') # pedagoogid
    seisuga = Column(DateTime) # kohalikus serveris: koha ja sellega seotud kirjete viimase uuendamise aeg
    testikohad = relationship('Testikoht', back_populates='koht') # testikohad
    kasutajarollid = relationship('Kasutajaroll', order_by=sa.desc(sa.text('Kasutajaroll.id')), back_populates='koht')
    kasutajakohad = relationship('Kasutajakoht', order_by=sa.desc(sa.text('Kasutajakoht.id')), back_populates='koht')
    koolinimed = relationship('Koolinimi', back_populates='koht')
    kohalogid = relationship('Kohalogi', back_populates='koht')
    oppekeeled = relationship('Oppekeel', back_populates='koht')
    sooritajad = relationship('Sooritaja', foreign_keys='Sooritaja.kool_koht_id', back_populates='kool_koht')
    koolioppekavad = relationship('Koolioppekava', back_populates='koht')
    allikas = None # andmete muutmise allikas, seatakse kontrolleris, kasutab Kohalogi
    ryhmad = relationship('Ryhm', back_populates='koht')
    sert = relationship('Sert', uselist=False, back_populates='koht')

    @classmethod
    def get_opt(cls, staatus=const.B_STAATUS_KEHTIV, tasekood=None, piirkond_id=None, nimi=None, on_soorituskoht=None, on_plangikoht=None):
        """Kõigi kohtade valik - kasutada ainult kõigile rakendustele ühises osas"""
        q = Koht.query
        if staatus is not None:
            q = q.filter_by(staatus=staatus)
        if tasekood:
            q = q.join(Koht.aadress)
            tase, kood = tasekood.split('.')
            tase = int(tase)
            q = q.filter(Aadress.get_field_tase(tase)==kood)
        if piirkond_id:
            from .piirkond import Piirkond
            prk = Piirkond.get(piirkond_id)
            piirkonnad_id = prk and prk.get_alamad_id() or [0]
            q = q.filter(Koht.piirkond_id.in_(piirkonnad_id))
        if nimi:
            q = q.filter(Koht.nimi.ilike('%' + nimi + '%'))
        if on_soorituskoht:
            q = q.filter(Koht.on_soorituskoht==True)
        if on_plangikoht:
            q = q.filter(Koht.on_plangikoht==True)
        log_query(q)
        return [(item.id, item.nimi) for item in q.order_by(Koht.nimi).all()]

    @classmethod
    def get_soorituskoht_opt(cls):
        """EISi põhimooduli kohtade valik"""
        return cls.get_opt(on_soorituskoht=True)

    @classmethod
    def get_plangikoht_opt(cls):
        """Plankide mooduli kohtade valik"""
        return cls.get_opt(on_plangikoht=True)

    def default(self):
        if not self.staatus:
            self.staatus = const.B_STAATUS_KEHTIV

    @property
    def staatus_nimi(self):
        if self.staatus == const.B_STAATUS_KEHTIV:
            return usersession.get_opt().STR_KEHTIV
        elif self.staatus == const.B_STAATUS_KEHTETU:
            return usersession.get_opt().STR_KEHTETU

    @property 
    def koolityyp_nimi(self):
        return Klrida.get_str('KOOLITYYP', str(self.koolityyp_kood))

    @property
    def valitsus_aadresskomponent(self):
        "Antud koha poolt valitsetav haldusüksus"
        from .aadresskomponent import Aadresskomponent
        if self.valitsus_tasekood:
            return Aadresskomponent.get_by_tasekood(self.valitsus_tasekood)

    @property
    def oppetasemed(self):
        return [r.oppetase_kood for r in self.koolioppekavad]

    @property
    def kavatasemed(self):
        return [r.kavatase_kood for r in self.koolioppekavad]

    @property
    def opt_klass_ryhm(self):
        "Kooli lasteaiarühmade või klasside valik"
        li = []
        kavatasemed = self.kavatasemed
        if const.E_OPPETASE_ALUS in kavatasemed:
            for r in self.ryhmad:
                # ryhma eristame klassidest r-tähega
                li.append((f'r{r.id}', r.nimi))
        if const.E_OPPETASE_YLD in kavatasemed or \
               const.E_OPPETASE_GYMN in kavatasemed or \
               const.E_OPPETASE_ERIVAJADUS in kavatasemed or \
               const.E_OPPETASE_ERIKASVATUS in kavatasemed or \
               const.E_OPPETASE_KUTSE in kavatasemed:
            li.extend(const.EHIS_KLASS)
        return li
            
    @property
    def tais_aadress(self):
        buf = ''
        a = self.aadress
        if a:
            buf = a.tais_aadress
        if self.normimata:
            buf += ' ' + self.normimata
        return buf

    def has_permission(self, permission, perm_bit, user=None):
        """Kontrollitakse jooksva kasutaja õigust 
        antud tegevusele antud kohal.
        """
        if not user:
            user = usersession.get_user()
        if not user:
            return False

        # avalikus vaates kontrollime, et kasutaja töötaks selles koolis
        rc = False
        kasutaja = user.get_kasutaja()
        if kasutaja:
            if kasutaja.has_permission(permission, perm_bit, koht_id=self.id):
                # kasutajal on nimekirja esitanud õppeasutuses mingi õigus
                log.debug(f'N: Kasutajal {kasutaja.nimi} on roll "{permission}" ({perm_bit}) kohal {self.id}')
                rc = True
        if not kasutaja:
            for p in user.get_pedagoogid(koht_id=self.id):
                # mingi õigus selles kohas on olemas
                if p.has_permission(permission, perm_bit):
                    rc = True
                    break
        return rc

    def get_koondvastus(self, toimumisaeg_id):
        from eis.model.testimine import Koondvastus
        item = Koondvastus.query.\
            filter_by(toimumisaeg_id=toimumisaeg_id).\
            filter_by(koht_id=self.id).\
            first()
        return item

    def give_koondvastus(self, toimumisaeg_id):
        from eis.model.testimine import Koondvastus
        item = self.get_koondvastus(toimumisaeg_id)
        if not item:
            item = Koondvastus(toimumisaeg_id=toimumisaeg_id,
                                     koht_id=self.id)
        return item

    def update_testiruumid(self, testikoht_id=None):
        "Uuendame kohtade arvu soorituskohtades"

        from eis.model.testimine import Testiruum, Testikoht, Toimumisaeg
        from eis.model.test import Testiosa
        from .ruum import Ruum

        if testikoht_id:
            # kui keegi võtab kinnituse maha, siis annab parameetriks testikoha
            f = Testikoht.id==testikoht_id
        else:
            # vaikimisi muudetakse need testiruumid, mille kohad on kinnitamata
            f = sa.or_(Toimumisaeg.kohad_kinnitatud==False,
                       Toimumisaeg.kohad_kinnitatud==None)

        q = (Testiruum.query.filter_by(ruum_id=None)
             .join(Testiruum.testikoht)
             .filter(Testikoht.koht_id==self.id)
             .join(Testikoht.toimumisaeg)
             .join(Toimumisaeg.testiosa)
             .filter(f))

        vastvorm_p = (const.VASTVORM_KP, const.VASTVORM_SP)
        vastvorm_e = (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I, const.VASTVORM_SH)
        qp = (q.filter(Testiosa.vastvorm_kood.in_(vastvorm_p))
              .filter(sa.or_(Testiruum.kohti==None,
                             Testiruum.kohti!=self.ptestikohti))
              )
        for rcd in qp.all():
            rcd.kohti = self.ptestikohti

        qe = (q.filter(Testiosa.vastvorm_kood.in_(vastvorm_e))
              .filter(sa.or_(Testiruum.kohti==None,
                             Testiruum.kohti!=self.etestikohti))
              )
        for rcd in qe.all():
            rcd.kohti = self.etestikohti

        # ruumiga testiruumid
        q = (Session.query(Testiruum, Ruum)
             .join(Testiruum.ruum)
             .join(Testiruum.testikoht)
             .filter(Testikoht.koht_id==self.id)
             .join(Testikoht.toimumisaeg)
             .join(Toimumisaeg.testiosa)
             .filter(f))

        qp = (q.filter(Testiosa.vastvorm_kood.in_(vastvorm_p))
              .filter(sa.or_(Testiruum.kohti==None,
                             Testiruum.kohti!=Ruum.ptestikohti))
              )
        for rcd in qp.all():
            truum, ruum = rcd
            truum.kohti = ruum.ptestikohti

        qe = (q.filter(Testiosa.vastvorm_kood.in_(vastvorm_e))
              .filter(sa.or_(Testiruum.kohti==None,
                             Testiruum.kohti!=Ruum.etestikohti))
              )
        for rcd in qe.all():
            truum, ruum = rcd
            truum.kohti = ruum.etestikohti

    def riik2piirkond(self):
        from .piirkond import Piirkond
        if self.riik_kood:
            riik_nimi = Klrida.get_str('RIIK', self.riik_kood)
            q = SessionR.query(Piirkond.id).filter_by(nimi=riik_nimi)
            for piirkond_id, in q.all():
                self.piirkond_id = piirkond_id

    @property
    def kehtiv_koolinimi(self):
        from .koolinimi import Koolinimi
        # kooli eelmised nimed hoitakse meeles
        if self.id:
            r = (Session.query(Koolinimi)
                 .filter_by(koht_id=self.id)
                 .order_by(sa.desc(Koolinimi.alates))
                 .first())
            return r
    
    def set_name(self):
        from .koolinimi import Koolinimi
        # kooli eelmised nimed hoitakse meeles
        r = self.kehtiv_koolinimi
        if not r or r.nimi != self.nimi:
            # senine nimi oli midagi muud
            self.koolinimed.append(Koolinimi(nimi=self.nimi, alates=datetime.now()))

    def delete_subitems(self):    
        if self.sert:
            self.sert.delete()
        self.delete_subrecords(['ruumid',
                                'koolinimed',
                                'koolioppekavad',
                                'oppekeeled',
                                'kohalogid',
                                'ryhmad',
                                ])

    def get_admin(self):
        "Leitakse soorituskoha administraatorid"
        from eis.model.kasutaja import Kasutaja, Pedagoog, Kasutajaroll

        grupid_id = (const.GRUPP_K_ADMIN, const.GRUPP_K_JUHT)
        q = (Session.query(Kasutaja)
             .filter(sa.or_(Kasutaja.pedagoogid.any(
                        sa.and_(Pedagoog.kasutajagrupp_id.in_(grupid_id),
                                Pedagoog.koht_id==self.id)),
                            Kasutaja.kasutajarollid.any(
                                sa.and_(Kasutajaroll.kasutajagrupp_id.in_(grupid_id),
                                        Kasutajaroll.koht_id==self.id,
                                        Kasutajaroll.kehtib_alates<=datetime.now(),
                                        Kasutajaroll.kehtib_kuni>=datetime.now()))
                            ))
             )
        return q.all()

    def get_aineopetajad(self, aine_kood, kasutaja_id=None):
        "Leitakse aineõpetajad"
        from eis.model.kasutaja import Kasutaja, Pedagoog, Kasutajaroll
        q = (Session.query(Kasutaja).
             filter(Kasutaja.kasutajarollid.any(
                 sa.and_(Kasutajaroll.kasutajagrupp_id==const.GRUPP_AINEOPETAJA,
                         Kasutajaroll.koht_id==self.id,
                         Kasutajaroll.aine_kood==aine_kood,
                         Kasutajaroll.kehtib_alates<=datetime.now(),
                         Kasutajaroll.kehtib_kuni>=datetime.now())
                 ))
             )
        if kasutaja_id:
            q = q.filter(Kasutaja.id==kasutaja_id)
            return q.first()
        else:
            return q.order_by(Kasutaja.nimi).all()

    def log_update(self):
        from .piirkond import Piirkond

        values = []
        for key, old_value in self._sa_instance_state.committed_state.items():
            if key in self.meta_fields:
                continue
            if key == 'ehis_seisuga':
                continue
            if self.__table__.columns.get(key) is None:
                # alamkirjete jada või _ algav atribuut
                continue

            new_value = self.__getattr__(key)
            if key == 'filedata':
                old_value = old_value and '*' or None
                new_value = new_value and '*' or None

            if isinstance(old_value, str):
                old_value = old_value.strip()
            if isinstance(new_value, str):
                new_value = new_value.strip()

            if isinstance(old_value, sa.util.langhelpers._symbol):
                old_value = None
            if isinstance(new_value, sa.util.langhelpers._symbol):
                new_value = None

            if type(old_value) == type(new_value):
                changed = old_value != new_value
            else:
                changed = str(old_value) != str(new_value)

            if changed:
                values.append((key,old_value,new_value))

        for key, old_value, new_value in values:
            if key == 'koolityyp_kood':
                key = 'koolityyp'
                if old_value:
                    old_value = Klrida.get_str('KOOLITYYP', old_value)
                if new_value:
                    new_value = Klrida.get_str('KOOLITYYP', new_value)                    
            elif key == 'piirkond_id':
                key = 'piirkond'
                if old_value:
                    old_value = Piirkond.get(old_value).nimi
                if new_value:
                    new_value = Piirkond.get(new_value).nimi

            self._append_log(key, old_value, new_value)
        
    def log_insert(self):
        self._append_log('LISAMINE', None, None)

    def _append_log(self, key, old_value, new_value):
        from .kohalogi import Kohalogi

        # # kohalikus eksamiserveris pole tarvis logida
        # if usersession.user.c.handler.app_eksam:
        #     return
        user = usersession.get_user()

        # kui allikat pole seatud, siis vaatame rakenduse järgi
        # allikas on vaja seada ainult EHISest korral
        allikas = self.allikas or \
            user.app_ekk and Kohalogi.ALLIKAS_EKK or \
            Kohalogi.ALLIKAS_SK

        rcd = Kohalogi(koht=self,
                       kasutaja_id=user.id,
                       allikas=allikas,
                       vali=key,
                       vana=old_value,
                       uus=new_value)
        self.kohalogid.append(rcd)

    def give_sert(self):
        from .sert import Sert
        if not self.sert:
            self.sert = Sert()
        return self.sert
    
