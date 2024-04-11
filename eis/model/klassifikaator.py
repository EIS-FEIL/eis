from .entityhelper import *
log = logging.getLogger(__name__)

# puhvrid mälus, et vähendada andmebaasi poole pöördumiste arvu
class CacheObj:
    def __init__(self, minutes=10, seconds=0):
        self._cache = dict()
        self._tdelta = timedelta(minutes=minutes, seconds=seconds)

    def get(self, key):
        item = self._cache.get(key)
        if item:
            dt, value = item
            if dt > datetime.now() - self._tdelta:
                return value

    def __getitem__(self, key):
        return self._cache[key][1]

    def __setitem__(self, key, value):
        self._cache[key] = datetime.now(), value

    def __delitem__(self, key):
        del self._cache[key]

    def has_key(self, key):
        return key in self._cache
    
    def keys(self):
        return list(self._cache.keys())
        
cache = CacheObj()
cache_kood = CacheObj()
cache_id = CacheObj()

class Klassifikaator(EntityHelper, Base):
    """Klassifikaatori liik
    """
    kood = Column(String(10), primary_key=True) # kirje identifikaator
    nimi = Column(String(100), nullable=False) # nimi
    kehtib = Column(Boolean) # olek: 1 - kehtib; 0 - ei kehti
    read = relationship('Klrida', order_by='Klrida.jrk,Klrida.id', back_populates='klassifikaator') # klassifikaatoriväärtused
    alamad = relationship('Klassifikaator', back_populates='ylem') # alamad
    ylem_kood = Column(String(10), ForeignKey('klassifikaator.kood'), index=True)# kasutajaliidese jaoks
    ylem = relationship('Klassifikaator', foreign_keys=ylem_kood, remote_side=kood, back_populates='alamad') 
    app = Column(String(6), sa.DefaultClause('eis'), nullable=False) # rakendus, mille administraator klassifikaatorit haldab: eis=const.APP_EIS - EISi põhimoodul; plank=const.APP_PLANK - plankide moodul
    seisuga = Column(DateTime) # EHISe klassifikaatori korral viimane EHISest andmete kontrollimise aeg
    trans = relationship('T_Klassifikaator', cascade='all', back_populates='orig') # kui cascade puudub, siis antakse kustutamisel viga

    @classmethod
    def get(cls, kood):
        return cls.query.filter_by(kood=kood).first()

    @classmethod
    def get_item(cls, **args):
        return cls.get(args['kood'])

    @classmethod
    def getR(cls, kood):
        return cls.queryR.filter_by(kood=kood).first()

    @classmethod
    def getR_item(cls, **args):
        return cls.getR(args['kood'])

    @property
    def ctran(self):
        "Jooksvalt valitud keele tõlkekirje"
        return self.tran(usersession.get_lang())

    def lisaread(self, li):
        for rida in li:
            #rida.klassifikaator_kood = self.kood
            self.read.append(rida)
        return self

    def before_insert(self):
        if self.kehtib is None:
            self.kehtib = True
        return EntityHelper.before_insert(self)

