"Testikorralduse andmemudel"
from eis.model.entityhelper import *

class Tunnistusekontroll(EntityHelper, Base):
    """Tunnistuse PDFi metaandmete kontroll
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tunnistus_id = Column(Integer, ForeignKey('tunnistus.id'), index=True, nullable=False) # viide tunnistusele
    tunnistus = relationship('Tunnistus', foreign_keys=tunnistus_id, back_populates='tunnistusekontroll')
    seisuga = Column(DateTime) # viimase kontrollimise aeg
    korras = Column(Boolean, nullable=False) # kontrolli tulemus: true - korras; false - viga
    viga = Column(String(256)) # vea korral vea kirjeldus

    @classmethod
    def encode_metadata(cls, kasutaja, sooritajad):
        li = [cls.encode_isik(kasutaja)]
        for sooritaja in sooritajad:
            li.append(cls.encode_sooritaja(sooritaja))
        data = ';'.join(li)
        version = '1'
        return version, data

    @classmethod
    def encode_isik(cls, kasutaja):
        if kasutaja.isikukood:
            ik = kasutaja.isikukood
        else:
            ik = kasutaja.synnikpv and kasutaja.synnikpv.strftime('%d.%m.%Y') or ''
        return ik

    @classmethod
    def encode_sooritaja(cls, sooritaja):
        if sooritaja.pallid is None:
            tulem = '-'
        else:
            tulem = re.sub(r'\,?0+$', '', ('%.3f' % sooritaja.pallid)
                           .replace('.',','))
        test = sooritaja.test
        return '%s %s' % (test.aine_kood, tulem)
