# -*- coding: utf-8 -*-
"Testikorralduse andmemudel"

from eis.model.entityhelper import *

class Kvstatistika(EntityHelper, Base):
    """Üksikküsimuste vastuste statistika
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    kysimusestatistika_id = Column(Integer, ForeignKey('kysimusestatistika.id'), index=True, nullable=False) # viide küsimusele
    kysimusestatistika = relationship('Kysimusestatistika', foreign_keys=kysimusestatistika_id, back_populates='kvstatistikad')
    vastuste_arv = Column(Integer, nullable=False) # antud vastuse andnute arv
    tyyp = Column(String(1)) # vastuse tüüp: NULL - vastust pole (kirjet kasutatakse hindepallide jaoks); t=const.RTYPE_CORRECT - õige/vale; s=const.RTYPE_STRING - sisu; f=const.RTYPE_FILE - filedata ja filename; i=const.RTYPE_IDENTIFIER - kood1; p=const.RTYPE_PAIR - kood1 ja kood2; o=const.RTYPE_ORDERED - järjestus; c=const.RTYPE_COORDS - koordinaadid; x=const.RTYPE_POINT - punkt
    sisu = Column(Text) # vabatekstiline vastus või muu mitte-valikvastus (nt punkti koordinaadid)
    kood1 = Column(String(256)) # valikvastuse korral valiku kood
    kood2 = Column(String(256)) # valikvastuste paari korral teise valiku kood
    oige = Column(Integer) # kas vastus oli õige või vale: 0=const.C_VALE - vale; 2=const.C_OIGE - õige; 8=const.C_LOETAMATU - loetamatu; 9=const.C_VASTAMATA - vastamata (õige/vale sisestamise korral sisestatakse; vastuse olemasolu korral arvutihinnatavas ülesandes arvutatakse hindamismaatriksi põhjal; kui hindaja määrab pallid; siis max pallide korral 2=const.C_OIGE; muu positiivse palli korral 1=const.C_OSAOIGE; 0p korral 0=const.C_VALE; '-' korral 9=const.C_VASTAMATA)
    maatriks = Column(Integer, sa.DefaultClause('1'), nullable=False) # mitmenda hindamismaatriksiga see vastus on hinnatav
    hindamismaatriks_id = Column(Integer) # viide hindamismaatriksi kirjele, vajalik statistikas vastuse selgituse otsimisel
