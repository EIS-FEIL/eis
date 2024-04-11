"Tööde PDF failid koos hindamisjuhendiga koolidele jagamiseks"

import mimetypes
import re
from lxml import etree
import urllib.request, urllib.parse, urllib.error

from eis.model.entityhelper import *
  
class Statistikaraport(EntityHelper, Base, S3File):
    """Eksami statistika raport avalikus vaates alla laadimiseks
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('test.id'), index=True, nullable=False) # viide testile, kui fail käib teatud testi kohta ja on loetav koolides, kus on selle testi sooritajaid
    test = relationship('Test', foreign_keys=test_id)
    #test = relationship('Test', foreign_keys=test_id, back_populates='statistikaraportid')
    kursus_kood = Column(String(10)) # lai või kitsas (matemaatika korral), klassifikaator KURSUS        
    aasta = Column(Integer, nullable=False) # aastaarv
    filename = Column(String(256)) # failinimi
    filesize = Column(Integer) # faili suurus baitides
    fileversion = Column(String(8)) # versioon
    avalik = Column(Boolean, sa.DefaultClause('0'), nullable=False) # kas raport on üle vaadatud ja avalik
    format = Column(String(6)) # faili formaat: pdf, html    
    _cache_dir = 'statistikaraport'

    @classmethod
    def get_raportid(cls, test_id, kursus, aasta, _format=None):
        "Leitakse antud testi/aasta/kursuse kõik raportid"
        q = (SessionR.query(Statistikaraport)
             .filter_by(test_id=test_id)
             .filter_by(aasta=aasta)
             )
        if kursus:
            q = q.filter_by(kursus_kood=kursus)
        if _format:
            q = q.filter_by(format=_format)
        q = q.order_by(Statistikaraport.id)
        return list(q.all())

    @classmethod
    def get_raport(cls, test_id, kursus, aasta, _format='pdf'):
        "Leitakse raport"
        for r in cls.get_raportid(test_id, kursus, aasta, _format):
            return r

    @classmethod
    def give_raport(cls, test_id, kursus, aasta, _format='pdf'):
        "Luuakse raport"
        r = cls.get_raport(test_id, kursus, aasta, _format)
        if not r:
            r = Statistikaraport(aasta=aasta,
                                 kursus_kood=kursus or None,
                                 test_id=test_id,
                                 format=_format)
        return r

    @classmethod
    def remove_raportid(cls, test_id, aasta, avalik):
        for r in cls.get_raportid(test_id, None, aasta):
            if (avalik is None) or r.avalik == avalik:
                r.delete()

