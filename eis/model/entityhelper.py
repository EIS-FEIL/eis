"Andmeklasside ühised omadused"

import eiscore.const as const
from eiscore.entitybase import *
from eis.s3file import S3File
from eis.model import Session, SessionR, meta, usersession

_ = usersession._
Base = declarative_base()
log = logging.getLogger(__name__)

LOG_UPDATE = 'U'
LOG_INSERT = 'I'
LOG_DELETE = 'D'

class classproperty(object):
    def __init__(self, f):
        self.f = f
    def __get__(self, obj, owner):
        return self.f(owner)
    
class EntityHelper(EntityBase):
    """Andmeklasside olemite baasklass, mis lisab ühised meetodid
    """

    # vanemale viitav väli
    _parent_key = None
    # kas logida muudatused (meetodiga logi())
    logging = False
    # kas muudatuste logimisel kasutada muudatuse liigi koodi või sõna: True - kood, False - sõna
    logging_type1 = False
    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)
        self.default()
        Session.add(self)

    @classmethod
    def init(cls, **kwargs):
        item = cls()
        item.set(**kwargs)
        return item

    @classproperty
    def query(cls):
        "Mugavusmeetod kirjet väljastava päringu alustamiseks, read-write seanss"
        return Session.query(cls)

    @classproperty
    def queryR(cls):
        "Mugavusmeetod kirjet väljastava päringu alustamiseks, readonly seanss"
        return SessionR.query(cls)

    @classmethod
    def get(cls, id, **kwargs):
        if id is not None:
            # id teisendamine stringist arvuks
            id = int(id)
        return cls.query.get(id, **kwargs)   

    @classmethod
    def getR(cls, id, **kwargs):
        if id is not None:
            # id teisendamine stringist arvuks
            id = int(id)
        return cls.queryR.get(id, **kwargs)   

    @property
    def is_writable(self):
        "Kas on Session kaudu saadud objekt, mitte SessionR"
        return sa.orm.object_session(self).in_transaction()

    def get_userid(self):
        return usersession.get_userid()
    
    # session methods
    def flush(self, *args, **kwargs):
        Session.flush()

    def delete(self, *args, **kwargs):
        if self in Session.deleted:
            return False
        log.info('DELETE %s %s' % (self.__class__.__name__, self.get_pkey()))
        from eis.model.deletelog import Deletelog
        Deletelog.add(self)
        self.delete_subitems()
        rc = Session.delete(self)
        return rc
        
    def delete_subitems(self):    
        pass

    def expire(self, *args, **kwargs):
        return Session.expire(self, *args, **kwargs)

    def refresh(self, *args, **kwargs):
        return Session.refresh(self, *args, **kwargs)

    def expunge(self, *args, **kwargs):
        return Session.expunge(self, *args, **kwargs)

    # query methods
    @classmethod
    def get_by(cls, *args, **kwargs):
        return cls.query.filter_by(*args, **kwargs).first()

    def default(self):
        "Vaikimisi väärtuste omistamine"
        return self

    def give_seq_id(self):
        if not self.id:
            id_seq_name = '%s_id_seq' % (self.__table__.name)
            seq = sa.Sequence(id_seq_name)
            self.id = Session.execute(seq)
        return self.id
    
    def __getattr__(self, key):
        """Klassifikaatoririte nimetused
        Nt kui klassis on väli teema_kood, 
        siis siitkaudu tekib võimalus küsida teema nime 
        teema_nimi kaudu.
        """
        if key.endswith('_nimi'):
            # kysitakse klassifikaatorirea nimetust
            klassifikaator_kood = key[:-5]
            fieldname = klassifikaator_kood + '_kood'
            if fieldname in self.__dict__ or \
                   self.__table__.columns.get(fieldname) is not None:
                kood = self.__dict__.get(fieldname)
                if kood:
                    from eis.model.klassifikaator import Klrida
                    ylem_kood = self._get_ylem_kood(klassifikaator_kood)
                    return Klrida.get_str(klassifikaator_kood.upper(), kood, ylem_kood=ylem_kood)
                else:
                    return None
        elif key.endswith('_id'):
            # kysitakse klassifikaatorirea id
            klassifikaator_kood = key[:-3]
            fieldname = klassifikaator_kood + '_kood'
            if fieldname in self.__dict__ or \
                   self.__table__.columns.get(fieldname) is not None:
                kood = self.__dict__.get(fieldname)
                if kood:
                    from eis.model.klassifikaator import Klrida
                    ylem_kood = self._get_ylem_kood(klassifikaator_kood)
                    obj = Klrida.get_by_kood(klassifikaator_kood.upper(), kood, ylem_kood=ylem_kood)
                    return obj and obj.id
                else:
                    return None
        else:
            fieldname = '%s_kood' % key
            if fieldname in self.__dict__ or \
                   self.__table__.columns.get(fieldname) is not None:
                kood = self.__dict__.get(fieldname)
                # kysitakse klassifikaatoririda
                if kood and isinstance(kood, str):
                    from eis.model.klassifikaator import Klrida
                    ylem_kood = self._get_ylem_kood(key)                
                    return Klrida.get_by_kood(key.upper(), kood, ylem_kood=ylem_kood)
                else:
                    return None
        return self.__getattribute__(key)

    def _get_ylem_kood(self, kood):
        """Antud on klassifikaatori kood. Kui sellel klassifikaatoril on olemas
        ülemklassifikaator, siis tagastatakse ülemklassifikaatori rea väärtus antud kirjes.
        """
        kood_upper = kood.upper()
        if kood_upper in ('TEEMA','OSKUS','KEELETASE','ASPEKT'):
            ylem_kood = 'AINE'
        elif kood_upper == 'ALATEEMA':
            ylem_kood = 'TEEMA'
        else:
            return None
        return self.__getattr__(ylem_kood.lower()+'_kood') or '0'

    def from_form(self, form_result, prefix='', ignore_if_none=[], lang=None, add_only=False):
        """
        Kirje väljadele omistatakse väärtused vormilt postitatud väljadelt.
        Kasutatakse kontrolleris andmeobjekti väärtustamisel sisestatud andmetega.
        Andmed võetakse kõigist sisestusväljadest, mille nimi algab antud prefiksiga.
        Prefiksile järgnev osa peab kattuma andmeobjekti vastava atribuudi nimega.
 
        form_result
           kontrolleri atribuut form_result, sisaldab valideeritud sisendparameetreid
        prefix
           vormiväljade nimede prefiks, mis määrab kasutatavad väljad.
        ignore_if_none
           list väljanimedest, mida ei muudeta, kui uus väärtus on None.
        lang
           tõlkekeel, kui muudetakse tõlget
        add_only
           lubatakse seada väärtust ainult siis, kui andmebaasis veel väärtust pole
        """
        t_rcd = None
        if lang:
            # tõlke salvestamine
            try:
                # kas antud tabel on tõlgitav?
                self.__getattribute__('trans')
            except AttributeError:
                # tabel pole tõlgitav
                pass
            else:
                # tabel on tõlgitav
                t_rcd = self.give_tran(lang)

        for field_name_form in form_result:
            if not prefix or field_name_form.startswith(prefix):
                value = form_result[field_name_form]
                field_name_db = field_name_form[len(prefix):]

                if field_name_db == 'id':
                    continue

                if value == const.MISSING:
                    continue

                self.from_form_value(field_name_db, value, t_rcd, add_only)
                
        if not self.is_existing():
            self.post_create()                
        return self

    def set_tran_field(self, key, value, lang=None, versioon_id=None):
        if lang or versioon_id:
            self.give_tran(lang, versioon_id).__setattr__(key, value)
        else:
            self.__setattr__(key, value)
            
    def from_form_value(self, field_name, value, t_rcd=None, add_only=False):
        if t_rcd:
            # tabel on tõlgitav
            # kas antud väli on tõlgitav?
            # filedata ei ole andmebaasiväli, seetõttu filedata korral kontrollime fileversion välja
            chk_name = field_name == 'filedata' and 'fileversion' or field_name
            if t_rcd.__table__.columns.get(chk_name) is not None:
                # antud väli on ka tõlgitav
                return t_rcd.from_form_value(field_name, value, None, add_only)

        if add_only:
            if self.__getattr__(field_name):
                # väärtus on olemas, muuta ei tohi
                return self 

        if field_name == 'filedata':
            self.file_from_form_value(value)
        else:
            if isinstance(value, str):
                # eemaldame sisestatud välja lõpust tühikud, aga nii, et
                # väli päris tühjaks ei jääks, muidu muutub NULLiks
                # ja kohustusliku välja korral tekib siis probleem
                if value.strip() != '':
                    value = value.strip()                
            self.__setattr__(field_name, value)       
        return self
    
    def file_from_form_value(self, value):
        if value == b'':
            # faili pole antud, andmebaas jääb muutmata
            return
        else:
            # value on FieldStorage objekt
            self.filename = _fn_local(value.filename)
            value = value.value
            self.filedata = value
            self.filesize = value is not None and len(value) or 0            

    def from_time(self, dd, timetuple):
        """Kuupäevale lisatakse kellaaeg.
        """
        if dd and timetuple:
            hour, minute = timetuple
            dd = datetime.combine(dd, time(hour, minute))
        return dd

    def get_seq_parent(self, parent_key, parent_id):
        if self.__table__.schema:
            table_name = '%s.%s' % (self.__table__.schema, self.__table__.name)
        else:
            table_name = self.__table__.name

        sql = sa.text('SELECT max(seq) FROM %s WHERE %s=:id' % (table_name, parent_key))
        params = {'id': int(parent_id)}
        rc = Session.execute(sql, params).scalar()
        return (rc or 0) + 1

    def tran(self, lang, original_if_missing=True, versioon_id=None):
        """Leitakse antud kirje tõlge (T_ prefiksiga tabelist)
        """
        if versioon_id:
            # soovitakse versiooni, mis asub t_tabelis
            # kui ei leia, tagastame versiooni põhikeeles
            orig = None
        elif not lang:
            # ei soovita versiooni, ei soovita tõlget - anname originaalkirje
            return self
        else:
            # soovitakse versioonita tõlget
            # kui ei leia, tagastame originaali
            orig = self

        for t in self.trans:
            try:
                # ainult ylesande tõlketabelite korral
                t_versioon_id = t.ylesandeversioon_id
            except:
                # testi tõlketabelite korral
                t_versioon_id = None
            #if t_versioon_id is None or t_versioon_id == versioon_id:
            if t_versioon_id == versioon_id:
                if t.lang == lang:
                    # õige on leitud
                    return t
                elif not t.lang:
                    # versioonitud põhikeel
                    orig = t

        if original_if_missing:
            # tõlget ei leitud, tagasame põhikeele kirje
            return orig
        else:
            # tõlget ei leitud ja põhikeele kirjet asendajana ei tahetud
            return 

    def give_tran(self, lang, versioon_id=None):
        """Tagastatakse antud kirje tõlge, vajadusel luuakse
        """
        t = self.tran(lang, False, versioon_id=versioon_id)
        if not t:
            t = self.get_translation_class()(lang=lang)                
            t.ylesandeversioon_id = versioon_id
            self.trans.append(t)
        return t

    def get_translation_class(self):
        #from eis.model import * # SyntaxWarning: import * only allowed at module level
        import eis.model
        tname = self.__table__.name.capitalize()
        # Valikupiirkonna puhul ei toimi self.__class__.__name__
        return eval('eis.model.T_' + tname)

   