class Klrida(EntityHelper, Base):
    """Klassifikaatori väärtus
    """
    __table_args__ = (
        sa.UniqueConstraint('klassifikaator_kood','kood','ylem_id','testiklass_kood'),
        )
    id = Column(Integer, primary_key=True, autoincrement=True) 
    jrk = Column(Integer) # järjekorranumber valikutes
    kood = Column(String(25), nullable=False) # väärtuse kood (EISi klassifikaatoritel kuni 10 kohta, EHISest üle võetud klassifikaatoritel kuni 25 kohta)
    kood2 = Column(String(2)) # kood teises klassifikaatoris (KODAKOND korral, ISO2)
    hkood = Column(String(109)) # hierarhia kood (TEEMA, ALATEEMA korral): ülemkirje hierarhia kood + punkt + selle kirje kood
    nimi = Column(String(500), nullable=False) # nimetus
    idurl = Column(String(1024)) # URL identifikaatorina (oppekava.edu.ee klassifikaatorite korral)
    # Täiendav kirjeldus (nt hindamisaspekti korral hindamisjuhend)
    kirjeldus = Column(Text) # täiendav kirjeldus
    kehtib = Column(Boolean) # olek: 1 - kehtib; 0 - ei kehti
    alates = Column(DateTime) # kehtivuse algus
    kuni = Column(DateTime) # kehtivuse lõpp
    avalik = Column(Boolean) # kas kehtib ka avalikus vaates (ülesandetüübi korral)
    klassifikaator_kood = Column(String(10), ForeignKey('klassifikaator.kood'), index=True, nullable=False)
    klassifikaator = relationship('Klassifikaator', foreign_keys=klassifikaator_kood, back_populates='read') # viide klassifikaatorile, mille üht väärtust esitab antud kirje 
    alamad = relationship('Klrida', back_populates='ylem') # alamad
    ylem_id = Column(Integer, ForeignKey('klrida.id'), index=True) # viide ülemale väärtusele (üldjuhul teisest klassifikaatorist)
    ylem = relationship('Klrida', foreign_keys=ylem_id, remote_side=id, back_populates='alamad')
    bitimask = Column(Integer) # valdkonna või teema või töökäsu puhul kooliastmete bittide summa, kooliastme bitimask on 2 astmes astme kood, vaikimisi kooliastmete korral on astme koodi asemel astendajaks I aste - 0, II  aste - 1, III aste - 2, gümnaasium - 3; õppeainete puhul: 1 - soorituskoha administraator saab isikutele lisada selle aine läbiviija profiili; NULL - soorituskoha administraator ei saa isikutele lisada selle aine läbiviija profiili; erivajaduste puhul: 4=const.ASTE_BIT_III - põhikool; 8=const.ASTE_BIT_G - gümnaasium; nulli põhjuse puhul: 1=const.NULLIP_BIT_P - kasutusel p-testides; 2=const.NULLIP_BIT_E - kasutusel e-testides
    #pais = Column(Text) # HTML päisesse lisatav osa (vahendite korral)
    #ikoon_url = Column(String(100)) # ikooni failinimi (vahendite korral)
    #laius = Column(Integer) # kuvamisel kasutatav laius (vahendite korral)
    #korgus = Column(Integer) # kuvamisel kasutatav kõrgus (vahendite korral)    
    kirjeldus2 = Column(Text) # kirjeldus 2. isikus (tagasisidevormi tunnuse korral)
    kirjeldus3 = Column(Text) # kirjeldus 3. isikus (tagasisidevormi tunnuse korral)
    kirjeldus_t = Column(Text) # tasemete kirjeldused (tagasisidevormi tunnuse korral)    
    testiklass_kood = Column(String(10), sa.DefaultClause('')) # viide klassile (tagasisidevormi tunnuse korral)
    ryhm_kood = Column(String(10)) # klassifikaatoriväärtuste rühma klassifikaatori kood (ainete korral ainevaldkond)
    nullipohjus = Column(Boolean) # kas e-testi hindamisel on kasutusel null punkti põhjuse valikväli (aine korral)
    kinnituseta = Column(Boolean) # kas taotlus ei vaja EKK kinnitust (erivajaduse korral)
    trans = relationship('T_Klrida', cascade='all', back_populates='orig') # kui cascade puudub, siis antakse kustutamisel viga
    eis_klvastavused = relationship('Klvastavus', foreign_keys='Klvastavus.eis_klrida_id', back_populates='eis_klrida')
    ehis_klvastavused = relationship('Klvastavus', foreign_keys='Klvastavus.ehis_klrida_id', back_populates='ehis_klrida')    
    ylem_klseosed = relationship('Klseos', foreign_keys='Klseos.ylem_klrida_id', back_populates='ylem_klrida')
    alam_klseosed = relationship('Klseos', foreign_keys='Klseos.alam_klrida_id', back_populates='alam_klrida')
    
    @classmethod
    def get_by_kood(cls, klassifikaator_kood, kood=None, ylem_kood=None, ylem_id=None):
        if kood is None:
            return None

        q = cls.queryR.filter_by(klassifikaator_kood=klassifikaator_kood)

        if kood is not None:
            # otsime yhe koodi järgi
            q = q.filter_by(kood=kood)
        else:
            # otsime kõiki kehtivaid
            q = q.filter(cls.kehtib==True)

        if ylem_id is not None:
            q = q.filter_by(ylem_id=ylem_id)
        elif ylem_kood is not None:
            q = q.filter(Klrida.ylem.has(Klrida.kood==ylem_kood))
        return q.first()

    @classmethod
    def get_q_by_kood(cls, klassifikaator_kood, kood=None, ylem_kood=None, ylem_id=None, ylem_none=False, lang=None):
        lang = lang or usersession.get_lang()
        if klassifikaator_kood == 'TOOKASK':
            fld_nimi = sa.func.coalesce(T_Klrida.kirjeldus, Klrida.kirjeldus)
            fld_kirjeldus = fld_nimi
        else:
            fld_nimi = sa.func.coalesce(T_Klrida.nimi, Klrida.nimi)
            fld_kirjeldus = sa.func.coalesce(T_Klrida.kirjeldus, Klrida.kirjeldus)            
        if klassifikaator_kood == 'KODAKOND2':
            fld_kood = Klrida.kood2
            klassifikaator_kood = 'KODAKOND'
        else:
            fld_kood = Klrida.kood
        q = (SessionR.query(Klrida.id,
                           fld_kood,
                           fld_nimi,
                           Klrida.ylem_id,
                           Klrida.bitimask,
                           fld_kirjeldus)
             .outerjoin((T_Klrida,
                         sa.and_(T_Klrida.orig_id==Klrida.id, T_Klrida.lang==lang)))
             )
        q = q.filter(Klrida.klassifikaator_kood==klassifikaator_kood)

        if kood is not None:
            # otsime yhe koodi järgi
            q = q.filter(Klrida.kood==kood)
        else:
            # otsime kõiki kehtivaid
            q = q.filter(Klrida.kehtib==True)

        if klassifikaator_kood == 'OPITULEMUS':
            # leiame õpitulemuse,
            # mis on seotud oppekava.edu.ee õppeainega,
            # mis omakorda vastab antud EISi õppeainele
            if ylem_kood:
                aine = Klrida.get_by_kood('AINE', ylem_kood)
                ylem_id = aine and aine.id or None
            q = q.filter(sa.exists().where(
                sa.and_(Klseos.alam_klrida_id==Klrida.id,
                        Klseos.ylem_klrida_id==Klvastavus.ehis_klrida_id,
                        Klvastavus.eis_klrida_id==ylem_id)
                ))
        elif ylem_id is not None:
            q = q.filter(Klrida.ylem_id==ylem_id)
        elif ylem_kood is not None:
            q = q.filter(Klrida.ylem.has(Klrida.kood==ylem_kood))
        elif ylem_none:
            q = q.filter(Klrida.ylem_id==None)
        return q

    @classmethod
    def get_str(cls, klassifikaator_kood, kood, ylem_kood=None, ylem_id=None, lang=None):
        if kood is None:
            return None
        if isinstance(kood, int):
            kood = str(kood)
        lang = lang or usersession.get_lang()
        _cache_key = (klassifikaator_kood, kood, ylem_kood, ylem_id, lang)
        value = cache.get(_cache_key)
        if not value:
            item = cls.get_by_kood(klassifikaator_kood, kood, ylem_kood, ylem_id)
            if item:
                if klassifikaator_kood == 'TOOKASK':
                    value = item.tran(lang).kirjeldus
                else:
                    value = item.tran(lang).nimi
                cache[_cache_key] = value
        return value

    @classmethod
    def get_kood_ryhm(cls, klassifikaator_kood):
        _cache_key = (klassifikaator_kood, 'ryhm')
        li = cache_kood.get(_cache_key)
        if not li:
            q = (SessionR.query(Klrida.kood, Klrida.ryhm_kood)
                 .filter(Klrida.klassifikaator_kood==klassifikaator_kood)
                 .filter(Klrida.ryhm_kood!=None)
                 .filter(Klrida.ryhm_kood!='')
                 )
            li = [(k,r) for (k,r) in q.all()]
            cache_kood[_cache_key] = li
        return li

    @classmethod
    def get_lang_nimi(cls, lang):
        return cls.get_str('SOORKEEL', lang)

    @property
    def ainevald_nimi(self):
        if self.klassifikaator_kood == 'AINE' and self.ryhm_kood:
            return Klrida.get_str('AINEVALD', self.ryhm_kood)

    @property
    def ctran(self):
        "Jooksvalt valitud keele tõlkekirje"
        return self.tran(usersession.get_lang())

    @classmethod
    def clean_cache(cls, klassifikaator_kood):
        "Klassifikaatoriväärtuste muutmisel tühjendame puhvri"
        for c in (cache, cache_id, cache_kood):
            for key in list(c.keys()):
                if not klassifikaator_kood or key == klassifikaator_kood or key[0] == klassifikaator_kood:
                    del c[key]
        
    @property
    def in_use(self):
        "Kas klassifikaatori väärtus on kasutusel?"

        # kontrollitakse, kas klassifikaatori väärtusest sõltub on alamklassifikaatoreid
        n = self.queryR.filter_by(ylem_id=self.id).count()
        if n > 0:
            return True

        # kontrollitakse, kas klassifikaatori väärtus on andmetabelites kasutusel
        # klassifikaatoriga täidetud andmevälja nimi on K_kood, kus K on klassifikaatori kood.

        if self.klassifikaator_kood == 'ASTE':
            return True
        elif self.klassifikaator_kood == 'AINEVALD':
            n = (SessionR.query(sa.func.count(Klrida.id))
                 .filter_by(klassifikaator_kood='AINE')
                 .filter_by(ryhm_kood=self.kood)
                 .scalar())
            if n > 0:
                return True
            
        field_name = '%s_kood' % (self.klassifikaator_kood.lower())
        sql = "SELECT table_schema, table_name FROM information_schema.columns WHERE column_name=:name AND is_updatable='YES'"
        params = {'name': field_name}

        ylem = self.ylem
        if ylem:
            if ylem.klassifikaator_kood == 'SPTYYP':
                ylem_field_name = 'tyyp'
            else:
                ylem_field_name = '%s_kood' % (ylem.klassifikaator_kood.lower())
            params1 = {'cname': ylem_field_name}

            ylem2 = ylem.ylem
            if ylem2:
                ylem2_field_name = '%s_kood' % (ylem2.klassifikaator_kood.lower())
                params2 = {'cname': ylem2_field_name}

        for (table_schema, table_name) in SessionR.execute(sa.text(sql), params):
            sql = 'SELECT count(*) FROM %s.%s WHERE %s=:kood' % (table_schema, table_name, field_name)
            params = {'kood': self.kood}

            if self.ylem:
                # vaatame, kas tabelis on ylemklassifikaatori väli
                sql1 = 'SELECT count(*) FROM information_schema.columns WHERE column_name=:cname '+\
                       " AND table_name=:tname AND table_schema=:sname AND is_updatable='YES'"
                params1['tname'] = table_name
                params1['sname'] = table_schema
                on_ylem = SessionR.execute(sa.text(sql1), params1).scalar()
                if on_ylem:
                    # kui ylema väli on olemas, siis kitsendame päringut ylema väärtusega
                    sql += ' AND %s=:ylem_kood' % (ylem_field_name)
                    params['ylem_kood'] = self.ylem.kood

                    if self.ylem.ylem:
                        # vaatame, kas tabelis on ylema ylemklassifikaatori väli
                        sql2 = 'SELECT count(*) FROM information_schema.columns WHERE column_name=:cname '+\
                               " AND table_name=:tname AND table_schema=:sname AND is_updatable='YES'"
                        params2['tname'] = table_name
                        params2['sname'] = table_schema
                        on_ylem2 = SessionR.execute(sa.text(sql2), params2).scalar()
                        if on_ylem2:
                            # kui ylema ylema väli on olemas, siis kitsendame päringut ylema väärtusega
                            sql += ' AND %s=:ylem2_kood' % (ylem2_field_name)
                            params['ylem2_kood'] = self.ylem.ylem.kood

            # leiame klassifikaatori väärtuse esinemiste arvu 
            cnt = SessionR.execute(sa.text(sql), params).scalar()
            if cnt > 0:
                return True
        
        return False

    def lisaalamad(self, klassifikaator_kood, li):
        n = 0
        for rida in li:
            rida.klassifikaator_kood = klassifikaator_kood
            while not rida.kood:
                n += 1
                kood = '%d' % n
                # kas sama kood on juba kasutusel?
                for r in self.alamad:
                    if r.kood == kood:
                        # on kasutusel, ei saa seda kasutada selles kirjes
                        kood = None
                        break
                if kood is None:
                    # on kasutusel
                    continue
                for r in li:
                    if r.kood == kood:
                        # on kasutusel, ei saa seda kasutada selles kirjes
                        kood = None
                        break
                if kood:
                    # kirje saab koodi
                    rida.kood = kood
            self.alamad.append(rida)
        return self

    def update_hkood(self, ylem_hkood=None):
        "Hierarhia koodi uuendamine"
        if ylem_hkood:
            hkood = '%s.%s' % (ylem_hkood, self.kood)
        else:
            ylem = self.ylem
            if ylem:
                if not ylem.hkood:
                    ylem.update_hkood()
                hkood = '%s.%s' % (ylem.hkood, self.kood)
            else:
                hkood = self.kood
        if hkood != self.hkood:
            self.hkood = hkood
        for alam in self.alamad:
            alam.update_hkood(hkood)

    def defaults(self):
        if self.kehtib is None:
            self.kehtib = True

        # automaatne koodi genereerimine kirjete ühekaupa lisamisel
        if self.kood is None or self.kood == '':
            klassifikaator = self.klassifikaator or \
                             Klassifikaator.get(self.klassifikaator_kood)
            #if not self in klassifikaator.read:
            #    klassifikaator.read.append(self)
            #n = klassifikaator.read.index(self) + 1
            n = 0
            rc = False
            while rc == False:
                rc = True
                n += 1
                kood = '%d' % n
                for a in klassifikaator.read:
                    if a.ylem_id == self.ylem_id and a.kood == kood:
                        rc = False
                        break
                    else:
                        log.debug('   %s ylem=%s kood=%s' % (a, a.ylem_id, a.kood))
            self.kood = kood
            log.debug('kood=%s, read=%s' % (kood, [a for a in klassifikaator.read]))
    def before_insert(self):
        self.defaults()
        return EntityHelper.before_insert(self)

    def before_update(self):
        self.defaults()
        return EntityHelper.before_update(self)

