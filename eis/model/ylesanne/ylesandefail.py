# -*- coding: utf-8 -*-
"Ülesande andmemudel"

from PIL import Image
import mimetypes
import re
from lxml import etree
import urllib.request, urllib.parse, urllib.error
from eis.s3file import S3File
from eis.model.entityhelper import *
from eis.model.klassifikaator import *
from eis.model.opt import *
from eis.model.kasutaja import *
from .t_ylesanne import T_Ylesandefail

class Ylesandefail(EntityHelper, Base, S3File):
    """Ülesande küljes olev fail.
    On seotud ülesandega
    """
    __tablename__ = 'ylesandefail'
    __table_args__ = (
        sa.UniqueConstraint('ylesanne_id','filename', 'fileurl'),
        )
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(256)) # failinimi
    filesize = Column(Integer) # faili suurus baitides
    #filedata_db = deferred(Column('filedata', LargeBinary)) # faili sisu (kui puudub fileurl)
    fileurl = Column(String(200)) # faili URL (kui puudub filedata)
    fileversion = Column(String(8)) # versioon
    mimetype = Column(String(256)) # failitüüp
    laius = Column(Integer) # faili kuvamise laius
    korgus = Column(Integer) # faili kuvamise kõrgus
    ylesanne_id = Column(Integer, ForeignKey('ylesanne.id'), index=True, nullable=False) # viide ülesandele
    ylesanne = relationship('Ylesanne', foreign_keys=ylesanne_id, back_populates='ylesandefailid')
    trans = relationship('T_Ylesandefail', cascade='all', back_populates='orig')
    ylesandefailimarkused = relationship('Ylesandefailimarkus', order_by='Ylesandefailimarkus.id', back_populates='ylesandefail')

    row_type = Column(String(40))
    __mapper_args__ = {'polymorphic_on': row_type}
    
    _parent_key = 'ylesanne_id'
    _cache_dir = 'ylesandefail'

    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .ylesanne import Ylesanne
        parent = self.ylesanne or self.ylesanne_id and Ylesanne.get(self.ylesanne_id)
        if parent:        
            parent.logi('Ülesandefail %s %s' % (self.id or '', liik), vanad_andmed, uued_andmed, logitase)

    def get_translation_class(self):
        return T_Ylesandefail

    def set_modifier(self):
        EntityHelper.set_modifier(self)
        self.set_mimetype()

    def set_mimetype(self):
        mimetype = self.guess_type()        
        if mimetype:
            self.mimetype = mimetype

    def copy(self):
        cp = EntityHelper.copy(self)
        self.copy_subrecords(cp, ['trans'])
        return cp

    def pack_subrecords(self, delete=True, modified=None):
        li = []
        for rcd in self.trans:
            li.extend(rcd.pack(delete, modified))
        return li

    def delete_subitems(self):    
        #self.delete_subrecords(['trans',
        #                        ])
        for rcd in self.ylesandefailimarkused:
            if rcd.ylem_id is None:
                rcd.delete()

    def guess_type(self):
        """Failinime või URLi järgi arvatakse ära MIME tüüp.
        """       
        mimetype = None
        if self.fileurl:
            # kui on antud URL, siis failisisu ei hoita
            self.filename = None
            self.filedata = None
            (mimetype, encoding) = mimetypes.guess_type(self.fileurl)
            if not mimetype:
                if self.fileurl.startswith('http://www.youtube.com/'):
                    # YouTube pakub ainult flashi formaadis videot
                    mimetype = 'application/x-shockwave-flash'
        elif self.filename:
            if self.fileext == 'm4a':
                mimetype = 'audio/mpeg'
            else:
                (mimetype, encoding) = mimetypes.guess_type(self.filename)
        return mimetype
       
    def post_create(self):
        if self.laius is None:
            self.laius = 0
        if self.korgus is None:
            self.korgus = 0

    @property
    def is_image(self):
        return self.mimetype_main == 'image'

    @property
    def is_audio(self):
        return self.mimetype_main == 'audio'

    @property
    def is_video(self):
        return self.mimetype_main in ('video', 'application')
        
    @property
    def mimetype_main(self):
        if not self.mimetype:
            self.set_mimetype()
        if self.mimetype:
            return self.mimetype.split('/')[0]

    @classmethod
    def get_by_item(cls, ylesanne_id, filename):
        return cls.query\
            .filter_by(ylesanne_id=int(ylesanne_id))\
            .filter_by(filename=filename)\
            .first()

    @classmethod
    def get_item(cls, **args):
        """Kui kirje on juba kohalikus baasis olemas, siis leitakse see.
        args - pakitud kirje 
        """
        # yle laaditud selleks, et kui row_type on krüptimisel kaotatud,
        # siis kasutataks Ylesandefaili klassi
        return Ylesandefail.get(args['id'])

# def Ylesandeobjekt(**kw):
#     kw['row_type'] = const.OBJ_ASSESSMENT
#     return Ylesandefail(**kw)

# def Lahendusobjekt(**kw):
#     kw['row_type'] = const.OBJ_SOLUTION
#     return Ylesandefail(**kw)

# def Lahteobjekt(**kw):
#     kw['row_type'] = const.OBJ_ORIGIN
#     return Ylesandefail(**kw)

class Ylesandeobjekt(Ylesandefail):
    "Ülesande fail"
    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': const.OBJ_ASSESSMENT}            

class Lahendusobjekt(Ylesandefail):
    "Ülesande lahenduse fail"
    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': const.OBJ_SOLUTION}            

class Lahteobjekt(Ylesandefail):
    "Ülesande lähtematerjal"
    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': const.OBJ_ORIGIN}        

class Hindamisobjekt(Ylesandefail):
    "Ülesande hindamisjuhend failina"
    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': const.OBJ_MARKING}        