def before_insert(mapper, connection, target):
    "Kirje loomise andmete väärtustamine"
    target.before_insert()

def before_update(mapper, connection, target):
    "Kirje muutmise andmete väärtustamine"
    target.before_update()

def before_flush(session, flush_context, instances):
    r_deleted = list(session.deleted)
    r_dirty = list(session.dirty)
    for r in r_deleted:
        r.log_delete()
    for r in r_dirty:
        r.log_update()

def after_flush(session, flush_context):
    r_new = list(session.new)
    for r in r_new:
        r.log_insert()

def receive_load(target, context):
    "Jätame meelde algsed väärtused, et neid kasutada muudatuste logimisel"
    if isinstance(target, EntityHelper):
        values = {}
        for col in target.__table__.columns:
            if col.type.python_type != bytes:
                # kui pole filedata
                key = col.name
                try:
                    values[key] = target.__getattribute__(key)
                except:
                    pass
        target._oldvalues = values

# pyyame kinni kõigi kirjete lisamised, muutmised ja kustutamised,
# et käivitada siis vastav funktsioon
event.listen(mapper, 'before_insert', before_insert)
event.listen(mapper, 'before_update', before_update)
event.listen(Session, 'before_flush', before_flush)
event.listen(Session, 'after_flush', after_flush)
# pildil oleva kujundi valiku lahendamine annab hoiatuse,
# kui restore_load_context=False
# nt https://eis.ekk.edu.ee/ekk/ylesanded/34445/lahendamine/edit
event.listen(mapper, 'load', receive_load, restore_load_context=True)

def is_read_only():
    status = Session.execute('SHOW TRANSACTION_READ_ONLY').scalar()
    return status == 'on'

def lang_sort(lang):
    "Keelte järgi sortimine"
    li =[const.LANG_ET, 
         const.LANG_EN, 
         const.LANG_RU, 
         const.LANG_DE,
         const.LANG_FR]
    try:
        return li.index(lang)
    except ValueError:
        return 100

def eval_formula(valem, e_locals, **kw):
    return eval_formula_sess(usersession, valem, e_locals)
    
def _fn_local(fnPath):
    """
    Rajast eraldatakse failinimi.
    """
    pos = max(fnPath.rfind('\\'), fnPath.rfind('/'))
    if pos > -1:
        return fnPath[pos + 1:]
    else:
        return fnPath

