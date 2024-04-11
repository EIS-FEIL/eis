import re
import random
import json
import eiscore.const as const
from eiscore.recordwrapper import RecordWrapper
import urllib.request, urllib.parse, urllib.error
from PIL import Image
import pymediainfo
import mimetypes
from eis.s3file import S3File
import logging
log = logging.getLogger(__name__)

class TestWrapper:
    @property
    def keeled(self):
        if not self.skeeled:
            return []
        return self.skeeled.split()

    @property
    def on_tseis(self):
        # kas on TSEISi liiki test (neid koheldakse pisut erinevalt muudest)
        return self.testiliik_kood in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS)

    @property
    def on_kutse(self):
        # kas on kutseeksam
        return self.testiliik_kood == const.TESTILIIK_KUTSE

    @property
    def on_jagatudtoo(self):
        return self.testityyp == const.TESTITYYP_TOO

    @property
    def on_avaliktest(self):
        return self.testityyp == const.TESTITYYP_AVALIK

    @property
    def naita_p(self):
        "Kas näidata lahendajale saadud palle"
        return not self.diagnoosiv and not self.pallideta
    
    
class YlesanneWrapper:
    "Ylesande kirje andmed"

    def get_kysimus(self, kood=None, kysimus_id=None):
        for sp in self.sisuplokid:
            for k in sp.kysimused:
                if (kood and k.kood == kood) \
                   or (kysimus_id and k.id == kysimus_id):
                    return k

    def get_ckeditor_icons(self):
        nupuriba = self.lahendusjuhis and self.lahendusjuhis.nupuriba
        if not nupuriba:
            # supsub nupuriba
            nupuriba = 'Undo,Redo,Subscript,Superscript,SupSub,mathck,MatMultiply,MatDivide,SpecialChar,eszett'
        return (nupuriba or '').split(',')

    def get_math_icons(self, matriba=None):
        nupuriba = matriba or self.lahendusjuhis and self.lahendusjuhis.matriba
        if nupuriba is None:
            # nupuriba pole veel määratud, kasutame vaikimisi
            nupuriba = 'fraction,square_root,root,superscript,subscript,multiplication,division'
        if nupuriba:
            return nupuriba.split(',')
        else:
            # redaktor ilma nupureata
            return [];

    def get_on_rtf_shared(self):
        "Kas lahendajal on jagatud nupuriba"
        for sp in self.sisuplokid:
            if sp.on_rtf_shared:
                return True
        return False

