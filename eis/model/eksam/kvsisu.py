"Testikorralduse andmemudel"

import pickle
from cgi import FieldStorage
import mimetypes
from simplejson import loads
from eis.model.entityhelper import *
from eiscore.examwrapper import KvsisuWrapper

class Kvsisu(EntityHelper, Base, S3File, KvsisuWrapper):
    """Küsimuse vastus sisu, sooritaja poolt ühe ülesande 
    ühele küsimusele antud ühe vastuse sisu
    (mitme vastusega küsimuste korral on iga vastuse jaoks eraldi kirje)
    """
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    kysimusevastus_id = Column(Integer, ForeignKey('kysimusevastus.id'), index=True, nullable=False)
    kysimusevastus = relationship('Kysimusevastus', foreign_keys=kysimusevastus_id, back_populates='kvsisud') # viide küsimuse vastuse kirjele
    seq = Column(Integer, nullable=False) # mitmes vastus (küsimuse piires); -2=const.SEQ_ANALYSIS - kogujärjestuse kirje analüüsi jaoks
    svseq = Column(Integer) # mitmes vastus statvastuse kood1 piires (paari korral ühe paarilise piires), lugemine algab 0-st
    tyyp = Column(String(1)) # vastuse tüüp: NULL - vastust pole (kirjet kasutatakse hindepallide jaoks); t=const.RTYPE_CORRECT - õige/vale; s=const.RTYPE_STRING - sisu; f=const.RTYPE_FILE - filedata ja filename; i=const.RTYPE_IDENTIFIER - kood1; p=const.RTYPE_PAIR - kood1 ja kood2; o=const.RTYPE_ORDERED - järjestus; c=const.RTYPE_COORDS - koordinaadid; x=const.RTYPE_POINT - punkt
    toorpunktid = Column(Float) # toorpunktid (ülesande skaala järgi)
    kood1 = Column(String(256)) # valikvastuse korral valiku kood
    kood2 = Column(String(256)) # valikvastuste paari korral teise valiku kood
    sisu = Column(Text) # vabatekstiline vastus või järjestus või lüngata panga kohaindeks vms (vastuste statistikas eristatakse eraldi reana); krati korral transkriptsioon
    koordinaat = Column(Text) # punkti või murdjoone koordinaadid stringina (vastuste statistikas ei eristata), kirjavahemärgi lünga asukoha indeks lauses; krati korral staatuse URL
    kujund = Column(String(10)) # koordinaatidega antud kujundi liik (line, polyline, ray)
    filename = Column(String(256)) # failinimi
    filesize = Column(Integer) # faili suurus baitides
    fileversion = Column(String(8)) # versioon
    url = None # faili korral, väärtustatakse enne kasutamist sõltuvalt kohast
    oige = Column(Integer) # kas vastus oli õige või vale: 0=const.C_VALE - vale; 1=const.C_OSAOIGE - osaliselt õige; 2=const.C_OIGE - õige; 8=const.C_LOETAMATU - loetamatu; 9=const.C_VASTAMATA - vastamata (õige/vale sisestamise korral sisestatakse (sisestamisel ei kasutata 2); vastuse olemasolu korral arvutihinnatavas ülesandes arvutatakse hindamismaatriksi põhjal; kui hindaja määrab pallid, siis: max pallide korral 2=const.C_OIGE; muu positiivse palli korral 1=const.C_OSAOIGE; 0p korral 0=const.C_VALE; '-' korral 9=const.C_VASTAMATA)
    maatriks = Column(Integer, sa.DefaultClause('1'), nullable=False) # mitmenda hindamismaatriksiga on see vastus hinnatav (sobitamise küsimusel võib olla mitu hindamismaatriksit)
    hindamismaatriks_id = Column(Integer) # arvutihinnatava ülesande korral viide hindamismaatriksi reale, mille alusel punkte anti; ei ole võti - hindamismaatriksi muutmisel võib osutada puuduvale reale; kasutusel psühholoogilises testis valimata vastuste arvu leidmisel
    sonade_arv = Column(Integer) # sõnade arv sisu veerus olevas vastuse tekstis
    hindamisinfo = Column(String(256)) # arvutihindamisel jäetav info, järjestamise ülesande korral jada liikmete õigsus (nt 1010011)
    analyysitav = Column(Boolean, sa.DefaultClause('true'), nullable=False) # kas kirjet tuleb arvestada vastuste analüüsis (järjestamise korral võib analüüsis kasutada üht kogujärjestuse kirjet, mitte iga üksikelemendi kirjet eraldi)
    __table_args__ = (sa.schema.Index('ix_kvsisu_kv_id_seq', "kysimusevastus_id", "seq"), )

    _cache_dir = 'kvsisu'
    _id_seq_name = 'kvsisu_id_seq'
    _parent_key = 'kysimusevastus_id'
    
    @property
    def on_hinnatud(self):
        return self.toorpunktid is not None

    @property
    def hindamismaatriks(self):
        from eis.model.ylesanne import Hindamismaatriks
        if self.hindamismaatriks_id:
            return Hindamismaatriks.get(self.hindamismaatriks_id)
    
    def on_max_p(self, responses, tulemus, kv, nullvale):
        "Kas vastus sai max punktid"
        return ks_on_max_p(responses, tulemus, kv, self, nullvale)
            
    @property
    def koordinaadid(self):
        # koordinaadid on sisus kujul "x1 y1;x2 y2;x3 y3;...xN yN"
        if self.koordinaat:
            punktid = [p.split(' ') for p in self.koordinaat.split(';')]
            return [[int(p[0]), int(p[1])] for p in punktid]
        return []

    @koordinaadid.setter
    def koordinaadid(self, value):
        self.koordinaat = ';'.join(['%s %s' % (p[0], p[1]) for p in value])

    @property
    def jarjestus(self):
        if self.sisu:
            return self.sisu.split(';')
        return []

    @jarjestus.setter
    def jarjestus(self, value):
        self.sisu = ';'.join(value)

    @property
    def punkt(self):
        try:
            x, y = list(map(float, self.koordinaat.split(' ')))
        except Exception as e:
            log.debug(e)
        else:
            return x, y

    @punkt.setter
    def punkt(self, value):
        x, y = value
        self.koordinaat = '%s %s' % (x, y)

    def get_txt_meta(self):
        "Leitakse estnltk tekstianalüüsi metainfo"
        for ksm in self.kysimusevastus.ksmarkused:
            if ksm.seq == self.seq and not ksm.ylesandehinne_id:
                # antud vastuse märkused ja automaatselt loodud
                li = loads(ksm.markus)
                for r in li:
                    # leiame selle itemi, mis sisaldab metainfot
                    if r[1] == 'meta':
                        return r[2]
                
    def as_string(self, use_oige=True):
        buf = ''
        if self.tyyp != const.RTYPE_CORRECT:
            if self.kood1 and self.kood2 and self.sisu:
                buf = '%s. %s %s' % (self.sisu, self.kood1, self.kood2)
            elif self.kood1 and self.kood2:
                buf = '%s %s' % (self.kood1, self.kood2)                
            elif self.kood1 and self.sisu:
                buf = '%s (%s)' % (self.kood1, self.sisu)
            elif not self.kood1 and self.kood2 and self.sisu:
                buf = '%s (%s)' % (self.sisu, self.kood2)                
            elif self.kood1 and self.koordinaat:
                buf = '%s (%s)' % (self.kood1, self.koordinaat)
            elif self.kood1:
                buf = '%s' % (self.kood1)
            elif self.sisu and self.koordinaat:
                # POSSTRING
                buf = '%s (%s)' % (self.sisu, self.koordinaat)                
            elif self.sisu:
                buf = self.sisu
                kv = self.kysimusevastus
                if kv:
                    kysimus = kv.kysimus
                    if kysimus.rtf:
                        buf = html_as_string(buf)
            elif self.kujund and self.koordinaat:
                buf = '%s:%s' % (self.kujund, self.koordinaat)
            elif self.koordinaat:
                buf = self.koordinaat               
            elif self.filedata and self.filename:
                buf = self.filename

        if not buf and self.oige is not None and (use_oige or self.tyyp == const.RTYPE_CORRECT):
            buf = '%s' % self.oige

        if self.maatriks and self.maatriks != 1 and buf:
            buf = buf + ' [%s]' % self.maatriks
        return buf or ''

    def __repr__(self):
        return '<Kvsisu %s %s tyyp=%s %s>' % (self.id, self.kysimusevastus_id, self.tyyp, self.as_string())

        
