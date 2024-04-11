"Ülesande andmemudel"

from PIL import Image
import mimetypes
import re
from lxml import etree
import urllib.request, urllib.parse, urllib.error

from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
from .valikvastus import Valikvastus
from .hindamismaatriks import Hindamismaatriks

class Tulemus(EntityHelper, Base):
    """Küsimusele antud vastuse hindamise tingimused ehk hindamismaatriks.
    Kirje vastab ühele küsimusele.
    Tulemuse jaoks on eraldi tabel tehtud QTIst mõjutatult
    (QTI vaste responseDeclaration, osaliselt ka responseDeclaration/mapping),
    põhimõtteliselt võiks QTIs olla üks tulemuse kirje mitme küsimuse peale.
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    kood = Column(String(30), nullable=False) # küsimuse kood, seob tulemuse kirje küsimusega
    yhisosa_kood = Column(String(10)) # eri ülesannete küsimuste sidumiseks kasutatav kood, kui küsimuste statistika tehakse ühiselt
    kardinaalsus = Column(String(10), sa.DefaultClause('single'), nullable=False) # QTI cardinality: single, multiple, ordered, orderedAdj, orderedSeq
    baastyyp = Column(String(15), nullable=False) # QTI baseType: identifier, boolean, integer, float, string, point, pair, directedPair, duration, file, uri
    min_pallid = Column(Float, sa.DefaultClause('0')) # minimaalne pallide arv, QTI lowerBound
    max_pallid = Column(Float) # QTI upperBound, koostaja määratud max pallide arv; kui punktiarvutus arvutab suurema pallide arvu, siis antakse max_pallid palli
    vaikimisi_pallid = Column(Float, sa.DefaultClause('0')) # hindamismaatriksis puuduva vastuse eest antavad pallid; QTI defaultValue
    oige_pallid = Column(Float) # õige vastuse eest antavad pallid (mitme valikuga tabelis, kus õige vastus märgitakse märkeruuduga)
    vastus_pallid = Column(Boolean) # kas küsimuse vastus ongi punktide arv (arvutatud väärtuse korral)
    max_pallid_arv = Column(Float, sa.DefaultClause('0')) # arvutatud max võimalik pallide arv, kui max_pallid oleks seadmata
    max_pallid_vastus = Column(Float) # hindamismaatriksis olev max pallide arv ühe üksikvastuse eest (kasutusel üksikvastuse õigsuse määramisel)
    max_vastus = Column(Integer) # kui vastuseid on sellest arvust rohkem, siis antakse min_pallid
    min_oige_vastus = Column(Integer) # kui õigeid vastuseid on sellest arvust vähem, siis antakse min_pallid
    min_sonade_arv = Column(Integer) # kui vastuses on arvust vähem sõnu, siis antakse min_pallid (avatud vastuse korral)
    pintervall = Column(Float) # lubatud punktide intervall (käsitsi hindamisel)
    tyhikud = Column(Boolean) # kas vastuse võrdlemisel arvestada tühikuid (true - arvestada, false - ignoreerida), juhul kui baastüüp on "string"
    lubatud_tyhi = Column(Boolean) # kas on lubatud tühi vastus (kui baastüüp on "string", "integer" või "float")
    tostutunne = Column(Boolean) # kas vastuse võrdlemisel olla tõstutundlik (kui baastüüp on "string"): true - tõstutundlik; false - tõstutundetu
    ladinavene = Column(Boolean) # kas vastuse võrdlemisel lugeda sama välimusega ladina ja vene tähed samaväärseks
    regavaldis = Column(Boolean) # kas vastuse võrdlemisel võtta hindamismaatriksi vastust regulaaravaldisena, juhul kui baastüüp on "string"
    regavaldis_osa = Column(Boolean) # kui kasutatakse regulaaravaldist, siis kas sellega kontrollitakse tekstiosa vastavust: true - tekstiosa vastamine avaldisele, false - terve vastuse vastamine avaldisele
    valem = Column(Boolean) # kas vastuse võrdlemisel võtta hindamismaatriksi vastust valemina (võib viidata teistele küsimustele), juhul kui baastüüp on arvuline
    #teisendatav = Column(Boolean) # kas vastuse võrdlemisel vastust lihstustatakse (matemaatika korral)
    vordus_eraldab = Column(Boolean) # kas võrdusmärk eraldab vastused, mida võrreldakse hindamismaatriksiga ükshaaval ja antakse palle kõrgeime pallide arvuga vastuse eest (matemaatika korral)
    koik_oiged = Column(Boolean) # kui võrdusmärk eraldab vastused, kas siis punktide saamiseks peavad kõik osad olema õiged (matemaatika korral)
    sallivusprotsent = Column(Float) # lubatud erinevus protsentides 
    ymard_komakohad = Column(Integer) # mitme kohani peale koma vastus hindamismaatriksiga võrdlemisel ümardatakse (kui baastyyp=float)
    ymardet = Column(Boolean) # kas hindamismaatriksis olevad arvud on ümardatud (true korral on tabamus juhul, kui lahendaja vastust saab ümardada hindamismaatriksis olevaks arvuks; false korral peab lahendaja vastama täpselt sama arvuga), reaalarvude korral
    arvutihinnatav = Column(Boolean) # kas tulemusele vastav küsimus on arvutiga hinnatav
    hybriidhinnatav = Column(Boolean) # kas käsitsihinnatav ülesanne on arvutihinnatav nende vastuste osas, mis leiduvad hindamismaatriksis
    naidisvastus = Column(Text) # näidisvastus (selgitav tekst) või hindamisjuhend
    naidis_naha = Column(Boolean) # kas näidisvastust näidata lahendajale (peale lahendamist) või ainult hindajale
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True) # viide ülesandele
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id, back_populates='tulemused')
    naide = Column(Boolean) # kas kysimus on vastuse näide (siis kuvatakse õige vastus alati lahendajale ja selle kysimuse eest palle ei anta); kui kogu sisuplokk on näide, siis vt sisuplokk.naide
    maatriksite_arv = Column(Integer, sa.DefaultClause('1'), nullable=False) # hindamismaatriksite arv
    hindamismaatriksid = relationship('Hindamismaatriks', order_by='Hindamismaatriks.jrk,Hindamismaatriks.id', back_populates='tulemus')
    valikvastused = relationship('Valikvastus', order_by='Valikvastus.maatriks', back_populates='tulemus')    
    oigsus_kysimus_id = Column(Integer, ForeignKey('kysimus.id'), index=True) # viide küsimusele, mille tulemus näitab, kas antud küsimus vastati õigesti (kasutusel õigete/valede vastuste värvimisel ja mitme küsimuse koos käsitsihindamisel)
    oigsus_kysimus = relationship('Kysimus', foreign_keys=oigsus_kysimus_id)
    kysimused = relationship('Kysimus', foreign_keys='Kysimus.tulemus_id', back_populates='tulemus') # viide kysimuse kirjele
    trans = relationship('T_Tulemus', cascade='all', back_populates='orig')

    _parent_key = 'ylesanne_id'

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .ylesanne import Ylesanne
        parent = self.ylesanne or self.ylesanne_id and Ylesanne.get(self.ylesanne_id)
        if parent:
            parent.logi('Tulemus %s %s %s' % (self.kood, self.id or '', liik), vanad_andmed, uued_andmed, logitase)

    def get_max_pallid(self, koefitsient=1):
        punktid = self.max_pallid
        if punktid is None:
            punktid = self.max_pallid_arv
        if punktid is not None and koefitsient is not None:
            return punktid * koefitsient

    def calc_max_pallid(self):
        """Arvutatakse tulemuse maksimaalne võimalik pallide arv.
        """
        from eis.model.ylesanne.sisuplokk import Sisuplokk
        if self.naide:
            summa = 0
        elif self.kardinaalsus in (const.CARDINALITY_ORDERED,
                                   const.CARDINALITY_ORDERED_ADJ,
                                   const.CARDINALITY_ORDERED_SEQ,
                                   const.CARDINALITY_ORDERED_SQ1,
                                   const.CARDINALITY_ORDERED_POS,
                                   const.CARDINALITY_ORDERED_COR):
            summa = 0
            for kysimus in self.kysimused:
                sp = kysimus.sisuplokk or Sisuplokk.get(kysimus.sisuplokk_id)
                if sp.naide:
                    continue
                # leiame parimad pallid
                for entry in kysimus.best_entries():
                    if entry.pallid is not None:
                        summa += entry.pallid
                    elif entry.oige:
                        summa += 1
        else:
            summa = 0
            vaikimisi = self.vaikimisi_pallid or 0
            vastuste_arv = 0
            #log.debug('tulemus.calc_max_pallid, kood=%s' % self.kood)

            for kysimus in self.kysimused:
                sp = kysimus.sisuplokk or Sisuplokk.get(kysimus.sisuplokk_id)
                if sp.naide:
                    continue
                min_vastus = kysimus.get_min_vastus()
                max_vastus = kysimus.get_max_vastus()
                li_pallid = [m.get_pallid() for m in kysimus.best_entries()]

                # iga valikut saab ühe korra valida
                pallid = 0
                log.debug('Kysimus %s (min %s, max %s), pos pallid %s' % \
                              (kysimus, min_vastus, max_vastus, str(li_pallid)))
                for i in range(max_vastus):
                    vastuste_arv += 1
                    #log.debug('vastuste arv %s, i=%s' % (vastuste_arv, i))
                    if len(li_pallid) > i and li_pallid[i] > vaikimisi:
                        lisada = li_pallid[i]
                    else:
                        lisada = vaikimisi
                    #log.debug('   lisada %s' % lisada)
                    if lisada < 0 and i >= min_vastus:
                        # mõistlikeim vastuste arv on täis, edasi tulevad miinimumpallid
                        break
                    pallid += lisada
                    #log.debug('   pallid=%s' % pallid)
                summa += pallid
            if len(self.kysimused) == 0:
                log.debug('tulemusel %s %s pole kasutuskohti' % (self.kood, self.id))

        log.debug('tulemuse %s %s max=%s/%s, ah=%s' % (self.kood,self.kardinaalsus,self.max_pallid,summa, self.arvutihinnatav))
        self.max_pallid_arv = summa
        return summa

    def copy(self):
        cp = EntityHelper.copy(self)
        self.copy_subrecords(cp, ['hindamismaatriksid',
                                  #'valikvastused',
                                  'trans'])
        return cp

    def pack_subrecords(self, delete=True, modified=None):
        li = []
        for rcd in self.hindamismaatriksid:
            li.extend(rcd.pack(delete, modified))
        if not self.ylesanne.pack_for_rpc:
            for rcd in self.trans:
                li.extend(rcd.pack(delete, modified))
        for rcd in self.valikvastused:
            li.extend(rcd.pack(delete, modified))
        return li

    def get_maatriksid(self):
        """Leiame hindamismaatriksid (kui neid on mitu - järjestamisel)"""
        di = {}
        for hm in self.hindamismaatriksid:
            n_mx = hm.maatriks
            if n_mx not in di:
                di[n_mx] = []
            di[n_mx].append(hm)

        li = []
        for n_mx in sorted(di.keys()):
            li.append((n_mx, di[n_mx]))
        return li

    def best_entries(self, max_vastus, correct=False):
        """Leiame vastused, mille korral saaks kõige rohkem hindepalle.
        Kutsuda kysimus.best_entries() kaudu, kuna oluline loogika on seal.
        """
        if self.max_vastus is not None and max_vastus is not None and self.max_vastus < max_vastus:
            max_vastus = self.max_vastus
            
        q = (Hindamismaatriks.query
             .filter_by(tulemus_id=self.id)
             .filter(sa.or_(Hindamismaatriks.pallid>0, Hindamismaatriks.oige==True))
             .filter(Hindamismaatriks.maatriks<3)
             )

        if self.kardinaalsus in (const.CARDINALITY_ORDERED,
                                 const.CARDINALITY_ORDERED_SEQ,
                                 const.CARDINALITY_ORDERED_ADJ,
                                 const.CARDINALITY_ORDERED_POS,
                                 const.CARDINALITY_ORDERED_COR):
            q = q.order_by(Hindamismaatriks.id)
        elif self.kardinaalsus == const.CARDINALITY_ORDERED_SQ1:
            # kui leidub mõni "õige" rida, siis kuvame ainult õiged read antud järjekorras
            # hindamismaatriksis võib olla ka alternatiivseid vastuseid, mida alati ei pea vastama
            q1 = q.filter(Hindamismaatriks.oige==True)
            if q1.count() > 0:
                q = q1
            q = q.order_by(Hindamismaatriks.id)
        else:
            if correct:
                # leiame vastused õige vastusena näitamiseks
                # eelistame märkeruuduga "õige" vastuseid
                q = q.order_by(sa.desc(sa.func.coalesce(Hindamismaatriks.oige, False)),
                               sa.desc(Hindamismaatriks.pallid),
                               Hindamismaatriks.id)
            else:
                # leiame vastused, mis annavad kõige rohkem punkte
                q = q.order_by(sa.desc(Hindamismaatriks.pallid),
                               sa.desc(sa.func.coalesce(Hindamismaatriks.oige, False)),
                               Hindamismaatriks.id)                        

        if max_vastus:
            q = q.limit(max_vastus)
        return q.all()

    def set_valikvastus(self,
                        valik1_kysimus_id,
                        valik2_kysimus_id,
                        maatriks=1,
                        vahetada=False,
                        statvastuses=True,
                        sisujarjestus=False,
                        paarina=None,
                        mittevastus=None,
                        analyys1=False):
        # valikvastuse kirje salvestamine, mis määrab, kuidas andmeid statistikutele kuvada
        vv = None
        for r in self.valikvastused:
            if r.maatriks == maatriks:
                vv = r
                break
        if not vv:
            vv = Valikvastus(tulemus_id=self.id, maatriks=maatriks)
            self.valikvastused.append(vv)
            
        vv.valik1_kysimus_id = valik1_kysimus_id
        vv.valik2_kysimus_id = valik2_kysimus_id
        vv.vahetada = vahetada
        vv.statvastuses = statvastuses
        vv.mittevastus = mittevastus
        vv.sisujarjestus = sisujarjestus
        vv.paarina = paarina
        vv.analyys1 = analyys1
        
    def delete_subitems(self):    
        self.delete_subrecords(['hindamismaatriksid',
                                'valikvastused',
                                ])
