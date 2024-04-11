import pickle
import uuid
from eiscore.entitybase import *
from .meta import Base, DBSession

class Tempvastus(EntityBase, Base):
    """Lahendaja poolt üles laaditud failide ajutine hoiupaik,
    kui ülesannet lahendatakse proovimiseks, ilma vastuseid salvestamata
    """
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    temp_id = Column(Integer) # vastuse id
    filename = Column(String(256)) # failinimi
    filedata = Column(LargeBinary) # faili sisu
    uuid = Column(String(36)) # äraarvamatu osa URList faili laadimise korral
    
    @classmethod
    def get(cls, id):
        return DBSession.query(cls).filter_by(id=id).first()

    @classmethod
    def get_by_temp_id(cls, handler, temp_id):
        li = handler.request.session.get('tempsooritus') or []
        for _temp_id, tv_id in li:
            if _temp_id == temp_id:
                return cls.get(tv_id)
        if handler.c.user.isikukood:
            tv = (DBSession.query(cls)
                  .filter_by(temp_id=temp_id)
                  .filter_by(creator=str(handler.c.user.id))
                  .first())
            return tv
        
    @classmethod
    def add_temp(cls, handler, sooritus):
        tv = cls(temp_id=sooritus.id,
                 filename='TempSooritus',
                 filedata=pickle.dumps(sooritus))
        DBSession.add(tv)
        DBSession.flush()
        
        session = handler.request.session
        if not session.get('tempsooritus'):
            session['tempsooritus'] = []
        session['tempsooritus'].insert(0, (sooritus.id, tv.id))

        # hoiame meeles mõned viimased sooritused
        MAX_LEN = 20
        while len(session['tempsooritus']) > MAX_LEN:
            sooritus_id, tv_id = session['tempsooritus'].pop()
            tv = cls.get(tv_id)
            if tv:
                DBSession.delete(tv)
        DBSession.flush()
        session.changed()

    @classmethod
    def get_temp(cls, handler, sooritus_id):
        try:
            sooritus_id = int(sooritus_id)
        except:
            return
        #log.info(' GET_TEMP %s' % sooritus_id)
        tv = cls.get_by_temp_id(handler, sooritus_id)
        if tv:
            sooritus = pickle.loads(tv.filedata)
            return sooritus
        
    @classmethod
    def save_temp(cls, handler, sooritus):
        #log.info(' SAVE_TEMP %s' % sooritus.id)
        tv = cls.get_by_temp_id(handler, sooritus.id)
        if tv:
            tv.filedata = pickle.dumps(sooritus)
            DBSession.flush()
        else:
            cls.add_temp(handler, sooritus)

    def gen_uuid(self):
        self.uuid = uuid.uuid4()
        return self.uuid