class SisuplokkWrapper:
    
    @property
    def kysimus(self):
        return self.get_kysimus()
    
    def get_kysimus(self, kood=None, seq=None):
        for k in self.kysimused:
            if kood is None and seq is None:
                return k
            elif seq is not None and k.seq == seq:
                return k
            elif seq == 0 and k.seq is None:
                return k            
            elif kood and k.kood == kood:
                return k
            
    def get_baaskysimus(self, seq=0):
        for k in self.kysimused:
            if k.kood is None:
                if not seq or seq == k.seq:
                    return k

    @property
    def pariskysimused(self):
        return [k for k in self.kysimused if k.kood]

    def get_prefix(self):
        return f'b{self.id}'
    
    def get_result(self):
        return f'b{self.id}_result'

    def replace_img_url(self, txt, lang=None):
        """Kui ülesandes on pildid ja nendele lingitakse kireva teksti seest
        kujul images/failinimi.jpg, siis tuleb asendada pildi URL niisuguse URLiga,
        kust saab ülesande ID kätte.
        """
        if txt:
            img_path = _get_img_path(self.ylesanne_id, lang=lang)
            return re.sub(' (src|background)=" *images/', ' \\1="%s/' % img_path, txt)

    def gen_piltobjekt_kood(self, gentype='1'):
        """Genereeritakse kood võimalikule uuele piltobjektile.
        gentype - 'A' (genereeritakse tähti) või '1' (genereeritakse arve)
        """
        for n in range(1,1000):
            if gentype == 'A' and n < 27:
                kood = chr(n+64)
            else:
                kood = 'PILT%d' % n
            found = False
            for rcd in self.piltobjektid:
                if rcd.kood == kood:
                    found = True
                    break
            if not found:
                return kood
        return ''
    
    def get_sisuobjekt(self, kood):
        for r in self.sisuobjektid:
            if r.kood == kood:
                return r

    @property
    def piltobjektid(self):
        return [o for o in self.sisuobjektid if o.row_type == const.OBJ_GAPIMG]

    @property
    def taustobjekt(self):
        for o in self.sisuobjektid:
            if o.row_type == const.OBJ_BACK:
                return o

    @property
    def meediaobjekt(self):
        for o in self.sisuobjektid:
            if o.row_type == const.OBJ_MEDIA:
                return o

    @property
    def meediaobjektid(self):
        return [o for o in self.sisuobjektid if o.row_type == const.OBJ_MEDIA]        

    @property
    def samameediaobjektid(self):
        "Multimeediaobjektid rühmitatud nii, et sama faili erinevad formaadid on koos"
        peaobjektid = {}
        objektid = []
        for obj in self.meediaobjektid:
            sf = obj.samafail
            if not sf:
                # fail, millel pole erinevaid formaate
                objektid.append(obj)
                obj.muudformaadid = []
            elif sf in peaobjektid:
                # varem leitud faili teine formaat
                peaobjektid[sf].muudformaadid.append(obj)
            else:
                # mitme formaadiga faili põhikirje
                objektid.append(obj)
                obj.muudformaadid = []
                peaobjektid[sf] = obj
        return objektid
    
    @property
    def is_interaction(self):
        "Kas on interaktsioon või staatiline plokk"
        return self.tyyp not in const.interaction_block

    @property
    def is_qti_interaction(self):
        "Kas on QTI interaktsioon"
        return self.tyyp in (const.INTER_POS,
                             const.INTER_DRAW,
                             const.INTER_GAP,
                             const.INTER_MATCH2,
                             const.INTER_MATCH3,
                             const.INTER_GR_GAP,
                             const.INTER_HOTSPOT,
                             const.INTER_GR_ORDER,
                             const.INTER_SELECT,
                             const.INTER_GR_ASSOCIATE,
                             const.INTER_SLIDER,
                             const.INTER_CHOICE,
                             const.INTER_HOTTEXT,
                             const.INTER_ORDER,
                             const.INTER_TEXT,
                             const.INTER_EXT_TEXT,
                             const.INTER_UPLOAD,
                             const.INTER_ASSOCIATE)

    @property
    def is_block(self):
        return self.tyyp in const.interaction_block

    @property
    def is_interaction_choice(self):
        return self.tyyp in const.interaction_choice

    @property
    def is_interaction_text(self):
        return self.tyyp in const.interaction_text

    @property
    def is_interaction_graphic(self):
        return self.tyyp in const.interaction_graphic
    
    @property
    def on_rtf_kysimusi(self):
        # iexttext korral: kas on kireva teksti sisestamisega lünki
        for k in self.kysimused:
            if k.rtf:
                return True
        return False

    @property
    def on_math_kysimusi(self):
        # kas on matemaatilise teksti sisestamise küsimusi
        if self.tyyp == const.INTER_MATH:
            return True
        elif self.tyyp == const.INTER_INL_TEXT:
            for k in self.kysimused:
                t = k.tulemus
                if t and t.baastyyp == const.BASETYPE_MATH:
                    return True
            # lisaks on võimalus sisestada mat teksti, kui CKEDITORi ikoonides on mathck,
            # aga see ei ole siis eraldi kysimus
        return False

    @property
    def on_rtf_shared(self):
        # iexttext,iinltext korral: kas on vaja nupuriba
        for k in self.kysimused:
            if k.rtf and not k.rtf_notshared:
                return True
        return False
       
    def get_json_sisu(self, lang=None):
        "GeoGebra, ristsõna, mitme valikuga tabeli, ipunkt korral: andmete hoidmine sisu sees"
        sisu = self.tran(lang).sisu
        if sisu:
            return json.loads(sisu)

    def louend_pos(self, lang, drag_images):
        """Arvutame lohistatavate piltide algsed asukohad lõuendil
        ja lõuendi suuruse
        """
        pos = {} # asukohad
        mo = self.taustobjekt
        dx = 5 # vahe piltide vahel
        dy = 3 # vahe piltide vahel 
        dx0 = 35 # vahe tausta ja piltide vahel, kui pildid on kõrval
        dy0 = 35 # vahe tausta ja piltide vahel, kui pildid on all
        taust_laius = mo.laius or 100
        taust_korgus = mo.korgus or 100
        taust_x = taust_y = 0

        if not drag_images:
            return pos, taust_laius, taust_korgus, taust_x, taust_y
    
        piltobjektid = list(self.piltobjektid)
        if mo.segamini:
            # ajame järjekorra sassi
            random.shuffle(piltobjektid)

        if mo.asend in (SisuobjektWrapper.ASEND_ALL, SisuobjektWrapper.ASEND_YLEVAL):
            # pildid kuvada tausta all või ylal
            x = 0
            if mo.asend == SisuobjektWrapper.ASEND_YLEVAL:
                y = 0
            else:
                y = taust_korgus + dy0
            max_korgus = 0

            for item in piltobjektid:
                item_korgus = item.tran(lang).korgus or item.korgus or 0
                item_laius = item.tran(lang).laius or item.laius or 0
                if x > 0 and x + item_laius > taust_laius:
                    # alustame uut rida
                    y += max_korgus + dy
                    x = 0
                    max_korgus = 0
                for seq in range(item.max_vastus or 1):
                    # lisame jooksvasse ritta
                    pos[item.id, seq] = x, y
                    max_korgus = max(max_korgus, item_korgus)
                x += item_laius + dx

            louend_laius = taust_laius
            if mo.asend == SisuobjektWrapper.ASEND_YLEVAL:
                taust_y = y + max_korgus + dy0
                louend_korgus = taust_y + taust_korgus
            else:
                louend_korgus = y + max_korgus
        else:
            # pildid kuvada taustast paremal või vasakul
            
            y = 0
            if mo.asend == SisuobjektWrapper.ASEND_VASAKUL:
                x = 0
            else:
                x = taust_laius + dx0
            max_laius = 0
            for item in piltobjektid:
                item_korgus = item.tran(lang).korgus or item.korgus or 0
                item_laius = item.tran(lang).laius or item.laius or 0
                cnt = item.max_vastus or 1
                for seq in range(cnt):
                    if seq == 0 or item.eraldi:
                        if y > 0 and y + item_korgus > taust_korgus:
                            # alustame uut tulpa
                            x += max_laius + dx
                            y = 0
                            max_laius = 0
                    # lisame jooksvasse tulpa
                    pos[item.id, seq] = x, y
                    if seq == cnt - 1 or item.eraldi:
                        max_laius = max(max_laius, item_laius)
                        y += item_korgus + dy

            louend_korgus = taust_korgus
            if mo.asend == SisuobjektWrapper.ASEND_VASAKUL:
                taust_x = x + max_laius + dx0
                louend_laius = taust_x + taust_laius
            else: 
                louend_laius = x + max_laius
            
        return pos, louend_laius, louend_korgus, taust_x, taust_y
    
    def get_crossword_map(self, lang=None):
        """Koostatakse ristsõna tabel, mille iga lahter on:
        - kui on vihje lahter, siis kysimus
        - kui on kasutamata lahter, siis None
        - kui on tähe lahter, siis list, mille:
          - esimene element fikseeritud tähe korral see täht, sisestatava tähe korral None
          - järgmised elemendid on tupled (sõna kysimuse kood, tähe positsioon sõnas),
            kus listis on element iga sõna kohta, milles see lahter sisaldub
        """
        t_block = lang and self.tran(lang, False) or None
        rows = t_block and t_block.korgus or self.korgus
        cols = t_block and t_block.laius or self.laius

        class CwCell:
            def __init__(self):
                self.fixed_char = None # fikseeritud täht
                self.title_k = None # kysimus (kui lahtris on sõna seletus)
                self.next = None # järgmise tähe asukoht cw-gap-Y-X
                self.words = [] # (kysimuse kood, mitmes täht sõnas)
            
        data = [[CwCell() for x in range(cols or 0)] for y in range(rows or 0)]

        def _char_pos(title_x, title_y, direction, n_char):
            "Leiame sõna n. tähe positsiooni"
            if direction == const.DIRECTION_RIGHT:
                return title_x + n_char + 1, title_y
            elif direction == const.DIRECTION_LEFT:
                return title_x - n_char - 1, title_y
            elif direction == const.DIRECTION_UP:
                return title_x, title_y - n_char - 1
            elif direction == const.DIRECTION_DOWN:
                return title_x, title_y + n_char + 1

        # paneme tabelisse etteantud tähed
        jdata = self.get_json_sisu(lang)
        if lang and jdata is None:
            jdata = self.get_json_sisu()
        if jdata:
            chars = jdata.get('chars') or []
            if chars:
                for title_x, title_y, ch in chars:
                    # fikseeritud täht, mitte kysimus
                    if title_y >= rows or title_x >= cols:
                        log.error('ristsõna koostamise viga 3 %s,%s' % (title_x, title_y))
                        continue
                    data[title_y][title_x].fixed_char = ch

        kysimused = [(k, k.tran(lang)) for k in self.kysimused]

        # lisame vihjed ja sisestatavad tähed
        for k, t_k in kysimused:
            title_x, title_y = t_k.pos_x, t_k.pos_y
            if title_x is None or title_y is None or k.pseudo:
                continue
            if title_y >= rows or title_x >= cols:
                log.error('ristsõna koostamise viga2 %s,%s' % (title_x, title_y))
                continue
            cell = data[title_y][title_x]
            if cell.fixed_char or cell.title_k:
                # viga, selle koha peal peaks olema tyhi list, aga on midagi muud
                log.error('ristsõna koostamise viga1 %s,%s: %s' % (title_x, title_y, cell))
            
            cell.title_k = k
            pikkus = t_k.pikkus
            init_value = ''
            prev_cell = None
            for n_char in range(pikkus):
                char_x, char_y = _char_pos(title_x, title_y, t_k.joondus, n_char)
                if char_x < 0 or char_x >= cols:
                    # viga!
                    log.error('ristsõna koostamise viga3 %s/%s' % (char_x, cols))
                    break
                if char_y < 0 or char_y >= rows:
                    # viga!
                    log.error('ristsõna koostamise viga4 %s/%s' % (char_y, rows))                    
                    break
                cell = data[char_y][char_x]
                if cell.title_k:
                    # viga, selle koha peal peaks olema täht, aga on kysimus
                    log.error('ristsõna koostamise viga2 %s,%s: %s' % (char_x, char_y, cell))
                    break
                cell.words.append((k.kood, n_char))
                if not cell.fixed_char:
                    # on sisestatav ruut
                    if prev_cell:
                        # eelmisele ruudule märgime, kuhu suunas edasi minna
                        if prev_cell.next:
                            # kui täht on kahes sõnas, siis automaatselt edasi ei liigu,
                            # sest ei tea, mis suunas kasutaja soovib minna
                            prev_cell.next = None
                        else:
                            prev_cell.next = f'cw-gap-{char_y}-{char_x}'
                    prev_cell = cell
                fixed_char = cell.fixed_char
                init_value += fixed_char or '_'
            k.init_value = init_value
            
        return data, cols, rows
                
