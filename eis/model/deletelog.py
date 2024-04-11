# -*- coding: utf-8 -*-
import pickle
from .entityhelper import *
log = logging.getLogger(__name__)

class Deletelog(EntityHelper, Base):
    """Kustutatud kirjete logi.
    Vajalik jälgede ajamiseks ja ka selleks,
    et kohalikus serveris teaks kustutada keskserveris kustutatud kirjed.
    """
    id = Column(Integer, primary_key=True, autoincrement=True)
    deleted_id = Column(Integer, nullable=False, index=True) # kustutatud kirje ID
    deleted_table = Column(String(50), nullable=False) # kustutatud kirje tabeli nimi
    data = Column(Text) # kustutatud kirje sisu stringina
    bdata = Column(LargeBinary) # kustutatud kirje pickle-formaadis
    delete_logging = True # siit saab logimise skriptisiseselt välja keerata
    logging = False
    
    @classmethod
    def add(cls, rcd):
        try:
            deleted_id = rcd.id
        except:
            # tõlketabeli korral
            try:
                deleted_id = rcd.orig_id
            except:
                # mingi selline tabel, millel pole id ega orig_id välja
                # näiteks Testiliik. sellise tabeli kirjeid polegi vaja logida
                deleted_id = None

        if deleted_id and cls.delete_logging:
            return Deletelog(rcd, deleted_id)

    def __init__(self, rcd, deleted_id):
        self.deleted_id = deleted_id
        self.deleted_table = rcd.__table__.name
        try:
            #self.data = rcd.as_str()
            di = rcd.pack_row()
            self.bdata = pickle.dumps(di)
            sdata = ''
            for key, value in di.items():
                if key == 'class' or value is None:
                    continue
                elif isinstance(value, datetime):
                    value = value.strftime('%d.%m.%Y %H.%M.%S')
                elif isinstance(value, date):
                    value = value.strftime('%d.%m.%Y')
                elif not isinstance(value, (str,int,bool,float)):
                    value = '*'
                sdata += f'{key}: {value}; '
                if key == 'fileversion' and value:
                    # kustutatava kirjega on seotud fail
                    # märkida failiserveris fail kustutamiseks
                    rcd.set_file_deleted()
            self.data = sdata
        except Exception as ex:
            log.error('deletelog: ' + ex)
            pass
        Session.add(self)
        for prop in self.__mapper__.relationships:
            if prop.direction.name == 'MANYTOONE':
                parent = rcd.__getattr__(prop.key)
                if parent:
                    Deletelog_parent(deletelog=self, 
                                     parent_id=parent.id,
                                     parent_table=prop.target.__table__.name)
        
class Deletelog_parent(EntityHelper, Base):
    """Kustutatud kirjete vanemtabelite logi.
    Vajalik selleks, et ka kohalikus serveris teaks kustutada keskserveris kustutatud kirjed.
    """
    logging = False
    id = Column(Integer, primary_key=True, autoincrement=True)
    deletelog_id = Column(Integer, ForeignKey('deletelog.id'), index=True) # viide kustutatud kirje logile
    deletelog = relationship('Deletelog', foreign_keys=deletelog_id)
    parent_id = Column(Integer) # kustutatud kirje vanemtabeli ID
    parent_table = Column(String(50)) # kustutatud kirje vanemtabeli nimi

        
