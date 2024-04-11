from eis.model.entityhelper import *

class Olekuinfo(EntityHelper, Base):
    """ADSi klassifikaatori jm viimase uuendamise aeg
    """

    ID_ADS_KOMPONENT = 1 # komponentide klassifikaatori uuendamise seisu kirje ID
    ID_ADS_AADRESS = 2 # aadresside logi jälgimise seisu kirje ID
    ID_KASUTAJA = 3 # kasutajate arv
    ID_TEST_KVS = 94 # koormustestis: ID, millest testkirjete kvsisu.id on suurem
    ID_TEST_YV = 96 # koormustestis: ID, millest testkirjete ylesandevastus.id on suurem
    ID_TEST_TOORVASTUS = 97 # koormustestis: ID, millest testkirjete toorvastus.id on suurem
    id = Column(Integer, primary_key=True) # kirje identifikaator: 1 - ADSi komponentide klassifikaatori uuendamise aeg; 2 - ADSi aadresside logi jälgimise aeg; 3 - kasutajate arv
    seisuga = Column(DateTime) # viimase uuendamise aeg
    seis_id = Column(Integer) # viimase saadud logikirje id

    @classmethod
    def give(cls, id):
        rcd = cls.get(id)
        if not rcd:
            rcd = cls(id=id)
        return rcd