class SisuobjektWrapper:
    
    ASEND_PAREMAL = 0
    ASEND_ALL = 1
    ASEND_VASAKUL = 2
    ASEND_YLEVAL = 3

    PLAYER_JPLAYER = 0 # jPlayer
    PLAYER_HTML5 = 1 # brauseri oma mängija 

    def get_json_sisu(self, lang=None):
        "GeoGebra, ristsõna, mitme valikuga tabeli, ipunkt korral: andmete hoidmine sisu sees"
        sisu = self.tran(lang).sisu
        if sisu:
            return json.loads(sisu)

    def get_sisuobjekt(self, kood):
        for r in self.sisuobjektid:
            if r.kood == kood:
                return r

    @property
    def piltobjektid(self):
        return [o for o in self.sisuobjektid if o.row_type == const.OBJ_GAPIMG]

    @property
    def taustobjekt(self):
        for o in self.sisuobjektid:
            if o.row_type == const.OBJ_BACK:
                return o

    @property
    def meediaobjekt(self):
        for o in self.sisuobjektid:
            if o.row_type == const.OBJ_MEDIA:
                return o

    @property
    def meediaobjektid(self):
        return [o for o in self.sisuobjektid if o.row_type == const.OBJ_MEDIA]        

    @property
    def samameediaobjektid(self):
        "Multimeediaobjektid rühmitatud nii, et sama faili erinevad formaadid on koos"
        peaobjektid = {}
        objektid = []
        for obj in self.meediaobjektid:
            sf = obj.samafail
            if not sf:
                # fail, millel pole erinevaid formaate
                objektid.append(obj)
                obj.muudformaadid = []
            elif sf in peaobjektid:
                # varem leitud faili teine formaat
                peaobjektid[sf].muudformaadid.append(obj)
            else:
                # mitme formaadiga faili põhikirje
                objektid.append(obj)
                obj.muudformaadid = []
                peaobjektid[sf] = obj
        return objektid

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

    def set_mimetype(self):
        mimetype = self.guess_type()        
        if mimetype:
            self.mimetype = mimetype

    @property
    def mimetype_main(self):
        if not self.mimetype:
            self.set_mimetype()
        if self.mimetype:
            return self.mimetype.split('/')[0]

    @property
    def tulemus(self):
        """Leitakse tulemuse kirje, kui sisuobjektil on oma tulemus
        (pildile lohistamise sisuploki (ipos) piltobjekti korral)
        """
        for k in self.kysimused:
            return k.tulemus


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
        url = '%s/%s' % (self.get_img_path(self.sisuplokk.ylesanne_id,
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

    def get_kysimus(self, objseq=const.OBJSEQ_K):
        """Leitkase kysimus 
        """
        for k in self.sisuplokk.kysimused:
            if k.sisuobjekt_id == self.id:
                if k.objseq == objseq:
                    return k

    @property
    def is_jplayer(self):
        "Kas on jPlayer"
        return self.player != self.PLAYER_HTML5

    
    def find_mediainfo(self, filedata):
        """Leitakse multimeedia failist metainfo
        """
        if not filedata:
            return

        info = []
        fn = self.path_for_response
        if fn:
            # Linux
            try:
                media_info = pymediainfo.MediaInfo.parse(fn)
            except:
                raise
            else:
                tracks = media_info.tracks
                for ind, track in enumerate(tracks):
                    log.debug('Track %d %s format=%s codec_id=%s' % (ind, track.track_type, track.format, track.codec_id))
                    track_type = track.track_type
                    info.append(track.to_data())
        return info

    def get_mediainfo(self):
        "Leitakse multimeedia metainfo, mida kuvada kasutajale"
        if self.mediainfo:
            duration = format_ = bit_depth = bit_rate = None
            info = json.loads(self.mediainfo)
            for track in info:
                if track['track_type'] == 'General':
                    value = track.get('other_duration')
                    if value:
                        duration = value[0]
                    else:
                        duration = track.get('duration')

                    format_ = track.get('format')

                    value = track.get('other_overall_bit_rate')
                    if value:
                        bit_rate = value[0]
                    else:
                        bit_rate = track.get('overallbitrate')

                elif track['track_type'] == 'Video':
                    value = track.get('other_bit_depth')
                    if value:
                        bit_depth = value[0]
                    else:
                        bit_depth = track.get('bitdepth')
                    break
            return {'duration': duration,
                    'format': format_,
                    'bit_depth': bit_depth,
                    'bit_rate': bit_rate,
                    }

class TSisuobjektWrapper:    
    @property
    def fileext(self):
        orig = self.orig
        if orig:
            return orig.fileext
                
class KysimusWrapper:
    valikud = []

    @property
    def result(self):
        """Vormis vastuse välja nimi
        """
        return const.RPREFIX + self.kood

    def get_valik(self, kood):
        for v in self.valikud:
            if v.kood == kood:
                return v
 
    @property
    def gap_lynkadeta(self):
        # pangaga lynga korral: kas on lohistamine igale poole või ainult lynkadesse
        return self.ridu == 2

    @property
    def tulemus(self):
        if self.tulemus_id:
            for t in self.sisuplokk.ylesanne.tulemused:
                if t.id == self.tulemus_id:
                    return t

    @property
    def sisuobjekt(self):
        if self.sisuobjekt_id:
            for obj in self.sisuplokk.sisuobjektid:
                if obj.id == self.sisuobjekt_id:
                    return obj
                
class ValikWrapper:
    
    @property
    def koordinaadid(self):
        return self.nimi

    @koordinaadid.setter
    def koordinaadid(self, value):
        self.nimi = value

    @property
    def cx(self):
        return util.cx(self.koordinaadid, self.kujund)
    
    @property
    def cy(self):
        return util.cy(self.koordinaadid, self.kujund)

    def border_pos(self):
        return util.border_pos(self.koordinaadid, self.kujund)

    def list_koordinaadid(self):
        return util.coords_to_list(self.koordinaadid)

class TulemusWrapper:

    def get_max_pallid(self, koefitsient=1):
        punktid = self.max_pallid
        if punktid is None:
            punktid = self.max_pallid_arv
        if punktid is not None and koefitsient is not None:
            return punktid * koefitsient
    
    @property
    def oigsus_kysimus(self):
        k_id = self.oigsus_kysimus_id
        if k_id:
            for sp in self.ylesanne.sisuplokid:
                for k in sp.kysimused:
                    if k.id == k_id:
                        return k

class MemTest(RecordWrapper, TestWrapper):
    pass

class MemYlesanne(RecordWrapper, YlesanneWrapper):
    pass

class MemSisuplokk(RecordWrapper, SisuplokkWrapper):
    _parent_key = 'ylesanne'
   
class MemTSisuobjekt(RecordWrapper, TSisuobjektWrapper, S3File):
    _cache_dir = 't_sisuobjekt'
    _parent_key = 'orig'

class MemSisuobjekt(RecordWrapper, SisuobjektWrapper, S3File):
    _parent_key = 'sisuplokk'
    _cache_dir = 'sisuobjekt'
    mimetype = None # yle kirjutatud S3File mimetype
    _childclsmap = {'trans': MemTSisuobjekt}
    
class MemKysimus(RecordWrapper, KysimusWrapper):
    _parent_key = 'sisuplokk'

class MemValik(RecordWrapper, ValikWrapper):
    _parent_key = 'kysimus'

class MemTulemus(RecordWrapper, TulemusWrapper):
    _parent_key = 'ylesanne'

def _get_img_path(ylesanne_id, sisuplokk_id=None, lang=None, with_hotspots=False, sisuobj=None):
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
    