class Klvastavus(EntityHelper, Base):
    """EISi ja teiste infosüsteemide (EHIS, oppekava.edu.ee) klassifikaatorite vastavus
    """
    __table_args__ = (
        sa.UniqueConstraint('eis_klrida_id','ehis_klrida_id'),
        )
    id = Column(Integer, primary_key=True, autoincrement=True) 
    eis_klrida_id = Column(Integer, ForeignKey('klrida.id'), index=True) # viide EISi klassifikaatorile
    eis_klrida = relationship('Klrida', foreign_keys=eis_klrida_id, back_populates='ehis_klvastavused')
    ehis_klrida_id = Column(Integer, ForeignKey('klrida.id'), index=True) # viide teise süsteemi klassifikaatorile
    ehis_klrida = relationship('Klrida', foreign_keys=ehis_klrida_id, back_populates='ehis_klvastavused')
    ehis_kl = Column(String(10), nullable=False) # teise (EHISe) klassifikaatori kood
    
class Klseos(EntityHelper, Base):
    """Klassifikaatorikirjete vahelised seosed
    """
    __table_args__ = (
        sa.UniqueConstraint('ylem_klrida_id','alam_klrida_id'),
        )
    id = Column(Integer, primary_key=True, autoincrement=True) 
    ylem_klrida_id = Column(Integer, ForeignKey('klrida.id'), index=True) # viide ülemkirjele
    ylem_klrida = relationship('Klrida', foreign_keys=ylem_klrida_id, back_populates='alam_klseosed')
    alam_klrida_id = Column(Integer, ForeignKey('klrida.id'), index=True) # viide alamkirjele
    alam_klrida = relationship('Klrida', foreign_keys=alam_klrida_id, back_populates='alam_klseosed')