def ks_on_max_p(responses, tulemus, kv, ks, nullvale):
    "Kas vastus sai max punktid"
    from eis.model.ylesanne import Tulemus, Hindamismaatriks
    if not isinstance(tulemus, EntityHelper):
        # siin on vaja päris kirjet
        tulemus = Tulemus.get(tulemus.id)
        
    okysimus = tulemus.oigsus_kysimus
    if okysimus:
        # vastuse õigsust mõõdab teine kysimus
        ks = None
        kv = responses.get(okysimus.kood)
        if kv:
            for ks in kv.kvsisud:
                break
        if not ks:
            # teise kysimuse vastus puudub
            return None
        tulemus = okysimus.tulemus
        if tulemus.oigsus_kysimus_id:
            # mitut taset ei toeta
            return None

    # Vastus kuvatakse rohelise või punase raamiga vastavalt sellele, kas vastus sai max punktid või mitte.
    # Arvutihinnatud vastus, mis leiti hindamismaatriksist, loetakse max punktid saanuks siis, kui:
    # - maatriksi real on märge "õige" või
    # - vastus ei saanud negatiivset arvu punkte ja maatriksi ükski rida ei anna sellest rohkem punkte või
    # - vastus ei saanud negatiivset arvu punkte ning küsimuse kõik vastused kokku said max punktid.
    # Kui vastus sai negatiivsed punktid, siis loetakse see valeks vastuseks.
    # Kui vastust ei leitud hindamismaatriksist ning sai 0p ning on sobitamises, piltide lohistamises,
    # tekstide lohistamises, tekstiosa valikus, pangaga lüngas (välja arvatud tühi vastus) või ristsõnas,
    # siis loetakse see valeks vastuseks.
    # Arvutihinnatud vastus, mida hindamismaatriksis ei leitud ning saab vaikimisi punktid,
    # loetakse max punktid saanuks siis, kui see vastus annab küsimuse max punktid.
    # Käsitsi hinnatud vastus loetakse max punktid saanuks siis, kui:
    # - vastus sai max punktid, mida küsimuse eest oli võimalik saada, või
    # - vastus ei saanud negatiivset arvu punkte ning küsimuse kõik vastused kokku said max punktid.

    # Tekstiosa valikus hinnatakse ka vastamata vastuseid, vt vastamata_on_oige

    if ks.toorpunktid is not None:
        # vastus on hinnatud
        diff = 1e-8
        hm_id = ks.hindamismaatriks_id
        hm = hm_id and Hindamismaatriks.get(hm_id)
        if hm:
            # arvutihinnatud maatriksi järgi
            if hm.oige:
                # maatriksi rida on märgitud õigeks
                #log.debug('ks %d max_p=true, sest hm %d.oige=True' % (ks.id, hm.id))
                return True

            if ks.toorpunktid < 0:
                # negatiivsed punktid
                return False
            
            # kas maatriksis on mõni rida, mis annab rohkem punkte
            is_best_hm = True
            for r in tulemus.hindamismaatriksid:
                if r.pallid > hm.pallid + diff:
                    # maatriksis on rida, mis annab rohkem punkte
                    #log.debug('ks %d max_p=false, sest hm %d anna rohkem palle' % (ks.id, hm.id))
                    is_best_hm = False
                    break
            if is_best_hm:
                # maatriksi ykski rida ei anna rohkem punkte
                #log.debug('ks %d max_p=true, sest ykski rida ei anna rohkem kui hm %s.pallid=%s' % (ks.id, hm.id, hm.pallid))
                return True

            if ks.toorpunktid > 0 and kv.toorpunktid and kv.toorpunktid >= tulemus.get_max_pallid() - diff:
                # kysimuse vastused kokku said max punktid
                # ja see vastus sai positiivse arvu punkte
                return True
            return False
        elif ks.toorpunktid < 0:
            # vastus sai negatiivsed punktid
            return False
        elif nullvale and ks.toorpunktid == 0:
            # vastus sai 0p sellises ülesandetüübis, kus 0p loeme valeks
            return False
        else:
            max_p = tulemus.get_max_pallid()
            if max_p is None:
                return None
            elif tulemus.arvutihinnatav:
                # arvutihinnatud vaikimisi punktidega vastuse eest, mida maatriksis pole
                #log.debug('%s ks %d tp=%s max_p=%s' % (tulemus.kood, ks.id, ks.toorpunktid, max_p))
                return ks.toorpunktid >= max_p - diff
            else:
                # käsitsihinnatud
                if ks.toorpunktid >= max_p - diff:
                    # see vastus yksi sai max punktid, mida kysimuse eest oli võimalik saada
                    return True
                if kv.toorpunktid and kv.toorpunktid >= max_p - diff:
                    # kysimuse vastused kokku said max punktid
                    return True
            return False

