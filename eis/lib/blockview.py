"""Ülesande sisu kuvamine
"""
from PIL import Image, ImageDraw
from io import BytesIO
from simplejson import loads
from eis.lib.base import *
_ = i18n._
import eis.lib.helpers as h
from eis.lib.block import BlockController
from eis.lib.blockcalc import BlockCalc

log = logging.getLogger(__name__)

class BlockView:
    "Ülesande kuvamine"

    def __init__(self, handler, ylesanne, lang):
        self.lang = lang
        self.handler = handler
        self.ylesanne = ylesanne
        self.request = handler.request
        self.c = handler.c # andmete hoiustamise objekt c
        self.need_save = False
        
    def gen_esitlus_sisu(self, template,
                         sooritus, ylesandevastus, responses, vy,
                         lahendaja, hindaja, hindamine_id, pcorrect, bcorrect,
                         random_responses):
        "Ülesande sisu esitluse genereerimine"
        # pcorrect - kas näidata lahendaja vastuse õigsust
        # bcorrect - kas näidata õige vastuse nuppu
        handler = self.handler
        c = self.c
        c.lang = self.lang
        c.ylesanne = ylesanne = self.ylesanne
        c.ylesandevastus = ylesandevastus
        c.sooritus = sooritus
        c.responses = responses
        c.responded = None
        c.responded_files = {}
        handler.prf()

        if ylesandevastus:
            self._set_vastusfail_url(c.responses, sooritus, ylesandevastus.id)

        # ylesande esmasel kuvamisel lahendajale võivad mõned vastused
        # edasi kanduda mõnest varasemast sama alatesti ylesandest

        c.evast_koodid = [] # kysimuste koodid, mille vastused võetakse eelmistest ylesannetest
        if ylesanne.evast_kasuta and vy and c.sooritus and lahendaja:
            alatest_id = vy.testiylesanne.alatest_id
            self._add_evast_responses(c.responses, c.sooritus, alatest_id, c.evast_koodid)

        # kas kuvada lynga tooltipis õiget vastust
        show_tips = not lahendaja

        # leiame antud vastused dictina, mida kasutada õige vastuse leidmisel juhul,
        # kui õige vastus arvutatakse valemiga, mis sõltub antud vastusest
        if show_tips and c.responses:
            r_locals = BlockCalc(handler)._calc_formula_locals(ylesanne, c.responses)
        else:
            r_locals = {}

        # kui kasutaja on hindaja, siis leitakse õiged vastused
        # kui kasutaja ei ole hindaja, siis leitakse näidisplokkide vastused
        #c.correct_responses

        handler.prf()
        c.show_response = c.prepare_response = True
        c.on_hindamine = hindaja
        c.hindamine = hindamine_id and model.Hindamine.get(hindamine_id) or None
        c.read_only = not lahendaja
        c.is_edit = lahendaja
        if not ylesanne.has_solution:
            pcorrect = False
        c.prepare_correct = pcorrect
        c.btn_correct = pcorrect and bcorrect
        c.block_correct = False

        if c.on_hindamine:
            handler.c.show_q_code = handler.c.show_r_code = True
            c.no_static_blocks = True # ainus koht, kus seda on tegelikult vaja määrata
        c.ks_sisu_ksmarkustega = ks_sisu_ksmarkustega
        html = self.render_assessment(random_responses, template)
        handler.prf()
        if self.need_save:
            # ylesande kuvamise käigus muudeti midagi, mida on vaja salvestada
            model.Session.commit()
        handler.prf()
        return html
   
    def _set_vastusfail_url(self, responses, sooritus, yv_id):
        c = self.c
        handler = self.handler
        h = handler.h
        test_id = sooritus and (c.test_id or c.test and c.test.id or sooritus.sooritaja.test_id)
        for kood, kv in responses.items():
            for ks in kv.kvsisud:
                if ks.filename:
                    if test_id:
                        ks.url = h.url('sooritamine_vastusfail_format',
                                       test_id=test_id,
                                       testiosa_id=sooritus.testiosa_id,
                                       sooritus_id=sooritus.id,
                                       id=ks.id,
                                       fileversion=ks.fileversion,
                                       format=ks.fileext)
                    else:
                        # yksiku ylesande sooritamine
                        ks.url = h.url('lahendamine_vastusfail_format',
                                       uuid=yv_id,
                                       id=ks.id,
                                       fileversion=ks.fileversion,
                                       format=ks.fileext)
    
    def assessment_include_view(self):
        """Ülesandele vajalike js failide valimine.
        """
        for block in self.ylesanne.sisuplokid:      
            if block.staatus == const.B_STAATUS_KEHTETU:
                # plokk pole nähtav
                continue

            # loome igale plokile oma kontrolleri
            ctrl = BlockController.get(block, self.ylesanne, self.handler)
            # jätame meelde vajalikud CSS ja JS failid
            ctrl.include_view()

    def assessment_view(self):
        """Ülesande kujundamine HTMLis lahendajale kuvamiseks
        """
        item_head = ''
        item_html = ''
        item_js = ''
        c = self.c
        c.ylesanne = ylesanne = self.ylesanne

        if c.block_correct:
            c.read_only = True

        paanid_html = {}

        # sisuplokkide segamine
        sisuplokid = self.order_sisuplokid(c.ylesandevastus)
        
        for block in sisuplokid:      
            if block.tyyp == const.BLOCK_HEADER and block.sisu:
                item_head += block.sisu
            if block.tyyp in (const.BLOCK_FORMULA, const.BLOCK_RANDOM):
                # plokk pole lahendajale nähtav
                continue
            if block.staatus == const.B_STAATUS_KEHTETU:
                # plokk pole nähtav
                continue

            if c.no_static_blocks and (block.naide or not block.is_interaction):
                # hindamise vaates ei näidata interaktsioonita sisuplokke
                block_html = ''
                paan_seq = 0
            else:
                # loome igale plokile oma kontrolleri
                ctrl = BlockController.get(block, ylesanne, self.handler)
                # keel
                ctrl.lang = self.lang
                # genereerime HTMLi
                block_html, block_js = ctrl.view()
                item_js += block_js
                paan_seq = block.paan_seq or 0
                
            # paneme ploki oma kohale
            paan_seq = ylesanne.paanide_arv == 2 and paan_seq or 0
            paan_html = paanid_html.get(paan_seq) or ''
            paan_html = BlockView.replace_placeholder(paan_html, block_html)
            paanid_html[paan_seq] = paan_html

        if ylesanne.paanide_arv != 2:
            # paanideta ylesanne
            item_html += paanid_html.get(0) or ''
        elif c.no_static_blocks:
            # paanidega ylesanne hindajale
            # hindamise vaade on ilma paanideta, aga järjestatud nii,
            # et esmalt vasaku poole plokid ja siis parema poole plokid
            item_html += (paanid_html.get(0) or '') + (paanid_html.get(1) or '')
        else:
            # paanidega ylesanne
            template = '/avalik/lahendamine/sisupooled.mako'
            c.paanid_html = paanid_html
            item_html = self.handler.render(template)

        if not item_html and c.no_static_blocks:
            helpers = h.RequestHelpers(self.handler.request)
            item_html = helpers.alert_notice(_("Sellel ülesandel interaktiivset osa ei ole"), False)

        if c.resize_prefixes:
            # ylesande funktsioon, mida kutsutakse välja akna suuruse muutumisel
            buf = ''
            for y1_prefix, b1_prefix in c.resize_prefixes:
                buf += "resize_%s();" % (b1_prefix)

            # igaks juhuks buf 2 korda
            item_js += "function resize() { for(var j_res=0; j_res<2; j_res++){" + buf + "};}\n" 
        
        if c.on_copy_resp_prefixes:
            # ylesande funktsioon, mida kutsutakse välja enne vastuste salvestamist
            buf = ''
            for y1_prefix, b1_prefix in c.on_copy_resp_prefixes:
                buf += "on_copy_resp_%s();" % (b1_prefix)
            item_js += "function on_copy_resp() { " + buf + "}\n"

        if c.prepare_correct:
            buf = ''
            for y1_prefix, b1_prefix in c.sh_correct_prefixes or []:
                buf += 'sh_correct_%s(rc); ' % (b1_prefix)
            item_js += 'function sh_correct(rc){ ' + buf + '}\n'
        if item_js:
            item_head += '<script>' + item_js + '</script>'

        return item_html, item_head      

    def render_assessment(self, random_responses, template):
        "Ülesande sisu esitluse genereerimine"

        c = self.c
        c.includes = dict()
        # list selle ylesande nende sisuplokkide ID-dest, 
        # millel on olemas resize-funktsioon 
        c.resize_prefixes = []
        # list nendest, millel on olemas on_copy_resize-funktsioon
        c.on_copy_resp_prefixes = []         
        self.assessment_include_view()
        if c.on_hindamine:
            # avatud tekstis vigade kommenteerimisel on värvimise võimalus
            c.includes['spectrum'] = True
        c.body, c.head = self.assessment_view()
        c.ylesanne = self.ylesanne

        if random_responses:
            for key, value in random_responses.items():
                r_key = '{%s}' % key
                s_value = h.fstr(value)
                c.body = c.body.replace(r_key, s_value)
        html = self.handler.render(template)
        return html

    def order_sisuplokid(self, ylesandevastus):
        "Sisuplokkide järjekorra segamine"
        ylesanne = self.ylesanne
        sisuplokid = list(ylesanne.sisuplokid)
        if ylesanne.segamini and ylesandevastus:
            jrk = ylesandevastus.valikujrk
            if not jrk:
                # segame segatavad sisuplokid
                jrk = [sp.id for sp in sisuplokid if not sp.fikseeritud]
                random.shuffle(jrk)
                # lisame kindla asukohaga sisuplokid
                for i in range(len(sisuplokid)):
                    sp = sisuplokid[i]
                    if sp.fikseeritud:
                        jrk.insert(i, sp.id)
                ylesandevastus.valikujrk = jrk
                self.need_save = True
                
            def _sortfunc(sp):
                try:
                    return jrk.index(sp.id)
                except ValueError:
                    return 0
            sisuplokid.sort(key=_sortfunc)
        return sisuplokid
   
    def _add_evast_responses(self, responses, sooritus, alatest_id, evast_koodid):
        "Lisame vastustele varasemate ülesannete edasi kantavate küsimuste vastused"
        # leiame kysimused, mille väärtuse võib võtta mõnest varasemast ylesandest
        q = (model.SessionR.query(model.Kysimus.kood)
             .filter(model.Kysimus.evast_kasuta==True)
             .join(model.Kysimus.sisuplokk)
             .filter(model.Sisuplokk.ylesanne_id==self.ylesanne.id))
        for kood, in q.all():
            evast_koodid.append(kood)

        # kui on kysimusi, mille väärtuse võib võtta varasemast, siis otsime varasemaid vastuseid
        if evast_koodid:
            if not model.is_temp_id(sooritus.id):
                # kui on andmebaasis salvestatud päris Sooritus
                q = (model.SessionR.query(model.Kysimusevastus, model.Kysimus.kood)
                     .join(model.Kysimusevastus.ylesandevastus)
                     .filter(model.Kysimusevastus.vastuseta==False)
                     .filter(model.Ylesandevastus.sooritus_id==sooritus.id)
                     .join((model.Kysimus,
                            model.Kysimus.id==model.Kysimusevastus.kysimus_id))
                     .filter(model.Kysimus.evast_edasi==True)
                     .filter(model.Kysimus.kood.in_(evast_koodid))
                     .join((model.Testiylesanne,
                            model.Testiylesanne.id==model.Ylesandevastus.testiylesanne_id))
                     .filter(model.Testiylesanne.alatest_id==alatest_id)
                     .order_by(model.sa.desc(model.Kysimusevastus.modified))
                     )
                for kv, k_kood in q.all():
                    #evast_koodid.append(k_kood)
                    if not responses.get(k_kood):
                        responses[k_kood] = kv
            else:
                # kui on eelvaate ajutine TempSooritus
                # leiame edasikantavad kysimused
                q = (model.SessionR.query(model.Kysimus.id,
                                         model.Kysimus.kood,
                                         model.Valitudylesanne.id)
                     .filter(model.Kysimus.evast_edasi==True)
                     .filter(model.Kysimus.kood.in_(evast_koodid))
                     .join(model.Kysimus.sisuplokk)
                     .join((model.Valitudylesanne,
                            model.Valitudylesanne.ylesanne_id==model.Sisuplokk.ylesanne_id))
                     .join(model.Valitudylesanne.testiylesanne)
                     .filter(model.Testiylesanne.testiosa_id==sooritus.testiosa_id)
                     .filter(model.Testiylesanne.alatest_id==alatest_id)
                     )
                # grupeerime kysimused valitudylesannete kaupa
                kysimused = dict()
                for k_id, k_kood, vy_id in q.all():
                    if vy_id not in kysimused:
                        kysimused[vy_id] = dict()
                    kysimused[vy_id][k_id] = k_kood
                #log.debug('evast_kysimused:%s' % str(kysimused))
                if kysimused:
                    valitudylesanded_id = list(kysimused.keys())
                    for yv in sooritus.ylesandevastused:
                        if yv.valitudylesanne_id in valitudylesanded_id:
                            vy_kysimused = kysimused[yv.valitudylesanne_id]
                            for kv in yv.kysimusevastused:
                                k_kood = vy_kysimused.get(kv.kysimus_id)
                                if k_kood and not kv.vastuseta:
                                    #evast_koodid.append(k_kood)
                                    if not responses.get(k_kood):
                                        # kysimus on vanast ylesandest edasikantav
                                        # ja pole veel uues ylesandes vastatud
                                        responses[k_kood] = kv
        return responses

    def assessment_analysis(self):
        """Ülesande kujundamine HTMLis antud vastuste analüüsijale
        """
        c = self.c
        item_html = ''
        c.read_only = True
        # leitakse näidisplokkide vastused
        c.correct_responses = self.ylesanne.correct_responses(
            c.ylesandevastus,
            lang=self.lang,
            naide_only=True,
            hindaja=True,
            naidistega=True)

        c.show_q_code = c.show_r_code = True
        c.ylesanne = self.ylesanne
        for block in self.ylesanne.sisuplokid:      
            if block.staatus == const.B_STAATUS_KEHTETU:
                # plokk pole nähtav
                continue

            # hindamise vaates ei näidata interaktsioonita sisuplokke
            if not block.is_interaction:
                continue

            # loome igale plokile oma kontrolleri
            ctrl = BlockController.get(block, self.ylesanne, self.handler)
            # keel
            ctrl.lang = self.lang
            # jätame meelde vajalikud CSS ja JS failid
            ctrl.include_view()
            # genereerime HTMLi
            item_html += ctrl.analysis()
        return item_html       

    @classmethod
    def assessment_entry(cls, ylesanne, lang, handler, is_correct=False):
        """P-testi ülesande kujundamine HTMLis vastuste sisestajale kuvamiseks
        is_correct - kas sisestada õige/vale (True) või vastus (False)
        """
        items = [] # sisuplokkide list
        for block in ylesanne.sisuplokid:      
            if block.staatus == const.B_STAATUS_KEHTETU or block.naide or not block.is_interaction:
                # plokk pole interaktiivne
                continue
            # loome igale plokile oma kontrolleri
            ctrl = BlockController.get(block, ylesanne, handler)
            # keel
            ctrl.lang = lang
            # genereerime HTMLi
            html = ctrl.entry(is_correct)
            if html:
                items.append((block, html))
        return items       

    @classmethod
    def replace_placeholder(cls, txt, block, literal=True):
        """Kui txt sisaldab ploki kohta, siis asendatakse see plokiga.
        Muidu pannakse uus plokk txt lõppu ning nende vahele kindel reavahetus.
        """
        pattern = r'<img [^>]*class="metablock"[^>]*/?>'
        m = re.search(pattern, txt)
        if m:
            # asendame ploki koha uue plokiga
            return txt[:m.start()] + block + txt[m.end():]
        else:
            # lisame lõppu
            return txt + block

    @classmethod
    def draw_hotspots(cls, sisuobjekt, filedata, valikud):
        """Piltülesande taustapildil piirkondade joonistamine taustapildi sisse.
        Kasutatakse HTML eksportimisel.
        valikud = sisuobjekt.sisuplokk.kysimus.valikud
        """
        def _draw_shape(draw, shape, pt_file, color):
            if shape == 'ellipse' or shape == 'circle':
                draw.ellipse(pt_file, outline=color)
            elif shape == 'rect':
                # x1 must be greater than or equal to x0
                # y1 must be greater than or equal to y0
                li_x = [x for (x,y) in pt_file]
                li_y = [y for (x,y) in pt_file]
                pt = [(min(li_x), min(li_y)), (max(li_x), max(li_y))]
                draw.rectangle(pt, outline=color)
            elif shape == 'poly':
                draw.polygon(pt_file, outline=color)                                                    
        def coords_to_list(koordinaadid):
            # koordinaadid on EISis kujul "[[x1,y1],[x2,y2]]"
            # teeme listiks [(x1,y1),(x2,y2)]
            li = []
            for point in re.findall(r'\[([^\[\]]+)\]', koordinaadid):
                x, y = point.split(',')
                li.append((float(x),float(y)))
            return li

        mimetype = sisuobjekt.mimetype or 'image/png'
        try:
            im = Image.open(BytesIO(filedata))
        except:
            # võib-olla SVG (PIL.UnidentifiedImageError),
            # tagastame algse pildi, piirkondi peale ei joonista
            return filedata, mimetype
        
        # leiame kordajad, millega tuleks piirkondade koordinaadid korrutada
        (laius_orig, korgus_orig) = im.size
        x_kordaja = sisuobjekt.laius and float(laius_orig)/sisuobjekt.laius or None
        y_kordaja = sisuobjekt.korgus and float(korgus_orig)/sisuobjekt.korgus or None
        x_kordaja = x_kordaja or y_kordaja or 1
        y_kordaja = y_kordaja or x_kordaja or 1

        if im.getpalette():
            # et _draw_shape() ei annaks viga "invalid literal for int() with base 10" (vt allpool)
            # ja et im.save() ei annaks viga "cannot write mode P as JPEG"
            im = im.convert('RGBA')

        draw = ImageDraw.Draw(im)
        
        color = "rgb(0,0,255)" # võetakse üks värv piirkonna joonistamiseks
        for v in valikud or []:
            if v.row_type == const.CHOICE_HOTSPOT:
                # v.is_valikupiirkond
                if v.nahtamatu:
                    continue
                # leiame koordinaadid EISi kasutatavas mõõdus
                pt_screen = coords_to_list(v.nimi)
                
                if v.kujund == 'poly':
                    if len(pt_screen) < 2:
                        log.debug('Valikupiirkond %d: polygooni jaoks pole koordinaate' % v.id)
                        continue
                else:
                    if len(pt_screen) != 2:
                        log.debug('Valikupiirkond %d: peab olema 2 punkti koordinaadid' % v.id)
                        continue
                # leiame koordinaadid faili originaalmõõdus
                pt_file = [(p[0] * x_kordaja, p[1] * y_kordaja) for p in pt_screen] 
                # joonistame kujundid pildile peale
                try:
                    _draw_shape(draw, v.kujund, pt_file, color)
                except ValueError:
                    # võib anda vea: 
                    # ValueError: invalid literal for int() with base 10: '\x1f'
                    # siis loodame, et paleti värv 0 on piisavalt kena
                    _draw_shape(draw, v.kujund, pt_file, 0)

        del draw
        f = BytesIO()
        fileext = _pil_ext(sisuobjekt.fileext)

        try:
            im.save(f, fileext)
        except OSError as ex:
            # cannot write mode RGBA as JPEG
            # asendame nähtamatu värvi valgega
            fill_color = '#ffffff'
            background = Image.new(im.mode[:-1], im.size, fill_color)
            background.paste(im, im.split()[-1])
            im = background
            im.save(f, fileext)
            
        f.seek(0)
        return f.read(), mimetype

