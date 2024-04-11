"Ülesande sisuobjekt"
import platform
from PIL import Image
import pymediainfo
import mimetypes
import re
import json
from lxml import etree
import urllib.request, urllib.parse, urllib.error
import pickle
import tempfile
from eis.s3file import S3File
from eis.model.entityhelper import *

from .kysimus import Kysimus
from eis.recordwrapper.testwrapper import SisuobjektWrapper

class Sisuobjekt(EntityHelper, Base, S3File, SisuobjektWrapper):
    """Ülesande sisus olev fail.
    On seotud sisuplokiga 
    """
    __tablename__ = 'sisuobjekt'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    seq = Column(Integer, nullable=False) # järjekorranumber sisuplokis
    kood = Column(String(100)) # hindamismaatriksis kasutatav kood, QTI responseIdentifier 
    min_vastus = Column(Integer) # piltobjekti min esinemiste arv (piltide lohistamine ja piltide lohistamine kujunditele)
    max_vastus = Column(Integer) # piltobjekti max esinemiste arv (piltide lohistamine ja piltide lohistamine kujunditele)
    eraldi = Column(Boolean) # kui esinemiste arv on ühest suurem, siis kas pilti kuvada pangas ühekordselt või iga eksemplar eraldi (piltide lohistamine kujunditele)
    nahtamatu = Column(Boolean, sa.DefaultClause('0')) # kas kuvatakse sisuplokiga määratud asukohas (või on mõeldud mujalt viitamiseks)
    segamini = Column(Boolean) # kas lohistavad pildid kuvada juhuslikus järjekorras
    asend = Column(Integer) # lohistatavate piltide asend: 0 - taustast paremal, 1 - tausta all, 2 - taustast vasakul, 3 - taustast üleval
    masonry_layout = Column(Boolean) # kas lohistatavad pildid paigutada masonry abil (müürpaigutus)
    tiitel = Column(String(256)) # pildi atribuut title (kasutatakse pildi algallikate märkimiseks)
    filename = Column(String(256)) # failinimi
    filesize = Column(Integer) # faili suurus baitides
    fileversion = Column(String(8)) # versioon
    fileurl = Column(String(200)) # faili URL (kui puudub filedata)
    mimetype = Column(String(256)) # failitüüp
    laius = Column(Integer) # kuvamisel kasutatav laius
    korgus = Column(Integer) # kuvamisel kasutatav kõrgus
    laius_orig = Column(Integer) # pildi/video tegelik laius
    korgus_orig = Column(Integer) # pildi/video tegelik kõrgus
    sisuplokk_id = Column(Integer, ForeignKey('sisuplokk.id'), index=True, nullable=False) # viide sisuplokile
    sisuplokk = relationship('Sisuplokk', foreign_keys=sisuplokk_id, back_populates='sisuobjektid')
    trans = relationship('T_Sisuobjekt', cascade='all', back_populates='orig')
    kysimused = relationship('Kysimus', back_populates='sisuobjekt') # sisuobjektiga seotud kysimused
    samafail = Column(Integer) # sama (mitte-null) väärtusega failid on ühe ja sama faili erinevad formaadid
    row_type = Column(String(1)) 
    __mapper_args__ = {'polymorphic_on': row_type}
    _parent_key = 'sisuplokk_id'

    _cache_dir = 'sisuobjekt'
    
    logging = True
    def logi(self, liik, vanad_andmed, uued_andmed, logitase):
        from .sisuplokk import Sisuplokk

        parent = self.sisuplokk or self.sisuplokk_id and Sisuplokk.get(self.sisuplokk_id)
        if parent:
            parent.logi('Sisuobjekt %s %s' % (self.id or '', liik), vanad_andmed, uued_andmed, logitase)
            
    def get_translation_class(self):
        from .t_ylesanne import T_Sisuobjekt
        return T_Sisuobjekt

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
        for k in self.kysimused:
            k.delete()

    def is_youtube(self):
        return self.fileurl and \
            (self.fileurl.startswith('http://www.youtube.com/') or \
            self.fileurl.startswith('https://www.youtube.com/'))
        # http://youtu.be/... URL EI OLE MANUSTATAV URL, vaid veebilehe URL

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
                if self.is_youtube():
                    # YouTube pakub ainult flashi formaadis videot
                    mimetype = 'application/x-shockwave-flash'
        elif self.filename:
            if self.fileext == 'm4a':
                # mimetypes pakub video/mp4
                mimetype = 'audio/mpeg'
            else:
                (mimetype, encoding) = mimetypes.guess_type(self.filename)
        return mimetype

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
    def get_by_plokk(cls, sisuplokk_id, filename):
        return (cls.query
                .filter_by(sisuplokk_id=int(sisuplokk_id))
                .filter_by(filename=filename)
                .first())

    @classmethod
    def get_by_item(cls, ylesanne_id, filename):
        from .sisuplokk import Sisuplokk
        return (cls.query
                .filter_by(filename=filename)
                .filter(Sisuobjekt.sisuplokk.has(
                    Sisuplokk.ylesanne_id==int(ylesanne_id)))
                .first())

    @property
    def tulemus(self):
        """Leitakse tulemuse kirje, kui sisuobjektil on oma tulemus
        (pildile lohistamise sisuploki (ipos) piltobjekti korral)
        """
        for k in self.kysimused:
            return k.tulemus

    def give_kysimus(self, objseq=const.OBJSEQ_K):
        """Tehakse kysimus (ipos piltobjekti korral)
        """
        from .sisuplokk import Sisuplokk
        k = self.get_kysimus(objseq)
        if not k:
            sisuplokk = self.sisuplokk or Sisuplokk.get(self.sisuplokk_id)
            assert sisuplokk, 'Sisuplokk puudub'
            k = Kysimus(sisuplokk=sisuplokk, objseq=objseq, sisuobjekt=self)
            if objseq == const.OBJSEQ_K:
                k.kood = self.kood
        return k

    def get_kysimus(self, objseq=const.OBJSEQ_K):
        """Leitkase kysimus 
        """
        for k in self.kysimused:
            if k.objseq == objseq:
                return k

    @classmethod
    def get_img_path(cls, ylesanne_id, sisuplokk_id=None, lang=None, with_hotspots=False, sisuobj=None):
        verinf = ''
        if sisuobj:
            # kaitse brauseri cache vastu
            tran = lang and sisuobj.tran(lang, False)
            if tran:
                verinf = 'tv%s' % (tran.fileversion)
            else:
                verinf = 'v%s' % (sisuobj.fileversion)
        path = 'images_%s_%s_%s%s_%s' % (ylesanne_id,
                                         sisuplokk_id or '',
                                         lang or '',
                                         with_hotspots and 'H' or '',
                                         verinf)
        return path.rstrip('_')

    @classmethod
    def get_cls_url(cls, ylesanne_id, filename, lang=None):
        # kasutamiseks juhul, kui sisuobjekti veel ei pruugi olla 
        # (aga lünktekstis on link)
        return '%s/%s' % (cls.get_img_path(ylesanne_id, lang=lang),
                          urllib.parse.quote(filename.encode('utf-8')))
        
    def get_url(self, lang=None, no_sp=False, with_hotspots=False, filename=None, encode=True):
        # filename antakse ette matemaatika taustobjektile ühe pisipildi urli saamiseks
        # no_sp=False lisab pildi URLi sisuploki ID ja pildi versiooni
        #     HTML ekspordis kasutada no_sp=True, kuna ylesande kõik pildid kindlas kaustas
        if not filename and filename != False:
            filename = self.filename
        if not filename:
            filename = '_F%s.file' % self.id
        elif encode:
            filename = urllib.parse.quote(filename.encode('utf-8'))
        if no_sp:
            sisuplokk_id = None
            sisuobj = None
            lang = None
            with_hotspots = False
        else:
            sisuplokk_id = self.sisuplokk_id
            sisuobj = self
        url = '%s/%s' % (Sisuobjekt.get_img_path(self.sisuplokk.ylesanne_id,
                                                 sisuplokk_id=sisuplokk_id,
                                                 lang=lang,
                                                 with_hotspots=with_hotspots,
                                                 sisuobj=sisuobj),
                         filename)
        return url

    def get_tran_url(self, lang=None, no_sp=False):
        tran = self.tran(lang)
        return tran.fileurl or self.get_url(lang, no_sp=no_sp)
    
    def get_min_vastus(self):
        return self.min_vastus or 0

    def get_max_vastus(self):
        return self.max_vastus or 1

    def set_image_size(self, filedata, stream, fn, lang=None, laius=None, korgus=None):
        """Parameetriks on antud failisisu (postitatud) või failinimi või failipointer.
        Kui see on pildifail, siis muudetakse kirje laius_orig ja korgus_orig vastavaks
        pildi originaalmõõtudele.
        Kui ei ole pildifail, siis visatakse IOError.
        Kui pildi kuvamismõõdud on määramata, siis omistatakse originaalmõõdud kuvamismõõtudeks.
        """
        t = self.give_tran(lang)
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
        elif laius and korgus:
            t.laius_orig, t.korgus_orig = laius, korgus

        if t.laius_orig and t.korgus_orig:
            if t.laius is None and t.korgus is None:
                t.laius = t.laius_orig
                t.korgus = t.korgus_orig
            elif t.laius is None:
                t.laius = t.laius_orig*t.korgus/t.korgus_orig
            elif t.korgus is None:
                t.korgus = t.korgus_orig*t.laius/t.laius_orig
            if t.laius and t.laius > 900:
                # div.esitlus-body laius on 900px
                t.korgus = t.korgus * 900 / t.laius
                t.laius = 900

    @classmethod
    def get_item(cls, **args):
        """Kui kirje on juba kohalikus baasis olemas, siis leitakse see.
        args - pakitud kirje 
        """
        # yle laaditud selleks, et kui row_type on krüptimisel kaotatud,
        # siis kasutataks Sisuobjekti klassi
        return Sisuobjekt.get(args['id'])

    def unpickle_sisu(self, lang=None):
        "GoogleChartsi korral: andmete hoidmine sisu sees"
        sisu = self.tran(lang).filedata
        if sisu:
            return pickle.loads(sisu)
                