def vastamata_on_oige(responses, tulemus, kv, valik_kood, nullvale):
    # vastamata hottext
    if not tulemus:
        return None
    if not isinstance(tulemus, EntityHelper):
        # siin on vaja päris kirjet
        from eis.model.ylesanne import Tulemus
        tulemus = Tulemus.get(tulemus.id)

    okysimus = tulemus.oigsus_kysimus
    if okysimus:
        # õigsust mõõdab teine küsimus
        rc = ks_on_max_p(responses, tulemus, kv, None, nullvale)
        return rc and const.C_OIGE or const.C_VALE
        
    if tulemus.arvutihinnatav:
        for hm in tulemus.hindamismaatriksid:
            if hm.pallid > 0:
                # õige vastus
                if hm.kood1 == valik_kood:
                    # vastamata valikul oleks andnud positiivseid punkte
                    # loeme vastamata jätmise valeks
                    return const.C_VALE
        # vastamata valikul pole hindamismaatriksis õiget vastust
        # loeme vastamata jätmise õigeks
        return const.C_OIGE
    else:
        # kui pole arvutihinnatav, siis ei värvi vastamata vastuseid
        return None

def ks_correct_cls(responses, tulemus, kv, ks, nullvale, for_resp=True):
    "Õige vastuse kuvamise klass"
    # nullvale - kui kysimus annab max 0p, kas siis 0p vastus lugeda valeks
    #rc = ks_on_max_p(responses, tulemus, kv, ks, nullvale)
    rc = ks.oige
    return ks_cls(rc, for_resp)

def ks_cls(rc, for_resp):
    "Õige vastuse kuvamise klass"
    if rc is not None:
        if for_resp:
            if rc == const.C_OIGE:
                # lahendaja antud õige vastus
                return 'corr2r'
            elif rc == const.C_OSAOIGE:
                return 'corr1r'
            else:
                # lahendaja antud vale vastus
                return 'corr0r'
        else:
            # maatriksis olev õige vastus
            return 'corr1c-inv'

def guess_mimetype(filename):
    """Failinime järgi arvatakse ära MIME tüüp.
    """       
    if filename:
        fileext = filename.split('.')[-1]
        if fileext == 'm4a':
            # mimetypes pakub video/mp4
            mimetype = 'audio/mpeg'
        else:
            (mimetype, encoding) = mimetypes.guess_type(filename)
        return mimetype