class T_Klassifikaator(EntityHelper, Base):
    """Tabeli Klassifikaator tõlge
    """
    id = Column(Integer, primary_key=True, autoincrement=True) 
    orig_kood = Column(String(10), ForeignKey('klassifikaator.kood'), index=True, nullable=False) # viide lähtetabelile
    orig = relationship('Klassifikaator', foreign_keys=orig_kood) 
    lang = Column(String(2), nullable=False) # tõlkekeel
    nimi = Column(String(100)) # nimetus
    __table_args__ = (
        sa.UniqueConstraint('orig_kood','lang'),
        )

class T_Klrida(EntityHelper, Base):
    """Tabeli Klrida tõlge
    """
    id = Column(Integer, primary_key=True, autoincrement=True)    
    orig_id = Column(Integer, ForeignKey('klrida.id'), index=True, nullable=False) # viide lähtetabelile
    orig = relationship('Klrida', foreign_keys=orig_id) 
    lang = Column(String(2), nullable=False) # tõlkekeel
    nimi = Column(String(500)) # nimetus
    kirjeldus = Column(Text) # täiendav kirjeldus 
    pais = Column(Text) # HTML päisesse lisatav osa (vahendite korral)    
    __table_args__ = (
        sa.UniqueConstraint('orig_id','lang'),
        )