class Taustobjekt(Sisuobjekt):
    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': const.OBJ_BACK}
    def post_create(self):
        self.seq = 0

    def from_form(self, form_result, prefix='', ignore_if_none=[], lang=None, is_image=True):
        EntityHelper.from_form(self, form_result, prefix=prefix, lang=lang)
        if is_image:
            fobj = form_result.get(prefix + 'filedata')
            if fobj != None and fobj != b'':
                filename = fobj.filename
                stream = fobj.file
            else:
                filename = stream = None
            self.set_image_size(None, stream, filename, lang)

class Piltobjekt(Sisuobjekt):
    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': const.OBJ_GAPIMG}    

    def from_form(self, form_result, prefix='', ignore_if_none=[], lang=None):
        EntityHelper.from_form(self, form_result, prefix=prefix, lang=lang)
        fobj = form_result.get(prefix + 'filedata')
        if fobj != None and fobj != b'':
            filename = fobj.filename
            stream = fobj.file
        else:
            filename = stream = None
        self.set_image_size(None, stream, filename, lang)

class Meediaobjekt(Sisuobjekt):
    __tablename__ = None
    __mapper_args__ = {'polymorphic_identity': const.OBJ_MEDIA}        
    def post_create(self):
        self.seq = 0

    autostart = Column(Boolean) # kas multimeedia käivitatakse automaatselt
    min_kordus = Column(Integer) # min korduste arv
    max_kordus = Column(Integer) # max korduste arv
    isekorduv = Column(Boolean) # kas peale mängimise lõppemist hakkab ise algusest uuesti peale
    pausita = Column(Boolean) # kas pausile panek on keelatud 
    player = Column(Integer) # MP3 ja MP4 mängija: 1 - brauseri mängija; 0 - jPlayer
    nocontrols = Column(Boolean) # kas kuvada <audio> ilma nuppudeta, ainult mängimise nupp
    mediainfo = Column(Text) # MediaInfo dict

    def copy(self):
        cp = Sisuobjekt.copy(self)
        cp.autostart = self.autostart
        cp.min_kordus = self.min_kordus
        cp.max_kordus = self.max_kordus
        cp.isekorduv = self.isekorduv
        cp.pausita = self.pausita
        cp.nocontrols = self.nocontrols
        return cp
    
    def from_form(self, form_result, prefix='', ignore_if_none=[], lang=None):
        EntityHelper.from_form(self, form_result, prefix=prefix, lang=lang)
        fobj = form_result.get(prefix + 'filedata')
        self.set_media_size(fobj != None and fobj != b'' and fobj.file, lang)

    def set_media_size(self, filedata, lang=None):
        "Salvestatakse multimeedia metainfo ja mõõdud"
        self.set_mimetype()
        t = self.give_tran(lang)
        if filedata:
            if not t.id:
                Session.flush()
            mediainfo = self.find_mediainfo(filedata)
            if mediainfo:
                self.mediainfo = json.dumps(mediainfo)
                for track in mediainfo:
                    if track['track_type'] == 'Video':
                        t.laius_orig = track['width']
                        t.korgus_orig = track['height']
                        break
        
        if self.is_audio:
            # audio
            if not t.laius:
                t.laius = 480
            if not t.korgus:
                t.korgus = 100
        else:
            # video
            if t.laius_orig and t.korgus_orig:
                if t.laius is None and t.korgus is None:
                    t.korgus = min(t.korgus_orig, 385)
                if t.laius is None:
                    t.laius = t.laius_orig*t.korgus/t.korgus_orig
                elif t.korgus is None:
                    t.korgus = t.korgus_orig*t.laius/t.laius_orig
                if t.laius and t.laius > 900:
                    # div.esitlus-body laius on 900px
                    t.korgus = t.korgus * 900 / t.laius
                    t.laius = 900

            if not self.laius and not self.korgus:
                # vaikimisi suurus
                t.laius, t.korgus = 480, 385
                    
