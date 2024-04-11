"Testikorralduse andmemudel"

from eis.model.entityhelper import *
from .kvsisu import Kvsisu

class Kysimusevastus(EntityHelper, Base):
    """Sooritaja poolt ühe ülesande ühele küsimusele antud vastuste koondkirje
    """
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    ylesandevastus_id = Column(Integer, ForeignKey('ylesandevastus.id'), index=True, nullable=False)
    ylesandevastus = relationship('Ylesandevastus', foreign_keys=ylesandevastus_id, back_populates='kysimusevastused') # viide ülesande vastusele
    kysimus_id = Column(Integer, index=True, nullable=False)
    kood = Column(String(100)) # küsimuse kood
    sptyyp = Column(String(10)) # sisuploki tüüp (sisuplokk.tyyp)
    baastyyp = Column(String(15)) # baastüüp (tulemus.baastyyp): identifier, boolean, integer, float, string, point, pair, directedPair, duration, file, uri
    sisestus = Column(Integer, sa.DefaultClause('1'), nullable=False) # mitmes sisestamine (1 või 2)
    toorpunktid = Column(Float) # toorpunktid (ülesande skaala järgi)
    pallid = Column(Float) # hindepallid (testiülesande skaala järgi)
    max_pallid = Column(Float) # max hindepallid
    nullipohj_kood = Column(String(10)) # null punkti andmise põhjus, klassifikaator NULLIPOHJ
    kvsisud = relationship('Kvsisu', order_by='Kvsisu.seq', back_populates='kysimusevastus') # vastuse sisu
    kysimusehinded = relationship('Kysimusehinne', back_populates='kysimusevastus')
    ksmarkused = relationship('Ksmarkus', back_populates='kysimusevastus')    

    #kvskannid = relationship('Kvskann', order_by='Kvskann.seq', back_populates='kysimusevastus') # vastuse skann
    oigete_arv = Column(Integer) # õigete vastuste arv (koolipsühholoogitesti jaoks)
    valede_arv = Column(Integer) # valede vastuste arv (koolipsühholoogitesti jaoks)
    vastuseta = Column(Boolean, sa.DefaultClause('false'), nullable=False) # kas anti tühi vastus (siis saab käsitsihinnatav küsimus automaatselt 0p)
    arvutihinnatud = Column(Boolean, sa.DefaultClause('false'), nullable=False) # arvutihinnatav või arvuti poolt hinnatud hübriidhinnatav või käsitsi hinnatav, aga vastuseta
    valikujrk = Column(ARRAY(String(100))) # valikute järjekord antud soorituses (valikute segamisega küsimuse korral)
    testjrk = Column(Integer) # küsimuse jrk nr sooritaja testis (statistikute jaoks)
    
    map_svseq = {} # paari korral vastuste jrk yhe paarilise piires (statvastus jaoks)

    @property
    def kysimus(self):
        from eis.model.ylesanne import Kysimus
        return Kysimus.get(self.kysimus_id)

    def set_kvsisu(self, seq, tyyp, vahetada=False, paarina=None, filedata=None, **kw):
        # paarina=False näitab, et svseq peab loendama kood1 piires
        if seq >= 0:
            self._current_seq = seq # vt blockresponse
        ks = self.give_kvsisu(seq, tyyp)
        ks.tyyp = tyyp
        if kw.get('maatriks') is None:
            kw['maatriks'] = 1
        for key, value in kw.items():
            ks.__setattr__(key, value)
        if filedata:
            # failid salvestame hiljem
            ks._unsaved_filedata = filedata

        # leiame jrk statvastuse jaoks
        if paarina == False:
            key = vahetada and kw.get('kood2') or kw.get('kood1')
            svseq = self.map_svseq.get(key)
            if svseq is None:
                svseq = 0
            else:
                svseq += 1
            self.map_svseq[key] = svseq
        else:
            svseq = seq
        ks.svseq = svseq
        return ks
    
    def get_kvsisud(self):
        # leiame päris vastuste kirjed (seq=SEQ_ANALYSIS jääb välja)
        return [ks for ks in self.kvsisud if ks.seq >= 0]

    def get_kvsisu(self, seq):
        for ks in self.kvsisud:
            if ks.seq == seq:
                return ks

    def give_kvsisu(self, seq, tyyp):
        ks = self.get_kvsisu(seq)
        if not ks:
            ks = Kvsisu(seq=seq, tyyp=tyyp)
            self.kvsisud.append(ks)
            self.kvsisud.sort(key=lambda r: r.seq)
        return ks

    @property
    def kvskannid(self):
        from eis.model.testimine.kvskann import Kvskann
        q = (Session.query(Kvskann)
             .filter_by(kysimusevastus_id=self.id)
             .order_by(Kvskann.seq))
        return [r for r in q.all()]
        
    def get_skann(self, seq):
        for rcd in self.kvskannid:
            if rcd.seq == seq:
                return rcd

    def give_skann(self, seq):
        from eis.model.testimine.kvskann import Kvskann        
        rcd = self.get_skann(seq)
        if not rcd:
            rcd = Kvskann(seq=seq)
            self.kvskannid.append(rcd)
        return rcd
    
    def delete_subitems(self):
        self.delete_subrecords(['kvsisud',
                                'kvskannid',
                                ])
        
def apply_shuffle(valikud, jrk):
    "Valikute segamine (jrk on varem loodud vt blockresponse.gen_shuffle())"
    def _sortfunc(v):
        try:
            return jrk.index(v.kood)
        except ValueError:
            return 0
    if jrk:
        valikud.sort(key=_sortfunc)
    return jrk
