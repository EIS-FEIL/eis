import cgi
import pickle
import eiscore.const as const
from eiscore.entitybase import *
from eis.s3file import S3File
from .meta import Base, DBSession
    
class Toorvastus(EntityBase, Base, S3File):
    """Testi sooritamise ajal saadetud ühe ülesande vastused.
    Tulemuste arvutamise ajal jagatakse need andmed põhibaasi tabelitesse
    kysimusevastus ja kvsisu, kuid see võtab aega ning testiaegse jõudluse
    optimeerimiseks tehakse seda alles siis, kui on vaja arvutada tulemusi.
    Kuni toorvastus ei ole veel põhibaasi viidud,
    seni on põhibaasis ylesandevastus.on_toorvastus = True
    """
    id = Column(Integer, primary_key=True, autoincrement=True)    
    ylesandevastus_id = Column(Integer, nullable=False, index=True) # põhibaasi ylesandevastus.id
    kood = Column(String(102), nullable=False) # küsimuse kood
    sisu = Column(Text) # tekstvastus (kui pole fail)
    filename = Column(String(256)) # failinimi (kui on fail)
    filesize = Column(Integer) # faili suurus baitides
    fileversion = Column(String(8)) # versioon
    on_pickle = Column(Boolean) # kas filedata sisaldab pickle-pakitud sisu (kasutusel siis, kui vastus on list)

    _cache_dir = 'toorvastus'
    _id_seq_name = 'toorvastus_id_seq'

    def give_seq_id(self):
        if not self.id and self._id_seq_name:
            seq = sa.Sequence(self._id_seq_name)
            self.id = DBSession.execute(seq)
        return self.id

    @classmethod
    def get_by_kood(cls, yv_id, kood):
        q = (DBSession.query(cls)
             .filter_by(ylesandevastus_id=yv_id)
             .filter_by(kood=kood)
             )
        return q.first()

    @classmethod
    def save_params(cls, yv_id, params):
        "Salvestatakse ülesande vastused ja ülesande vastamise info"
        vastuseta = True
        DBSession.begin()
        for key, value in params.items():
            # R_, DR_, b - vastused
            # vb - vbloadtm, vbsavetm, vbtimer_* 
            if key.startswith(const.RPREFIX) \
                   or key.startswith(const.DUMMY_RPREFIX) \
                   or key.startswith('b') \
                   or key.startswith('vb'):
                sisu = filename = filedata = None
                on_pickle = False
                if isinstance(value, cgi.FieldStorage):
                    filedata = value.value
                    filename = _fn_local(value.filename)
                elif isinstance(value, list):
                    filedata = pickle.dumps(value)
                    on_pickle = True
                else:
                    sisu = value

                if filename or sisu or on_pickle:
                    vastuseta = False

                # leiame kirje, kuhu salvestada
                trv = Toorvastus.get_by_kood(yv_id, key)
                if not trv:
                    # uus toorvastus
                    trv = Toorvastus(ylesandevastus_id=yv_id,
                                     kood=key,
                                     sisu=sisu,
                                     filename=filename,
                                     filedata=filedata,
                                     on_pickle=on_pickle)
                    DBSession.add(trv)
                    #log.debug('NEW TOORVASTUS %d %s %s' % (yv_id, key, filename or ''))
                elif not filename and trv.filename:
                    # varem salvestatud fail, praegu faili pole - ei muuda midagi
                    #log.debug('IGN TOORVASTUS %s' % trv.filename)
                    pass
                else:
                    # olemasoleva toorvastuse yle kirjutamine
                    #log.debug('SET TOORVASTUS %d %s %s' % (yv_id, key, filename or ''))
                    trv.sisu = sisu
                    trv.filename = filename
                    trv.filedata = filedata
                    trv.on_pickle = on_pickle
            #else:
            #    log.debug('ei salvesta: %s' % key)
        DBSession.commit()
        return vastuseta

    @classmethod
    def get_params(cls, yv_id):
        q = (DBSession.query(Toorvastus)
             .filter_by(ylesandevastus_id=yv_id))
        params = {}
        for trv in q.all():
            if trv.filename:
                value = TFileStorage(trv)
            elif trv.on_pickle:
                value = pickle.loads(trv.filedata)
            else:
                value = trv.sisu
            key = trv.kood
            #log.debug('GET TOORVASTUS %d %s %s' % (yv_id, key, trv.filename or ''))
            params[key] = value
        return params
    
class TFileStorage:
    "Failina antud vastuse esitamine cgi.FieldStorage klassiga sarnaselt"
    def __init__(self, trv):
        self._toorvastus = trv
        self.filename = trv.filename

    @property
    def value(self):
        return self._toorvastus.filedata

def _fn_local(fnPath):
    """
    Rajast eraldatakse failinimi.
    """
    pos = max(fnPath.rfind('\\'), fnPath.rfind('/'))
    if pos > -1:
        return fnPath[pos + 1:]
    else:
        return fnPath
