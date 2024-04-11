"Avalehel kuvatavad pildid"
from PIL import Image
from lxml import etree
from eis.s3file import S3File
from eis.model.entityhelper import *

class Avalehepilt(EntityHelper, Base, S3File):
    """Avalehe pilt
    """
    __tablename__ = 'avalehepilt'

    # vaikimisi kuvatava pildi ID
    DEFAULT_ID = 1
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(256)) # failinimi
    filesize = Column(Integer) # faili suurus baitides
    fileversion = Column(String(8)) # versioon
    laius_orig = Column(Integer) # pildi/video tegelik laius
    korgus_orig = Column(Integer) # pildi/video tegelik kõrgus
    alates = Column(Date, nullable=False) # kuvamise alguse kuupäev
    kuni = Column(Date, nullable=False) # kuvamise lõpu kuupäev
    autor = Column(String(200)) # autor
    allikas = Column(String(200)) # allikas
    
    _cache_dir = 'avalehepilt'

    @classmethod
    def get_kehtiv(cls):
        "Leitakse praegu kehtiv pilt"
        today = date.today()
        # kui kuupäeva järgi on mõni pilt määratud, siis kuvame selle
        q = (Session.query(Avalehepilt)
             .filter(Avalehepilt.alates <= today)
             .filter(Avalehepilt.kuni >= today)
             .filter(Avalehepilt.fileversion != None)
             .filter(Avalehepilt.id != cls.DEFAULT_ID)
             .order_by(Avalehepilt.id)
             )
        for rcd in q.all():
            return rcd
        
        # vaikimisi kuvatakse esimest pilti
        rcd = Avalehepilt.get(cls.DEFAULT_ID)
        if rcd and rcd.has_file:
            return rcd
    
    @property
    def kuni_ui(self):
        """Andmebaasis on kuupäeval väärtus, mida kasutajale ei näidata.
        """
        if not self.kuni or self.kuni >= const.MAX_DATE:
            return None
        else:
            return self.kuni

    def set_image_size(self, filedata, stream, fn):
        """Parameetriks on antud failisisu (postitatud) või failinimi või failipointer.
        Kui see on pildifail, siis muudetakse kirje laius_orig ja korgus_orig vastavaks
        pildi originaalmõõtudele.
        Kui ei ole pildifail, siis visatakse IOError.
        Kui pildi kuvamismõõdud on määramata, siis omistatakse originaalmõõdud kuvamismõõtudeks.
        """
        t = self
        if filedata or stream:
            ext = fn.split('.')[-1].lower()
            if ext == 'svg':
                try:
                    if filedata:
                        svg = etree.XML(filedata)
                    else:
                        tree = etree.parse(stream)
                        svg = tree.getroot()
                    try:
                        width, height = svg.attrib['width'], svg.attrib['height']
                    except:
                        width, height = svg.attrib['viewBox'].split()[-2:]
                    try:
                        t.laius_orig = int(float(width))
                        t.korgus_orig = int(float(height))
                    except:
                        # mõõt võib olla koos yhikuga nt "38.39cm"
                        t.laius_orig = t.korgus_orig = None
                except Exception as ex:
                    # pole SVG
                    log.error(ex)
                    raise
            else:
                try:
                    image = Image.open(filedata or stream)
                except IOError as e: # IOError
                    # pole pildifail
                    raise
                else:
                    (t.laius_orig, t.korgus_orig) = image.size

    def from_form(self, form_result, prefix='', ignore_if_none=[], lang=None):
        EntityHelper.from_form(self, form_result, prefix=prefix, lang=lang)
        fobj = form_result.get(prefix + 'filedata')
        if fobj != None and fobj != b'':
            filename = fobj.filename
            stream = fobj.file
        else:
            filename = stream = None
        self.set_image_size(None, stream, filename)