def _pil_ext(ext):
    if ext.upper() in ('XBM','PCX','MSP','HD5','TIFF','BUFR','EPS','PPM','GIF','TGA','IM','JPEG','PDF','PNG'):
        return ext
    elif ext.upper() == 'JPG':
        return 'JPEG'
    else:
        return 'PNG'

def ks_sisu_ksmarkustega(kv, ks_seq, buf, on_hindamine, hindamine):
    "Sisu, millesse on lisatud hindajate kommentaarid"

    if not buf:
        return buf

    monda_naeb_sooritaja = False
    hitems = []
    q = (model.Session.query(model.Ksmarkus)
         .filter_by(kysimusevastus_id=kv.id)
         .filter_by(seq=ks_seq)
         .order_by(model.Ksmarkus.seq))
    for ksm in q.all():
        # leiame sama vastuse
        # ylesandehinne puudub siis, kui on automaatse tekstianalyysi kirje
        yhinne = ksm.ylesandehinne
        ksm_h = yhinne and yhinne.hindamine
        if ksm_h:
            if ksm_h.tyhistatud:
                # tyhistatud hindamiste märkusi ei kuva
                continue
            if ksm_h.ksm_naeb_sooritaja and ksm_h.staatus == const.H_STAATUS_HINNATUD:
                monda_naeb_sooritaja = True
        # Testimiskorrata lahendamisel:
        # - sooritaja näeb lõpetatud hindamiste märkusi, mis on sooritajale lubatud
        # - hindaja näeb märkusi, mis on hindajatele nähtavad või enda tehtud
        # Testimiskorraga lahendamisel:
        # - sooritaja näeb lõpetatud hindamiste märkusi, mis on sooritajale lubatud, kui Seade on sees
        # - hindaja näeb märkusi, mis on hindajatele nähtavad (ja Seade sees) või enda tehtud
        # - eksperthindamine ja eksperthindamise vaataja näevad kõiki märkusi

        show = False
        if not ksm_h:
            # estnltk märgitud viga kuvatakse kõigile
            show = True
        elif on_hindamine:
            if not hindamine or hindamine.liik >= const.HINDAJA4:
                # eksperthindamise vaatamine või eksperthindamine
                show = True
            elif hindamine.id == ksm_h.id:
                # hindaja näeb enda tehtud märkusi
                show = True
            elif ksm_h.ksm_naeb_hindaja:
                # hindaja näeb teise hindaja tehtud märkusi
                show = True
        else:
            # sooritaja näeb hinnatud märkusi, kui on lubatud
            if ksm_h.ksm_naeb_sooritaja and ksm_h.staatus == const.H_STAATUS_HINNATUD:
                show = True
        if show:
            li = loads(ksm.markus)
            hitems.append((li, ksm_h))

    if not on_hindamine and not monda_naeb_sooritaja:
        # kui hindajate märkusi ei või vaadata, siis ei luba sooritajale
        # ka automaatset tekstianalyysi
        hitems = []
        
    return sisu_ksmarkustega(buf, hitems)

