# -*- coding: utf-8 -*-

import hashlib

from eis.model.entityhelper import *
from eis.model.klassifikaator import Klrida
log = logging.getLogger(__name__)
        
class Leping(EntityHelper, Base):
    """Testide läbiviijatega sõlmitavate lepingute liigid
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    testsessioon_id = Column(Integer, ForeignKey('testsessioon.id'), index=True) # viide testsessioonile    
    testsessioon = relationship('Testsessioon', foreign_keys=testsessioon_id)
    nimetus = Column(String(256), nullable=False) # lepingu nimetus
    url = Column(String(512), nullable=False) # link lepingu teksti PDFile Innove veebis
    #rollivalem = Column(String(92)) # kus lepingut kasutatakse: grupid+ained+testiliigid;...;grupid+ained+testiliigid
    # grupid:
    # HINDAJA_S=29
    # VAATLEJA=28
    # HINDAJA_S2=35
    # HINDAJA_K=30
    # INTERVJUU=36
    # HIND_INT=53
    sessioonita = Column(Boolean, sa.DefaultClause('0')) # kas leping sõlmitakse testsessiooniüleselt
    yldleping = Column(Boolean, sa.DefaultClause('0')) # kas leping on üldine teenuste leping, mis ei lähe akti (kuni 2020)
    lepingurollid = relationship('Lepinguroll', back_populates='leping')
    aasta_alates = Column(Integer) # õppeaasta, alates
    aasta_kuni = Column(Integer) # õppeaasta, kuni
    testilepingud = relationship('Testileping', order_by='Testileping.testimiskord_id', back_populates='leping')
    labiviijalepingud = relationship('Labiviijaleping', back_populates='leping')
    """
    # shindajad ja intervjueerijad + EN/ET2 + riigieksam või põhikoolieksam
    # 29,35,36,53+I,R+r,p
    http://www.innove.ee/UserFiles/lepingud/2015/suuline_hindaja_intervjueerija.pdf
    # khindajad + EN/ET2 + riigieksam või põhikoolieksam
    # 30+I,R+r,p
    http://www.innove.ee/UserFiles/lepingud/2015/kirjalik_inglise_eesti2keelena_hindaja.pdf
    # 29,30,35+M+r
    # hindajad + M + riigieksam
    http://www.innove.ee/UserFiles/lepingud/2015/matemaatika_hindaja.pdf
    # hindajad + E + riigieksam (pole suulist osa)
    # 30+E+r
    http://www.innove.ee/UserFiles/lepingud/2015/eesti_keel_hindaja.pdf
    # vaatlejad + riigieksamid; vaatlejad + ET2 + põhikool
    # 28++r;28+R+p
    http://www.innove.ee/UserFiles/lepingud/2015/valisvaatleja.pdf

    # # yldtingimused kuni 2015
    # # 28,29,30,35++r,p
    # http://www.innove.ee/UserFiles/Organisatsioonist/lepingutingimused.pdf

    # yldtingimused
    # 28,29,30,35++r,p,rv;46,38,47,36,53,29,35,30++te;36,53+I,R+r,p
    http://www.innove.ee/UserFiles/Organisatsioonist/Innove_teenuste_osutamise_uldtingimused_01_09_2015.pdf

    # # komisjoniesimehed,komisjonillikmed,konsultandid,intervjueerijad,suuline I hindaja + riigikeel + TE
    # # 46,38,47,36,53,29+RK+te
    # http://www.innove.ee/UserFiles/lepingud/2016/riigikeel_labiviija.pdf
    # # TE suuline II hindaja, kirjalik hindaja + riigikeel + TE
    # # 35,30+RK+te
    # http://www.innove.ee/UserFiles/lepingud/2016/riigikeel_hindaja.pdf

    # komisjoniesimehed,komisjonillikmed,konsultandid,intervjueerijad,suuline I hindaja,
    # suuline II hindaja, kirjalik hindaja + riigikeel + TE
    # 46,38,47,36,53,29,30,35+RK+te
    http://www.innove.ee/UserFiles/lepingud/2016/riigikeel_labiviija-hindaja.pdf

    # suuline I hindaja,suuline II hindaja, kirjalik hindaja + prantsuse keel + rahvusvaheline eksam
    29,30,35+P+rv
    http://www.innove.ee/UserFiles/lepingud/2016/prantsuse_hindaja.pdf
    """

    @property
    def on_hindajaleping(self):
        "Kas on selline leping, mille juures saab anda nõusolekud III hindajana osalemiseks"
        if not self.yldleping:
            grupid = (const.GRUPP_HINDAJA_K,
                      const.GRUPP_HINDAJA_S,
                      const.GRUPP_HINDAJA_S2)
            q = (Session.query(sa.func.count(Lepinguroll.id))
                 .filter_by(leping_id=self.id)
                 .filter(Lepinguroll.testiliik_kood!=const.TESTILIIK_TASE)
                 .filter(Lepinguroll.kasutajagrupp_id.in_(grupid))
                 )
            return q.scalar() > 0
        return False

    @classmethod
    def opt_hindajaleping(cls):
        grupid = (const.GRUPP_HINDAJA_K,
                  const.GRUPP_HINDAJA_S,
                  const.GRUPP_HINDAJA_S2)
        q = (SessionR.query(Leping)
             .filter(Leping.yldleping==False)
             .filter(Leping.lepingurollid.any(Lepinguroll.kasutajagrupp_id.in_(grupid)))
             .order_by(Leping.nimetus))
        li = []
        for l in q.all():
            li.append((l.id, l.nimetus))
        return li

    @classmethod
    def opt_hindajaained(cls):
        grupid = (const.GRUPP_HINDAJA_K,
                  const.GRUPP_HINDAJA_S,
                  const.GRUPP_HINDAJA_S2)
        q = (SessionR.query(Lepinguroll.aine_kood, Klrida.nimi).distinct() # ctran?
             .filter(Lepinguroll.kasutajagrupp_id.in_(grupid))
             .join((Klrida, sa.and_(Klrida.kood==Lepinguroll.aine_kood,
                                    Klrida.klassifikaator_kood=='AINE')))
             .order_by(Klrida.nimi))
        return [r for r in q.all()]

    def get_hindajaained(self):
        grupid = (const.GRUPP_HINDAJA_K,
                  const.GRUPP_HINDAJA_S,
                  const.GRUPP_HINDAJA_S2)
        q = (SessionR.query(Lepinguroll.aine_kood).distinct()
             .filter(Lepinguroll.kasutajagrupp_id.in_(grupid))
             .filter(Lepinguroll.leping==self))
        return [r for r, in q.all()]
        

class Lepinguroll(EntityHelper, Base):
    """Rollid, mille jaoks leping sõlmitakse
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    leping_id = Column(Integer, ForeignKey('leping.id'), index=True, nullable=False) # viide lepingule
    leping = relationship('Leping', foreign_keys=leping_id, back_populates='lepingurollid')
    kasutajagrupp_id = Column(Integer, ForeignKey('kasutajagrupp.id'), index=True, nullable=False) # roll
    aine_kood = Column(String(10)) # õppeaine, klassifikaator AINE
    testiliik_kood = Column(String(10), nullable=False) # testi liik, klassifikaator TESTILIIK