###########################################################
# import pymediainfo
# media_info = pymediainfo.MediaInfo.parse(fn)
# for t in media_info.tracks:
#    print (t.track_type)
#    for k,v in t.to_data().items():
#       print(f'    {k}={v}')

# General.format # MPEG-4
# General.duration # millisekundite arv
# General.other_duration[0] # 1 min 0 s
# General.other_overall_bit_rate[0] # 734 kb/s
# Video.format_info # Advanced Video Codec
# Video.bit_rate # baitide arv
# Video.other_bit_rate[0] # 613 kb/s
# Video.width
# Video.height
# Video.bit_depth # 8
# Video.other_bit_depth # 8 bits
# Audio.bit_rate # baitide arv
# Audio.other_bit_Rate[0]

# General
#     track_type=General
#     count=331
#     count_of_stream_of_this_kind=1
#     kind_of_stream=General
#     other_kind_of_stream=['General']
#     stream_identifier=0
#     count_of_video_streams=1
#     count_of_audio_streams=1
#     othercount=2
#     video_format_list=AVC
#     video_format_withhint_list=AVC
#     codecs_video=AVC
#     video_language_list=English
#     audio_format_list=AAC LC
#     audio_format_withhint_list=AAC LC
#     audio_codecs=AAC LC
#     audio_language_list=English
#     other_format_list=RTP / RTP
#     other_format_withhint_list=RTP / RTP
#     other_codec_list=RTP / RTP
#     other_language_list=English / English
#     complete_name=big_buck_bunny.mp4
#     file_name=big_buck_bunny.mp4
#     other_file_name=['big_buck_bunny']
#     file_extension=mp4
#     format=MPEG-4
#     other_format=['MPEG-4']
#     format_extensions_usually_used=mov mp4 m4v m4a m4b m4p m4r 3ga 3gpa 3gpp 3gp 3gpp2 3g2 k3g jpm jpx mqv ismv isma ismt f4a f4b f4v
#     commercial_name=MPEG-4
#     format_profile=Base Media / Version 2
#     internet_media_type=video/mp4
#     codec_id=mp42
#     other_codec_id=['mp42 (mp42/avc1)']
#     codec_id_url=http://www.apple.com/quicktime/download/standalone.html
#     codecid_compatible=mp42/avc1
#     file_size=5510872
#     other_file_size=['5.26 MiB', '5 MiB', '5.3 MiB', '5.26 MiB', '5.256 MiB']
#     duration=60095
#     other_duration=['1 min 0 s', '1 min 0 s 95 ms', '1 min 0 s', '00:01:00.095', '00:01:00:00', '00:01:00.095 (00:01:00:00)']
#     overall_bit_rate=733621
#     other_overall_bit_rate=['734 kb/s']
#     frame_rate=24.000
#     other_frame_rate=['24.000 FPS']
#     frame_count=1440
#     stream_size=423077
#     other_stream_size=['413 KiB (8%)', '413 KiB', '413 KiB', '413 KiB', '413.2 KiB', '413 KiB (8%)']
#     proportion_of_this_stream=0.07677
#     headersize=37106
#     datasize=5473766
#     footersize=0
#     isstreamable=Yes
#     encoded_date=UTC 2010-02-09 01:55:39
#     tagged_date=UTC 2010-02-09 01:55:40
#     file_last_modification_date=UTC 2022-04-21 13:08:54
#     file_last_modification_date__local=2022-04-21 16:08:54
# Video
#     track_type=Video
#     count=375
#     count_of_stream_of_this_kind=1
#     kind_of_stream=Video
#     other_kind_of_stream=['Video']
#     stream_identifier=0
#     streamorder=1
#     track_id=2
#     other_track_id=['2']
#     format=AVC
#     other_format=['AVC']
#     format_info=Advanced Video Codec
#     format_url=http://developers.videolan.org/x264.html
#     commercial_name=AVC
#     format_profile=Baseline@L3
#     format_settings=2 Ref Frames
#     format_settings__cabac=No
#     other_format_settings__cabac=['No']
#     format_settings__reframes=2
#     other_format_settings__reframes=['2 frames']
#     format_settings__gop=M=1, N=64
#     internet_media_type=video/H264
#     codec_id=avc1
#     codec_id_info=Advanced Video Coding
#     duration=60095
#     other_duration=['1 min 0 s', '1 min 0 s 95 ms', '1 min 0 s', '00:01:00.095', '00:01:00:00', '00:01:00.095 (00:01:00:00)']
#     duration_lastframe=95
#     other_duration_lastframe=['95 ms', '95 ms', '95 ms', '00:00:00.095']
#     bit_rate=613147
#     other_bit_rate=['613 kb/s']
#     width=640
#     other_width=['640 pixels']
#     height=360
#     other_height=['360 pixels']
#     stored_height=368
#     sampled_width=640
#     sampled_height=360
#     pixel_aspect_ratio=1.000
#     display_aspect_ratio=1.778
#     other_display_aspect_ratio=['16:9']
#     rotation=0.000
#     frame_rate_mode=CFR
#     other_frame_rate_mode=['Constant']
#     frame_rate=24.000
#     other_frame_rate=['24.000 FPS']
#     frame_count=1440
#     color_space=YUV
#     chroma_subsampling=4:2:0
#     other_chroma_subsampling=['4:2:0']
#     bit_depth=8
#     other_bit_depth=['8 bits']
#     scan_type=Progressive
#     other_scan_type=['Progressive']
#     bits__pixel_frame=0.111
#     stream_size=4598601
#     other_stream_size=['4.39 MiB (83%)', '4 MiB', '4.4 MiB', '4.39 MiB', '4.386 MiB', '4.39 MiB (83%)']
#     proportion_of_this_stream=0.83446
#     language=en
#     other_language=['English', 'English', 'en', 'eng', 'en']
#     encoded_date=UTC 2010-02-09 01:55:39
#     tagged_date=UTC 2010-02-09 01:55:40
#     colour_description_present=Yes
#     colour_description_present_source=Stream
#     color_range=Limited
#     colour_range_source=Stream
#     color_primaries=BT.601 NTSC
#     colour_primaries_source=Stream
#     transfer_characteristics=BT.709
#     transfer_characteristics_source=Stream
#     matrix_coefficients=BT.601
#     matrix_coefficients_source=Stream
#     codec_configuration_box=avcC
# Audio
#     track_type=Audio
#     count=277
#     count_of_stream_of_this_kind=1
#     kind_of_stream=Audio
#     other_kind_of_stream=['Audio']
#     stream_identifier=0
#     streamorder=0
#     track_id=1
#     other_track_id=['1']
#     format=AAC
#     other_format=['AAC LC']
#     format_info=Advanced Audio Codec Low Complexity
#     commercial_name=AAC
#     format_additionalfeatures=LC
#     codec_id=mp4a-40-2
#     duration=60095
#     other_duration=['1 min 0 s', '1 min 0 s 95 ms', '1 min 0 s', '00:01:00.095', '00:00:58:18', '00:01:00.095 (00:00:58:18)']
#     source_duration=60140
#     other_source_duration=['1 min 0 s', '1 min 0 s 140 ms', '1 min 0 s', '00:01:00.140']
#     bit_rate_mode=CBR
#     other_bit_rate_mode=['Constant']
#     bit_rate=64000
#     other_bit_rate=['64.0 kb/s']
#     channel_s=2
#     other_channel_s=['2 channels']
#     channel_positions=Front: L R
#     other_channel_positions=['2/0/0']
#     channel_layout=L R
#     samples_per_frame=1024
#     sampling_rate=22050
#     other_sampling_rate=['22.05 kHz']
#     samples_count=1325095
#     frame_rate=21.533
#     other_frame_rate=['21.533 FPS (1024 SPF)']
#     frame_count=1294
#     source_frame_count=1295
#     compression_mode=Lossy
#     other_compression_mode=['Lossy']
#     stream_size=489194
#     other_stream_size=['478 KiB (9%)', '478 KiB', '478 KiB', '478 KiB', '477.7 KiB', '478 KiB (9%)']
#     proportion_of_this_stream=0.08877
#     source_stream_size=489201
#     other_source_stream_size=['478 KiB (9%)', '478 KiB', '478 KiB', '478 KiB', '477.7 KiB', '478 KiB (9%)']
#     source_streamsize_proportion=0.08877
#     language=en
#     other_language=['English', 'English', 'en', 'eng', 'en']
#     encoded_date=UTC 2010-02-09 01:55:39
#     tagged_date=UTC 2010-02-09 01:55:40
# Other
#     track_type=Other
#     count=118
#     count_of_stream_of_this_kind=2
#     kind_of_stream=Other
#     other_kind_of_stream=['Other']
#     stream_identifier=0
#     other_stream_identifier=['1']
#     streamorder=2
#     track_id=3
#     other_track_id=['3']
#     type=Hint
#     format=RTP
#     other_format=['RTP']
#     commercial_name=RTP
#     codec_id=rtp
#     duration=60095
#     other_duration=['1 min 0 s', '1 min 0 s 95 ms', '1 min 0 s', '00:01:00.095', '00:01:00.095']
#     frame_count=1440
#     title=Hinted Video Track
#     language=en
#     other_language=['English', 'English', 'en', 'eng', 'en']
#     default=No
#     other_default=['No']
#     encoded_date=UTC 2010-02-09 01:55:39
#     tagged_date=UTC 2010-02-09 01:55:40
#     duration_lastframe=95
# Other
#     track_type=Other
#     count=123
#     count_of_stream_of_this_kind=2
#     kind_of_stream=Other
#     other_kind_of_stream=['Other']
#     stream_identifier=1
#     other_stream_identifier=['2']
#     streamorder=3
#     track_id=4
#     other_track_id=['4']
#     type=Hint
#     format=RTP
#     other_format=['RTP']
#     commercial_name=RTP
#     codec_id=rtp
#     duration=60095
#     other_duration=['1 min 0 s', '1 min 0 s 95 ms', '1 min 0 s', '00:01:00.095', '00:01:00.095']
#     frame_count=648
#     title=Hinted Sound Track
#     language=en
#     other_language=['English', 'English', 'en', 'eng', 'en']
#     default=No
#     other_default=['No']
#     encoded_date=UTC 2010-02-09 01:55:39
#     tagged_date=UTC 2010-02-09 01:55:40
#     source_duration=60140
#     source_duration_firstframe=46
#     source_frame_count=648
#     source_stream_size=41456
#     stream_size=41456
#     bit_rate_mode=VBR