def sisu_ksmarkustega(buf, hitems):
    "Sisu, millesse on lisatud hindajate kommentaarid"
    # hitems on jada elementidest (markused, hindamine)
    
    # markused sisaldab selliseid ridu:
    # (offset, mtype, text)
    # või
    # (offset, mtype, text, length, color, bgcolor)
    # kus:
    # - offset - märkuse alguse indeks vastuse originaaltekstis
    # - mtype - märkuse tüüp 
    # - text - sisu (ainult kommentaari korral)
    # - length - märgistatud sõna pikkus alates offset (sõnakorduste korral)
    # - color - sõna värv (sõnakorduste korral)
    # - bgcolor - tausta värv

    # MÄRKUSE TÜÜP

    # EstNLTK metaandmete tüüp, juures on analyysitulemuste dict:
    # - meta
    # Käsitsi märgitavad tüübid:
    #  - I
    #  - p
    #  - X
    #  - V
    #  - L
    #  - S
    #  - typo
    #  - Z
    # EstNLTK leitud ortograafiaviga:
    # - auto
    # EstNLTK leitud ja hindaja poolt muudetud viga:
    # - TÜÜP,auto
    # Vanad tüübid:
    # - orthography
    # - interpunktion
    # - meaning
    # - questionable
    # - missing
    # - indent
    # Käsitsi märgitav kommentaar, sisaldab teksti:
    # - text
    # EstNLTK märkused, kuvatakse ikoon:
    # - autoorthography
    # EstNLTK märkused, kuvatakse värvitult:
    # - rpt1 (sõna kordub lause sees)
    # - rpt2 (sõna kordub järjestikustes lausetes)
    # Käsitsi tehtud märge EstNLTK vea valeks tunnistamiseks:
    # - rm

    buf = str(buf) # kui enne tehti h.escape(), siis on vaja
    # eemaldame CR, sest CKEditoris märkuse offseti arvestades neid ei arvestata
    buf = buf.replace('\r','')

    # nende EstNLTK leitud vigade offsetid, mida hindaja on muutnud ja mida ei peaks originaalis kuvama
    rm_auto_offsets = []
    # märkuste loetelu
    items = []
    for li, hindamine in hitems:
        if hindamine:
            # käsitsi loodud märkused
            autor_nimi = hindamine.hindaja_kasutaja.nimi
            hindamine_id = hindamine.id
        else:
            # automaatselt loodud märkused
            autor_nimi = hindamine_id = 'EstNLTK'

        for r in li:
            if r[1] != 'meta':
                offset, mtype, text = r[:3]
                if not mtype:
                    # imelik
                    continue
                length = 0
                color = bgcolor = None
                if len(r) > 3:
                    length = r[3]
                    color = r[4]
                if len(r) > 5:
                    bgcolor = r[5]
                if hindamine and 'auto' in mtype:
                    # EstNLTK leitud viga, mille hindaja on kustutanud või muutnud
                    # kuvatakse nii, nagu hindaja on soovinud
                    rm_auto_offsets.append(offset)
                elif mtype not in ('rpt1','rpt2'):
                    # ainult kordusi kuvame värvilise tekstiga,
                    # sest kirjavigu märgib ka hindaja ja teeb seda ikooniga
                    length = 0
                if length:
                    # lisame lõpu
                    items.append((offset + length, -1, 'END', None, None, None, None, None))
                items.append((offset, length, mtype, text, autor_nimi, hindamine_id, color, bgcolor))

    if rm_auto_offsets:
        # eemaldame need EstNLTK vead, mida hindaja on muutnud
        items = [r for r in items if not (r[0] in rm_auto_offsets and r[5] == 'EstNLTK')]
                
    # järjestame märkused tagantpoolt ettepoole
    sorted_items = sorted(items, key=lambda r: (0-r[0], 0-r[1]))

    for offset, length, mtype, text, autor_nimi, hindamine_id, color, bgcolor in sorted_items:
        # spani klass

        # vanad vealiigid, millel on uued vasted
        if mtype == 'orthography':
            mtype = 'I'
        elif mtype == 'interpunktion':
            mtype = 'p'
        elif mtype == 'autoorthography':
            mtype = 'auto'

        # kas on EstNLTK leitud viga ja/või kas on korduv viga
        is_auto = is_recurrent = False
        li1 = mtype.split(',')
        mtype = li1[0]
        if li1[0] == 'auto':
            # EstNLTK viga, mida pole muudetud
            is_auto = True
            # vaikimisi on ortograafiaviga
            mtype = 'I'
        else:
            mtype = li1[0]
            # kas on muudetud EstNLTK viga
            is_auto = 'auto' in li1
            # kas on korduv viga
            is_recurrent = 'recurrent' in li1
            
        mcls = f'mcomment mcomment-{mtype}'
        if is_recurrent:
            mcls += ' mcomment-recurrent'
        if is_auto:
            mcls += ' mcomment-auto'
            
        if mtype in ('I','p','X','V','L','S','typo','Z','auto','rm',
                     # vanad vealiigid:
                     'autoorthography',
                     'orthography',
                     'interpunktion',
                     'meaning',
                     'indent',
                     'questionable',
                     'missing'):
            mcls += ' mcomment-icon'

        if mtype == 'END':
            # eristatud sõna lõpp
            spn = '</span>'
        elif length > 0:
            # eristamise algus
            spn = f'<span class="{mcls}" data-offset="{offset}"' +\
                f' data-author="{autor_nimi}" data-h_id="{hindamine_id}" data-color="{color}">'
        else:
            # teksti vahele lisatud märkus
            spn = f'<span class="{mcls}" data-offset="{offset}"'
            if bgcolor:
                spn += f' style="background-color:{bgcolor}"'
            spn += f' data-author="{autor_nimi}" data-h_id="{hindamine_id}">{text}</span>'

        end_tag = buf[offset:].find('>')
        start_tag = buf[offset:].find('<')
        if -1 < end_tag < start_tag:
            # positsioon on sassis, viitab sildi sisse
            log.debug(f'ksmarkus vigane pos {offset}')
            offset += end_tag + 1
        buf = buf[:offset] + spn + buf[offset:]
    return buf
    