class Labiviijaleping(EntityHelper, Base):
    """Testide läbiviija nõusolek testsessiooni ja rolliga seotud lepingu tingimustega
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kasutaja_id = Column(Integer, ForeignKey('kasutaja.id'), index=True, nullable=False) # viide kasutajale
    kasutaja = relationship('Kasutaja', foreign_keys=kasutaja_id, back_populates='labiviijalepingud')
    testsessioon_id = Column(Integer, ForeignKey('testsessioon.id'), index=True) # viide testsessioonile    
    testsessioon = relationship('Testsessioon', foreign_keys=testsessioon_id)
    leping_id = Column(Integer, ForeignKey('leping.id'), index=True, nullable=False) # viide lepingule
    leping = relationship('Leping', foreign_keys=leping_id, back_populates='labiviijalepingud')
    noustunud = Column(DateTime) # lepinguga nõustumise aeg
    on_hindaja3 = Column(Boolean) # kas on nõus osalema kolmanda hindajana

    __table_args__ = (
        sa.UniqueConstraint('kasutaja_id', 'leping_id', 'testsessioon_id'),
        )
    
class Testileping(EntityHelper, Base):
    """Testimiskorra seos lepingutega, mis on testimiskorra läbiviimiseks vajalikud
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    testimiskord_id = Column(Integer, ForeignKey('testimiskord.id'), index=True, nullable=False) # viide testimiskorrale
    testimiskord = relationship('Testimiskord', back_populates='testilepingud')
    leping_id = Column(Integer, ForeignKey('leping.id'), index=True, nullable=False) # viide lepingule
    leping = relationship('Leping', foreign_keys=leping_id, back_populates='testilepingud')
    kasutajagrupp_id = Column(Integer, ForeignKey('kasutajagrupp.id'), index=True) # läbiviija roll, mille korral leping on vajalik
    kasutajagrupp = relationship('Kasutajagrupp', foreign_keys=kasutajagrupp_id)

    @property
    def kasutajagrupp_nimi(self):
        if self.kasutajagrupp:
            return self.kasutajagrupp.nimi

    @classmethod
    def give_for(cls, tkord):
        required = list()
        if tkord.testsessioon_id:
            from eis.model.test.test import Test
            from eis.model.test.testsessioon import Testsessioon
            test = tkord.test or Test.get(tkord.test_id)
            testsessioon = Testsessioon.get(tkord.testsessioon_id)
            # leiame testimiskorra jaoks vajalikud lepingud
            q = (Session.query(Leping.id,
                               Lepinguroll.kasutajagrupp_id)
                 .filter(sa.or_(Leping.aasta_alates==None,
                                Leping.aasta_alates<=testsessioon.oppeaasta))
                 .filter(sa.or_(Leping.aasta_kuni==None,
                                Leping.aasta_kuni>=testsessioon.oppeaasta))                 
                 .join(Leping.lepingurollid)
                 .filter(sa.or_(Lepinguroll.aine_kood==None,
                                Lepinguroll.aine_kood==test.aine_kood))
                 .filter(Lepinguroll.testiliik_kood==test.testiliik_kood)
                 )
            for leping_id, grupp_id in q.all():
                required.append((grupp_id, leping_id))

        # kustutame liigsed lepingud
        for rcd in list(tkord.testilepingud):
            try:
                required.remove((rcd.kasutajagrupp_id, rcd.leping_id))
            except ValueError:
                rcd.delete()

        # lisame uued lepingud
        for grupp_id, leping_id in required:
            rcd = cls(kasutajagrupp_id=grupp_id,
                      leping_id=leping_id)
            tkord.testilepingud.append(rcd)
                
                


