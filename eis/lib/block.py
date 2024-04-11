"""Ülesannete sisuplokkide pseudokontrollerid.
Eri tüüpi sisuplokkide koostamine ja kasutamine.
"""

from lxml import etree
from lxml.builder import E
import urllib.parse
from io import BytesIO
import html
import json
import pickle
import formencode
import base64
import html.parser
import mimetypes
import requests
from eis.lib.base import *
from eis.lib.basegrid import BaseGridController
_ = i18n._
import eis.lib.helpers as h
from eis.forms import validators
from eis.lib.formulaenv import FormulaEnv
from eis.lib.testsaga import TestSaga
log = logging.getLogger(__name__)

class BlockController(object):
    "Ühele sisuplokile vastav objekt"
    
    @classmethod
    def get(cls, block, ylesanne, handler):
        """Sisuploki sidumine oma tüübile vastava kontrolleriga.
        block 
           sisuploki mudeli objekt
        handler
           päriskontroller (handler)
        """
        clsname = '_' + block.type_name + 'Controller'
        ctrl = eval(clsname)(handler)
        ctrl.block = block
        ctrl.ylesanne = ylesanne
        block.ctrl = ctrl
        return ctrl

    @classmethod
    def after_copy_task(cls, ylesanne, handler):
        """Peale ylesande kopeerimist või importimist võib olla vaja
        muuta sisuploki teksti sisu (nt sisuploki ID)
        """
        ylesanne.lukus = None
        keeled = ylesanne.keeled
        for sp in ylesanne.sisuplokid:
            cls.after_copy_block(ylesanne, sp, keeled, handler)
            
    @classmethod
    def after_copy_block(cls, ylesanne, sp, keeled, handler):
        """Peale sisuploki kopeerimist või importimist võib olla vaja
        muuta sisuploki teksti sisu (nt sisuploki ID)
        """
        ctrl = BlockController.get(sp, ylesanne, handler)
        if sp.tyyp in (const.INTER_HOTTEXT,
                       const.INTER_INL_TEXT,
                       const.INTER_GAP,
                       const.INTER_COLORTEXT):
            for lang in keeled:
                if lang != ylesanne.lang:
                    ctrl.lang = lang
                    is_tr = True
                else:
                    ctrl.lang = None
                    is_tr = False
                sisu, tree = ctrl.parse_sisu()
                if tree is not None:
                    ctrl._update_sisuvaade(tree, is_tr=is_tr, is_import=True)
        ctrl.set_valikvastused()

    def set_valikvastused(self):
        """Valikvastuse tabelisse kirjutatakse sisuploki tyybist sõltuvalt
        viited kysimustele, mille valikute koode vastustes kasutatakse.
        """
        pass

    def _set_valik_max_p(self, valikuhulk, tulemus, limxn, k_max_v, max_v_by_mx={}):
        "Paar-vastuste korral: märgime iga valiku juurde, mitu palli selle valikuga seotud paarid kokku võivad anda"
        # limxn on list elementidest (maatriksi jrk nr, koodi jrk nr (1/2))
        hms_map = {}
        for hm in tulemus.hindamismaatriksid:
            for mx, n in limxn:
                if hm.maatriks == mx:
                    if n == 1:
                        kood = hm.kood1
                    else:
                        kood = hm.kood2
                    if kood in hms_map:
                        hms_map[kood].append(hm)
                    else:
                        hms_map[kood] = [hm]

        for v in valikuhulk.valikud:
            hms = hms_map.get(v.kood) or []
            hms.sort(reverse=True, key=lambda hm: hm.pallid)

            # valiku max vastuste arv või kysimuse max vastuste arv, kumb on väiksem
            max_v = v.max_vastus
            if k_max_v is not None and (max_v is None or max_v > k_max_v):
                max_v = k_max_v
            _max_v_by_mx = max_v_by_mx.copy()
            
            max_p = 0
            n = 0
            log.debug('Valik %s (max_v=%s), %d rida' % (v.kood, max_v, len(hms)))
            for hm in hms:
                # kas maatriksil on oma max_v ?
                mx_max_v = _max_v_by_mx.get(hm.maatriks)
                if mx_max_v is not None:
                    if mx_max_v == 0:
                        # sellest maatriksist rohkem vastuseid ei või arvestada
                        log.debug('  mx %d täis' % (hm.maatriks))
                        continue
                    else:
                        _max_v_by_mx[hm.maatriks] -= 1
                log.debug('   lisab %s (mx %d)' % (hm.pallid, hm.maatriks))
                max_p += hm.pallid
                if max_v is not None:
                    max_v -= 1
                    if max_v == 0:
                        # max vastuste arv on täis
                        log.debug('   max vastuste arv täis')
                        break

            # valiku max pallid on arvutatud
            v.max_pallid = max_p

    def gen_selgitused(self, overwrite):
        """Statistikute jaoks valikute selgituste genereerimine
        """
        for kysimus in self.block.kysimused:
            for valik in kysimus.valikud:
                if valik.nimi and (overwrite or not valik.selgitus):
                    if kysimus.rtf:
                        selgitus = _html2txt(valik.nimi)
                    else:
                        selgitus = valik.nimi
                    valik.selgitus = selgitus[:255]

    def __init__(self, handler):
        self.lang = None # tõlkekeel
        self.handler = handler # pyramidi handler
        if handler:
            self.request = handler.request
            self.c = handler.c # andmete hoiustamise objekt c
            if handler.form:
                self.form_result = handler.form.data # postitatud andmed

    def edit(self):
        """Sisuploki koostamine
        """
        template = '/sisuplokk/%s.mako' % self._TEMPLATE_NAME
        self.c.block = self.block
        self.c.is_sp_edit = True
        self._edit()
        return self.handler.render(template)

    def view(self):
        """Sisuploki kuvamine ülesande lahendamisel
        """
        template = '/sisuplokk/%s.mako' % self._TEMPLATE_NAME
        self.block.read_only = self.c.read_only or self.block.naide
        self.block.prepare_response = self.c.prepare_response or self.block.naide
        self.c.block = self.block
        
        self.c.is_sp_view = True
        self.c.is_sp_view_js = False
        self._view()
        html = self.render_with_prompt(template)
        self.c.is_sp_view = False
        self.c.is_sp_view_js = True
        js = self.handler.render(template)
        return html, js
    
    def analysis(self):
        """Sisuploki vastuste analüüsimine
        """
        template = '/sisuplokk/%s.mako' % self._TEMPLATE_NAME
        self.block.read_only = self.c.read_only or self.block.naide
        self.block.prepare_response = self.c.prepare_response or self.block.naide
        self.c.block = self.block
        self.c.is_sp_analysis = True        
        self._view()
        return self.handler.render(template)

    def view_print(self, exporter=None):
        """Sisuploki kuvamine ainult vaatamiseks või printimiseks
        (HTML-eksportimiseks)
        """
        if exporter:
            self._export_files(exporter)

        template = '/sisuplokk/%s.mako' % self._TEMPLATE_NAME
        self.c.block = self.block
        self.c.is_sp_print = True
        self._view()
        return self.render_with_prompt(template)

    def preview(self):
        """Sisuploki kuvamine sisu koostamise lehel vaatamiseks
        """
        template = '/sisuplokk/%s.mako' % self._TEMPLATE_NAME
        self.c.block = self.block
        self.c.is_sp_preview = True
        self._view()
        return self.render_with_prompt(template)

    def entry(self, is_correct):
        """Sisuploki kuvamine vastuste sisestamise lehe jaoks
        """
        template = '/sisuplokk/%s.mako' % self._TEMPLATE_NAME
        self.c.block = self.block
        self.c.is_sp_entry = True
        self.c.is_correct = is_correct
        return h.literal(self.handler.render(template))

    def _export_files(self, exporter):
        exporter.export_obj(self.block.taustobjekt)
        exporter.export_obj(self.block.meediaobjekt)
        for obj in self.block.piltobjektid:
            exporter.export_obj(obj)

    def render_with_prompt(self, template):
        """Sisuploki kuvamine koos pealdisega.
        """
        return h.literal(self.handler.render(template))

    def _edit(self):
        pass

    def _view(self):
        pass

    def include_edit(self):
        """Milliseid CSS ja JS faile on vaja laadida koostamise vaates
        """
        pass

    def include_view(self):
        """Milliseid CSS ja JS faile on vaja laadida lahendamise vaates
        """
        pass

    def update(self, is_tr, not_locked):
        """Sisuploki muudatuste salvestamine
        is_tr - toimub tõlkimine (ei saa muuta mittetekstilisi andmeid)
        not_locked - ülesande sisu pole lukus (saab muuta ülesande sisu)
           kui not_locked=True, siis saab ainult hindamismaatriksit muuta
        """
        pass

    def _update_choices(self, kysimus=None, rootdiv=True):
        """Valikute salvestamine.
        """
        if kysimus is None:
            kysimus = self.block.kysimus
        v = self.form_result['v']
        self._unique_kood(v, 'v')
        rtf_old = self.form_result.get('v_rtf_old')
        kysimus.rtf = self.form_result.get('v_rtf')
        if rtf_old and not kysimus.rtf:
            self._remove_rtf(kysimus, v)

        ylesanne = self.ylesanne
        # kasutajaliideses määratakse sisuplokid prefiksiga sp-
        # hiljem failis ichoice.mako lisatakse ette tegelik prefix eis-
        sp_tahised = ['sp-%s' % (sp.tahis or sp.seq) for sp in ylesanne.sisuplokid]

        errors = {}
        if kysimus.rtf:
            for ind, r in enumerate(v):
                err = self._check_img_urls(r['nimi'], ylesanne.id)
                if err:
                    errors['v-%s.nimi' % ind] = err

        BaseGridController(kysimus.valikud, model.Valik).save(v)

        def rmspace(value):
            if value:
                return value.replace(' ', '') or None
            
        for ind, v in enumerate(kysimus.valikud):
            v.kysimus = kysimus

            v.kohustuslik_kys = rmspace(v.kohustuslik_kys)
            v.sp_kuva = rmspace(v.sp_kuva)
            v.sp_peida = rmspace(v.sp_peida)

            if v.kohustuslik_kys:
                for k_kood in v.kohustuslik_kys.split(','):
                    k = ylesanne.get_kysimus(kood=k_kood)
                    err = None
                    if not k:
                        err = _("Küsimust {s} ei ole olemas").format(s=k_kood)
                    elif k.sisuplokk.tyyp not in (const.INTER_TEXT,
                                                  const.INTER_EXT_TEXT,
                                                  const.INTER_INL_TEXT,
                                                  const.INTER_HOTTEXT,
                                                  const.INTER_CHOICE):
                        err = _("Küsimus {s} on sellist liiki sisuplokis, mida ei saa valikuga kohustuslikuks muuta").format(s=k_kood)
                    if err:
                        errors['v-%s.kohustuslik_kys' % ind] = err
            if v.sp_peida:
                for sp_tahis in v.sp_peida.split(','):
                    if sp_tahis not in sp_tahised:
                        errors['v-%s.sp_peida' % ind] = _("Sisuplokki {s} ei ole").format(s=sp_tahis)
            if v.sp_kuva:
                for sp_tahis in v.sp_kuva.split(','):
                    if sp_tahis not in sp_tahised:
                        errors['v-%s.sp_kuva' % ind] = _("Sisuplokki {s} ei ole").format(s=sp_tahis)
        if errors:
            self._raise_error(errors)

    def _tran_update_choices(self, kysimus=None, rootdiv=True):
        """Valikute salvestamine tõlkimise resiimis.
        """
        if kysimus is None:
            kysimus = self.block.kysimus
        v = self.form_result['v']
        errors = {}

        if kysimus.rtf:
            ylesanne = self.ylesanne
            for ind, r in enumerate(v):
                nimi = r.get('nimi')
                if nimi:
                    # väli puudub siis, kui ylesanne on lukus
                    err = self._check_img_urls(nimi, ylesanne.id)
                    if err:
                        errors['v-%s.nimi' % ind] = err
        if errors:
            self._raise_error(errors)

        BaseGridController(kysimus.valikud, model.Valik).update(v, lang=self.lang)        

    def _unique_kood(self, valikud, prefix, koodid=None):
        """Kontrollitakse, et kõigi valikute koodid oleks unikaalsed.
        """
        if not koodid:
            koodid = []
        errors = {}
        for n, v in enumerate(valikud):
            kood = v['kood']
            if not kood:
                errors['%s-%s.kood' % (prefix, n)] = _("Palun sisestada kood")
            elif kood in koodid:
                errors['%s-%s.kood' % (prefix, n)] = _("Pole unikaalne")
            else:
                koodid.append(kood)

        if errors:
            self._raise_error(errors)

    def _valik_selgitus(self, valikud, rtf):
        """Selgituse puudumisel kopeeritakse nimetus selgituseks
        """
        for n, v in enumerate(valikud):
            selgitus = v.get('selgitus')
            if not selgitus:
                nimi = v['nimi']
                if rtf:
                    nimi = _html2txt(nimi)
                v['selgitus'] = nimi[:255]

    def _raise_error(self, errors, message=None):
        """Visatakse erind, mis pyytakse päris-kontrolleris kinni.
        """
        if not message:
            message = _("Palun kõrvaldada vead")
        raise ValidationError(self.handler, errors, message)
    
    def _update_hotspots(self, kysimus):
        """Piltülesande piirkondade salvestamine.
        """
        hs = self.form_result['hs']
        self._unique_kood(hs, 'hs')
        BaseGridController(kysimus.valikud, model.Valikupiirkond).\
            save(hs)

    def _update_hotspots_x(self, kysimus, mo):
        """Piltülesande piirkondade salvestamine, automaatselt lisatakse määramata piirkond.
        """
        hs = self.form_result['hs']
        # lisame automaatselt ylejäänud ala piirkonna
        item_x = None
        for v in kysimus.valikud:
            if v.kood == const.VALIK_X:
                item_x = v
                break
        row_x = {'id': item_x and item_x.id or None}
        row_x['kood'] = const.VALIK_X
        row_x['koordinaadid'] = '[[0,0],[%d,%d]]' % (mo.laius, mo.korgus)
        row_x['kujund'] = 'rect'
        row_x['nahtamatu'] = True
        row_x['selgitus'] = _("Määramata ala")
        hs_x = [row_x]
        koodid = [const.VALIK_X]

        self._unique_kood(hs, 'hs', koodid)
        hs = hs + hs_x
        for ind, row in enumerate(hs):
            row['seq'] = ind
        BaseGridController(kysimus.valikud, model.Valikupiirkond).\
            save(hs)

    def _update_tulemus(self, kysimus, tulemus, basetype=None, cardinality=None, prefix='am1', am=None):
        """Küsimuse tulemuse salvestamine hindamismaatriksi vormilt
        """
        kysimus.kood = tulemus.kood = am['kood']
        tulemus.from_form(am)
        if tulemus.yhisosa_kood == '':
            tulemus.yhisosa_kood = None
        kysimus.from_form(am, 'k_')
        if tulemus.oigsus_kysimus_id:
            tulemus.arvutihinnatav = True
        if tulemus.min_sonade_arv and not (tulemus.arvutihinnatav or tulemus.hybriidhinnatav):
            tulemus.hybriidhinnatav = True
        if basetype:
            tulemus.baastyyp = basetype
        if tulemus.baastyyp not in (const.BASETYPE_STRING, const.BASETYPE_MATH):
            tulemus.ladinavene = None
        if cardinality:
            tulemus.kardinaalsus = cardinality
        return tulemus
    
    def _update_mapping(self, kysimus, basetype=None, cardinality=None, prefix='am1', am=None, hm_key='hm1', copy_from_t=None, tulemus=None, is_hm=True):
        """Küsimuse hindamismaatriksi salvestamine
        """
        if not am:
            # am on hindamismaatriksi väljad
            ylesanne = self.ylesanne
            am = self.form_result.get(prefix)
            if not am:
                if not kysimus.kood:
                    kysimus.kood = ylesanne.gen_kysimus_kood()
                am = {'kood': kysimus.kood}
                is_hm = False

        if not tulemus:
            tulemus = kysimus.give_tulemus()
        if copy_from_t:
            # kopeeritakse maatriksi ridade väärtused teiselt kysimuselt
            self._copy_hm(tulemus, copy_from_t)
            return tulemus

        valem_old = tulemus.valem
        self._update_tulemus(kysimus, tulemus, basetype, cardinality, prefix, am)

        if is_hm:
            # salvestatakse maatriks
            html2txt = False
            self._save_hm(kysimus, tulemus, basetype, cardinality, prefix, am, hm_key, html2txt, valem_old)
            # arvutame yle, kui palju palle on võimalik saavutada
            tulemus.calc_max_pallid()
        return tulemus
    
    def _copy_hm(self, tulemus, tulemus1):
        "Kopeeritakse tulemus1 hindamismaatriksi ridade väärtused tulemus hindamismaatriksisse"
        # kui samal positsioonil olev rida on olemas, siis punkte ei muudeta
        # ridu ei kustutata
        hms = list(tulemus.hindamismaatriksid)
        for indh, hm1 in enumerate(tulemus1.hindamismaatriksid):
            if indh < len(hms):
                hm = hms[indh]
                hm.kujund = hm1.kujund
                hm.koordinaadid = hm1.koordinaadid
                hm.selgitus = hm1.selgitus
                hm.sallivus = hm1.sallivus
                hm.tahis = hm1.tahis
            else:
                hm = hm1.copy(jrk=indh, tulemus_id=tulemus.id)
                tulemus.hindamismaatriksid.append(hm)

    def _save_hm(self, kysimus, tulemus, basetype, cardinality, prefix, am, hm_key, html2txt, valem_old, copy_from_t=None):
        if copy_from_t:
            # kopeeritakse maatriksi ridade väärtused teiselt kysimuselt
            self._copy_hm(tulemus, copy_from_t)
            return
        
        # hindamismaatriksi read
        if hm_key == 'hmx':
            # mitme hindamismaatriksi võimalus
            hmx = am.get(hm_key)
            max_maatriks = tulemus.maatriksite_arv or 1
            collection = []
            for m_cnt, hm1 in enumerate(hmx):
                if m_cnt < max_maatriks:
                    maatriks = m_cnt + 1
                    collection2 = hm1.get('hm')
                    if collection2:
                        m_prefix = '%s.hmx-%d.hm' % (prefix, maatriks)
                        self._unique_map_entry(collection2, m_prefix, tulemus, kysimus)
                        for rcd in collection2:
                            rcd['maatriks'] = maatriks
                            collection.append(rcd)
        elif basetype == const.BASETYPE_POINT or basetype == const.BASETYPE_POLYLINE:
            collection = am.get('hs')
            self._unique_area_map_entry(collection, '%s.hs' % prefix)
        elif basetype == const.BASETYPE_IDLIST:
            # hm_key == 'ht'
            collection = am.get(hm_key)            
        else:
            # hindamismaatriks
            collection = am.get(hm_key)
            self._unique_map_entry(collection, '%s.%s' % (prefix, hm_key), tulemus, kysimus)
            if not (kysimus.rtf and not tulemus.valem):
                # seadistatud on tavaline tekst; kontrollime, kas varem oli kirev tekst
                try:
                    rtf_old = kysimus.rtf_old
                except:
                    rtf_old = False
                if rtf_old and not valem_old:
                    # kireva teksti asendamine tavalisega
                    html2txt = True

        BaseGridController(tulemus.hindamismaatriksid, 
                           model.Hindamismaatriks).\
                           save(collection, delete_hidden=True)

        if html2txt:
            # kireva teksti asendamine tavalisega
            for r in tulemus.hindamismaatriksid:
                r.kood1 = _html2txt(r.kood1)

        # yksikvastuse max pallid
        pallid = self._calc_max_pallid_vastus(tulemus)
        
        # mõned kontrollid
        if tulemus.max_pallid is not None and tulemus.arvutihinnatav and (len(tulemus.hindamismaatriksid) > 0) and pallid:
            if cardinality == const.CARDINALITY_SINGLE:
                max_pallid = max(pallid)
                if max_pallid < tulemus.max_pallid:
                    msg = _("Hindamismaatriksi järgi on võimalik max {d} palli").format(d=max_pallid)
                    self._raise_error({'%s.max_pallid' % prefix:msg})
            if tulemus.min_oige_vastus:
                oigete_vastuste_arv = len([r for r in pallid if r > 0])
                if oigete_vastuste_arv < tulemus.min_oige_vastus:
                    msg = _("Hindamismaatriksis on ainult {n} õiget vastust").format(n=oigete_vastuste_arv)
                    self._raise_error({'%s.min_oige_vastus' % prefix:msg})

    def _calc_max_pallid_vastus(self, tulemus):
        "Leitakse yksikvastuse max p, mille järgi vastus roheliseks värvida"
        pallid = [r.get_pallid() for r in tulemus.hindamismaatriksid \
                  if r not in model.Session.deleted]
        # yksikvastuse max pallide arv
        tulemus.max_pallid_vastus = pallid and max(pallid) or None
        return pallid
    
    def _tran_update_mapping(self, kysimus, basetype=None, cardinality=None, prefix='am1'):
        """Hindamismaatriksi salvestamine tõlkimisel.
        Peaks saama muuta ainult vastuseid, mitte palle.
        """
        am = self.form_result.get(prefix)
        tulemus = kysimus.give_tulemus()
        if 'naidisvastus' in am:
            tulemus.give_tran(self.lang).naidisvastus = am['naidisvastus']
        if basetype == const.BASETYPE_POINT:
            collection = am.get('hs')
            m_prefix = '%s.hs' % prefix
        else:
            collection = am.get('hm1')
            m_prefix = '%s.hm1' % prefix
            
        errors = {}
        # tõlkimise korral on pallid hidden väljadel olemas selleks, et
        # inline väljade korral saaks dialoogiaken koostada ckeditori sisse välja htmli
        # aga me ignoreerime neid palle siin
        for n, rcd in enumerate(collection):
            msg = self._unique_map_entry_row(rcd, tulemus, kysimus, is_tran=True)
            kood1_rtf = rcd.get('kood1_rtf')
            if kood1_rtf:
                rcd['kood1'] = kood1_rtf
            if 'pallid' in rcd:
                del rcd['pallid']
            if 'oige' in rcd:
                del rcd['oige']
            if msg:
                errors['%s-%s.kood1' % (m_prefix, n)] = msg

        if errors:
            self._raise_error(errors)
            
        BaseGridController(tulemus.hindamismaatriksid, 
                           model.Hindamismaatriks).\
                           update(collection, lang=self.lang)
        return

    def _unique_map_entry_row(self, v, tulemus, kysimus, is_tran=False):
        "Lisakontroll maatriksireale, tagastab veateate või None"
        return None
    
    def _unique_map_entry(self, valikud, prefix, tulemus, kysimus):
        """Kontrollitakse hindamismaatriksi ridade väärtuste kõlblikkust.
        """
        koodid = []
        errors = {}
        baastyyp = tulemus.baastyyp
        valem = tulemus.valem
        for n, v in enumerate(valikud):
            if v.get('deleted'):
                continue
            try:
                ind = v['_arr_ind']
            except:
                ind = n
            msg = self._unique_map_entry_row(v, tulemus, kysimus)
            kood1_rtf = v.get('kood1_rtf')
            if kood1_rtf:
                kood1 = v['kood1'] = kood1_rtf
            else:
                kood1 = v.get('kood1')
            kood2 = v.get('kood2')

            if not tulemus.lubatud_tyhi and not kood1:
                msg = _("Palun sisestada väärtus")

            if v['pallid'] is None:
                v['pallid'] = 1

            if valem and baastyyp in (const.BASETYPE_INTEGER, const.BASETYPE_FLOAT, const.BASETYPE_STRING):
                e_locals = dict()
                ylesanne = self.ylesanne
                for t in ylesanne.tulemused:
                    if t.kood != tulemus.kood and t != tulemus:
                        if t.baastyyp in (const.BASETYPE_INTEGER,
                                          const.BASETYPE_FLOAT):
                            e_locals[t.kood] = 1
                        elif t.baastyyp in (const.BASETYPE_STRING,
                                            const.BASETYPE_IDENTIFIER):
                            e_locals[t.kood] = '1'
                        elif t.baastyyp in (const.BASETYPE_PAIR,
                                            const.BASETYPE_DIRECTEDPAIR):
                            e_locals[t.kood] = ('A','B')
                n_kood1, err0, msg, buf1 = model.eval_formula(kood1, e_locals)
                if not msg and kood2:
                    n_kood2, err0, msg, buf1 = model.eval_formula(kood2, e_locals)

            if baastyyp in (const.BASETYPE_INTEGER, const.BASETYPE_FLOAT, const.BASETYPE_MATH):
                # kontrollime, et on arvud või arvude vahemikud
                kood1 = kood1.strip()
                kood2 = kood2.strip()

                if not kood1 and not kood2:
                    # tyhjad vastused
                    kood1 = ''
                    kood2 = None
                    
                elif not valem:
                    n_kood1 = n_kood2 = None
                    if baastyyp == const.BASETYPE_MATH:
                        if kood2:
                            # vahemiku korral kontrollime, et algus ja lõpp oleks arvud
                            try:
                                kood1 = model.fixlatex(kood1)
                                m_kood1 = model.process_sympy(kood1)
                            except:
                                msg = _("Pole arusaadav matemaatiline avaldis")
                            if not msg and not m_kood1.is_number:
                                msg = _("Vahemikku saab kasutada ainult arvude korral")
                            else:
                                try:
                                    n_kood1 = float(m_kood1)
                                except:
                                    msg = _("Vahemikku saab kasutada ainult arvude korral")
                            if not msg:
                                try:
                                    n_kood2 = _float_c(kood2)
                                except:
                                    msg = _("Pole reaalarv")
                            
                    elif baastyyp == const.BASETYPE_INTEGER:
                        try:
                            n_kood1 = int(kood1)
                            if kood2:
                                n_kood2 = int(kood2)
                        except:
                            msg = _("Pole täisarv")
                    else:
                        try:
                            n_kood1 = _float_c(kood1)
                            if kood2:
                                n_kood2 = _float_c(kood2)
                        except:
                            msg = _("Pole reaalarv")

                    if not msg and n_kood2 is not None and n_kood2 < n_kood1:
                        msg = _("Vahemiku algus peab olema väiksem kui lõpp")
                    
                # kui on vahemik, siis salvestame vahemiku lõpu väljale kood2
                valikud[n]['kood1'] = kood1
                valikud[n]['kood2'] = kood2

            elif baastyyp == const.BASETYPE_MATH:
                # eemaldame liigsed tyhikud
                kood1 = v['kood1'] = model.stdlatex(kood1)
                
            v_valem = (valem or v.get('valem')) and True or False
            teisendatav = v.get('teisendatav')
            kood = (kood1, kood2, v_valem, teisendatav)
            if kood in koodid:
                msg = _("Tingimus pole unikaalne")
            elif baastyyp == const.BASETYPE_PAIR and (kood2, kood1, v_valem, teisendatav) in koodid:
                msg = _("Tingimus pole unikaalne")
            else:
                koodid.append(kood)                    

            if msg:
                errors['%s-%s.kood1' % (prefix, ind)] = msg

        if errors:
            self._raise_error(errors)

    def _unique_area_map_entry(self, valikud, prefix):
        """Kontrollitakse piirkonda märkivata hindamismaatriksi ridade kõlblikkust.
        """
        koodid = []
        errors = {}
        for n, v in enumerate(valikud):
            if v.get('deleted'):
                continue
            kood = (v.get('koordinaadid'), v.get('kujund'))
            if kood in koodid:
                errors['%s-%s.koordinaadid' % (prefix, n)] = _("Piirkond pole unikaalne")
            else:
                koodid.append(kood)
            if v['pallid'] is None:
                v['pallid'] = 1
        if errors:
            self._raise_error(errors)

    def _unique_kysimus(self, kysimus, prefix='am1'):
        """Kontrollitakse, et kysimuse kood oleks ylesande piires unikaalne.
        """
        ylesanne = self.ylesanne
        koodid = []
        for rcd1 in ylesanne.sisuplokid:
            for rcd2 in rcd1.kysimused:
                if rcd2.kood == kysimus.kood and rcd2 != kysimus:
                    message = _("Kood {s} on selles ülesandes juba kasutusel.").format(s=kysimus.kood)
                    if prefix:
                        self._raise_error({'%s.kood' % prefix: message})
                    else:
                        self._raise_error({}, message)

        yhisosa_kood = kysimus.tulemus and kysimus.tulemus.yhisosa_kood
        if yhisosa_kood:
            for t in ylesanne.tulemused:
                if t.kood != kysimus.kood and t.yhisosa_kood == yhisosa_kood:
                    message = _("Ühisosa kood {s} on selles ülesandes juba kasutusel.").format(s=yhisosa_kood)
                    if prefix:
                        self._raise_error({'%s.yhisosa_kood' % prefix: message})
                    else:
                        self._raise_error({}, message)                    

    def _update_staatus(self):
        if self.form_result.get('staatus2'):
            # sisuplokk on algselt nähtamatu, togglebutton teeb nähtavaks
            self.block.staatus = const.B_STAATUS_NAHTAMATU
        elif self.block.tyyp in (const.BLOCK_IMAGE, const.BLOCK_CUSTOM, const.BLOCK_MEDIA):
            # nendel tyypidel on linnuke kuvamise kohta
            self.block.staatus = self.form_result.get('staatus') and const.B_STAATUS_KEHTIV or const.B_STAATUS_KEHTETU
        else:
            # linnukest kuvamise kohta ei ole, siis on vaikimisi nähtav
            self.block.staatus = const.B_STAATUS_KEHTIV

    def _update_taustobjekt(self):
        """Taustapildi salvestamine
        """
        t = self.block.taustobjekt
        filedata = self.form_result['mo'].get('filedata')
        if filedata != b'' and filedata is not None and not self.lang:
            # salvestatakse uus fail, tyhistame mõõdud
            t.pikkus = t.laius = None
        mo = self.form_result['mo']
        if mo['laius'] == None and mo['korgus'] == None:
            # toimetamine või tõlkimine (is_tr)
            mo['laius'] = t.laius
            mo['korgus'] = t.korgus
        try:
            t.from_form(self.form_result['mo'], lang=self.lang)
        except IOError as e:
            raise ValidationError(self.handler, 
                                  {'mo.filedata': _("Pole pildifail")})                                        
        if not t.filename:
            raise ValidationError(self.handler, 
                                  {'mo.filedata': _("Fail puudub")})                
        return t
    
    def _update_drag_images(self, images, is_tr):
        """Lohistatavate piltide andmete salvestamine, piltide kustutamine
        Piltide lisamine vt piltobjektid.py
        """
        data = {r['id']: r for r in images}
        for obj in list(self.block.piltobjektid):
            rcd = data.get(obj.id)
            if rcd:
                # muuta
                obj.from_form(rcd, lang=self.lang)
            elif is_tr:
                # kustutada tõlge
                tr_obj = obj.tran(self.lang, False)
                if tr_obj:
                    tr_obj.delete()
            else:
                # kustutada põhikirje
                obj.delete()
                self.block.sisuobjektid.remove(obj)

    def _update_block_kysimus(self):
        k = self.block.kysimus
        k.from_form(self.form_result['l'])
        if k.min_vastus is None:
            k.min_vastus = 1
        if k.rtf and not k.rtf_notshared:
            icons = self.ylesanne.get_ckeditor_icons()
            if 'Maximize' in icons:
                errors = {'l.rtf_notshared': _("Maksimeerimise nupp eeldab nupuriba asumist lahtri sees")}
                self._raise_error(errors)
                
    def _remove_rtf(self, kysimus, params):
        """HTMLi märgendite eemaldamine valikutest, 
        mida varem võib-olla ckeditoriga sisestati.
 
        params
          valikute jada
        """
        pattern = re.compile('(<[^<>]*>)')
        for subitem in params:
            subitem['nimi'] = pattern.sub('',subitem['nimi']).replace('&nbsp;','').strip()

        for v in kysimus.valikud:
            for tr_v in v.trans:
                if not tr_v.ylesandeversioon_id and tr_v.nimi:
                    tr_v.nimi = pattern.sub('',tr_v.nimi).replace('&nbsp;','').strip()

    def parse_sisu(self):
        """Tekstülesandes teksti parsimine XMLi dokumendiks.
        Kui XML on vigane, siis visatakse siit XMLSyntaxError.
        """
        t_block = self.block.tran(self.lang)
        sisu = t_block.sisu
        sisu, tree = self.block.parse_sisu(sisu, True)
        if sisu:
            t_block.sisu = sisu
        return sisu, tree

    def _parse_sisu(self):
        """Tekstülesandes teksti parsimine XMLi dokumendiks ja salvestamine
        """
        t_block = self.block.tran(self.lang)
        sisu, tree = self._parse_rtf(t_block.sisu, 'f_sisu')
        if sisu:
            t_block.sisu = sisu
        return sisu, tree            

    def _parse_rtf(self, sisu, name, rootdiv=True, need_pos=True):
        """Kireva teksti korrektsuse kontroll
        """
        if not sisu:
            return None, None

        # eemaldame zero width space &#8203; mis võib olla kuskilt kopeerides kaasa saadud            
        sisu = sisu.replace('\u200b', '')
        
        if self.handler:
            # asendame pildiviite alguses olevad tyhikud
            sisu = re.sub(r' src="\s+', ' src="', sisu)
            # asendame absoluutsed viited EISi oma serveris olevatele piltidele
            # paistab nagu CKEDITOR asendaks vahel suhtelised URLid absoluutsetega
            u = self.handler.request.url
            host = '/'.join(u.split('/')[:3])
            settings = self.handler.request.registry.settings
            warn = False
            for host in set([host,
                             settings.get('eis.id.url'),
                             settings.get('eis.pw.url')]):
                if host:
                    sisu = re.sub(r' src="%s[^"]*/images[^/]*/' % host, r' src="images/', sisu)
                    sisu = re.sub(r' src="%s[^"]*/shared/' % host, r' src="shared/', sisu)
                    if re.match(r'^[a-z]+://', host):
                        # eemaldame protokolli domeeni eest
                        host = host.split('//', 1)[1]
                    if sisu.find(host) > -1:
                        warn = True
            if warn:
                errors = {name: _("Tekst sisaldab URLi, mis ei pruugi olla lahendajale ligipääsetav")}
                self._raise_error(errors)

            ylesanne_id = self.ylesanne.id
            err = self._check_img_urls(sisu, ylesanne_id)
            if err:
               self._raise_error({name: err})
                              
        try:
            # HTML korrektsuse kontroll
            sisu, tree = self.block.parse_sisu(sisu, rootdiv=rootdiv)
        except Exception as e:
            errors = {name: _("Kireva teksti HTML on vigane") + ' (%s)' % e}
            self._raise_error(errors)
        else:
            # sisu on korras
            if tree is not None:
                changed = False
                
                for field in tree.xpath('//*[@avg]'):
                    # Wordist kopeerides tekib avg atribuut
                    del field.attrib['avg']                    
                    changed = True
                for field in tree.xpath('//*[@f]'):
                    # Wordist kopeerides tekib f atribuut
                    del field.attrib['f']                    
                    changed = True                    

                if need_pos:
                    # et saaks kasutada sisu elementides koordinaate, siis 
                    # lisame juurelemendile position:relative, juhul kui position on seadmata
                    style = (tree.attrib.get('style') or '').strip()
                    if style:
                        # style on olemas, kas ka position?
                        keys = [s.split(':', 1)[0].strip() for s in style.split(';')]
                        if 'position' in keys:
                            # position on seatud, me ei muuda seda
                            need_pos = False
                    if need_pos:
                        # vaja panna position
                        if style and not style.endswith(';'):
                            style += ';'
                        style += 'position:relative;'
                        tree.attrib['style'] = style
                        changed = True
                    
            if changed:
                sisu = _outer_xml(tree)

            # ckeditor kaotab <textarea eest tavalise tyhiku ära
            sisu = sisu.replace(' <textarea', '&nbsp;<textarea')

            return sisu, tree

    def _check_img_urls(self, sisu, ylesanne_id):
        # kontrollime tekstist viidatud piltide olemasolu
        err_urls = []
        for src in re.findall(' src="[^"]+"', sisu or ''):
            url = src.split('"')[1]
            if url.startswith('images/'):
                # sama ylesande juures olev fail
                fn = url.split('/', 1)[1]
                q = (model.SessionR.query(model.Sisuobjekt.id)
                     .join(model.Sisuobjekt.sisuplokk)
                     .filter(model.Sisuplokk.ylesanne_id==ylesanne_id)
                     .filter(model.Sisuobjekt.filename==fn))
                if q.count() == 0:
                    err_urls.append(url)
            elif url.startswith('shared/'):
                # yhine fail
                fn = url.split('/', 1)[1]
                q = (model.SessionR.query(model.Yhisfail.id)
                     .filter(model.Yhisfail.filename==fn))
                if q.count() == 0:
                    err_urls.append(url)
            elif not url.startswith('/static/images/'):
                # ([P] on /static/images/placeholder.gif)
                if url.startswith('//'):
                    # vaikimisi protokolli kasutav URL
                    url = 'https:' + url
                if re.match(r'^[a-z]+://', url):
                    # protokolliga URL
                    kw = {}
                    settings = self.handler.request.registry.settings
                    http_proxy = settings.get('http_proxy')
                    if http_proxy:
                        kw['proxies'] = {'http': http_proxy,
                                         'https': http_proxy,
                                         }
                    try:
                        if not requests.get(url, **kw).ok:
                            err_urls.append(url)
                    except:
                        err_urls.append(url)
                else:
                    # URL oma serverisse, aga vale
                    err_urls.append(url)
        if err_urls:
            return _("Tekstis on vigased URLid: {s}").format(s='\n'.join(err_urls))

    def _check_sisu(self):
        "Kontrollitakse sisus olevad URLid, kõigis ülesande keeltes"
        li = []
        ylesanne = self.ylesanne
        for lang in ylesanne.keeled:
            if lang == ylesanne.lang:
                tr = self.block
            else:
                tr = self.block.tran(lang, False)
            if tr:
                sisu = tr.sisu
                err = self._check_img_urls(sisu, ylesanne.id)
                if err:
                    if lang != ylesanne.lang:
                        err = '[%s] %s' % (lang, err)
                    li.append(err)
        return li

    def _check_valikud_sisu(self, kysimus):
        """Kui küsimus on kireva tekstiga, siis
        kontrollitakse valikute sisus olevad URLid,
        kõigis ülesande keeltes
        """
        li = []
        if kysimus.rtf:
            ylesanne = self.ylesanne
            for valik in kysimus.valikud:
                for lang in ylesanne.keeled:
                    tr = lang == ylesanne.lang and valik or valik.tran(lang, False)
                    if tr:
                        sisu = valik.nimi
                        err = self._check_img_urls(sisu, ylesanne.id)
                        if err:
                            if lang != ylesanne.lang:
                                err = '[%s] %s' % (lang, err)
                            li.append(err)
        return li
    
    def check(self, arvutihinnatav):
        rc = True
        li = []

        # kontrollime, et ei oleks ühes sisuplokis nii arvutihinnatavaid kui ka mitte-arvutihinnatavaid küsimusi
        # (mitte, et see meid segaks, aga kui tuuakse eraldi välja arvuti- ja mitte-arvutihinnatavad punktid,
        # siis võib lahendaja segadusse minna)
        _arvutihinnatav = None
        for k in self.block.kysimused:
            tulemus = k.tulemus
            if tulemus:
                k_arvutihinnatav = bool(tulemus.arvutihinnatav)
                if _arvutihinnatav is None:
                    _arvutihinnatav = k_arvutihinnatav
                elif _arvutihinnatav != k_arvutihinnatav:
                    li.append(_("Sisuplokis on nii arvutihinnatavaid kui ka mitte-arvutihinnatavaid küsimusi"))
                    rc = False
                    break

        return rc, li

    @classmethod
    def check_ylesanne(cls, handler, ylesanne, staatus=None):
        "Ülesande sisu kontroll"
        y_errors = []
        
        k_errors = {}
        def add_k_error(kood, msg):
            if kood in k_errors:
                k_errors[kood].append(msg)
            else:
                k_errors[kood] = [msg]

        k_warnings = {}
        def add_k_warning(kood, msg):
            if kood in k_warnings:
                k_warnings[kood].append(msg)
            else:
                k_warnings[kood] = [msg]

        sp_errors = {}
        def add_sp_error(sp_id, msg):
            if sp_id in sp_errors:
                sp_errors[sp_id].append(msg)
            else:
                sp_errors[sp_id] = [msg]

        keeled = ylesanne.keeled
        has_interaction = False
        k_koodid = set()
        l_tahised = set()
        for cnt, plokk in enumerate(ylesanne.sisuplokid):
            has_interaction |= plokk.is_interaction
            sp_pallid = 0
            plokk_kysimused = list(plokk.kysimused)

            # kysimuste koodide kontroll
            for k in plokk_kysimused:
                if k.kood:
                    t = k.tulemus
                    if k.kood in k_koodid:
                        add_k_error(k.kood, _("Küsimuse kood pole unikaalne"))
                    else:
                        k_koodid.add(k.kood)

                    if t and t in model.Session.deleted:
                        t = None
                    if t:
                        tahised = set([hm.tahis for hm in t.hindamismaatriksid if hm.tahis])
                        l_tahised.update(tahised)
                        if not k.selgitus and handler.c.app_ekk:
                            add_k_warning(k.kood, _("Küsimusel puudub selgitus"))

                        if not t.arvutihinnatav and ylesanne.arvutihinnatav:
                            add_k_error(k.kood, _("Küsimus tuleb märkida arvutihinnatavaks"))
            # sisukysimuste tõlkimise kontroll
            sisukysimused = plokk.get_sisukysimused()
            koodid_orig = set([sk.kood for sk in sisukysimused])

            ctrl = BlockController.get(plokk, ylesanne, handler)
            for err in ctrl.check_tr(keeled, koodid_orig):
                add_sp_error(plokk.id, err)

            rc1, li = ctrl.check(ylesanne.arvutihinnatav)
            for err in li:
                add_sp_error(plokk.id, err)


        lk = [l for l in l_tahised if l in k_koodid]
        if lk:
            err = _("Tabamuste loendur ei tohi olla kasutusel küsimuse koodina (kattuvad koodid {s})").format(s=', '.join(lk))
            y_errors.append(err)

        if not has_interaction:
            stmallid = (const.Y_STAATUS_MALL, const.Y_STAATUS_AV_MALL)
            if staatus not in stmallid:
                err = _("Ülesanne ei sisalda ühtki küsimust")
                y_errors.append(err)

        if y_errors or sp_errors or k_errors:
            rc = False
        else:
            rc = True
        return rc, y_errors, sp_errors, k_errors, k_warnings
    
    def check_tr(self, keeled, koodid_orig):
        "Sisukysimuste tõlkimise kontroll"
        plokk = self.block
        lang_orig = self.ylesanne.lang
        for lang in keeled:
            if lang != lang_orig:
                tr_sisukysimused = plokk.get_sisukysimused(lang=lang)
                koodid = set([sk.kood for sk in tr_sisukysimused])
                puudu = koodid_orig - koodid
                if puudu:
                    s = ', '.join(sorted(list(puudu)))
                    lang_nimi = model.Klrida.get_lang_nimi(lang).lower()
                    if len(puudu) == 1:
                        err = _("Tõlkes ({lang}) puudub küsimus {s}").format(lang=lang_nimi, s=s)
                    else:
                        err = _("Tõlkes ({lang}) puuduvad küsimused {s}").format(lang=lang_nimi, s=s)
                    yield err

                liigsed = koodid - koodid_orig
                if liigsed:
                    s = ', '.join(sorted(list(liigsed)))
                    lang_nimi = model.Klrida.get_lang_nimi(lang).lower()
                    if len(liigsed) == 1:
                        err = _("Tõlkes ({lang}) on liigne küsimus {s}").format(lang=lang_nimi, s=s)
                    else:
                        err = _("Tõlkes ({lang}) on liigsed küsimused {s}").format(lang=lang_nimi, s=s)
                    yield err
    
#########################################################
# Vastuseta sisuplokid

class _rubricBlockController(BlockController):
    _TEMPLATE_NAME = 'brubric'

    def include_edit(self):
        self.c.includes['ckeditor'] = True
        if self.block.wirismath and not self.c.is_edit:
            self.c.includes['wiris'] = True
            
    def include_view(self):
        if self.block.kommenteeritav:
            self.c.includes['rcomment'] = True
        if self.block.wirismath:
            self.c.includes['wiris'] = True

    def update(self, is_tr, not_locked):
        """Sisuploki muudatuste salvestamine
        is_tr - toimub tõlkimine (ei saa muuta mittetekstilisi andmeid)
        not_locked - ülesande sisu pole lukus (saab muuta ülesande sisu)
           kui not_locked=True, siis saab ainult hindamismaatriksit muuta
        """
        if not_locked:
            if not is_tr:
                self._update_staatus()
            # kui on olemas sisu, siis kontrollime, et see on korrektne
            # kui pole, siis visatakse siit veateade
            sisu, tree = self._parse_sisu()
            self._update_sisuvaade(tree, is_tr)

            if self.block.kopikeeld:
                self.block.kommenteeritav = False
            # kysimus, mille juurde salvestada kommentaarid
            if self.block.kommenteeritav:
                k = self.block.kysimus
                k.kood = '_%s' % self.block.seq
                k.pseudo = True
            else:
                k = self.block.get_kysimus()
                if k:
                    k.delete()
        
    def _update_sisuvaade(self, tree, is_tr=False, is_import=False):

        if tree is not None:
            err = None
            # kontrollime, kas plokipeitmisnuppude loendurid on olemas
            ylesanne = self.ylesanne
            for field in tree.xpath('//button[@counts][starts-with(@class, "togglebutton")]'):
                counts = field.get('counts')
                if counts:
                    k = ylesanne.get_kysimus(counts)
                    if not k:
                        err = _("Ülesandes puudub lühivastusega küsimus koodiga {s}").format(s=counts)
                    else:
                        sp = k.sisuplokk
                        if sp.tyyp != const.INTER_TEXT:
                            err = _("Ülesande {id} küsimus {s} ei ole lühivastusega küsimus, ei saa kasutada loendurina").format(id=ylesanne.id, s=counts)
                        elif sp.staatus != const.B_STAATUS_NAHTAMATU:
                            err = _("Ülesande {id} sisuplokk pole nähtamatu, ei saa kasutada loendurina").format(id=ylesanne.id)
            
            if err:
                self._raise_error({}, err)

        buf = (tree is not None) and _outer_xml(tree) or None

        if buf and self.block.reanr:
            # ridade nummerdamine
            len_buf = len(buf)
            prev_ch = None
            tag_name = ''
            n_newlines = []
            n_last_newline = None
            in_open_tag = in_close_tag = in_tag_name = False
            is_new_line = True
            for n in range(len_buf):
                ch = buf[n]
                if ch == '<':
                    # algab tag
                    in_tag = True
                    tag_name = ''
                elif ch == '>':
                    # lõpeb tag
                    in_tag = in_open_tag = in_close_tag = in_tag_name = False
                    if tag_name in ('div','br','p'):
                        is_new_line = True
                elif in_tag:
                    # tagi sees
                    if prev_ch == '<':
                        if ch == '/':
                            in_close_tag = True
                        else:
                            in_open_tag = in_tag_name = True
                            tag_name = ''
                    if in_open_tag:
                        if ch == ' ' or ch == '/':
                            in_tag_name = False
                        if in_tag_name:
                            tag_name += ch
                else:
                    # tekst, ei ole tag
                    if is_new_line:
                        n_last_newline = n
                        is_new_line = False
                    if ch.strip():
                        # tekst on olemas
                        if n_last_newline:
                            n_newlines.append(n_last_newline)
                            n_last_newline = None
                prev_ch = ch

            buf1 = ''
            cnt = 0
            STEP = 5
            prev_n = 0
            for ind, n in enumerate(n_newlines):
                buf1 += buf[prev_n: n]
                prev_n = n
                cnt += 1
                if (cnt - 1) % STEP == 0:
                    # lisada reanr ridadele 1, 6, 11, 16 jne
                    buf1 += f'<span class="lineno">{cnt}</span>'
            buf1 += buf[prev_n:]
            buf = buf1
        self.block.give_tran(self.lang).sisuvaade = buf

    def check(self, arvutihinnatav):
        li = self._check_sisu()
        rc = not li and True or False
        return rc, li

class _headerController(BlockController):
    "HTML päise sisestamine"
    _TEMPLATE_NAME = 'bheader'

    def update(self, is_tr, not_locked):
        # ei kuvata
        self.block.staatus = const.B_STAATUS_KEHTETU

class _googlechartsController(BlockController):
    "Google Charts diagramm"
    _TEMPLATE_NAME = 'bgooglecharts'

    def include_edit(self):
        self.c.includes['googlecharts'] = True
        # laadime kõik paketid, et diagrammi tyybi muutmisel
        # oleks uue tyybi pakett juba laaditud
        #self.c.includes['googlecharts.map'] = True
        self.c.includes['googlecharts.geochart'] = True
        self.c.includes['googlecharts.corechart'] = True

    def include_view(self):
        self.c.includes['googlecharts'] = True
        charttype = self.block.alamtyyp.split('.')[0]
        if charttype == 'GeoChart':
            self.c.includes['googlecharts.geochart'] = True
        else:
            self.c.includes['googlecharts.corechart'] = True

    def update(self, is_tr, not_locked):
        if not_locked:
            if not is_tr:
                self._update_staatus()
            self.block.give_tran(self.lang).sisuvaade = self.form_result['f_sisuvaade']
            ggc = self.form_result['ggc']
            mo = self.block.give_meediaobjekt()
            mo_data = self.form_result['mo']
            mo.from_form(mo_data, lang=self.lang)
            mo.give_tran(self.lang).filedata = pickle.dumps(ggc, 0)

            png_file = self.form_result.get('png_file')
            if png_file:
                mo2 = self.block.give_taustobjekt()
                mo2.give_tran(self.lang).filedata = png_file.encode('utf-8')
            else:
                charttype = self.block.alamtyyp.split('.')[0]
                if charttype in ('Map', 'GeoChart'):
                    mo2 = self.block.taustobjekt
                    if mo2:
                        mo2.delete()
                        
class _mathController(BlockController):
    _TEMPLATE_NAME = 'bmath'

    def update(self, is_tr, not_locked):
        # kirjutame MathML avaldise taustobjekti kirjesse
        if not_locked:
            if not is_tr:
                self._update_staatus()
            latex = self.form_result['f_sisu']
            if not latex:
                raise ValidationError(self.handler, 
                                      {'f_sisu': _("Väärtus puudub")})            
            self.block.give_tran(self.lang).sisu = latex

    def include_edit(self):
        self.c.includes['math'] = True

    def include_view(self):
        self.c.includes['math'] = True

class _wmathController(BlockController):
    _TEMPLATE_NAME = 'bwmath'

    def update(self, is_tr, not_locked):
        # kirjutame MathML avaldise taustobjekti kirjesse
        if not_locked:
            if not is_tr:
                self._update_staatus()
            mathml = self.form_result['f_sisu']
            if not mathml:
                raise ValidationError(self.handler, 
                                      {'f_sisu': _("Väärtus puudub")})            
            self.block.give_tran(self.lang).sisu = mathml

    def include_edit(self):
        self.c.includes['wiris'] = True

    def include_view(self):
        self.c.includes['wiris'] = True

class _mediaInteractionController(BlockController):
    _TEMPLATE_NAME = 'bmedia'
    def update(self, is_tr, not_locked):
        if not_locked:
            images = self.form_result['mot']
            if not is_tr:
                self._update_staatus()
                # kontrollitakse loendurite koodide unikaalsust
                self._unique_kysimused(images)
            # salvestatakse sisuobjektide andmed
            self._update_drag_images(images, is_tr)
            if not is_tr and self.request.params.get('muudform'):
                # märgime sama pala erinevad formaadid
                model.Session.flush()
                self._muudform()

    def _update_drag_images(self, images, is_tr):
        """Lohistatavate piltide andmete salvestamine, piltide kustutamine
        Piltide lisamine vt piltobjektid.py
        """
        data = {int(r['id']): r for r in images if r['id']}
        for obj in list(self.block.meediaobjektid):
            rcd = data.get(obj.id)
            if rcd:
                # muuta
                obj.from_form(rcd, lang=self.lang)
                self._check_file(obj, rcd, is_tr)
                if not is_tr:
                    # loenduri kysimus
                    self._update_kpc(obj, rcd)
            elif is_tr:
                # kustutada tõlge
                tr_obj = obj.tran(self.lang, False)
                if tr_obj:
                    tr_obj.delete()
            else:
                # kustutada põhikirje
                obj.delete()
                self.block.sisuobjektid.remove(obj)

        # kui on olemas uus kirje URLiga, ilma failita
        if not is_tr:
            for rcd in images:
                if not rcd['id']:
                    obj = model.Meediaobjekt(sisuplokk=self.block)
                    obj.from_form(rcd)
                    self._check_file(obj, rcd, is_tr)
                    self._update_kpc(obj, rcd)

    def _muudform(self):
        "Grupeerime sama failinime erinevad formaadid"
        fnames = {}
        for obj in self.block.meediaobjektid:
            if not obj.filename:
                # ei ole fail, vaid URL
                continue
            basename = obj.filename.rsplit('.', 1)[0]
            pea = fnames.get(basename)
            if pea:
                # sama nimega fail on eespool olemas, see siin on muu formaat
                obj.samafail = pea.id
                pea.samafail = pea.id
            else:
                # sama nimega faili eespool pole, vbl tagapool tuleb
                fnames[basename] = obj
                if obj.samafail and obj.samafail != obj.id:
                    obj.samafail = None
                    
    def _check_file(self, mo, rcd, is_tr):
        "Kontrollid"
        if not mo.has_file and not mo.fileurl:
            raise ValidationError(self.handler, {},
                                  _("Palun sisestada kas fail või URL"))
        
        if not is_tr:
            if not mo.autostart and mo.nahtamatu:
                self.handler.notice(_("Soovitav on märkida Autostart või eemaldada märge Nähtamatu, muidu ei ole faili üldse võimalik lahendajale esitada."))

    def _unique_kysimused(self, images):
        ylesanne = self.ylesanne
        k_koodid = ylesanne.get_kysimus_koodid(self.block, True)
        for ind, rcd in enumerate(images):
            kood = rcd['kpc_kood']
            if kood:
                if kood in k_koodid:
                    self._raise_error({'mot-%s.kpc_kood' % ind: _("Kood {s} on selles ülesandes juba kasutusel.").format(s=kood)})
                else:
                    k_koodid.append(kood)

    def _update_kpc(self, mo, modata):
        # kuulamiste arvu loendur
        kpc = mo.give_kysimus(const.OBJSEQ_COUNTER)
        kpc_kood = modata.get('kpc_kood')
        if not kpc_kood:
            kpc_kood = kpc.gen_kood('ML')

        kpc.kood = kpc_kood
        kpc.selgitus = _("Kuulamiste arv")
        tulemus = kpc.give_tulemus()
        tulemus.baastyyp = const.BASETYPE_INTEGER
        tulemus.kardinaalsus = const.CARDINALITY_SINGLE
        tulemus.min_pallid = tulemus.max_pallid = 0
        tulemus.arvutihinnatav = True

        # kuulamise järg
        kpp = mo.give_kysimus(const.OBJSEQ_POS)
        kpp.kood = f'{kpc_kood}_POS'
        kpp.selgitus = _("Kuulamise järg")
        
    def include_edit(self):
        self.c.includes['dropzone'] = True

    def include_view(self):
        self.c.includes['jplayer'] = True
        
class _imageController(BlockController):
    _TEMPLATE_NAME = 'bimage'

    def include_edit(self):
        self.c.includes['dropzone'] = True

    def update(self, is_tr, not_locked):
        if not_locked:
            if not is_tr:
                self._update_staatus()
            images = self.form_result['moi']
            self._update_drag_images(images, is_tr)

class _customInteractionController(BlockController):
    _TEMPLATE_NAME = 'bcustom'

    def update(self, is_tr, not_locked):
        if not_locked:
            if not is_tr:
                self._update_staatus()
            t = self.block.give_taustobjekt()
            filedata = self.form_result['mo'].get('filedata')
            t.from_form(self.form_result['mo'], lang=self.lang, is_image=False)
            if not t.filename:
                raise ValidationError(self.handler, 
                                      {'mo.filedata': _("Fail puudub")})
            

class _geogebraInteractionController(BlockController):
    _TEMPLATE_NAME = 'igeogebra'
    def update(self, is_tr, not_locked):
        if not_locked:
            k = self.block.kysimus
            if not is_tr:
                self._update_staatus()
                self._update_mapping(k,
                                     basetype=const.BASETYPE_FILE,
                                     cardinality=const.CARDINALITY_SINGLE)
                self._unique_kysimus(k)
            else:
                self._tran_update_mapping(k)
            tulemus = k.give_tulemus()
            if not is_tr:
                tulemus.arvutihinnatav = not tulemus.max_pallid
                if not tulemus.max_pallid:
                    tulemus.max_pallid = 0
                
                ggb_data = self.form_result.get('ggb') or {}
                self.block.set_json_sisu(ggb_data, self.lang)

            mo = self.block.give_meediaobjekt()
            is_import = is_upload = False
            if not is_tr:
                mo_data = self.form_result['mo']
                mo.from_form(mo_data, lang=self.lang)
                if mo_data.get('kood'):
                    # imporditakse ID kaudu uus materjal
                    is_import = True
                    mo.filedata = mo.filename = None
                if mo_data.get('filedata') != b'':
                    is_upload = True 
            if not is_tr and not is_import and not is_upload:
                # kui faili ei laaditud
                filedata_b64 = self.form_result.get('ggb_filedata_b64')
                if filedata_b64:
                    motran = mo.give_tran(self.lang)
                    motran.filedata = base64.b64decode(filedata_b64)
                    motran.filename = 'geogebra-export.ggb'
                png_b64 = self.form_result.get('ggb_png_b64')
                if png_b64:
                    mo2 = self.block.give_taustobjekt()
                    mo2tran = mo2.give_tran(self.lang)
                    mo2tran.filedata = base64.b64decode(png_b64)
                    mo2tran.filename = 'geogebra-export.png'

    def include_view(self):
        self.c.includes['geogebra'] = True

    def include_edit(self):
        self.c.includes['geogebra'] = True

class _desmosInteractionController(BlockController):
    _TEMPLATE_NAME = 'idesmos'
    def update(self, is_tr, not_locked):
        if not_locked:
            k = self.block.kysimus
            if not is_tr:
                self._update_staatus()
                self._update_mapping(k,
                                     basetype=const.BASETYPE_FILE,
                                     cardinality=const.CARDINALITY_SINGLE)
                self._unique_kysimus(k)
            else:
                self._tran_update_mapping(k)
            tulemus = k.give_tulemus()
            if not is_tr:
                tulemus.arvutihinnatav = not tulemus.max_pallid
                if not tulemus.max_pallid:
                    tulemus.max_pallid = 0
                uioptions = {'images': bool(self.form_result.get('dmo_images')),
                             'folders': bool(self.form_result.get('dmo_folders')),
                             'notes': bool(self.form_result.get('dmo_notes')),
                             'degreeMode': bool(self.form_result.get('dmo_degreeMode')),
                             'links': bool(self.form_result.get('dmo_links')),
                             'settingsMenu': bool(self.form_result.get('dmo_settingsMenu')),
                             }
                desm_options = self.form_result.get('desm_options')
                try:
                    options = json.loads(desm_options)
                except Exception as e:
                    errors = {'desm_options': str(e)}
                    self._raise_error(errors)
                state = self.form_result.get('desm_state')
                data = {'uioptions': uioptions, # seaded, mille jaoks kasutajaliideses on märkeruudud tehtud
                        'options': options, # seadete väljale käsitsi kirjutatud muud seaded
                        'state': state # graafiku sisu
                        }
                self.block.set_json_sisu(data, self.lang)

            mo = self.block.give_meediaobjekt()
            if not is_tr:
                mo_data = self.form_result['mo']
                mo.from_form(mo_data, lang=self.lang)

    def include_view(self):
        self.c.includes['desmos'] = True

    def include_edit(self):
        self.c.includes['desmos'] = True

#########################################################
# Valikud

class _match2InteractionController(BlockController):
    _TEMPLATE_NAME = 'imatch2'
    def update(self, is_tr, not_locked):
        errors = {}

        valikuhulk1 = self.block.give_baaskysimus(seq=1)
        valikuhulk2 = self.block.give_baaskysimus(seq=2)
            
        if not is_tr:
            valikuhulk2.rtf = self.form_result.get('v2_rtf')

        if not_locked:
            if not is_tr:
                self._update_staatus()

            if not is_tr:               
                # üldine min_vastus/max_vastus (paaride arv) salvestame esimese hulga juure
                valikuhulk1.from_form(self.form_result['l'])
                if valikuhulk1.min_vastus is None:
                    valikuhulk1.min_vastus = 1
                valikuhulk1.rtf = self.form_result.get('v1_rtf')
            khulk_seq = valikuhulk1.ridu
            ylesanne_id = self.ylesanne.id
            hulgad = (valikuhulk1, valikuhulk2)
            for i in range(1, 3):
                valikuhulk = hulgad[i-1]
                params = self.form_result.get('v%d' % i)

                if not is_tr:
                    valikuhulk.from_form(self.form_result, 'h_%s_' % i)
                    self._unique_kood(params, 'v%d' % i)
                    self._valik_selgitus(params, valikuhulk.rtf)

                    rtf_old = self.form_result.get('v%d_rtf_old' % i)
                    if rtf_old and not valikuhulk.rtf:
                        self._remove_rtf(valikuhulk, params)                        

                if valikuhulk.rtf:
                    for ind, v in enumerate(params):
                        err = self._check_img_urls(v['nimi'], ylesanne_id)
                        if err:
                            errors['v%d-%s.nimi' % (i, ind)] = err

                BaseGridController(valikuhulk.valikud, model.Valik).save(params, lang=self.lang)                    
        if errors:
            self._raise_error(errors)

        if not is_tr:
            if valikuhulk1.ridu == 2:
                khulk = valikuhulk2
                vhulk = valikuhulk1
            else:
                khulk = valikuhulk1
                vhulk = valikuhulk2
            pariskysimused = self.block.pariskysimused
            
            # kontrollime, et valikuhulga koodid on kysimuste koodideks vabad
            self._unique_kysimusvalik(khulk, 'v1')
            # moodustame igale valikule oma kysimuse
            k_koodid = list()
            for ind, valik in enumerate(khulk.valikud):
                kysimus = self.block.give_kysimus(kood=valik.kood)
                kysimus.seq = ind + 1
                kysimus.min_vastus = valik.min_vastus
                kysimus.max_vastus = valik.max_vastus
                k_koodid.append(kysimus.kood)
                if kysimus.id:
                    # salvestame hindamismaatriksi
                    for n, am in enumerate(self.form_result['am']):
                        if am['kysimus_id'] == kysimus.id:
                            am['k_selgitus'] = valik.selgitus
                            self._update_mapping(kysimus, 
                                                 basetype=const.BASETYPE_IDENTIFIER,
                                                 cardinality=const.CARDINALITY_MULTIPLE,
                                                 prefix='am-%d' % n,
                                                 am=am)
                            kysimus.tulemus.kood = kysimus.kood
                            break
                else:
                    tulemus = kysimus.give_tulemus(True)
                    tulemus.baastyyp = const.BASETYPE_IDENTIFIER
                    tulemus.kardinaalsus = const.CARDINALITY_MULTIPLE

            # kustutame liigsed kysimused
            for kysimus in pariskysimused:
                k_kood = kysimus.kood
                if k_kood and k_kood not in k_koodid:
                    if kysimus.tulemus:
                        kysimus.tulemus.delete()
                        kysimus.tulemus_id = None
                    kysimus.delete()

    def gen_selgitused(self, overwrite):
        """Genereeritakse valikute selgitused statistikute jaoks"""
        BlockController.gen_selgitused(self, overwrite)
        
        # kopeerime valikute selgitused kysimusele
        valikuhulk1 = self.block.give_baaskysimus(seq=1)
        if valikuhulk1.ridu == 2:
            valikuhulk2 = self.block.give_baaskysimus(seq=2)
            khulk = valikuhulk2
        else:
            khulk = valikuhulk1
        for valik in khulk.valikud:
            kysimus = self.block.give_kysimus(kood=valik.kood)
            kysimus.selgitus = valik.selgitus
        
    def _unique_kysimusvalik(self, valikuhulk, prefix='v1'):
        """Kontrollitakse, et kysimuse kood oleks ylesande piires unikaalne.
        """
        ylesanne = self.ylesanne
        koodid = ylesanne.get_kysimus_koodid(self.block)
        for ind, valik in enumerate(valikuhulk.valikud):
            #validators.PyIdentifier().to_python(valik.kood)
            if valik.kood in koodid:
                message = _("Kood {s} on selles ülesandes juba kasutusel.").format(s=valik.kood)
                self._raise_error({'%s-%d.kood' % (prefix, ind): message})
        
    def include_edit(self):
        self.c.includes['ckeditor'] = True

    def include_view(self):
        self.c.includes['raphael'] = True
        self.c.includes['jqueryui'] = True

    def check(self, arvutihinnatav):
        rc, li = BlockController.check(self, arvutihinnatav)
        valikuhulk1 = self.block.get_baaskysimus(1)
        for ind in range(1, 3):
            valikuhulk = self.block.get_baaskysimus(ind)
            if not valikuhulk:
                rc = False
                li.append(_("Puudub valikuhulk {n}").format(n=ind) + '\n')                
                continue
            if len(valikuhulk.valikud) <= 1:
                rc = False
                li.append(_("Valikuhulgas {n} pole piisavalt valikuid").format(n=ind) + '\n')
                continue
            if valikuhulk.seq == valikuhulk1.ridu:
                # kysimuste hulk
                for valik in valikuhulk.valikud:
                    kysimus = self.block.get_kysimus(kood=valik.kood)
                    if not kysimus:
                        li.append(_("Puudub küsimuse {s} hindamismaatriks").format(s=valik.kood) + '\n')
                        rc = False

            li1 = self._check_valikud_sisu(valikuhulk)
            if li1:
               li.extend(li1)
               rc = False

        for kysimus in self.block.pariskysimused:
            tulemus = kysimus.tulemus
            if not tulemus:
                rc = False
                li.append(_("Puudub küsimuse {s} hindamismaatriks").format(s=kysimus.kood) + '\n')
                continue
        return rc, li

    def set_valikvastused(self):
        valikuhulk1 = self.block.give_baaskysimus(seq=1)
        if valikuhulk1.ridu == 2:
            valik_kysimus_id = valikuhulk1.id
        else:
            valikuhulk2 = self.block.give_baaskysimus(seq=2)                
            valik_kysimus_id = valikuhulk2.id

        for kysimus in self.block.pariskysimused:
            if sa.inspect(kysimus).persistent:
                tulemus = kysimus.tulemus
                if tulemus:
                    tulemus.set_valikvastus(valik_kysimus_id, None, paarina=None)

class _match3InteractionController(BlockController):
    _TEMPLATE_NAME = 'imatch3'

    def give_valikuhulgad(self):
        valikuhulk1 = self.block.give_kysimus(seq=1)
        model.Session.flush()
        valikuhulk2 = self.block.give_kysimus(seq=2)
        model.Session.flush()
        valikuhulk3 = self.block.give_kysimus(seq=3)
        model.Session.flush()
        return valikuhulk1, valikuhulk2, valikuhulk3
    
    def update(self, is_tr, not_locked):
        errors = {}
        valikuhulk1, valikuhulk2, valikuhulk3 = self.give_valikuhulgad()
        
        if not is_tr:
            valikuhulk2.rtf = self.form_result.get('v2_rtf')

        if not_locked:
            if not is_tr:
                self._update_staatus()

            if not is_tr:               
                self._update_minmax(valikuhulk1, valikuhulk2, valikuhulk3)

            ylesanne_id = self.ylesanne.id
            hulgad = (valikuhulk1, valikuhulk2, valikuhulk3)
            for i in range(1, 4):
                valikuhulk = hulgad[i-1]
                if not valikuhulk:
                    break
                params = self.form_result.get('v%d' % i)
                if valikuhulk.rtf:
                    for ind, v in enumerate(params):
                        err = self._check_img_urls(v['nimi'], ylesanne_id)
                        if err:
                            errors['v%d-%s.nimi' % (i, ind)] = err

                if is_tr:
                    #if valikuhulk.rtf:
                    #    self._move_rtf(params, 'v%d' % i)                    
                    BaseGridController(valikuhulk.valikud, model.Valik).\
                        update(params, lang=self.lang)
                else:
                    rtf_old = self.form_result.get('v%d_rtf_old' % i)
                    if rtf_old and not valikuhulk.rtf:
                        self._remove_rtf(valikuhulk, params)
                    valikuhulk.from_form(self.form_result, 'h_%s_' % i)
                    self._unique_kood(params, 'v%d' % i)
                    self._valik_selgitus(params, valikuhulk.rtf)                    
                    #if valikuhulk.rtf:
                    #    self._move_rtf(params, 'v%d' % i)
                    BaseGridController(valikuhulk.valikud, model.Valik).\
                        save(params)

        if errors:
            self._raise_error(errors)
        if not is_tr:
            self._update_mapping_match3(valikuhulk1, valikuhulk2, valikuhulk3)
            self._set_valikud_max_p(valikuhulk1, valikuhulk2, valikuhulk3)

    def _update_minmax(self, valikuhulk1, valikuhulk2, valikuhulk3):
        "Sisuploki üldised min ja max vastuste arvud"
        # üldine max_vastus (paaride arv) salvestame esimese hulga juure
        valikuhulk1.from_form(self.form_result['l'])
        valikuhulk1.rtf = self.form_result.get('v1_rtf')
        if valikuhulk1.min_vastus is None:
            valikuhulk1.min_vastus = 1

        valikuhulk3.rtf = self.form_result.get('v3_rtf')
        # hulkade 1-2 vaheline max paaride arv salvestame teise hulga juurde
        valikuhulk2.max_vastus = self.form_result['l2']['max_vastus']
        valikuhulk2.min_vastus = self.form_result['l2']['min_vastus']
        # hulkade 2-3 vaheline max paaride arv salvestame kolmanda hulga juurde
        valikuhulk3.max_vastus = self.form_result['l3']['max_vastus']
        valikuhulk3.min_vastus = self.form_result['l3']['min_vastus']

        min1 = (valikuhulk2.min_vastus or 0) + (valikuhulk3.min_vastus or 0)
        if min1 > (valikuhulk1.min_vastus or 0):
            valikuhulk1.min_vastus = min1

    def _update_mapping_match3(self, valikuhulk1, valikuhulk2, valikuhulk3):
        self._update_mapping(valikuhulk1, 
                             basetype=const.BASETYPE_DIRECTEDPAIR,
                             cardinality=const.CARDINALITY_MULTIPLE,
                             hm_key='hmx')
        self._unique_kysimus(valikuhulk1)

    def _set_valikud_max_p(self, valikuhulk1, valikuhulk2, valikuhulk3):
        tulemus = valikuhulk1.tulemus
        if tulemus:
            max_v = valikuhulk1.max_vastus
            max_v_by_mx = {1: valikuhulk2.max_vastus,
                           2: valikuhulk3.max_vastus,
                           3: min(valikuhulk2.max_vastus or 1000, valikuhulk3.max_vastus or 1000)
                           }
            self._set_valik_max_p(valikuhulk1, tulemus, [(1, 1), (3,1)], max_v, max_v_by_mx)
            self._set_valik_max_p(valikuhulk2, tulemus, [(1, 2), (2,1)], max_v, max_v_by_mx)
            self._set_valik_max_p(valikuhulk3, tulemus, [(2, 2), (3,2)], max_v, max_v_by_mx)

    def include_edit(self):
        self.c.includes['ckeditor'] = True

    def include_view(self):
        self.c.includes['raphael'] = True
        self.c.includes['jqueryui'] = True

    def _unique_kysimusvalik(self, valikuhulk, prefix='v1'):
        """Kontrollitakse, et kysimuse kood oleks ylesande piires unikaalne.
        """
        ylesanne = self.ylesanne
        koodid = ylesanne.get_kysimus_koodid(self.block)
        for ind, valik in enumerate(valikuhulk.valikud):
            try:
                validators.PyIdentifier().to_python(valik.kood)
            except formencode.api.Invalid as ex:
                self._raise_error({'%s-%d.kood' % (prefix, ind): ex.msg})
                
            if valik.kood in koodid:
                message = _("Kood {s} on selles ülesandes juba kasutusel.").format(s=valik.kood)
                self._raise_error({'%s-%d.kood' % (prefix, ind): message})

    def check(self, arvutihinnatav):
        rc, li = BlockController.check(self, arvutihinnatav)

        valikuhulk1 = self.block.get_kysimus(seq=1)
        for n in range(1,4):
            kysimus = self.block.get_kysimus(seq=n)
            if not kysimus:
                if n < 3:
                    rc = False
                    li.append(_("Puudub valikuhulk {n}").format(n=n) + '\n')
                continue
            if arvutihinnatav and n in (1,3):
                if not kysimus.tulemus:
                    rc = False
                    li.append(_("Puudub valikuhulga {n} hindamismaatriks").format(n=n) + '\n')
                    continue
                if not kysimus.best_entries():
                    rc = False
                    li.append(_("Valikuhulga {n} õige vastus on määramata").format(n=n) + '\n')
            if len(kysimus.valikud) <= 1:
                rc = False
                li.append(_("Valikuhulgas {n} pole piisavalt valikuid").format(n=n) + '\n')

            li1 = self._check_valikud_sisu(kysimus)
            if li1:
               li.extend(li1)
               rc = False

        return rc, li

    def set_valikvastused(self):
        kysimus = valikuhulk1 = self.block.get_kysimus(seq=1)
        tulemus = kysimus.tulemus
        if tulemus:
            valikuhulk2 = self.block.give_kysimus(seq=2)
            valikuhulk3 = self.block.give_kysimus(seq=3)
            tulemus.set_valikvastus(valikuhulk1.id, valikuhulk2.id, 1, paarina=False)
            tulemus.set_valikvastus(valikuhulk2.id, valikuhulk3.id, 2, vahetada=True, paarina=False)
            tulemus.set_valikvastus(valikuhulk1.id, valikuhulk3.id, 3, statvastuses=False, paarina=False)

class _match3aInteractionController(_match3InteractionController):
    # sobitamine kolme hulgaga paaride hindamisega
    _TEMPLATE_NAME = 'imatch3a'

    def give_valikuhulgad(self):
        valikuhulk1 = self.block.give_baaskysimus(seq=1, pseudo=True)
        valikuhulk2 = self.block.give_baaskysimus(seq=2, pseudo=True)
        valikuhulk3 = self.block.give_baaskysimus(seq=3, pseudo=True)
        return valikuhulk1, valikuhulk2, valikuhulk3

    def _update_mapping_match3(self, valikuhulk1, valikuhulk2, valikuhulk3):
        valikuhulk1.ridu = 2
        khulk = valikuhulk2
        pariskysimused = self.block.pariskysimused
        # kontrollime, et valikuhulga koodid on kysimuste koodideks vabad
        self._unique_kysimusvalik(khulk, 'v2')
        # moodustame igale valikule oma kysimuse
        k_koodid = []
        # esimesed 3 kysimust on pseudokysimused valikute hoidmiseks
        k_seq = 3
        for valik in khulk.valikud:
            # igale keskmise hulga valikule vastab 2 kysimust:
            # esimese hulga valikutega kysimus ja kolmanda hulga valikutega kysimus
            for n_valikuhulk in (1, 3):
                k_kood = valik.kood + (n_valikuhulk == 1 and '_H1' or '_H3')
                kysimus = self.block.give_kysimus(kood=k_kood)
                if not kysimus.max_vastus:
                    kysimus.max_vastus = valik.max_vastus 
                if n_valikuhulk == 1:
                    kysimus.max_vastus_arv = len(valikuhulk1.valikud)
                else:
                    kysimus.max_vastus_arv = len(valikuhulk3.valikud)
                k_seq += 1
                kysimus.seq = k_seq
                k_koodid.append(k_kood)
                tulemus = kysimus.give_tulemus(True)
                tulemus.baastyyp = const.BASETYPE_IDENTIFIER
                tulemus.kardinaalsus = const.CARDINALITY_MULTIPLE
                tulemus.kood = k_kood
                if kysimus.id:
                    # salvestame hindamismaatriksi
                    for n, am in enumerate(self.form_result['am']):
                        if am['kysimus_id'] == kysimus.id:
                            kysimus.min_vastus = am['min_vastus']
                            kysimus.max_vastus = am['max_vastus']
                            am['k_selgitus'] = valik.selgitus
                            self._update_mapping(kysimus, 
                                                 basetype=const.BASETYPE_IDENTIFIER,
                                                 cardinality=const.CARDINALITY_MULTIPLE,
                                                 prefix='am-%d' % n,
                                                 am=am,
                                                 tulemus=tulemus)
                            break

        # kustutame liigsed kysimused
        for kysimus in pariskysimused:
            k_kood = kysimus.kood
            if k_kood and k_kood not in k_koodid:
                tulemus = kysimus.tulemus
                if tulemus:
                    tulemus.delete()
                    kysimus.tulemus_id = None
                kysimus.delete()

    def _unique_kysimusvalik(self, valikuhulk, prefix='v1'):
        """Kontrollitakse, et kysimuse kood oleks ylesande piires unikaalne.
        """
        ylesanne = self.ylesanne
        koodid = ylesanne.get_kysimus_koodid(self.block)
        for ind, valik in enumerate(valikuhulk.valikud):
            try:
                validators.PyIdentifier().to_python(valik.kood)
            except formencode.api.Invalid as ex:
                self._raise_error({'%s-%d.kood' % (prefix, ind): ex.msg})
            for n_valikuhulk in (1,3):
                k_kood = valik.kood + (n_valikuhulk == 1 and '_H1' or '_H3')
                if valik.kood in koodid:
                    message = _("Kood {s} on selles ülesandes juba kasutusel.").format(s=k_kood)
                    self._raise_error({'%s-%d.kood' % (prefix, ind): message})

    def _set_valikud_max_p(self, valikuhulk1, valikuhulk2, valikuhulk3):
        return

    def check(self, arvutihinnatav):
        rc, li = BlockController.check(self, arvutihinnatav)

        valikuhulk1 = self.block.get_kysimus(seq=1)
        for n in range(1,4):
            kysimus = self.block.get_kysimus(seq=n)
            if not kysimus:
                if n < 3:
                    rc = False
                    li.append(_("Puudub valikuhulk {n}").format(n=n) + '\n')
                continue
            if len(kysimus.valikud) <= 1:
                rc = False
                li.append(_("Valikuhulgas {n} pole piisavalt valikuid").format(n=n) + '\n')

            li1 = self._check_valikud_sisu(kysimus)
            if li1:
               li.extend(li1)
               rc = False

        return rc, li

    def set_valikvastused(self):
        valikuhulk1 = self.block.give_baaskysimus(seq=1)
        valikuhulk3 = self.block.give_baaskysimus(seq=3)
        for k in self.block.pariskysimused:
            tulemus = k.tulemus
            k_kood = k.kood
            if k_kood.endswith('_H1'):
                tulemus.set_valikvastus(valikuhulk1.id, None, paarina=None)
            elif k_kood.endswith('_H3'):
                tulemus.set_valikvastus(valikuhulk3.id, None, paarina=None)

class _match3bInteractionController(_match3aInteractionController):
    # sobitamine kolme hulgaga kolmikute hindamisega
    _TEMPLATE_NAME = 'imatch3b'

    def give_valikuhulgad(self):
        valikuhulk1 = self.block.give_baaskysimus(seq=1, pseudo=True)
        valikuhulk2 = self.block.give_baaskysimus(seq=2, pseudo=True)
        valikuhulk3 = self.block.give_baaskysimus(seq=3, pseudo=True)
        return valikuhulk1, valikuhulk2, valikuhulk3

    def _update_minmax(self, valikuhulk1, valikuhulk2, valikuhulk3):
        # selles tyybis ei toimu min ja max seadmist,
        # sest loetakse kolmikuid, mitte paare
        return
    
    def _update_mapping_match3(self, valikuhulk1, valikuhulk2, valikuhulk3):
        valikuhulk1.ridu = 2
        khulk = valikuhulk2
        pariskysimused = self.block.pariskysimused
        # kontrollime, et valikuhulga koodid on kysimuste koodideks vabad
        self._unique_kysimusvalik(khulk, 'v1')
        # moodustame igale valikule oma kysimuse
        k_koodid = list()
        for ind, valik in enumerate(khulk.valikud):
            kysimus = self.block.give_kysimus(kood=valik.kood)
            kysimus.seq = ind + 4 # esimesed kolm kysimust on pseudokysimused
            kysimus.min_vastus = valik.min_vastus
            if valik.max_vastus is None:
                valik.max_vastus = 2
            if valik.max_vastus > 2:
                errors = {f'v2-{ind}.max_vastus': _("Arv ei tohi olla suurem kui {n}").format(n=2)}
                self._raise_error(errors)

            # iga teise hulga valik võib osaleda yhes kolmikus
            kysimus.max_vastus = 1
            k_koodid.append(kysimus.kood)
            if kysimus.id:
                # salvestame hindamismaatriksi
                for n, am in enumerate(self.form_result['am']):
                    if am['kysimus_id'] == kysimus.id:
                        am['k_selgitus'] = valik.selgitus
                        self._update_mapping(kysimus, 
                                             basetype=const.BASETYPE_DIRECTEDPAIR,
                                             cardinality=const.CARDINALITY_MULTIPLE,
                                             prefix='am-%d' % n,
                                             am=am)
                        kysimus.tulemus.kood = kysimus.kood
                        break
            else:
                tulemus = kysimus.give_tulemus(True)
                tulemus.baastyyp = const.BASETYPE_DIRECTEDPAIR
                tulemus.kardinaalsus = const.CARDINALITY_MULTIPLE

        # kustutame liigsed kysimused
        for kysimus in pariskysimused:
            k_kood = kysimus.kood
            if k_kood and k_kood not in k_koodid:
                if kysimus.tulemus:
                    kysimus.tulemus.delete()
                    kysimus.tulemus_id = None
                kysimus.delete()

    def _set_valikud_max_p(self, valikuhulk1, valikuhulk2, valikuhulk3):
        pass

    def set_valikvastused(self):
        valikuhulk1 = self.block.give_baaskysimus(seq=1)
        valikuhulk3 = self.block.give_baaskysimus(seq=3)
        for k in self.block.pariskysimused:
            tulemus = k.tulemus
            tulemus.set_valikvastus(valikuhulk1.id, valikuhulk3.id, 1, paarina=True)
    
class _choiceInteractionController(BlockController):
    _TEMPLATE_NAME = 'ichoice'

    def update(self, is_tr, not_locked):
        kysimus = self.block.kysimus
        if not_locked:
            if is_tr:
                self._tran_update_choices()
            else:
                kysimus.rtf_old = kysimus.rtf
                self._update_block_kysimus()
                self._update_choices()
                kysimus.max_vastus_arv = len(kysimus.valikud)
            if not is_tr:
                self._update_staatus()
                
        if not is_tr:
            self._update_mapping(kysimus, 
                                 basetype=const.BASETYPE_IDENTIFIER,
                                 cardinality=const.CARDINALITY_MULTIPLE)
            self._unique_kysimus(kysimus)

    def include_edit(self):
        self.c.includes['ckeditor'] = True

    def check(self, arvutihinnatav):
        rc = True
        li = []

        kysimus = self.block.kysimus
        if arvutihinnatav:
            if not kysimus.tulemus:
                rc = False
                li.append(_("Puudub hindamismaatriks"))
            elif not kysimus.best_entries():
                rc = False
                li.append(_("Õige vastus on määramata"))
        if len(kysimus.valikud) <= 1:
            rc = False
            li.append(_("Valikuid on liiga vähe"))

        li1 = self._check_valikud_sisu(kysimus)
        if li1:
            li.extend(li1)
            rc = False

        return rc, li

    def set_valikvastused(self):
        kysimus = self.block.give_kysimus()
        tulemus = kysimus.tulemus
        if tulemus:
            tulemus.set_valikvastus(kysimus.id, None, paarina=None)

class _mchoiceInteractionController(BlockController):
    _TEMPLATE_NAME = 'imchoice'

    def update(self, is_tr, not_locked):
        errors = {}
        ylesanne_id = self.ylesanne.id
        bkysimus = self.block.give_baaskysimus(seq=1)
        valikuhulk = self.block.give_baaskysimus(seq=2)
        if not is_tr:
            bkysimus.rtf = valikuhulk.rtf = self.form_result.get('v1_rtf')
            bkysimus.segamini = self.form_result.get('segamini') and True or False
        rtf_old = self.form_result.get('v1_rtf_old')
        
        if not_locked:
            if not is_tr:
                self._update_staatus()

            v1 = self.form_result.get('v1')
            v2 = self.form_result.get('v2')
            if not is_tr:
                # valikuhulga salvestamine
                #valikuhulk.from_form(self.form_result, 'h_1_' % i)
                self._unique_kood(v2, 'v2')
                self._valik_selgitus(v2, valikuhulk.rtf)
                if rtf_old and not valikuhulk.rtf:
                    self._remove_rtf(valikuhulk, v2)                        

            # kysimuste veeru päis
            khdr = self.form_result.get('f_sisuvaade')
            if valikuhulk.rtf and khdr:
                khdr, tree = self._parse_rtf(khdr, 'f_sisuvaade')
            self.block.give_tran(self.lang).sisuvaade = khdr

            if valikuhulk.rtf:
                for ind, v in enumerate(v2):
                    err = self._check_img_urls(v['nimi'], ylesanne_id)
                    if err:
                        errors['v2-%s.nimi' % (ind)] = err

            # kysimuse koodi kontroll
            for ind, v in enumerate(v1):
                try:
                    validators.PyIdentifier().to_python(v['kood'])
                except formencode.api.Invalid as ex:
                    errors['v1-%s.kood' % ind] = ex.msg

            if errors:
                self._raise_error(errors)
            BaseGridController(valikuhulk.valikud, model.Valik).save(v2, lang=self.lang)

            if not is_tr:
                # kas on yhetaolised hindamise seaded
                is_common = self.block.alamtyyp != 'N'
                am1 = self.form_result.get('am1')

            # kysimuste tekstide salvestamine valiku tabelis
            vanad_koodid = {v.id: v.kood for v in bkysimus.valikud}
            if not is_tr:
                self._unique_kood(v1, 'v1')
                self._unique_kysimused(v1)
                self._valik_selgitus(v1, bkysimus.rtf)
                if rtf_old and not bkysimus.rtf:
                    self._remove_rtf(bkysimus, v1)                        

            BaseGridController(bkysimus.valikud, model.Valik).save(v1, lang=self.lang)

            # salvestame kysimused
            if not is_tr:
                vanadkysimused = list(self.block.pariskysimused)
                for valik in bkysimus.valikud:
                    # leiame kysimuse
                    kysimus = None
                    if valik.id:
                        vana_kood = vanad_koodid.get(valik.id)
                        if vana_kood:
                            kysimus = self.block.get_kysimus(kood=vana_kood)
                    if not kysimus:
                        kysimus = self.block.give_kysimus(kood=valik.kood)
                        kysimus.sisuplokk = self.block
                    kysimus.kood = valik.kood
                    kysimus.selgitus = valik.selgitus
                    kysimus.seq = 2 + valik.seq
                    kysimus.max_vastus_arv = len(valikuhulk.valikud)
                    
                    # loome tulemuse
                    tulemus = kysimus.give_tulemus(arvutihinnatav=True)
                    tulemus.baastyyp = const.BASETYPE_IDENTIFIER
                    tulemus.kardinaalsus = const.CARDINALITY_MULTIPLE
                    tulemus.kood = kysimus.kood
                       
                    if is_common and am1:
                        # loome tulemuse ja salvestame yhised seaded
                        am1['kood'] = kysimus.kood
                        self._update_tulemus(kysimus,
                                             tulemus,
                                             basetype=const.BASETYPE_IDENTIFIER,
                                             cardinality=const.CARDINALITY_MULTIPLE,
                                             prefix='am1',
                                             am=am1)
                        kysimus.min_vastus = am1.get('kht_min_vastus')
                        kysimus.max_vastus = am1.get('kht_max_vastus')
                        tulemus.calc_max_pallid()

                    # leiame kysimusele vastavad postitatud andmed
                    data = None
                    for r in v1:
                        if r['kood'] == kysimus.kood:
                            data = r
                            break
                    if data:
                        self._save_oige(kysimus, tulemus, data)

                    try:
                        vanadkysimused.remove(kysimus)
                    except:
                        pass

                # eemaldame liigsed kysimused
                for kysimus in vanadkysimused:
                    kysimus.delete()

            if not is_tr:
                # salvestame veergude laiused
                mch = self.form_result.get('mch')
                colwidths = mch.get('colwidth')
                self.block.set_json_sisu({'colwidths': colwidths})

    def _save_oige(self, kysimus, tulemus, data):
        # salvestame linnukesega märgitud õiged vastused
        oigekood = data.get('oigekood')
        if not isinstance(oigekood, list):
            # valiti 1 õige vastus
            oigekood = [oigekood]

        # mitu palli anda õigele vastusele?
        max_pallid = tulemus.max_pallid
        if tulemus.oige_pallid:
            # koostaja on ette andnud, mitu palli õige vastuse eest anda
            oigepallid = tulemus.oige_pallid
        else:
            # muidu saab 1 palli
            oigepallid = 1

        for hm in list(tulemus.hindamismaatriksid):
            hm_kood1 = hm.kood1
            if hm_kood1 in oigekood:
                # muudame olemasolevad read
                if hm.pallid <= 0:
                    hm.pallid = oigepallid
                oigekood.remove(hm_kood1)
            elif hm.pallid > 0:
                # kustutame vastused, mis pole enam õiged
                hm.delete()
        # lisame uued read
        for v_kood in oigekood:
            hm = model.Hindamismaatriks(tulemus=tulemus,
                                        kood1=v_kood,
                                        pallid=oigepallid,
                                        oige=True)
            tulemus.hindamismaatriksid.append(hm)

    def _unique_kysimused(self, v1):
        ylesanne = self.ylesanne
        k_koodid = ylesanne.get_kysimus_koodid(self.block, True)
        for ind, rcd in enumerate(v1):
            kood = rcd['kood']
            if kood in k_koodid:
                self._raise_error({'v1-%s.kood' % ind: _("Kood {s} on selles ülesandes juba kasutusel.").format(s=kood)})
            else:
                k_koodid.append(kood)

    def edit_kysimus(self, kysimus):
        """Sisuploki koostamine
        """
        template = '/sisuplokk/imchoice.kysimus.mako'
        self.c.block = self.block
        self.c.kysimus = kysimus

        # leiame valikute kysimuse
        self.c.kysimus2 = self.block.give_baaskysimus(seq=2)

        # leiame kysimuse teksti
        bkysimus = self.block.give_baaskysimus(seq=1)
        q = (model.Session.query(model.Valik.nimi)
             .filter_by(kysimus_id=bkysimus.id)
             .filter_by(kood=kysimus.kood))
        for r in q.all():
            self.c.kysimusesisu = r[0]
            break
        
        self.c.is_sp_edit = True
        return self.handler.render(template)

    def update_kysimus(self, kysimus):
        # tabeli yhe rea hindamismaatriksi salvestamine
        am1 = self.form_result.get('am1')
        if self.block.alamtyyp == 'N':
            # igal kysimusel oma seaded
            self._update_mapping(kysimus,
                                 basetype=const.BASETYPE_IDENTIFIER, 
                                 cardinality=const.CARDINALITY_MULTIPLE,
                                 prefix='am1',
                                 am=am1)
            kysimus.min_vastus = am1.get('kht_min_vastus')
            kysimus.max_vastus = am1.get('kht_max_vastus')
        else:
            # yhised seaded on salvestatud peavormil,
            # siin salvestatakse ainult hindamismaatriks
            tulemus = kysimus.give_tulemus()
            self._save_hm(kysimus,
                          tulemus,
                          const.BASETYPE_IDENTIFIER, 
                          const.CARDINALITY_MULTIPLE,
                          'am1',
                          am1,
                          'hm1',
                          False,
                          None)
        if not self.ylesanne.lukus:
            self._unique_kysimus(kysimus)
               
    def tran_update_kysimus(self, kysimus):
        # EI MUUDA MIDAGI, kuna valikute koodid on samad, mis põhikeeles
        return
                
    def include_edit(self):
        self.c.includes['ckeditor'] = True

    def check(self, arvutihinnatav):
        rc = True
        li = []

        valikuhulk = self.block.get_baaskysimus(seq=2)
        if not valikuhulk:
            rc = False
            li.append(_("Puudub valikute hulk"))
        else:
            valikud = valikuhulk.valikud
            laius = self.block.laius or 1
            if len(valikud) < laius:
                rc = False
                li.append(_("Valikuid on liiga vähe"))

        li1 = self._check_valikud_sisu(valikuhulk)
        if li1:
            li.extend(li1)
            rc = False

        for kysimus in self.block.pariskysimused:
            tulemus = kysimus.tulemus
            if not tulemus:
                rc = False
                li.append(_("Puudub hindamismaatriks"))
            else:
                if arvutihinnatav and not kysimus.best_entries():
                    rc = False
                    li.append(_("Õige vastus on määramata"))
                for hm in tulemus.hindamismaatriksid:
                    if not hm.kood1:
                        li.append(_("Hindamismaatriksis on tühi vastus"))

        return rc, li

    def set_valikvastused(self):
        bkysimus = self.block.give_baaskysimus(seq=1)
        valikuhulk = self.block.give_baaskysimus(seq=2)
        valikuhulk_id = valikuhulk.id
        for kysimus in self.block.pariskysimused:
            if sa.inspect(kysimus).persistent:
                tulemus = kysimus.tulemus
                if tulemus:
                    tulemus.set_valikvastus(valikuhulk_id, None, paarina=None)
    
class _associateInteractionController(BlockController):
    _TEMPLATE_NAME = 'iassociate'
    def update(self, is_tr, not_locked):
        # seostamine
        kysimus = self.block.kysimus
        if not_locked:
            if not is_tr:
                self._update_staatus()            
            if is_tr:
                self._tran_update_choices()
            else:
                kysimus.rtf_old = kysimus.rtf
                self._update_block_kysimus()
                self._update_choices()
                if not kysimus.max_vastus:
                    kysimus.max_vastus = int(len(kysimus.valikud)/2)
        if not is_tr:
            self._update_mapping(kysimus,
                                 basetype=const.BASETYPE_PAIR,
                                 cardinality=const.CARDINALITY_MULTIPLE)
            self._unique_kysimus(kysimus)
            self._set_valikud_max_p(kysimus)

    def _set_valikud_max_p(self, kysimus):
        tulemus = kysimus.tulemus
        self._set_valik_max_p(kysimus, tulemus, [(1, 1), (1,2)], kysimus.max_vastus)
            
    def include_edit(self):
        self.c.includes['ckeditor'] = True

    def include_view(self):
        self.c.includes['iassociate'] = True

    def check(self, arvutihinnatav):
        rc = True
        li = []

        kysimus = self.block.kysimus
        if arvutihinnatav:
            if not kysimus.tulemus:
                rc = False
                li.append(_("Puudub hindamismaatriks"))
            elif not kysimus.best_entries():
                rc = False
                li.append(_("Õige vastus on määramata"))
        if len(kysimus.valikud) <= 2:
            rc = False
            li.append(_("Valikuid on liiga vähe") )

        li1 = self._check_valikud_sisu(kysimus)
        if li1:
            li.extend(li1)
            rc = False

        return rc, li

    def set_valikvastused(self):
        kysimus = self.block.give_kysimus()
        tulemus = kysimus.tulemus
        if tulemus:
            tulemus.set_valikvastus(kysimus.id, kysimus.id, paarina=True)

class _orderInteractionController(BlockController):
    _TEMPLATE_NAME = 'iorder'
    def update(self, is_tr, not_locked):
        kysimus = self.block.kysimus
        if not_locked:
            if not is_tr:
                self._update_staatus()
            if is_tr:
                self._tran_update_choices()
            else:
                kysimus.rtf_old = kysimus.rtf                
                self._update_block_kysimus()
                self._update_choices()

        if not is_tr:
            self._update_mapping(kysimus,
                                 basetype=const.BASETYPE_IDENTIFIER,
                                 hm_key='hmx')

            self._check_max_len_s(kysimus)
            
            model.Session.flush()
            self._check_mapping(kysimus)
            self._unique_kysimus(kysimus)

    def _check_max_len_s(self, kysimus):
        # valikute selgituste kogupikkus koos semikoolonitega ei või ületada 255,
        # kuna nii suur on statvastus view selgituse väli
        MAX_LEN_S = 255
        selgitused = [v.selgitus or '' for v in kysimus.valikud]
        len_s = len(';'.join(selgitused))
        if len_s > MAX_LEN_S:
            err = _("Valikute selgitused on liiga pikad (kogupikkus ei või ületada {n1} sümbolit, praegu on {n2})").format(n1=MAX_LEN_S, n2=len_s)
            raise ValidationError(self.handler, {}, err)

    def _check_mapping(self, kysimus):
        # jagame valikud gruppidesse, kus järjestamine on võimalik grupisiseselt
        # (iga fikseeritud valik on eraldi grupp)
        errors = {}
        tulemus = kysimus.tulemus
        
        # list, mille igal positsioonil on list vastaval positsioonil olevaist võimalikest koodidest
        positions = []
        # jätkatav list
        group = None
        # gruppide list, kus iga grupp on yhe korra
        all_groups = []

        for ind, v in enumerate(kysimus.valikud):
            if v.fikseeritud:
                if ind != 0 and ind != len(kysimus.valikud) - 1:
                    err = "Et õpilasi mitte segadusse ajada, on lubatud fikseerida ainult esimest ja/või viimast valikut"
                    # kuna vahepealsete fikseerimine võib olla õpilasele segadust tekitav
                    errors['v-%d.fikseeritud' % ind] = err
                # loome uue 1-kohalise listi
                group = [v.kood]
                positions.append(group)
                all_groups.append(group)
                group = None
            elif group:
                # lisame vanasse listi
                group.append(v.kood)
                positions.append(group)
            else:
                # loome uue listi ja jätame meele
                group = [v.kood]
                positions.append(group)
                all_groups.append(group)

        for n_mx, hm_read in tulemus.get_maatriksid():
            if tulemus.kardinaalsus in (const.CARDINALITY_ORDERED, const.CARDINALITY_ORDERED_POS):
                # kontrollime, et hindamismaatriksis antud järjekord on saavutatav
                for ind, hm in enumerate(hm_read):
                    if ind < len(positions):
                        group = positions[ind]
                        if hm.kood1 not in group:
                            err = _("Sellel kohal võimalikud valikud on: {s}").format(s=', '.join(group))
                            errors['am1.hmx-%d.hm-%d.kood1' % (n_mx-1, ind)] = err

            else:
                # kontrollime, et hindamismaatriksi valik saab järgneda eelneval maatriksi real olevale valikule
                prev_kood = None
                for ind, hm in enumerate(hm_read):
                    if prev_kood:
                        for group in all_groups:
                            if prev_kood in group:
                                # leiti eelmise koodi grupp
                                break
                            if hm.kood1 in group:
                                # eelmise koodi grupini pole veel jõutud, kuid leiti juba järgmise koodi grupp
                                err = _("Valik {s1} ei saa olla peale {s2}").format(s1=hm.kood1, s2=prev_kood)
                                errors['am1.hmx-%d.hm-%d.kood1' % (n_mx-1, ind)] = err
                                break
                    prev_kood = hm.kood1
                    
        if errors:
            raise ValidationError(self.handler, errors)
        
    def include_edit(self):
        self.c.includes['ckeditor'] = True

    def include_view(self):
        self.c.includes['sortablejs'] = True        

    def check(self, arvutihinnatav):
        rc = True
        li = []

        kysimus = self.block.kysimus
        if arvutihinnatav:
            if not kysimus.tulemus:
                rc = False
                li.append(_("Puudub hindamismaatriks"))
            elif not kysimus.best_entries():
                rc = False
                li.append(_("Õige vastus on määramata"))
        if len(kysimus.valikud) <= 1:
            rc = False
            li.append(_("Valikuid on liiga vähe") )

        li1 = self._check_valikud_sisu(kysimus)
        if li1:
            li.extend(li1)
            rc = False

        return rc, li

    def set_valikvastused(self):
        kysimus = self.block.give_kysimus()
        tulemus = kysimus.tulemus
        if tulemus:
            tulemus.set_valikvastus(kysimus.id, None, sisujarjestus=True, paarina=None)

#########################################################
# Tekstid

class _hottextBase:
    "Tekstiosa valiku ja tekstiosa värvimise ühine osa"

    def _update_sisu(self, tree, is_tr=False):
        # kui kogemata on üks span teise sisse sattunud, siis tõstame need kõrvutiseks
        for field in tree.xpath('//span'):
            if field.get('class') == 'hottext':
                # meie span
                for subfield in field.iterchildren(tag='span'):
                    # kui meie spani sees on mingi span, siis tõstame välja
                    subfield.getparent().remove(subfield)
                    #field.getparent().replace(field, subfield)
                text = field.text or ''
                n = text.find(')')
                if n > -1:
                    text = text[n+1:]
                field.text = '(%s:%s)%s' % (field.get('group'), field.get('name'), text)

        self.block.give_tran(self.lang).sisu = _outer_xml(tree)
    
    def _update_sisuvaade(self, tree, is_tr=False, is_upgrade=False, is_import=False):
        # CHECKBOXiga tekstiosad on kujul
        # <span class="hottext" name="KOOD" group="GRUPP" uitype="UITYPE" explan="SELGITUS"
        #       style="background-color: rgb(192, 192, 254);">
        # (KOOD)NIMI
        # </span>
        #
        # kus UITYPE on "checkbox" või "underline" (lahendajale märke kuvamise viis)
        # ning GRUPP (võib puududa) ühendab tekstiosi, mille seast saab valida ainult ühe.
        #
        # Kui UITYPE="checkbox" ja GRUPP puudub, siis viime kujule:
        # <span class="hottext inter-bID hottext-unselected" name="KOOD">
        # <input name="PLOKIPREFIX" value="KOOD" type="checkbox" />NIMI
        # </span>
        #
        # Kui UITYPE="checkbox" ja GRUPP on olemas, siis viime kujule:
        # <span class="hottext inter-bID hottext-unselected" name="KOOD" group="GRUPP"> 
        # <input name="PLOKIPREFIX_GRUPP" value="KOOD" type="radio" />NIMI
        # </span>
        #
        # Kui UITYPE="underline", siis viime kujule:
        # <span class="hottext inter-bID hottext-unselected" name="KOOD" group="GRUPP"> 
        # NIMI
        # </span>
        all_groups = list()
        group_valikud = dict()

        # esmalt tuvastame kysimused
        for field in tree.xpath('//span[@class="hottext"]'):
            kood = field.get('name')
            group = field.get('group')
            nimi = field.text
            if not nimi:
                nimi = ' '
            else:
                n = nimi.find(')')
                if n > -1:
                    nimi = nimi[n+1:]
            selgitus = (field.get('explan') or nimi)[:255]

            if not kood:
                # midagi on sassis
                field.getparent().remove(field)
                continue

            if not group:
                group = self.block.kysimus.kood
                field.set('group', group)
            group = group.strip()
            if group not in all_groups:
                all_groups.append(group)
                group_valikud[group] = dict()
            group_valikud[group][kood] = (nimi, selgitus)

        # loome uued kysimused, kustutame liigsed, salvestame kysimuste valikud
        if not self._give_kysimused(all_groups, group_valikud, is_tr, is_upgrade):
            raise ValidationError(self.handler, {})

        # leiame näiteküsimuste vastused
        naide_selected = list()
        for k in self.block.pariskysimused:
            tulemus = k.tulemus
            if tulemus and tulemus.naide:
                for hm in tulemus.hindamismaatriksid:
                    naide_selected.append((k.kood, hm.kood1))

        # muudame sisuteksti
        for field in tree.xpath('//span[@class="hottext"]'):
            kood = field.get('name')
            group = field.get('group').strip()
            uitype = field.get('uitype') or 'checkbox'

            nimi = field.text
            if not nimi:
                nimi = ' '
            else:
                n = nimi.find(')')
                if n > -1:
                    nimi = nimi[n+1:]


            kysimus = self.block.get_kysimus(kood=group)

            if uitype == 'underline':
                # teeme allajoonitava
                cb_type = None
            elif kysimus.max_vastus == 1:
                cb_type = 'radio'
            else:
                cb_type = 'checkbox'

            # kas on näide?
            tulemus = kysimus.tulemus
            on_naide = is_selected = False
            if tulemus and tulemus.naide:
                on_naide = True
                for hm in tulemus.hindamismaatriksid:
                    if hm.kood1 == kood:
                        is_selected = True
                        break
                
            if not on_naide:
                # pole näide
                f_class = 'hottext inter-b%s hottext-unselected' % self.block.id
            elif is_selected:
                # näide, õige vastus
                f_class = 'hottext-selected'
            else:
                # näide, vale vastus
                f_class = 'hottext-unselected'
            if cb_type:
                # raadionupp või märkeruut, kasutame oma kujundust
                f_class += ' custom-control custom-control-inline custom-' + cb_type
                field.tag = 'div'
            field.set('class', f_class)

            field.set('group', group)
            field.set('id', kood)
            if 'style' in field.attrib:
                del field.attrib['style']
            if 'explan' in field.attrib:
                del field.attrib['explan']
                
            name = const.DUMMY_RPREFIX + group
            if cb_type:
                
                cb = E.input(name=name, value=kood, type=cb_type)
                # nbsp, mis paneb märkeruudu muu reaga samale kõrgusele
                field.text = '\u00A0' 
                field.append(cb)
                if on_naide:
                    cb.attrib['disabled'] = 'disabled'
                    if is_selected:
                        cb.attrib['checked'] = 'checked'

                cb_id = 'cb_%s_%s' % (kysimus.id, kood)
                cb.attrib['id'] = cb_id
                cb.attrib['class'] = 'custom-control-input'
                lbl = E.label(nimi)
                lbl.attrib['class'] = 'custom-control-label'
                lbl.attrib['for'] = cb_id
                field.append(lbl)
            else:
                # teeme allajoonitava
                field.text = nimi

        self.block.give_tran(self.lang).sisuvaade = _outer_xml(tree)

    def _give_kysimused(self, all_groups, group_valikud, is_tr, is_upgrade=False):
        log.debug('ALL_GROUPS:%s' % all_groups)
        kysimused = dict()
        need_flush = False
        for k in self.block.pariskysimused:
            if k.kood not in all_groups and not is_tr:
                if is_upgrade:
                    k.max_vastus = 0
                else:
                    k.delete()
                    need_flush = True
            else:
                kysimused[k.kood] = k

        for k_seq, group in enumerate(all_groups):
            valikud = sorted(iter(group_valikud[group].items()), key=lambda r: r[0])
            v_koodid = [r[0] for r in valikud]
            k_kood = group
            kysimus = kysimused.get(k_kood)
            if is_tr:
                # tõlkekeel
                if not kysimus:
                    err = _("Küsimus {s} puudub põhikeelsest ülesandest").format(s=k_kood)
                    if self.handler:
                        self.handler.error(err)
                    log.debug(err)
                    return False
                for seq, (v_kood, (v_nimi, v_selgitus)) in enumerate(valikud):
                    valik = kysimus.get_valik(v_kood)
                    if not valik:
                        err = _("Küsimus {s} puudub põhikeelsest ülesandest").format(s='%s:%s' % (k_kood, v_kood))
                        if self.handler:
                            self.handler.error(err)
                        log.debug(err)
                        return False
            else:
                # põhikeel
                if not kysimus:
                    kysimus = model.Kysimus(sisuplokk=self.block, kood=k_kood)
                    self.block.kysimused.append(kysimus)
                    self._give_tulemus(kysimus)
                    
                kysimus.seq = k_seq + 1           
                
                # kustutame valikud, mida enam põhikeeles ei ole
                for valik in list(kysimus.valikud):
                    if valik.kood not in v_koodid:
                        valik.delete()

                for seq, (v_kood, (v_nimi, v_selgitus)) in enumerate(valikud):
                    valik = kysimus.get_valik(v_kood)
                    if not valik:
                        valik = model.Valik(kood=v_kood)
                        kysimus.valikud.append(valik)
                    valik.seq = seq
                    valik.nimi = v_nimi
                    valik.selgitus = v_selgitus

                if kysimus.max_vastus:
                    cnt_valik = len(kysimus.valikud)
                    if cnt_valik < kysimus.max_vastus:
                        kysimus.max_vastus = None
                self._unique_kysimus(kysimus, prefix=None)

        if need_flush:
            model.Session.flush()
        return True
    
    def _update_transform(self):
        nkood = self.form_result.get('nkood')
        unit = self.form_result.get('unit')
        unitc = self.form_result.get('unitc')
        unitn = self.form_result.get('unitn')
        unity = self.form_result.get('unity')
        splitby = self.form_result.get('splitby')
        vuitype = self.form_result.get('vuitype')
        ylesanne = self.ylesanne
        err = None
        if unity and not splitby:
            err = _("Palun sisestada erisümboli lahtrisse märgid, mis tuleb tekstiosaks teisendada")
        if not unit and not unitc and not unitn and not unity:
            err = _("Palun valida, mille järgi tekstiosadeks jaotada")
        if not nkood:
            nkood = ylesanne.gen_kysimus_kood('A')
        else:
            koodid = [t.kood for t in ylesanne.tulemused]
            if nkood in koodid:
                err = _("Küsimus {s} on ülesande mõnes teises sisuplokis juba kasutusel").format(s=nkood)
        if err:
            raise ValidationError(self.handler, {}, err)
        
        nseq = 0
        def _hottext(word, seq):
            buf = extra = ''
            if unit == 'W':
                extra = ''
                # kui sõna lõpus on sidekriips, siis jätame selle sõnast välja
                len_w = len(word) - 1
                for r in range(len_w, -1, -1):
                    _ch = word[r]
                    if _ch != '-':
                        if r < len_w:
                            extra = word[r + 1:]
                            word = word[:r + 1]
                        break

            if word:
                explan = re.sub('<[^>]+>', '', word)[:255]
                buf += '<span class="hottext" explan="{explan}" group="{kood}" name="{seq}" uitype="{uitype}">({kood}:{seq}){word}</span>'.format(
                    explan=explan,
                    kood=nkood,
                    seq=seq,
                    uitype=vuitype and 'checkbox' or 'underline',
                    word=word)
            if extra:
                buf += extra

            return buf
  
        t_block = self.block.tran(self.lang)
        sisu = t_block.sisu
        if not sisu:
            return
        sisu = html.unescape(sisu)
        sisu2 = '' # uus sisu
        current_tag = ''
        len_sisu = len(sisu)
        in_tag = in_close_tag = in_end = False
        level = word_level = 0
        word = ''
        prev_ch = None
        ind_ch = 0
        ch = sisu[0]
        while ch:
            next_ind_ch = ind_ch + 1
            next_ch = next_ind_ch < len_sisu and sisu[next_ind_ch] or None
            
            if not in_tag and ch == '<':
                # algab algav või lõppev tag
                in_tag = True
                if next_ch == '/':
                    # see on lõppev tag
                    in_close_tag = True
                else:
                    # see on algav tag
                    in_close_tag = False
                    level += 1
                if unit == 'W':
                    # kui mõni sõna on pooleli, siis see lõpeb siin
                    if word:
                        #log.debug('--- sõna lõpeb, sest tag algab')
                        nseq += 1
                        sisu2 += _hottext(word, nseq)
                        word = ''
                elif unit == 'S':
                    # kui mõni lause on pooleli ja see lause on alustatud sügavamal tasemel,
                    # siis peab tasemelt väljudes lause lõppema
                    if word and in_close_tag and level <= word_level:
                        # väljumine oma tasemelt, peame lause lõpetama
                        #log.debug('--- lause lõpeb, sest väljumine tasemelt %d' % word_level)
                        nseq += 1
                        sisu2 += _hottext(word, nseq)
                        word = ''
                current_tag += ch
            elif in_tag:
                current_tag += ch
                if ch == '>':
                    # tag lõpeb
                    in_tag = False
                    if prev_ch == '/':
                        in_close_tag = True
                    if in_close_tag:
                        level -= 1
                    if word:
                        # tag asub tekstiosa sees
                        m = re.match(r'</?([^/ >]+)', current_tag)
                        tag_name = m.groups()[0]
                        if tag_name not in ('a', 'A'):
                            # tekstiosa sisse ei saa jätta linke, sest siis ei saa tekstiosal klikkida
                            word += current_tag
                    else:
                        # tag ei asu tekstiosa sees
                        sisu2 += current_tag
                    current_tag = ''

            elif not in_tag:
                # tekst väljaspool tage
                if unitc or unitn or unity:
                    if unitc and ch.isalpha() or \
                       unitn and ch.isdigit() or \
                       unity and ch in splitby:
                        nseq += 1
                        sisu2 += _hottext(ch, nseq)
                    else:
                        sisu2 += ch
                elif unit == 'W':
                    # iga sõna on tekstiosa
                    if ch.isalpha() or ch == "'" or word and ch == '-':
                        word += ch
                    else:
                        # sõnade vahe, tyhik vms
                        if word:
                            #log.debug('--- sõnade vahe')
                            nseq += 1
                            sisu2 += _hottext(word, nseq)
                            word = ''
                        sisu2 += ch
                elif unit == 'S':
                    # iga lause kuni lauselõpumärgini on tekstiosa
                    if ch in '.?!':
                        # on lauselõpp (võib olla mitu märki järjest)
                        in_end = True
                    elif in_end:
                        # ei ole lauselõpp, aga eelmine märk oli lause lõpp
                        #log.debug('--- eelmine märk oli lause lõpp')
                        nseq += 1
                        sisu2 += _hottext(word, nseq)
                        word = ''
                        in_end = False
                    if ch.isspace() and not word:
                        # tyhik enne uut lauset
                        sisu2 += ch
                    else:
                        if not word:
                            word_level = level
                        word += ch

            ch = next_ch
            ind_ch = next_ind_ch
            
        if word:
            nseq += 1
            sisu2 += _hottext(word, nseq)
        t_block.sisu = sisu2
        log.debug(sisu2)

    def _undo_transform(self, tree):
        "Eemaldame kõik tekstiosad"
        for field in list(tree.xpath('//span[@class="hottext"]')):
            # muudame sildi ära, et hiljem selle järgi element eemaldada
            field.tag = 'HOTTEXT'
            # eemaldame (KOOD:N)
            text = field.text
            n = text.find(')')
            if n > -1:
                field.text = text[n+1:]
        etree.strip_tags(tree, 'HOTTEXT')

    def edit_kysimus(self, kysimus):
        """Sisuploki koostamine
        """
        template = '/sisuplokk/ihottext.kysimus.mako'
        self.c.block = self.block
        self.c.kysimus = kysimus
        if not self.c.valik:
            # vigade korral
            self.c.valik = self.c.new_item()
        self.c.is_sp_edit = True
        return self.handler.render(template)

    def parse_kysimus_valik(self, kysimus, field):
        """Parsitakse HTMLina antud küsimus (sellisel kujul on see sisuploki sisus)
        <span class="hottext" explan="..." group="k_kood" name="v_kood" uitype="underline|checkbox">(k_kood:v_kood)tekst</span>
        """
        vkood = field.get('name')
        valik = kysimus.get_valik(vkood)
        if not valik:
            valik = self.c.new_item(kood=vkood)

        nimi = field.text or ''
        n = nimi.find(')')
        if n > -1:
            nimi = nimi[n+1:]
        valik.nimi = nimi
        selgitus = field.get('explan') or nimi
        if selgitus:
            valik.selgitus = selgitus[:255]
        valik.uitype = field.get('uitype') or 'checkbox'
        return valik

    def update_kysimus(self, kysimus):
        # muudetakse ainult üht tekstiosa
        params = self.request.params
        vkood = params.get('vkood')

        self._give_tulemus(kysimus)
        
        valik = kysimus.get_valik(vkood)
        if not valik:
            valik = model.Valik(kood=vkood,
                                seq = len(kysimus.valikud))
            kysimus.valikud.append(valik)
        if not self.ylesanne.lukus:
            valik.nimi = params.get('vnimi')
            valik.selgitus = (params.get('vselgitus') or valik.nimi)[:255]
            valik.uitype = params.get('vuitype')
        self.c.valik = valik
        
    def tran_update_kysimus(self, kysimus):
        # muudetakse ainult üht lahtrit
        params = self.request.params
        vkood = params.get('vkood')
        valik = kysimus.get_valik(vkood)
        if not valik:
            errors = {'vkood': _("Põhikeeles sellise koodiga tekstiosa pole")}
            raise ValidationError(self.handler, errors=errors)
        valik.give_tran(self.lang).nimi = params.get('vnimi')
        valik.uitype = params.get('vuitype')
        self.c.valik = valik

class _hottextInteractionController(BlockController, _hottextBase):
    _TEMPLATE_NAME = 'ihottext'
    def update(self, is_tr, not_locked):
        if not is_tr:
            self.block.kujundus = self.form_result.get('f_kujundus')
            for ind, am in enumerate(self.form_result.get('am')):
                kood = am.get('kood')
                kysimus = self.block.get_kysimus(kood=kood)
                if kysimus:
                    prefix = 'am-%d' % ind
                    self._update_mapping(kysimus,
                                         prefix=prefix,
                                         am=am,
                                         cardinality=const.CARDINALITY_MULTIPLE,
                                         basetype=const.BASETYPE_IDENTIFIER)
                    kysimus.min_vastus = am.get('kht_min_vastus')
                    kysimus.max_vastus = am.get('kht_max_vastus')
                    kysimus.max_vastus_arv = len(kysimus.valikud)                    

        if not_locked:
            if not is_tr:
                self._update_staatus()
            if self.request.params.get('transform'):
                # transformer jagab kõik tähed/sõnad/laused vms
                self._update_transform()
            sisu, tree = self._parse_sisu()
            if not sisu:
                return
            if self.request.params.get('undotransform'):
                # eemaldada tekstiosadeks jaotus
                self._undo_transform(tree)
            self._update_sisu(tree)
            self._update_sisuvaade(tree, is_tr)
        
    def _give_tulemus(self, kysimus):
        tulemus = kysimus.give_tulemus(True)
        tulemus.kardinaalsus = const.CARDINALITY_MULTIPLE
        tulemus.baastyyp = const.BASETYPE_IDENTIFIER
        
    def include_edit(self):
        self.c.includes['ckeditor'] = True

    def check(self, arvutihinnatav):
        rc = True
        li = []
            
        if arvutihinnatav:
            bkysimus = self.block.give_kysimus(0)
            for kysimus in self.block.kysimused:
                if kysimus != bkysimus:
                    if not kysimus.tulemus:
                        rc = False
                        li.append(_("Puudub hindamismaatriks"))
                    elif not kysimus.best_entries():
                        rc = False
                        li.append(_("Õige vastus on määramata"))

        li1 = self._check_sisu()
        if li1:
            li.extend(li1)
            rc = False

        return rc, li

    def set_valikvastused(self):
        for kysimus in self.block.kysimused:
            if sa.inspect(kysimus).persistent:
                tulemus = kysimus.tulemus
                if tulemus:
                    tulemus.set_valikvastus(kysimus.id, None, paarina=None)

class _colortextInteractionController(BlockController, _hottextBase):
    _TEMPLATE_NAME = 'icolortext'
    def update(self, is_tr, not_locked):
        bkysimus = self.block.give_baaskysimus()
        if not_locked:
            # salvestame värvid
            self._update_choices(bkysimus, is_tr=is_tr)
        if not is_tr:
            self.block.kujundus = self.form_result.get('f_kujundus')
            for ind, am in enumerate(self.form_result.get('am')):
                kood = am.get('kood')
                kysimus = self.block.get_kysimus(kood=kood)
                if kysimus:
                    prefix = 'am-%d' % ind
                    self._update_mapping(kysimus,
                                         prefix=prefix,
                                         am=am,
                                         cardinality=const.CARDINALITY_MULTIPLE,
                                         basetype=const.BASETYPE_DIRECTEDPAIR)
                    kysimus.min_vastus = am.get('kht_min_vastus')
                    kysimus.max_vastus = am.get('kht_max_vastus')
                    self._set_valikud_max_p(kysimus)
            
        if not_locked:
            if not is_tr:
                self._update_staatus()
            if self.request.params.get('transform'):
                # transformer jagab kõik tähed/sõnad/laused vms
                self._update_transform()
            sisu, tree = self._parse_sisu()
            if not sisu:
                return
            if self.request.params.get('undotransform'):
                # eemaldada tekstiosadeks jaotus
                self._undo_transform(tree)
            self._update_sisu(tree)
            self._update_sisuvaade(tree, is_tr)

    def _update_choices(self, kysimus=None, rootdiv=True, is_tr=False):
        """Valikute salvestamine.
        """
        v = self.form_result['v']
        if not is_tr:
            self._unique_kood(v, 'v')
            self._valik_selgitus(v, kysimus.rtf)
            
        for ind, rcd in enumerate(v):
            if not rcd['varv']:
                errors = {'v-%d.varv' % ind: _("puudub")}
                raise ValidationError(self.handler, errors)                

        BaseGridController(kysimus.valikud, model.Valik).save(v, lang=self.lang)
        for v in kysimus.valikud:
            v.kysimus = kysimus

    def _give_tulemus(self, kysimus):
        tulemus = kysimus.give_tulemus(True)
        tulemus.kardinaalsus = const.CARDINALITY_MULTIPLE
        tulemus.baastyyp = const.BASETYPE_DIRECTEDPAIR
           
    def include_edit(self):
        self.c.includes['ckeditor'] = True
        self.c.includes['spectrum'] = True

    def check(self, arvutihinnatav):
        rc = True
        li = []
            
        if arvutihinnatav:
            bkysimus = self.block.give_kysimus(0)
            for kysimus in self.block.pariskysimused:
                if kysimus != bkysimus:
                    if not kysimus.tulemus:
                        rc = False
                        li.append(_("Puudub hindamismaatriks"))
                    elif not kysimus.best_entries():
                        rc = False
                        li.append(_("Õige vastus on määramata"))

        li1 = self._check_sisu()
        if li1:
            li.extend(li1)
            rc = False

        return rc, li

    def _set_valikud_max_p(self, kysimus):
        tulemus = kysimus.tulemus
        self._set_valik_max_p(kysimus, tulemus, [(1, 1)], kysimus.max_vastus)
            
    def set_valikvastused(self):
        bkysimus = self.block.give_baaskysimus()
        for kysimus in self.block.pariskysimused:
            if sa.inspect(kysimus).persistent:
                tulemus = kysimus.tulemus
                if tulemus:
                    tulemus.set_valikvastus(kysimus.id, bkysimus.id, paarina=False)

class _inlineTextInteractionController(BlockController):
    _TEMPLATE_NAME = 'iinltext'
    def update(self, is_tr, not_locked):
        if not_locked:
            if not is_tr:
                self._update_staatus()
            sisu, tree = self._parse_sisu()
            if not sisu:
                return
            self._update_sisu(tree, is_tr)
            if self.handler.has_errors():
                raise ValidationError(self.handler, {}, '')
            self._update_sisuvaade(tree)

            if not is_tr:
                # eemaldame ülearused sisuvalikud
                self.ylesanne.remove_unused() 
                model.Session.flush()
                
                # kui muudeti lynkade tyype, siis muudame ka tõlgetes
                self._update_tran_sisu(tree)

    def _update_sisu(self, tree, is_tr):
        no_name = False
        koodid = []
        korduvad_koodid = []
        liigsed_koodid = []

        seq = 0
        for field in tree.xpath('//input[@type="text"]|//textarea'):
            if field.tag == 'input':
                kood = field.get('value')
            else:
                kood = field.text
            if not kood:
                kood = field.get('id') or field.get('name') # tagasiyhilduvuseks
            if not kood:
                no_name = True
                continue
            if kood in koodid:
                korduvad_koodid.append(kood)
            else:
                koodid.append(kood)

            kysimus = self.block.get_kysimus(kood=kood)
            if not kysimus:
                if is_tr:
                    liigsed_koodid.append(kood)
                else:
                    kysimus = model.Kysimus(sisuplokk=self.block, kood=kood)
            if kysimus:
                self.parse_kysimus_text(kysimus, field)
                seq += 1
                kysimus.seq = seq
                
        if no_name:
            self.handler.error(_("Mõnel lüngal pole koodi"))

        if len(korduvad_koodid):
            skoodid = (', ').join(korduvad_koodid)
            msg = _("Lünkadel pole unikaalsed koodid (korduvad koodid {s})").format(s=skoodid)
            self.handler.error(msg)

        if is_tr:
            if len(liigsed_koodid):
                skoodid = (', ').join(liigsed_koodid)
                if len(liigsed_koodid) == 1:
                    buf = _("Koodiga {s} lünka ülesande põhikeelses variandis ei esine").format(s=skoodid)
                else:
                    buf = _("Koodidega {s} lünki ülesande põhikeelses variandis ei esine").format(s=skoodid)
                self.handler.error(buf)
            # leiame põhikeelse variandi kõik koodid
            orig_koodid = [sv.kood for sv in self.block.sisukysimused]
            puuduvad = [k for k in orig_koodid if not k in koodid]
            if len(puuduvad):
                if len(puuduvad) == 1:
                    buf = _("Puudub tõlge küsimusele koodiga {s}").format(s=', '.join(puuduvad))
                else:
                    buf = _("Puudub tõlge küsimustele koodidega {s}").format(s=', '.join(puuduvad))
                self.handler.error(buf)
        else:
            # põhikeeles salvestamisel kontrollime, et tõlgetes on samad kysimused
            keeled = self.ylesanne.keeled
            for err in self.check_tr(keeled, set(koodid)):
                self.handler.notice(err)

        self.block.flush()
        ylesanne = self.ylesanne
        ylesanne.calc_max_pallid()

    def _update_tran_sisu(self, tree1):
        # kontrollime, et peale põhikeeles muutmist on tõlgetes väljadel samad tyybid
        tyybid = {}
        for k in self.block.kysimused:
            tulemus = k.tulemus
            if tulemus:
                tyybid[k.kood] = tulemus.baastyyp
                
        for t_block in self.block.trans:
            if t_block.ylesandeversioon_id is None and t_block.sisu:
                sisu = t_block.sisu
                sisu, tree = self.block.parse_sisu(sisu)
                if sisu:
                    for field in tree.xpath('//input[@type="text"]|//textarea'):                    
                        if field.tag == 'input':
                            kood = field.get('value')
                        else:
                            kood = field.text
                        baastyyp = kood and tyybid.get(kood)
                        if baastyyp:
                            field.attrib['baastyyp'] = baastyyp

                    t_block.sisu = _outer_xml(tree)
                    self._update_sisuvaade(tree, True, t_block.lang)
               
    def parse_kysimus_text(self, kysimus, field):
        """Parsitakse HTMLina antud küsimus (sellisel kujul on see sisuploki sisus)
        <input|textarea
                baastyyp="string" hm0="319/värviline/10,5/0" hm1="320/punane/20/0"
                max_pallid="10" min_pallid="3" pattern="\d+" size|cols="10" maxlength="10"
                title="vihje..." [rows="3"]
                [type="text"] vaikimisi_pallid="3" value="RESPONSE" />
        (siit pattern,size,title võivad puududa)
        """
        #kysimus.tyyp = const.INTER_TEXT
        vihje = field.get('title')
        if vihje:
            kysimus.give_tran(self.lang).vihje = vihje
        elif 'title' in field.attrib:
            del field.attrib['title']
        kysimus.max_vastus = 1

        if field.tag == 'input':
            kysimus.give_tran(self.lang).pikkus = _int_none(field.get('size'))
        else:
            kysimus.give_tran(self.lang).pikkus = _int_none(field.get('cols'))            
            kysimus.give_tran(self.lang).ridu = _int_none(field.get('rows'))            
        kysimus.give_tran(self.lang).max_pikkus = _int_none(field.get('maxlength'))            

        mask = field.get('pattern')
        if mask:
            kysimus.give_tran(self.lang).mask = mask
        elif 'pattern' in field.attrib:
            del field.attrib['pattern']

        if not self.lang:
            kysimus.rtf = field.tag == 'textarea'
        
        # hindamismaatriksit salvestame ainult kysimuse sisuplokis salvestamisel
        # kuna seal sees võib igasugu sümboleid olla, mida ei saa XMLi atribuudi sees kasutada
        #hm = self._parse_hm(field)

        ylesanne = self.ylesanne

        tulemus = kysimus.give_tulemus()
        # hindamismaatriksi salvestamine
        if not self.lang:
            tulemus.min_pallid = _float_none(field.get('min_pallid'))
            tulemus.max_pallid = _float_none(field.get('max_pallid'))
            tulemus.vaikimisi_pallid = _float_none(field.get('vaikimisi_pallid'))
            tulemus.baastyyp = field.get('baastyyp') or const.BASETYPE_STRING
            tulemus.kardinaalsus = const.CARDINALITY_SINGLE
            tulemus.calc_max_pallid()
        return tulemus

    def _update_sisuvaade(self, tree, is_tr=False, lang=None, is_import=False):
        # asendame:
        # <input baastyyp="string" hm0="värviline/10/0" hm1="punane/20/0"
        #        max_pallid="10" min_pallid="3" pattern="\d+" size="10" maxlength="10"
        #        type="text" vaikimisi_pallid="3" value="RESPONSE" />
        # kujule
        # <input pattern="\d+" size="10" type="text" name="RPREFIXRESPONSE" value="" />

        # IE ei oska type=text panna
        for field in tree.xpath('//input[not(@type)]'):
            field.attrib['type'] = 'text'

        for field in tree.xpath('//input[@type="text"]|//textarea'):
            if field.tag == 'input':
                kood = field.get('value')
            else:
                kood = field.text
            if not kood:
                continue
            kysimus = self.block.get_kysimus(kood=kood)
            if not kysimus:
                if lang:
                    # ei anna viga juhul, kui kutsuti update_tran_sisu seest
                    # ja tegelikult muudeti praegu põhikeelset sisu
                    continue
                message = _("Küsimus {s} puudub").format(s=kood)
                if is_import:
                    self.handler.error('%s (%s)' % (message, _("Ülesanne {id}").format(id=self.ylesanne.id)))
                    continue
                raise ValidationError(self.handler, {}, message)                
            baastyyp = 'baastyyp' in field.attrib and field.attrib['baastyyp'] 
            keys = ('pattern', 'style', 'class', 'name', 'title', 'size', 'maxlength', 'type', 'rows', 'cols') # 'placeholder')

            for key in field.attrib:               
                if not key in keys:
                    del field.attrib[key]
            vihje = kysimus.tran(lang or self.lang).vihje                    
            if baastyyp != const.BASETYPE_MATH:
                initval = kysimus and kysimus.algvaartus and vihje or ''
                if field.tag == 'input':
                    field.attrib['value'] = initval
                else:
                    field.text = initval
                    # et example plugin ei pyyaks vihjet kuvada
                    _add_field_class(field, 'noexample', [])                
            field.attrib['id'] = kood
            field.attrib['name'] = const.RPREFIX + kood
            field.attrib['spellcheck'] = 'false'
            if baastyyp == const.BASETYPE_MATH:
                field.attrib['type'] = 'hidden'
                _add_field_class(field, 'math-editable', [])                
                parent = field.getparent()

                wrapper = E.div('',
                                style='display:inline-block',
                                Class='gap-math-wrap')
                parent.insert(parent.index(field), wrapper);
                div_math = E.div('', id="me_%s" % field.attrib['id'],
                                 name=field.attrib['name'],
                                 n_asend=str(kysimus.n_asend),
                                 style="min-width:%dpx" % (kysimus.pikkus and kysimus.pikkus*10 or 300),
                                 Class="math-view-edit")
                wrapper.append(div_math);
                wrapper.append(field);

                # välja järel olnud sõnad lisame wrapperi järele
                tail = field.tail
                if tail:
                    wrapper.tail = tail
                    field.tail = ''
                if vihje:
                    div_math.attrib['title'] = vihje
                if 'title' in field.attrib:
                    del field.attrib['title']
                field = div_math
            elif baastyyp == const.BASETYPE_INTEGER:
                _add_field_class(field, 'integer', ['float'])
            elif baastyyp == const.BASETYPE_FLOAT:
                _add_field_class(field, 'float', ['integer'])
            else:
                _add_field_class(field, None, ['integer', 'float'])

            tulemus = kysimus.tulemus
            # kas on lubatud tyhi vastus
            if tulemus.lubatud_tyhi:
                _add_field_class(field, 'emptyval', [])
            else:
                _add_field_class(field, None, ['emptyval'])

            # kas on lubatud mitte vastata
            if kysimus.min_vastus == 0:
                _add_field_class(field, 'optional', [])
            else:
                _add_field_class(field, None, ['optional'])

            if kysimus.sonadearv or kysimus.vastus_taisekraan:
                parent = field.getparent()
                wrapper = E.div('',
                                style='display:inline-block',
                                Class='ks-outer')
                parent.insert(parent.index(field), wrapper);
                iconbar = E.div('', Class='ks-icons')
                wrapper.append(iconbar)
                wrapper.append(field)
                if kysimus.sonadearv:
                    _add_field_class(field, kysimus.rtf and 'ck-wordcounting' or 'wordcounting', [])
                    txt = _("{s} sõna").format(s='<span class="wordcount">0</span>')
                    wcnter = etree.XML('<div class="ks-wordcounter">%s</div>' % txt)
                    iconbar.append(wcnter)
                
        self.block.give_tran(lang or self.lang).sisuvaade = _outer_xml(tree)

    def include_edit(self):
        self.c.includes['ckeditor'] = True
        self.c.includes['gapedit'] = True        
        self.c.includes['math'] = True        

    def include_view(self):
        # kui mõni lynk on rtf
        if self.block.on_rtf_kysimusi:
            self.c.includes['ckeditor'] = True
        if self.block.on_math_kysimusi:
            self.c.includes['math'] = True        

    def update_kysimus(self, kysimus):
        # muudetakse ainult üht lahtrit
        if not self.ylesanne.lukus:
            kysimus.rtf_old = kysimus.rtf
            if self.form_result.get('l'):
                kysimus.from_form(self.form_result['l'])

        basetype = None # tuleb vormilt
        self._update_mapping(kysimus,
                             basetype=basetype, 
                             cardinality=const.CARDINALITY_SINGLE)
        if not self.ylesanne.lukus:
            am = self.form_result['am1']
            kysimus.min_vastus = not am.get('kht_min_vastus0') and 1 or 0

            self._unique_kysimus(kysimus)

            if self.request.params.get('on_matriba'):
                # matemaatika nupuriba
                icons = self.request.params.getall('icon') or []
                kysimus.matriba = ','.join(icons)
            else:
                kysimus.matriba = None

    def tran_update_kysimus(self, kysimus):
        # muudetakse ainult üht lahtrit
        if self.form_result.get('l'):
            kysimus.from_form(self.form_result['l'], lang=self.lang)        
        self._tran_update_mapping(kysimus)

    def edit_kysimus(self, kysimus):
        """Sisuploki koostamine
        """
        template = '/sisuplokk/iinltext.kysimus.mako'
        self.c.block = self.block
        self.c.kysimus = kysimus
        self.c.is_sp_edit = True
        return self.handler.render(template)

    def _view(self):
        if self.c.is_sp_print:
            try:
                tree = etree.XML(self.block.sisuvaade)
            except etree.XMLSyntaxError as e:
                sisu = '<div>%s</div>' % self.block.sisuvaade
                tree = etree.XML(sisu)
                
            # asendame <input> punktiiriga
            for field in tree.xpath('//input'):
                f = E.span(h.print_input())
                f.tail = field.tail
                parent = field.getparent()
                if parent is not None:
                    parent.replace(field, f)
                else:
                    # input on ise root
                    tree = field

            self.c.sisuvaade = _outer_xml(tree)
    
    def check(self, arvutihinnatav):
        rc = True
        li = []

        kysimus = self.block.kysimus
        if arvutihinnatav:
            if not kysimus.tulemus:
                rc = False
                li.append(_("Puudub hindamismaatriks"))
            elif not kysimus.best_entries():
                rc = False
                li.append(_("Õige vastus on määramata"))
        if len(self.block.sisukysimused) == 0:
            rc = False
            li.append(_("Lüngad puuduvad") )

        li1 = self._check_sisu()
        if li1:
            li.extend(li1)
            rc = False

        return rc, li

class _inlineChoiceInteractionController(BlockController):
    # mitu inlineChoice
    _TEMPLATE_NAME = 'iinlchoice' 
    def update(self, is_tr, not_locked):
        if not_locked:
            if not is_tr:
                self._update_staatus()
            sisu, tree = self._parse_sisu()
            if not sisu:
                return
            self._update_sisu(tree, is_tr)
            if self.handler.has_errors():
                raise ValidationError(self.handler, {}, '')
            self._update_sisuvaade(tree)

            if not is_tr:
                # eemaldame ülearused sisuvalikud
                self.ylesanne.remove_unused() 
        
    def _update_sisu(self, tree, is_tr):
        no_name = False
        koodid = []
        korduvad_koodid = []
        liigsed_koodid = []
        ylesanne = self.ylesanne

        seq = 0
        need_save = False
        for field in tree.xpath('//select'):
            kood = field.get('id') or field.get('name')

            # kontrollime, et valikuna koostajale kuvatav kood on sama, mis atribuudis
            # (lynga kopeerimisel võib tekkida erinevus)
            if not kood:
                for o in field.iterdescendants('option'):
                    if not o.get('value'):
                        kood = o.text
                        field.attrib['id'] = field.attrib['name'] = kood
                        need_save = True
                        break
            else:
                for o in field.iterdescendants('option'):
                    if not o.get('value'):
                        if kood != o.text:
                            o.text = kood
                            need_save = True
                        break
                
            if not kood:
                no_name = True
                continue

            if kood in koodid:
                korduvad_koodid.append(kood)
            else:
                koodid.append(kood)

            kysimus = self.block.get_kysimus(kood=kood)
            if not kysimus:
                if is_tr:
                    liigsed_koodid.append(kood)
                else:
                    kysimus = model.Kysimus(sisuplokk=self.block, kood=kood)
                    self.block.kysimused.append(kysimus)
            if kysimus:
                kysimus.rtf = bool(field.get('rtf'))
                seq += 1
                kysimus.seq = seq
                kysimus.tulemus = ylesanne.get_tulemus(kood)
                if not is_tr:
                    self.parse_kysimus_choice(kysimus, field)            

                # valikute salvestamine
                self._update_sisu_choices(kysimus, field)

        if no_name:
            self.handler.error(_("Mõnel lüngal pole koodi"))

        if len(korduvad_koodid):
            msg = _("Lünkadel pole unikaalsed koodid (korduvad koodid {s})").format(s=', '.join(korduvad_koodid))
            buf = msg
            self.handler.error(buf)

        if is_tr:
            if len(liigsed_koodid):
                if len(liigsed_koodid) == 1:
                    buf = _("Koodiga {s} lünka ülesande põhikeelses variandis ei esine").format(s=', '.join(liigsed_koodid))
                else:
                    buf = _("Koodidega {s} lünki ülesande põhikeelses variandis ei esine").format(s=', '.join(liigsed_koodid))
                self.handler.error(buf)
            # leiame põhikeelse variandi kõik koodid
            orig_koodid = [sv.kood for sv in self.block.sisukysimused]
            puuduvad = [k for k in orig_koodid if not k in koodid]
            if len(puuduvad):
                if len(puuduvad) == 1:
                    buf = _("Puudub tõlge küsimusele koodiga {s}").format(s=', '.join(puuduvad))
                else:
                    buf = _("Puudub tõlge küsimustele koodidega {s}").format(s=', '.join(puuduvad))
                self.handler.error(buf)
        else:
            # põhikeeles salvestamisel kontrollime, et tõlgetes on samad kysimused
            keeled = self.ylesanne.keeled
            for err in self.check_tr(keeled, set(koodid)):
                self.handler.notice(err)

        if need_save:
            self.block.give_tran(self.lang).sisu = _outer_xml(tree)            
        self.block.flush()
        ylesanne.calc_max_pallid()

    def _update_sisu_choices(self, kysimus, field):
        """Valikute salvestamine HTMLi optionitest tabelisse Valik,
        et statistikud saaksid sealt vaadata valiku teksti ja selgitust
        """
        rows = []
        for o in field.iterdescendants('option'):
            kood = o.get('value')
            if kood:
                row = {'kood': kood,
                       'nimi': o.text,
                       }
                if not self.lang:
                    row['selgitus'] = (o.get('desc') or o.text)[:255]
                rows.append(row)
        BaseGridController(kysimus.valikud, model.Valik, pkey='kood').save(rows, lang=self.lang)

    def parse_kysimus_choice(self, kysimus, field):
        """Parsitakse HTMLina antud küsimus (sellisel kujul on see sisuploki sisus)
        Küsimus on antud SELECTina 

        <select hm0="A/6/0" hm1="B//1" max_pallid="5" min_pallid="1" id="K2" vaikimisi_pallid="2" rtf="1">
        <option value="A" desc="esimene">esimene</option>
        <option value="B" desc="teine">teine</option>
        <option value="C" desc="kolmas">kolmas</option>
        </select>

        Valikud jäävad <option> kujul sisuvalikutena sisu sisse.
        Kui rtf==True, siis on <option> sisu kodeeritud javascripti escape() abil.
        """
        #kysimus.tyyp = const.INTER_CHOICE
        kysimus.max_vastus = 1

        hm = self._parse_hm(field)

        ylesanne = self.ylesanne
        tulemus = kysimus.give_tulemus(True)
                
        # hindamismaatriksi salvestamine
        if not self.lang:
            tulemus.min_pallid = _float_none(field.get('min_pallid'))
            tulemus.max_pallid = _float_none(field.get('max_pallid'))
            tulemus.vaikimisi_pallid = _float_none(field.get('vaikimisi_pallid'))
            tulemus.baastyyp = const.BASETYPE_IDENTIFIER
            tulemus.kardinaalsus = const.CARDINALITY_SINGLE
            # kas kood1 asemel võiks seq kaudu valiku määrata?
            BaseGridController(tulemus.hindamismaatriksid, model.Hindamismaatriks, pkey='kood1').save(hm)
            tulemus.calc_max_pallid()
        return tulemus

    def _parse_hm(self, field):
        """Leiame hindamismaatriksi read XMLi elemendi atribuutidest
        """
        li = []
        for n in range(1000):
            buf = field.get('hm%d' % n)
            # hindamismaatriksi reale vastava atribuudi väärtus on kujul
            # kood1/pallid/oige
            # kus kood1 võib ise ka sisaldada kaldkriipsu
            
            if not buf:
                break
            try:
                arr = buf.split('/')
                oige = bool(_int_none(arr.pop(-1)))
                pallid = _float_none(arr.pop(-1))
                if pallid is None:
                    pallid = 1
                kood1 = '/'.join(arr)
            except Exception as ex:
                # läbu
                log.info('Viga hindamismaatriksi rea (%s) parsimisel, %s' % (buf, ex))
            else:
                li.append({'id':'', 'kood1':kood1, 'pallid': pallid, 'oige': oige})

        return li

    def _update_sisuvaade(self, tree):
        # vigaste XMLi valikute arv
        cnt_not_well_xml = 0
        for field in tree.xpath('//select'):
            kood = field.get('id') or field.get('name')
            # millegipärast läheb name IEs kaduma
            # eemaldame IE pandud "selected"
            if not kood:
                continue
            name = const.RPREFIX + kood
            is_rtf = bool(field.get('rtf'))

            try:
                select_header = _("-- Vali --", locale=self.lang or self.ylesanne.lang)
            except TypeError:
                # QTI import
                select_header = "-- Vali --"
                log.debug('TypeError')
            if self.block.select_promptita:
                # mitte kuvada valitud väärtust --Vali--, aga jätta see alles valikute sekka
                select_header = '<span class="dd-no-prompt">' + select_header + '</span>'

            # asendame select > div.dropdown
            # et saaks kireva tekstiga valikuid kasutada
            # ja õiget vastust tooltipina näidata

            dd_xml = f"""
            <div class="dropdown">
            <input type="hidden" name="{name}" id="{kood}" value=""/>
            <button class="btn btn-select dropdown-toggle" type="button" id="_drdb_{kood}" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            <label>{select_header}</label>
            <i class="mdi mdi-chevron-down"> </i>    
            </button>
            <div class="dropdown-menu" aria-labelledby="_drdb_{kood}">
            <div class="dropdown-item" data-value="">{select_header}</div>
            """

            for o in field.iterdescendants('option'):
                opt_id = o.get('value')
                if opt_id:
                    if not o.text:
                        opt_html = ''
                    elif is_rtf:
                        opt_html = urllib.parse.unquote(o.text) or ''
                        try:
                            etree.XML('<root>' + opt_html + '</root>')
                        except:
                            # vigane XML sisestatud, eemaldame kõik tagid
                            cnt_not_well_xml += 1
                            opt_html = re.sub('<[^>]+>','',opt_html)
                    else:
                        opt_html = html.escape(o.text)
                    dd_xml += f'<div class="dropdown-item" data-value="{opt_id}">{opt_html}</div>'
            dd_xml += '</div></div>'
            dropdown = etree.XML(dd_xml)

            # asendame select -> span
            dropdown.tail = field.tail
            field.getparent().replace(field, dropdown);

        self.block.give_tran(self.lang).sisuvaade = _outer_xml(tree)

        if cnt_not_well_xml > 0:
            if cnt_not_well_xml == 1:
                msg = _("{n} valik sisaldas vigast HTMLi").format(n=cnt_not_well_xml)
            else:
                msg = _("{n} valikut sisaldasid vigast HTMLi").format(n=cnt_not_well_xml)
            self.handler.error(msg)

    def include_edit(self):
        self.c.includes['ckeditor'] = True
        self.c.includes['gapedit'] = True        

    def update_kysimus(self, kysimus):
        # muudetakse ainult üht lahtrit
        if not self.ylesanne.lukus:
            kysimus.rtf_old = kysimus.rtf
            if self.form_result.get('l'):
                kysimus.from_form(self.form_result['l'])
            kysimus.rtf = self.form_result.get('v_rtf')
        basetype = const.BASETYPE_IDENTIFIER
        self._update_mapping(kysimus,
                             basetype=basetype, 
                             cardinality=const.CARDINALITY_SINGLE)
        if not self.ylesanne.lukus:
            self._unique_kysimus(kysimus)

    def tran_update_kysimus(self, kysimus):
        # muudetakse ainult üht lahtrit tõlkes
        # EI MUUDA MIDAGI, kuna valikute koodid on samad, mis originaalkeeles
        return
    
    def update_sisuvalikud(self, kysimus):
        """Vormilt postitatud andmed valikute kohta tehakse sisuvaliku objektideks,
        mida kasutatakse vormi kuvamisel
        """
        valikud = []

        v = self.form_result['v']
        self._unique_kood(v, 'v')
        self._valik_selgitus(v, kysimus.rtf)        
        for rcd in v:
            kood = rcd['kood']
            nimi = rcd['nimi']
            if kysimus.rtf:
                nimi = urllib.parse.unquote(nimi)
            selgitus = rcd.get('selgitus')
            valikud.append(model.Sisuvalik(id=rcd['id'], kood=kood, nimi=nimi, selgitus=selgitus))
        return valikud

    def edit_kysimus(self, kysimus):
        """Sisuploki koostamine
        """
        template = '/sisuplokk/iinlchoice.kysimus.mako'
        self.c.block = self.block
        self.c.kysimus = kysimus
        self.c.is_sp_edit = True
        return self.handler.render(template)

    def _view(self):
        if self.c.is_sp_print:
            try:
                tree = etree.XML(self.block.sisuvaade)
            except etree.XMLSyntaxError as e:
                sisu = '<div>%s</div>' % self.block.sisuvaade
                tree = etree.XML(sisu)
 
            # asendame <select> allakriipsutatud valikutega
            for field in tree.xpath('//select'):
                f = E.span('')
                for option in field.findall('option'):
                    f2 = E.span(option.text, {'class':'hottext'})
                    f2.tail = ' '
                    f.append(f2)
                f.tail = field.tail
                field.getparent().replace(field, f)

            self.c.sisuvaade = _outer_xml(tree)
    
    def check(self, arvutihinnatav):
        rc = True
        li = []

        kysimused = self.block.sisukysimused
        if len(kysimused) == 0:
            rc = False
            li.append(_("Gaps are missing\n"))

        li1 = self._check_sisu()
        if li1:
            li.extend(li1)
            rc = False

        return rc, li

    def set_valikvastused(self):
        for kysimus in self.block.pariskysimused:
            if sa.inspect(kysimus).persistent:
                tulemus = kysimus.tulemus
                if tulemus:
                    tulemus.set_valikvastus(kysimus.id, None, paarina=None)

class _punktInteractionController(BlockController):
    _TEMPLATE_NAME = 'ipunkt'

    def update(self, is_tr, not_locked):
        # kogu sisuploki salvestamine
        errors = {}
        ylesanne_id = self.ylesanne.id
        bkysimus = self.block.give_baaskysimus(seq=1)
        bkysimus.rtf = True

        if not_locked:
            if not is_tr:
                self._update_staatus()
            
            v1 = self.form_result.get('v1')

            # kysimused on antud baaskysimuse valikutena
            # kysimuse koodi kontroll
            k_koodid = self.ylesanne.get_kysimus_koodid(self.block, True)
            for ind, v in enumerate(v1):
                try:
                    kood = validators.PyIdentifier().to_python(v['kood'])
                    if kood in k_koodid:
                        errors['v1-%s.kood' % ind] = _("Kood {s} on selles ülesandes juba kasutusel.").format(s=kood)
                    k_koodid.append(kood)
                except formencode.api.Invalid as ex:
                    errors['v1-%s.kood' % ind] = ex.msg

            if errors:
                self._raise_error(errors)

            # kysimuste tekstide salvestamine valiku tabelis
            vanad_koodid = {v.id: v.kood for v in bkysimus.valikud}
            if not is_tr:
                self._valik_selgitus(v1, bkysimus.rtf)

            # kysimuste tekstide salvestamine baaskysimuse valikutena
            BaseGridController(bkysimus.valikud, model.Valik).save(v1, lang=self.lang)

            # salvestame kysimused
            if not is_tr:
                vanadkysimused = list(self.block.pariskysimused)
                for valik in bkysimus.valikud:
                    # leiame kysimuse
                    kysimus = None
                    if valik.id:
                        vana_kood = vanad_koodid.get(valik.id)
                        if vana_kood:
                            kysimus = self.block.get_kysimus(kood=vana_kood)
                    if not kysimus:
                        kysimus = self.block.give_kysimus(kood=valik.kood)
                        kysimus.sisuplokk = self.block
                    kysimus.kood = valik.kood
                    kysimus.selgitus = valik.selgitus
                    kysimus.seq = 2 + valik.seq
                    kysimus.rtf = False
                    
                    # loome tulemuse
                    tulemus = kysimus.give_tulemus(arvutihinnatav=True)
                    tulemus.baastyyp = const.BASETYPE_POSSTRING
                    tulemus.kardinaalsus = const.CARDINALITY_MULTIPLE
                    tulemus.kood = kysimus.kood

                    try:
                        vanadkysimused.remove(kysimus)
                    except:
                        pass

                # eemaldame liigsed kysimused
                for kysimus in vanadkysimused:
                    kysimus.delete()

            self.update_sisuvaade(bkysimus, is_tr)

    def update_sisuvaade(self, bkysimus, is_tr):
        """Lahendajale kuvatava teksti kokkupanek"""
        buf = '<div>'
        for valik in bkysimus.valikud:
            t_valik = valik.tran(self.lang)
            sisu = t_valik.nimi
            if sisu:
                k_kood = valik.kood
                k_buf, map_kood2seq, ndrop = self._update_sisuvaade_lynkadeta(k_kood, sisu, is_tr)
                kysimus = self.block.get_kysimus(valik.kood)
                buf += f'<span data-kood="{k_kood}"'
                buf += ' class="ipunkt-sent">' + k_buf + '</span>'
                if not is_tr:
                    # märgime hindamismaatriksi juurde iga lynga asukoha jrk
                    kysimus.max_vastus_arv = ndrop
                    tulemus = kysimus.tulemus
                    for hm in list(tulemus.hindamismaatriksid):
                        pos = map_kood2seq.get(hm.kood2)
                        if pos is None:
                            # lynka enam pole
                            hm.delete()
                        else:
                            # märgime lynga asukoha jrk
                            hm.koordinaadid = pos
                    tulemus.calc_max_pallid()
                    
        buf += '</div>'
        if is_tr:
            t_block = self.block.give_tran(self.lang)
        else:
            t_block = self.block
        t_block.sisuvaade = buf

    def _update_sisuvaade_lynkadeta(self, k_kood, sisu, is_tr=False):
        # teeme kõik sõnavahed lynkadeks
        # ja eemaldame koostamise <input> elemendid

        buf = '' # sisuvaate XML koos span-lynkadega
        ndrop = 0 # span-lynkade loendur
        text_start = 0
        prev_nl = True # kas peale viimast reavahetust ei ole lynka veel tehtud
        prev_space = False # kas viimane element oli tyhi span
        map_kood2seq = dict() # vastavus õiget vastuste kohtade ja span-lynkade vahel
        #log.debug('\n\n\nTEKST:%s' % sisu)
        def _newpos(ndrop):
            return f'<div data-seq="{ndrop}" class="interpunkt-pos" contenteditable="true"> </div>'
        
        # asendame kõik tekstis olevad tyhjad kohad nähtamatute lynkadega
        prev_word_need_pos = False
        while True:
            # leiame järgmise HTML elemendi
            tag_start = sisu.find('<', text_start)
            # leiame teksti jooksvast kohast kuni järgmise elemendini
            if tag_start > -1:
                text = sisu[text_start:tag_start]
            else:
                text = sisu[text_start:]
            #log.debug('tag_start=%s, text="%s"' % (tag_start, text))
            if text:
                # leidsime elemendi, millel on tekst
                # tekstis asendame tyhikud lyngaga
                words = re.split('\s+', text)
                for ind_word, word in enumerate(words):
                    # tekst tykeldati sõnadeks, lisame iga sõna ja selle järele võib-olla lynga
                    # välja arvatud siis, kui sõna on tyhi ja eelmisest elemendist ei jäänud lynga nõuet
                    #log.debug('word=%s' % word)
                    if word or prev_word_need_pos:
                        if prev_nl:
                            # sellel real veel ei ole midagi, lisame sõna ette lynga
                            ndrop += 1
                            buf += ' ' + _newpos(ndrop)
                            prev_word_need_pos = False
                            #log.debug(u'lisan lynga %s sõna "%s" ette' % (ndrop, word)) 
                            #log.debug('NEWPOS %s (prev_nl): %s' % (ndrop, word)) 
                        buf += word
                        prev_nl = False

                        # lisame lynga peale sõna
                        if ind_word == len(words) - 1 and tag_start:
                            # kui on teksti lõpp ja on tulemas järgmine element, siis pole teada, kas on lynka vaja
                            # (et ei saaks lohistada sinna, kus tyhikut pole, aga lõpeb/algab span, em vms)
                            prev_word_need_pos = True
                            #log.debug(u'teksti viimane sõna, lynka veel ei pane')
                        else:
                            ndrop += 1
                            buf += _newpos(ndrop)
                            #log.debug(u'lisan lynga %s peale sõna "%s"' % (ndrop, word))
                            #log.debug('NEWPOS %s (word): %s' % (ndrop, word))                         
                            prev_word_need_pos = False
                            
            # leiame järgmise HTML elemendi nime
            if tag_start >= 0:
                # ees on mingi XML element
                tag_end = sisu.find('>', tag_start)
                if tag_end == -1:
                    # vigane XML
                    break
                text_start = tag_end + 1
                tag = sisu[tag_start:text_start]
                tag_name = re.sub(r'^<([A-Za-z]+).*', '\\1', tag)
                end_tag_name = re.sub(r'^</([A-Za-z]+).*', '\\1', tag)
                #log.info('TAG:%s' % tag_name)
                #log.debug(u'järgmine element on "%s":"%s"' % (tag_name, end_tag_name))
                if tag_name == 'input':
                    # algab input (õige vastuse lynk)
                    # jätame meelde inputi koodi, aga uude XMLi ei pane
                    if prev_word_need_pos or prev_nl:
                        # sellel real veel ei ole lynka, lisame
                        ndrop += 1
                        buf += _newpos(ndrop)                        
                        prev_nl = prev_word_need_pos = False
                        
                    m = re.search(r'kood=\"([^"]+)\"', tag)
                    if m:
                        kood = m.groups()[0]
                        if kood in map_kood2seq:
                            message = _("Lüngakood {s} ei ole unikaalne").format(s=kood)
                            raise ValidationError(self.handler, {}, message)
                        log.debug('MAP %s -> %s' % (kood, ndrop))
                        map_kood2seq[kood] = str(ndrop)
                else:
                    # kui ei ole input-element, siis lisame XMLi sisse
                    nl_tags = ('div', 'br', 'p', 'td', 'table')
                    if tag_name in nl_tags or end_tag_name in nl_tags:
                        if prev_word_need_pos:
                            # lisame lynga enne uut elementi
                            ndrop += 1
                            buf += _newpos(ndrop)
                            #log.debug(u'lisan lynga %s enne uut elementi "%s"' % (ndrop, tag_name or end_tag_name))
                            #log.debug('NEWPOS %s (before): %s' % (ndrop, tag_name or end_tag_name))
                            prev_word_need_pos = False
                        buf += tag
                        prev_nl = True
                    else:
                        buf += tag
                continue
            else:
                # rohkem XML elemente ei ole
                #log.debug('rohkem pole')
                if not prev_nl and prev_word_need_pos:
                    #log.debug('lisan lõppu')
                    ndrop += 1
                    buf += _newpos(ndrop)
                break
        return buf, map_kood2seq, ndrop
                
    def edit_kysimus(self, kysimus):
        """Sisuploki koostamine: kysimuse yhe lynga hindamismaatriks
        """
        template = '/sisuplokk/ipunkt.kysimus.mako'
        self.c.block = self.block
        self.c.kysimus = kysimus
        self.c.kood2 = self.handler.request.params.get('kood2')
        self.c.is_sp_edit = True
        return self.handler.render(template)

    def update_kysimus(self, kysimus):
        # muudetakse ainult üht kysimust või lynka
        self.c.kood2 = self.handler.request.params.get('kood2') 
        if self.c.kood2:
            # lynga hindamismaatriks
            # lisame hindamismaatriksisse lynga koodi
            collection = []
            am = self.form_result['am1']
            for r in am['hm1']:
                # lisame kirjele kood2
                r['kood2'] = self.c.kood2
                # tõstame vastuse ckeditori väljalt tavalisele väljale
                r['kood1'] = r['kood1_rtf'].replace('&nbsp;',' ').replace('\xa0',' ')
                if r['pallid'] is None:
                    r['pallid'] = 1
                collection.append(r)
            tulemus = kysimus.tulemus
            # salvestame selle osa hindamismaatriksist, kus on sama lynga kood
            hindamismaatriksid = [r for r in tulemus.hindamismaatriksid \
                                  if r.kood2 == self.c.kood2]

            class NoStripGridController(BaseGridController):
                # muudetud, et kood1 salvestamisel jääksid tyhikud alguses ja lõpus alles
                def update_subitem(self, subitem, rcd, lang=None):
                    super().update_subitem(subitem, rcd, lang)
                    subitem.kood1 = rcd['kood1']
                    return subitem
                def create_subitem(self, rcd, lang=None):
                    subitem = super().create_subitem(rcd, lang)
                    subitem.kood1 = rcd['kood1']
                    return subitem
            NoStripGridController(hindamismaatriksid,
                                model.Hindamismaatriks,
                                supercollection=tulemus.hindamismaatriksid)\
                    .save(collection, delete_hidden=True)
            model.Session.flush()
            # arvutame yle, kui palju palle on võimalik saavutada
            tulemus.calc_max_pallid()
            self._calc_max_pallid_vastus(tulemus)
            
        elif not self.ylesanne.lukus:
            # kogu lause hindamise seaded, ilma hindamismaatriksita
            self._update_mapping(kysimus, 
                                 basetype=const.BASETYPE_POSSTRING,
                                 prefix='am1',
                                 is_hm=False)
            # ei taha, et vastuseid töödeldaks HTMLina
            kysimus.rtf = False
            am = self.form_result.get('am1')            
            kysimus.min_vastus = am['kht_min_vastus']
            kysimus.max_vastus = am['kht_max_vastus']            
            
    def include_view(self):
        self.c.includes['ckeditor'] = True
            
    def check(self, arvutihinnatav):
        rc = True
        li = []
        kysimused = list(self.block.pariskysimused)
        if not kysimused:
            rc = False
            li.append(_("Küsimused puuduvad"))
        for kysimus in kysimused:
            if arvutihinnatav:
                if not kysimus.tulemus:
                    rc = False
                    li.append(_("Puudub hindamismaatriks"))
                elif not kysimus.best_entries():
                    rc = False
                    li.append(_("Õige vastus on määramata"))
        return rc, li

    def set_valikvastused(self):
        for kysimus in self.block.pariskysimused:
            tulemus = kysimus.tulemus
            if tulemus:
                tulemus.set_valikvastus(None, None, analyys1=True)
                    
class _gapMatchInteractionController(BlockController):
    _TEMPLATE_NAME = 'igap'
    def update(self, is_tr, not_locked):
        map_kood2seq = None
        bkysimus = self.block.give_kysimus(0) # valikute sidumiseks, mitte vastamiseks
        if not_locked:
            if not is_tr:
                self._update_staatus()
            if not is_tr:
                ldata = self.form_result['l']
                bkysimus.ridu = ldata['ridu']            
                bkysimus.erand346 = ldata.get('erand346') or False
                bkysimus.segamini = ldata.get('segamini') or False
                bkysimus.n_asend = ldata.get('n_asend')
                if bkysimus.gap_lynkadeta:
                    # muu vastus (väljaspool lünka)
                    am = self.form_result['am1']
                    bkysimus.max_vastus = am['kht_max_vastus']
                    if bkysimus.max_vastus == 1:
                        cardinality = const.CARDINALITY_SINGLE
                    else:
                        cardinality = const.CARDINALITY_MULTIPLE
                    self._update_mapping(bkysimus, 
                                         basetype=const.BASETYPE_IDENTIFIER,
                                         cardinality=cardinality)
                
            sisu, tree = self._parse_sisu()
            if sisu:
                self._update_sisu(tree, is_tr)
                if bkysimus.gap_lynkadeta:
                    map_kood2seq = self._update_sisuvaade_lynkadeta(tree, is_tr)
                else:
                    self._update_sisuvaade(tree, is_tr)

        if is_tr:
            self._tran_update_choices(rootdiv=False)
        else:
            self._update_choices(rootdiv=False)

        if not is_tr:
            if bkysimus.gap_lynkadeta:
                if map_kood2seq:
                    # muu vastus (väljaspool lünka)
                    # vastavus koostaja antud koodide ja span-ide järjekorra vahel
                    for kysimus in self.block.kysimused:
                        if kysimus != bkysimus:
                            kysimus.seq = map_kood2seq.get(kysimus.kood)
            else:
                if bkysimus.tulemus:
                    bkysimus.tulemus.delete()
                    bkysimus.tulemus = None

    def _copy_kysimus(self, field, kood):
        "Kui HTML elemendil field on atribuut copy, siis luuakse uus kysimus vastava kysimuse koopiana"
        o_kood = field.get('copy')
        if o_kood:
            o_kysimus = self.block.get_kysimus(kood=o_kood)
            if o_kysimus:
                kysimus = o_kysimus.copy()
                kysimus.sisuplokk = self.block
                kysimus.kood = kood
                tulemus = kysimus.tulemus
                if tulemus:
                    tulemus.kood = kood
                del field.attrib['copy']
                return kysimus
            
    def _update_sisu(self, tree, is_tr=False):
        if self.block.give_kysimus(0).gap_lynkadeta:
            self.block.give_tran(self.lang).sisu = _outer_xml(tree)
            return
        
        ylesanne = self.ylesanne
        err_koodid = []
        koodid = []
        seq = 0
        for field in tree.xpath('//input'):
            kood = field.get('value')
            if not kood:
                # midagi on sassis
                field.getparent().remove(field)
                continue
            try:
                validators.PyIdentifier().to_python(kood)
            except formencode.api.Invalid as ex:
                err_koodid.append(kood)
                continue

            if kood in koodid:
                message = _("Lüngakood {s} ei ole unikaalne").format(s=kood)
                raise ValidationError(self.handler, {}, message)
            koodid.append(kood)

            kysimus = self.block.get_kysimus(kood=kood)
            if not kysimus:
                if not is_tr:
                    kysimus = self._copy_kysimus(field, kood) or \
                              model.Kysimus(sisuplokk=self.block, kood=kood)
                    self.block.kysimused.append(kysimus)
                else:
                    message = _("Küsimus {s} puudub põhikeelsest ülesandest").format(s=kood)
                    raise ValidationError(self.handler, {}, message)
            seq += 1
            kysimus.seq = seq
            self.parse_kysimus(kysimus, field)

        if len(err_koodid):
            errors = {}
            message = _("Kood tohib sisaldada ainult tähti (aga mitte täpitähti), numbreid ja alakriipsu. Nendele tingimustele ei vasta:") +\
                      ' ' + (', ').join(err_koodid)
            raise ValidationError(self.handler, errors, message)
        
        # kustutame liigsed kysimused
        for kysimus in list(self.block.kysimused):
            if kysimus.seq != 0 and kysimus.id and kysimus.kood not in koodid:
                if kysimus.on_vastatud():
                    msg = _("Küsimust {s} ei saa kustutada").format(s=kysimus.kood)
                    raise ValidationError(self.handler, {}, msg)
                self.block.kysimused.remove(kysimus)
                kysimus.delete()
        model.Session.flush()
        self.block.give_tran(self.lang).sisu = _outer_xml(tree)                

    def _update_sisuvaade(self, tree, is_tr=False, is_import=False):
        # Lünk tuleb kujul
        # <input size="10" type="text" value="KOOD" />
        # Viime kujule 
        # <span id="KOOD" class="droppable-gap"></span>

        bkysimus = self.block.give_kysimus(0)
        if bkysimus.gap_lynkadeta:
            # kui lib.importpackage kutsub
            self._update_sisuvaade_lynkadeta(tree, is_tr)
            return
        
        ylesanne = self.ylesanne
        for field in tree.xpath('//input'):
            kood = field.get('value')
            if not kood:
                # midagi on sassis
                field.getparent().remove(field)
                continue
            kysimus = self.block.get_kysimus(kood=kood)
            if kysimus.max_vastus is None:
                kmax = ''
            else:
                kmax = str(kysimus.max_vastus)
            div = E.span('...',{'id':kood, 'class':'droppable-gap', 'max_vastus': kmax})
            div.tail = field.tail
            field.getparent().replace(field, div)
            
        self.block.give_tran(self.lang).sisuvaade = _outer_xml(tree)
                    
    def _update_sisuvaade_lynkadeta(self, tree, is_tr=False):
        # teeme kõik sõnavahed lynkadeks
        # ja eemaldame <input> elemendid
        bkysimus = self.block.give_kysimus(0) # valikute sidumiseks, mitte vastamiseks
        bmax_vastus = bkysimus.max_vastus # vaikimisi max vastuste arv ühes lüngas, mis on sõnade vahel ja pole eraldi lünk
        if bmax_vastus is None:
            bmax_vastus = ''
        xml = _outer_xml(tree) # olemasolev XML
        buf = '' # sisuvaate XML koos span-lynkadega
        ndrop = 0 # span-lynkade loendur
        text_start = 0
        prev_nl = True # kas peale viimast reavahetust ei ole lynka veel tehtud
        prev_space = False # kas viimane element oli tyhi span
        map_kood2seq = dict() # vastavus õiget vastuste kohtade ja span-lynkade vahel
        kysimused = list(self.block.kysimused)
        map_kood2max = {k.kood: k.max_vastus for k in kysimused}
        map_kood2min = {k.kood: k.min_vastus for k in kysimused}        
        
        def _newpos(ndrop):
            return '<span id="_seq%d" class="droppable-pos" max_vastus="%s"> </span>' % (ndrop, bmax_vastus)

        def _setmax(buf, ndrop, max_vastus):
            if max_vastus is None:
                max_vastus = ''
            if max_vastus == bmax_vastus:
                return buf
            return buf.replace('<span id="_seq%d" class="droppable-pos" max_vastus="%s">' % (ndrop, bmax_vastus),
                               '<span id="_seq%d" class="droppable-pos" max_vastus="%s">' % (ndrop, max_vastus))

        def _setmin(buf, ndrop, min_vastus):
            if not min_vastus:
                return buf
            else:
                return buf.replace('<span id="_seq%d" ' % (ndrop),
                                   '<span id="_seq%d" min_vastus="%s" ' % (ndrop, min_vastus))                
                
        # asendame kõik tekstis olevad tyhjad kohad span-lynkadega
        prev_word_need_pos = False
        while True:
            # leiame järgmise HTML elemendi
            tag_start = xml.find('<', text_start)
            # leiame teksti jooksvast kohast kuni järgmise elemendini
            text = xml[text_start:tag_start]
            #log.debug('tag_start=%s, text="%s"' % (tag_start, text))
            if text:
                # leidsime elemendi, millel on tekst
                # tekstis asendame tyhikud lyngaga
                words = re.split('\s+', text)
                for ind_word, word in enumerate(words):
                    # tekst tykeldati sõnadeks, lisame iga sõna ja selle järele võib-olla lynga
                    # välja arvatud siis, kui sõna on tyhi ja eelmisest elemendist ei jäänud lynga nõuet
                    #log.debug('word=%s' % word)
                    if word or prev_word_need_pos:
                        if prev_nl:
                            # sellel real veel ei ole midagi, lisame sõna ette lynga
                            ndrop += 1
                            buf += ' ' + _newpos(ndrop)
                            prev_word_need_pos = False
                            #log.debug(u'lisan lynga %s sõna "%s" ette' % (ndrop, word)) 
                            #log.debug('NEWPOS %s (prev_nl): %s' % (ndrop, word)) 
                        buf += word
                        prev_nl = False

                        # lisame lynga peale sõna
                        if ind_word == len(words) - 1 and tag_start:
                            # kui on teksti lõpp ja on tulemas järgmine element, siis pole teada, kas on lynka vaja
                            # (et ei saaks lohistada sinna, kus tyhikut pole, aga lõpeb/algab span, em vms)
                            prev_word_need_pos = True
                            #log.debug(u'teksti viimane sõna, lynka veel ei pane')
                        else:
                            ndrop += 1
                            buf += _newpos(ndrop)
                            #log.debug(u'lisan lynga %s peale sõna "%s"' % (ndrop, word))
                            #log.debug('NEWPOS %s (word): %s' % (ndrop, word))                         
                            prev_word_need_pos = False
                            
            # leiame järgmise HTML elemendi nime
            if tag_start >= 0:
                # ees on mingi XML element
                tag_end = xml.find('>', tag_start)
                if tag_end == -1:
                    # vigane XML
                    break
                text_start = tag_end + 1
                tag = xml[tag_start:text_start]
                #tag_name = tag[1:].split(' ', 2)[0].lower()
                tag_name = re.sub(r'^<([A-Za-z]+).*', '\\1', tag)
                end_tag_name = re.sub(r'^</([A-Za-z]+).*', '\\1', tag)
                #log.info('TAG:%s' % tag_name)
                #log.debug(u'järgmine element on "%s":"%s"' % (tag_name, end_tag_name))
                if tag_name == 'input':
                    # algab input (õige vastuse lynk)
                    # jätame meelde inputi koodi, aga uude XMLi ei pane
                    if prev_word_need_pos or prev_nl:
                        # sellel real veel ei ole lynka, lisame
                        ndrop += 1
                        #buf += ' ' + _newpos(ndrop)
                        buf += _newpos(ndrop)                        
                        #if prev_nl:
                        #    log.debug(u'lisame lynga %s rea "%s" algusse' % (ndrop, word))
                        #else:
                        #    log.debug(u'lisame lynga %s peale viimast sõna' % (ndrop))
                        #log.info('NEWPOS %s (input): %s' % (ndrop, word)) 
                        prev_nl = prev_word_need_pos = False
                        
                    m = re.search(r'value=\"([^"]+)\"', tag)
                    if m:
                        kood = m.groups()[0]
                        if kood in map_kood2seq:
                            message = _("Lüngakood {s} ei ole unikaalne").format(s=kood)
                            raise ValidationError(self.handler, {}, message)
                        log.debug('MAP %s -> %s' % (kood, ndrop))
                        map_kood2seq[kood] = str(ndrop)
                        # lisame tagantjärgi lynga sisse max lubatud vastuste arvu
                        max_vastus = map_kood2max.get(kood)
                        min_vastus = map_kood2min.get(kood)                        
                        buf = _setmax(buf, ndrop, max_vastus)
                        buf = _setmin(buf, ndrop, min_vastus)
                else:
                    # kui ei ole input-element, siis lisame XMLi sisse
                    nl_tags = ('div', 'br', 'p', 'td', 'table')
                    if tag_name in nl_tags or end_tag_name in nl_tags:
                        if prev_word_need_pos:
                            # lisame lynga enne uut elementi
                            ndrop += 1
                            buf += _newpos(ndrop)
                            #log.debug(u'lisan lynga %s enne uut elementi "%s"' % (ndrop, tag_name or end_tag_name))
                            #log.debug('NEWPOS %s (before): %s' % (ndrop, tag_name or end_tag_name))
                            prev_word_need_pos = False
                        buf += tag
                        prev_nl = True
                    else:
                        buf += tag
                continue
            else:
                # rohkem XML elemente ei ole
                break
        tree = etree.XML(buf)

        err_koodid = []
        for v in kysimused:
            if v.seq != 0 and v.kood not in map_kood2seq:
                if v.on_vastatud():
                    msg = _("Küsimust {s} ei saa kustutada").format(s=v.kood)
                    raise ValidationError(self.handler, {}, msg)
                log.debug('delete %s' % (v.kood))
                self.block.kysimused.remove(v)
                v.delete()
            else:
                try:
                    validators.PyIdentifier().to_python(v.kood)
                except formencode.api.Invalid as ex:
                    err_koodid.append(kood)

        if len(err_koodid):
            errors = {}
            message = _("Kood tohib sisaldada ainult tähti (aga mitte täpitähti), numbreid ja alakriipsu. Nendele tingimustele ei vasta:") +\
                      ' ' + (', ').join(err_koodid)
            raise ValidationError(self.handler, errors, message)

        self.block.give_tran(self.lang).sisuvaade = _outer_xml(tree)
        return map_kood2seq
    
    def include_edit(self):
        self.c.includes['ckeditor'] = True
        self.c.includes['gapedit'] = True        

    def include_view(self):
        self.c.includes['igap'] = True

    def update_kysimus(self, kysimus):
        # muudetakse ainult üht lahtrit
        if not self.ylesanne.lukus:
            if self.form_result.get('l'):
                kysimus.from_form(self.form_result['l'])
            am = self.form_result['am1']
            kysimus.min_vastus = am['kht_min_vastus']
            kysimus.max_vastus = am['kht_max_vastus']
        basetype = const.BASETYPE_IDENTIFIER
        self._update_mapping(kysimus,
                             basetype=basetype)
        if not self.ylesanne.lukus:
            self._unique_kysimus(kysimus)

    def tran_update_kysimus(self, kysimus):
        # muudetakse ainult üht lahtrit
        self._tran_update_mapping(kysimus)

    def edit_kysimus(self, kysimus):
        """Sisuploki koostamine
        """
        template = '/sisuplokk/igap.kysimus.mako'
        self.c.block = self.block
        self.c.kysimus = kysimus
        self.c.is_sp_edit = True
        return self.handler.render(template)

    def parse_kysimus(self, kysimus, field):
        """Parsitakse HTMLina antud küsimus (sellisel kujul on see sisuploki sisus)
        <input
                hm0="319/vkood1/10,5/0" hm1="320/vkood2/20/0"
                max_pallid="10" min_pallid="3" 
                type="text" vaikimisi_pallid="3" value="KKOOD" />
        """
        #kysimus.max_vastus = 1
        hm = self._parse_hm(field)
        ylesanne = self.ylesanne
        tulemus = kysimus.give_tulemus()
        if not hm and not 'max_pallid' in field.attrib:
            # lähtekood, mis ei sisalda maatriksit (tõlge?)
            # igaks juhuks ei kustuta
            tulemus.baastyyp = const.BASETYPE_IDENTIFIER            
            return tulemus

        # hindamismaatriksi salvestamine
        if not self.lang:
            tulemus.min_pallid = _float_none(field.get('min_pallid'))
            tulemus.max_pallid = _float_none(field.get('max_pallid'))
            tulemus.vaikimisi_pallid = _float_none(field.get('vaikimisi_pallid'))
            tulemus.baastyyp = const.BASETYPE_IDENTIFIER
            #tulemus.kardinaalsus = const.CARDINALITY_SINGLE
            tulemus.calc_max_pallid()
            # kas kood1 asemel võiks seq kaudu valiku määrata?
            BaseGridController(tulemus.hindamismaatriksid, model.Hindamismaatriks, pkey='kood1', pkey_empty=True).save(hm)
            tulemus.calc_max_pallid()
        # Pangaga lünga tõlkes ei saa hindamismaatriksit muuta, seetõttu pole hindamismaatriksi tõlkekirjeid vaja

        return tulemus

    def _parse_hm(self, field):
        """Leiame hindamismaatriksi read XMLi elemendi atribuutidest
        """
        li = []
        for n in range(1000):
            buf = field.get('hm%d' % n)
            # hindamismaatriksi reale vastava atribuudi väärtus on kujul
            # kood1/pallid/oige
            # kus kood1 võib ise ka sisaldada kaldkriipsu
            
            if not buf:
                break
            try:
                arr = buf.split('/')
                oige = bool(_int_none(arr.pop(-1)))
                pallid = _float_none(arr.pop(-1))
                if pallid is None:
                    pallid = 1
                kood1 = '/'.join(arr)
            except Exception as ex:
                # läbu
                log.info('Viga hindamismaatriksi rea (%s) parsimisel, %s' % (buf, ex))
            else:
                li.append({'id':'', 'kood1':kood1, 'pallid': pallid, 'oige': oige})
        return li

    def _view(self):
        if self.c.is_sp_print:
            txt = self.block.sisuvaade
            if txt:
                # asendame <span class="droppable-gap"> punktiiriga
                tree = etree.XML(self.block.sisuvaade)
                for field in tree.xpath('//span[@class="droppable-gap"]'):
                    f = E.span(h.print_input())
                    f.tail = field.tail
                    field.getparent().replace(field, f)
                self.c.sisuvaade = _outer_xml(tree)
            else:
                self.c.sisuvaade = ''

    def check(self, arvutihinnatav):
        rc = True
        li = []
        found = False
        for kysimus in self.block.kysimused:
            if kysimus.seq == 0:
                continue
            found = True
            if arvutihinnatav:
                tulemus = kysimus.tulemus
                if not tulemus:
                    rc = False
                    li.append(_("Küsimusel {s} puudub hindamismaatriks").format(s=kysimus.kood))
                elif not kysimus.best_entries():
                    k_arvutihinnatav = bool(tulemus.arvutihinnatav)
                    rc = False
                    li.append(_("Küsimuse {s} õige vastus on määramata").format(s=kysimus.kood))
        if not found:
            rc = False
            li.append(_("No gaps\n") )

        li1 = self._check_sisu()
        if li1:
            li.extend(li1)
            rc = False
            
        bkysimus = self.block.give_kysimus(0)
        li1 = self._check_valikud_sisu(bkysimus)
        if li1:
            li.extend(li1)
            rc = False

        return rc, li

    def set_valikvastused(self):
        bkysimus = self.block.give_kysimus(0)
        for kysimus in self.block.pariskysimused:
            if sa.inspect(kysimus).persistent:
                tulemus = kysimus.tulemus
                if tulemus:
                    # ES-2539 (18) Merit: muu vastuse korral mitte väljastada excelis vastust, ainult punktid
                    mittevastus = kysimus == bkysimus
                    tulemus.set_valikvastus(bkysimus.id, None, paarina=None, mittevastus=mittevastus)
        
class _textEntryInteractionController(BlockController):
    _TEMPLATE_NAME = 'itext'

    def update(self, is_tr, not_locked):
        kysimus = self.block.kysimus
        kysimus.rtf_old = kysimus.rtf
        if not_locked:
            if not is_tr:
                self._update_staatus()
            if is_tr:
                self._tran_update_mapping(kysimus)
                kysimus.give_tran(self.lang).vihje = self.form_result['l']['vihje']
            else:
                kysimus.from_form(self.form_result['l'])
        if not is_tr:
            if kysimus.max_vastus == 1:
                cardinality = const.CARDINALITY_SINGLE
            else:
                cardinality = const.CARDINALITY_MULTIPLE
            self._update_mapping(self.block.kysimus, cardinality=cardinality)
            self._unique_kysimus(self.block.kysimus)
            self.block.kysimus.vorming_kood = self.block.kysimus.tulemus.baastyyp
        
    def check(self, arvutihinnatav):
        rc = True
        li = []

        kysimus = self.block.kysimus
        if arvutihinnatav:
            if not kysimus.tulemus:
                rc = False
                li.append(_("Puudub hindamismaatriks"))
            elif not kysimus.best_entries():
                rc = False
                li.append(_("Õige vastus on määramata"))

        li1 = self._check_sisu()
        if li1:
            li.extend(li1)
            rc = False
        return rc, li

class _extendedTextInteractionController(BlockController):
    _TEMPLATE_NAME = 'iexttext'
    def include_edit(self):
        self.c.includes['ckeditor'] = True

    def include_view(self):
        if self.block.kysimus.rtf:
            self.c.includes['ckeditor'] = True
        
    def update(self, is_tr, not_locked):
        kysimus = self.block.kysimus
        kysimus.rtf_old = kysimus.rtf
        if not_locked and not is_tr:
            self._update_block_kysimus()
            self._update_staatus()
        if is_tr:
            if kysimus.max_vastus == 1:
                cardinality = const.CARDINALITY_SINGLE
            else:
                cardinality = const.CARDINALITY_MULTIPLE
            self._tran_update_mapping(kysimus, cardinality=cardinality)
            kysimus.give_tran(self.lang).vihje = self.form_result['l']['vihje']            
        else:
            self._update_mapping(kysimus) # basetype: string, integer, float
            self._unique_kysimus(kysimus)

    def check(self, arvutihinnatav):
        rc = True
        li = []
        
        kysimus = self.block.kysimus
        if arvutihinnatav:
            if not kysimus.tulemus:
                rc = False
                li.append(_("Puudub hindamismaatriks"))
            else:
                if not kysimus.best_entries():
                    rc = False
                    li.append(_("Õige vastus on määramata"))

        return rc, li

class _crosswordController(BlockController):
    _TEMPLATE_NAME = 'icrossword'
    def include_edit(self):
        self.c.includes['ckeditor'] = True

    def include_view(self):
        if self.block.kysimus.rtf:
            self.c.includes['ckeditor'] = True
        
    def update(self, is_tr, not_locked):
        if not_locked and not is_tr:
            self._update_staatus()
        self._move_crossword()
        if not is_tr:
            for mo in self.block.sisuobjektid:
                if not mo.kysimused:
                    mo.delete()
        self._check_uniq_cell()

    def _check_uniq_cell(self):
        "Kontrollime, et samas ruudus pole mitu kysimust"
        pos = {}
        err = []
        for k in self.block.kysimused:
            t_k = k.tran(self.lang)
            key = (t_k.pos_x, t_k.pos_y)
            if pos.get(key):
                pos[key].append(k.kood)
            else:
                pos[key] = [k.kood]
        for key, values in pos.items():
            if len(values) > 1:
                err.append('Ruudus [%d,%d] on mitu küsimust: %s' % \
                           (key[0]+1, key[1]+1, ', '.join(values)))
        if err:
            raise ValidationError(self.handler, {}, '\n '.join(err))
        
    def check(self, arvutihinnatav):
        rc = True
        li = []
        
        kysimus = self.block.kysimus
        if arvutihinnatav:
            if not kysimus.tulemus:
                rc = False
                li.append(_("Puudub hindamismaatriks"))
            else:
                if not kysimus.best_entries():
                    rc = False
                    li.append(_("Õige vastus on määramata"))
        return rc, li

    def update_kysimus(self, kysimus, is_tr=False):
        errors = {}
        ldata = self.form_result['l']
        if 'pikkus' in ldata and not ldata['pikkus']:
            for r in self.form_result['am1'].get('hm1'):
                # kui pikkust pole antud, kasutame hindamismaatriksis oleva sõna pikkust
                if r['kood1']:
                    ldata['pikkus'] = len(r['kood1'])
                    break
            if not ldata['pikkus']:
                errors['l.pikkus'] = _("puudub")
                raise ValidationError(self.handler, errors)
        
        if is_tr:
            self._give_k_tran(kysimus)
            
        kysimus.from_form(ldata, lang=self.lang)
        if is_tr:
            self._tran_update_mapping(kysimus)           
        else:
            self._update_mapping(kysimus,
                                 basetype=const.BASETYPE_STRING,
                                 cardinality=const.CARDINALITY_SINGLE)
            self._unique_kysimus(kysimus)

        tulemus = kysimus.tulemus
        tulemus.tostutunne = True

        mo = kysimus.sisuobjekt
        mo_data = self.form_result['mo']
        is_new_file = mo_data.get('filedata') != b''
        is_old_file = self.form_result.get('mo_id')
        if is_new_file or is_old_file:
            if mo is None:
                mo = model.Piltobjekt(kood=kysimus.kood, sisuplokk=self.block)
                kysimus.sisuobjekt = mo
            mo.kood = kysimus.kood
            mo.from_form(mo_data, lang=self.lang)
            COLSIZE = 50
            if is_new_file and (mo.laius > COLSIZE or mo.korgus > COLSIZE):
                if mo.laius > mo.korgus:
                    mo.laius = COLSIZE
                    mo.korgus = mo.laius * mo.korgus_orig / mo.laius_orig
                else:
                    mo.korgus = COLSIZE
                    mo.laius = mo.korgus * mo.laius_orig / mo.korgus_orig
        elif mo and not is_tr:
            mo.delete()

        self._check_crossword_size(kysimus)

    def tran_update_kysimus(self, kysimus):
        self.update_kysimus(kysimus, True)

    def _check_crossword_size(self, kysimus):
        errors = {}
        data, cols, rows = self.block.get_crossword_map(self.lang)
        t_kysimus = kysimus.tran(self.lang)
        pikkus = t_kysimus.pikkus
        title_x, title_y = t_kysimus.pos_x, t_kysimus.pos_y
        n_char = 0

        def _on_kysimus(value):
            return value.title_k is not None
        
        # kontrollime, et vaba ruumi on sõna pikkuse jaoks piisavalt
        for n_char in range(1, pikkus + 1):
            is_available = True
            suund = t_kysimus.joondus
            if suund == const.DIRECTION_DOWN:
                if title_y + n_char == rows or _on_kysimus(data[title_y + n_char][title_x]):
                    is_available = False
            elif suund == const.DIRECTION_UP:
                if title_y - n_char < 0 or _on_kysimus(data[title_y - n_char][title_x]):
                    is_available = False
            elif suund == const.DIRECTION_RIGHT:
                if title_x + n_char == cols or _on_kysimus(data[title_y][title_x + n_char]):
                    is_available = False
            elif suund == const.DIRECTION_LEFT:
                if title_x - n_char < 0 or _on_kysimus(data[title_y][title_x - n_char]):
                    is_available = False
            if not is_available:
                errors = {'l.pikkus': _("Nii pikk sõna ei mahu ära (mahub max {n} tähte)").format(n=n_char-1)}
                break

        if errors:
            raise ValidationError(self.handler, errors)                

    def _move_crossword(self):

        def _char_pos(k, title_x, title_y, direction, n_char):
            "Leiame sõna n. tähe positsiooni"
            if direction == const.DIRECTION_RIGHT:
                return title_x + n_char, title_y
            elif direction == const.DIRECTION_LEFT:
                return title_x - n_char, title_y
            elif direction == const.DIRECTION_UP:
                return title_x, title_y - n_char
            elif direction == const.DIRECTION_DOWN:
                return title_x, title_y + n_char

        dx = dy = 0
        move_cnt = self.form_result.get('move_cnt') or 0
        if move_cnt:
            move_dir = self.form_result.get('move_dir')
            if move_dir == const.DIRECTION_LEFT:
                dx = 0 - move_cnt
            elif move_dir == const.DIRECTION_RIGHT:
                dx = move_cnt
            elif move_dir == const.DIRECTION_UP:
                dy = 0 - move_cnt
            elif move_dir == const.DIRECTION_DOWN:
                dy = move_cnt

        t_block = self.block.tran(self.lang)
        cols = t_block.laius or 1 
        rows = t_block.korgus or 1
        for k in self.block.kysimused:
            t_k = self._give_k_tran(k)
            title_x, title_y = t_k.pos_x, t_k.pos_y
            if title_x is None or title_y is None:
                continue
            if dx or dy:
                title_x += dx
                title_y += dy

            # kontrollime, et sõna mahub peale nihutamist ära
            if t_k.pikkus:
                # sõna kysimus
                w_x, w_y = _char_pos(k, title_x, title_y, t_k.joondus, t_k.pikkus)
            else:
                # etteantud täht
                w_x = title_x
                w_y = title_y
            if min(title_x, w_x) < 0 or max(title_x, w_x) >= cols or \
                   min(title_y, w_y) < 0 or max(title_y, w_y) >= rows:
                errors = {}
                err = _("Ristsõna ei mahu ruudustikule")
                if dx or dy:
                    # nihutati
                    errors['move_cnt'] = err
                else:
                    # muudeti suurust
                    if max(title_x, w_x) > cols:
                        errors['f_laius'] = err
                    else:
                        errors['f_korgus'] = err
                raise ValidationError(self.handler, errors)                
            if dx:
                t_k.pos_x += dx
            if dy:
                t_k.pos_y += dy

    def edit_kysimus(self, kysimus):
        """Sisuploki koostamine
        """
        template = '/sisuplokk/icrossword.kysimus.mako'
        self.c.block = self.block
        self.c.kysimus = kysimus
        self.c.is_sp_edit = True
        return self.handler.render(template)

    def _unique_map_entry_row(self, v, tulemus, kysimus, is_tran=False):
        msg = None
        kood1 = v['kood1'] = v['kood1'].upper()
        if len(kood1) != kysimus.tran(self.lang).pikkus:
            msg = _("Sõna pikkus erineb kirjeldatud pikkusest")
        return msg

    def _give_k_tran(self, kysimus):
        "Luuakse kysimuse tõlge"
        if self.lang:
            t_k = kysimus.tran(self.lang, False)
            if not t_k:
                # kui tõlke kirjet veel ei ole, siis loome kirje
                # ja kopeerime põhikirjest väärtused
                t_k = kysimus.give_tran(self.lang)
                t_k.pikkus = kysimus.pikkus
                t_k.vihje = kysimus.vihje
                t_k.pos_x = kysimus.pos_x
                t_k.pos_y = kysimus.pos_y
                t_k.joondus = kysimus.joondus
        else:
            t_k = kysimus
        return t_k
    
class _mathInteractionController(BlockController):
    _TEMPLATE_NAME = 'imath'

    def include_edit(self):
        self.c.includes['math'] = True        

    def include_view(self):
        self.c.includes['math'] = True        

    def check(self, arvutihinnatav):
        rc = True
        li = []
        kysimus = self.block.kysimus
        if arvutihinnatav:
            if not kysimus.tulemus:
                rc = False
                li.append(_("Puudub hindamismaatriks"))
            else:
                if not kysimus.best_entries():
                    rc = False
                    li.append(_("Õige vastus on määramata"))
        return rc, li

    def update(self, is_tr, not_locked):
        if not_locked and not is_tr:
            self._update_staatus()
            kysimus = self.block.kysimus
            kysimus.from_form(self.form_result['l'])
            if kysimus.vihje and kysimus.vihje.strip() != '':
                kysimus.algvaartus = True
            else:
                kysimus.algvaartus = None
                kysimus.vihje = None

            if kysimus.max_vastus == 1:
                cardinality = const.CARDINALITY_SINGLE
            else:
                cardinality = const.CARDINALITY_MULTIPLE
            self._update_mapping(kysimus,
                                 basetype=const.BASETYPE_MATH,
                                 cardinality=cardinality)
            self._unique_kysimus(kysimus)
            
        if is_tr:
            kysimus = self.block.kysimus            
            self._tran_update_mapping(kysimus)


class _wmathInteractionController(BlockController):
    _TEMPLATE_NAME = 'iwmath'

    def include_edit(self):
        self.c.includes['wiris'] = True        

    def include_view(self):
        self.c.includes['wiris'] = True        

    def check(self, arvutihinnatav):
        rc = True
        li = []
        kysimus = self.block.kysimus
        if arvutihinnatav:
            if not kysimus.tulemus:
                rc = False
                li.append(_("Puudub hindamismaatriks"))
            else:
                if not kysimus.best_entries():
                    rc = False
                    li.append(_("Õige vastus on määramata"))
        return rc, li

    def update(self, is_tr, not_locked):
        if not_locked and not is_tr:
            self._update_staatus()
            kysimus = self.block.kysimus
            kysimus.from_form(self.form_result['l'])
            if kysimus.vihje and kysimus.vihje.strip() != '':
                kysimus.algvaartus = True
            else:
                kysimus.algvaartus = None
                kysimus.vihje = None
                
            if kysimus.max_vastus == 1:
                cardinality = const.CARDINALITY_SINGLE
            else:
                cardinality = const.CARDINALITY_MULTIPLE
            self._update_mapping(kysimus,
                                 basetype=const.BASETYPE_MATHML,
                                 cardinality=cardinality)
            self._unique_kysimus(kysimus)
            
        if is_tr:
            kysimus = self.block.kysimus            
            self._tran_update_mapping(kysimus)


class _sliderInteractionController(BlockController):
    _TEMPLATE_NAME = 'islider'
    def update(self, is_tr, not_locked):
        kysimus = self.block.kysimus
        kyslisa = kysimus.give_kyslisa()
        if not_locked and not is_tr:
            kyslisa.from_form(self.form_result['sl'])

        if not is_tr:
            self._update_mapping(self.block.kysimus,
                                 cardinality=const.CARDINALITY_SINGLE)
            self._check_hm()
            self._update_staatus()        
            self._unique_kysimus(self.block.kysimus)
        else:
            kyslisa.give_tran(self.lang).yhik = self.form_result['sl']['yhik']

    def _check_hm(self):
        """Kontrollitakse, et hindamismaatriksisse oleks sisestatud mõistlikud väärtused.
        """
        prefix = 'am1'
        kyslisa = self.block.kysimus.give_kyslisa()
        min_vaartus = kyslisa.min_vaartus
        max_vaartus = kyslisa.max_vaartus
        samm = kyslisa.samm
        am = self.form_result.get(prefix)
        basetype = am.get('baastyyp')
        collection = am.get('hm1')
        errors = {}
        diff = 1e-12

        for n,rcd in enumerate(collection):
            alates = _float_c(rcd['kood1'])
            kuni = rcd.get('kood2')
            if kuni:
                kuni = _float_c(kuni)
            else:
                kuni = alates

            msg = None
            if alates + diff < min_vaartus:
                msg = _("Ei tohi olla väiksem kui {s}").format(s=h.fstr(min_vaartus))
            elif kuni - diff > max_vaartus:
                msg = _("Ei tohi olla suurem kui {s}").format(s=h.fstr(max_vaartus))

            if not msg and samm:
                # kui pole vahemik, siis kontrollime, kas väärtus on saavutatav
                i = min_vaartus
                found = False
                while i <= max_vaartus + diff:
                    if alates - diff < i < kuni + diff:
                        found = True
                        break
                    i += samm
                if not found:
                    msg = _("Väärtus pole valitud sammuga saavutatav")

            if msg:
                errors['%s.hm1-%d.kood1' % (prefix, n)] = msg

        if errors:
            self._raise_error(errors)

    def check(self, arvutihinnatav):
        rc = True
        li = []
        kysimus = self.block.kysimus
        if arvutihinnatav:
            if not kysimus.tulemus:
                rc = False
                li.append(_("Puudub hindamismaatriks"))
            elif not kysimus.best_entries():
                rc = False
                li.append(_("Õige vastus on määramata"))

        return rc, li

#########################################################
# Piltküsimused

class _positionObjectInteractionController(BlockController):
    _TEMPLATE_NAME = 'ipos'
    def update(self, is_tr, not_locked):
        if not_locked:
            self._update_taustobjekt()
            images = self.form_result['mod']
            self._update_drag_images(images, is_tr)
            model.Session.flush()
            
        if not is_tr:
            self._update_staatus()
            kysimused = []
            for obj in self.block.piltobjektid:
                kysimus = obj.give_kysimus()
                kysimus.min_vastus = obj.min_vastus
                kysimus.max_vastus = obj.max_vastus
                kysimus.seq = obj.seq
                kysimus.kood = obj.kood
                kysimused.append((kysimus, obj))

            # kas on vaja kopeerida
            is_copyarea = self.request.params.get('copyarea')
            # kust on vaja kopeerida
            tulemus1 = None

            for n, am in enumerate(self.form_result['am']):
                kysimus, obj = kysimused[n]
                am['kood'] = obj.kood
                self._update_mapping(kysimus, 
                                     basetype=const.BASETYPE_POINT,
                                     cardinality=const.CARDINALITY_MULTIPLE,                                                 
                                     prefix='am-%d' % n,
                                     am=am,
                                     copy_from_t=tulemus1)
                tulemus = kysimus.tulemus
                tulemus.kood = obj.kood
                if is_copyarea and not tulemus1:
                    # selle maatriksi kopeerime teistele kysimustele
                    tulemus1 = tulemus
                    
    def include_edit(self):
        self.c.includes['raphael'] = True
        self.c.includes['dropzone'] = True
        self.c.includes['fancybox'] = True

    def include_view(self):
        self.c.includes['raphael'] = True

    def check(self, arvutihinnatav):
        rc = True
        li = []
        kysimus = self.block.kysimus
        if arvutihinnatav:
            if len(self.block.piltobjektid) == 0:
                rc = False
                li.append(_("Puuduvad lohistatavad pildid"))
            else:
                for rcd in self.block.piltobjektid:
                    if not rcd.tulemus:
                        rc = False
                        li.append(_("Pildil {s} puudub hindamismaatriks").format(s=rcd.kood))

        mo = self.block.taustobjekt
        if not mo or not mo.has_file and not mo.fileurl:
            rc = False
            li.append(_("Puudub taustobjekt"))
                
        return rc, li

class _positionObject2InteractionController(BlockController):
    _TEMPLATE_NAME = 'ipos2'
    def update(self, is_tr, not_locked):
        prkkysimus = self.block.give_baaskysimus(1, True)
        if not_locked:
            mo = self._update_taustobjekt()
            if not is_tr:
                # piirkonnad - prkkysimus
                self._update_hotspots_x(prkkysimus, mo)

            images = self.form_result['mod']
            self._update_drag_images(images, is_tr)
            model.Session.flush()
            
        if not is_tr:
            self._update_staatus()
            kysimused = []
            for obj in self.block.piltobjektid:
                kysimus = obj.give_kysimus()
                kysimus.min_vastus = obj.min_vastus
                kysimus.max_vastus = obj.max_vastus
                kysimus.seq = obj.seq
                kysimus.kood = obj.kood
                kysimused.append((kysimus, obj))

            # kas on vaja kopeerida
            is_copyarea = self.request.params.get('copyarea')
            # kust on vaja kopeerida
            tulemus1 = None

            for n, am in enumerate(self.form_result['am']):
                kysimus, obj = kysimused[n]
                am['kood'] = obj.kood
                self._update_mapping(kysimus, 
                                     basetype=const.BASETYPE_IDENTIFIER,
                                     cardinality=const.CARDINALITY_MULTIPLE,                                                 
                                     prefix='am-%d' % n,
                                     am=am,
                                     copy_from_t=tulemus1)
                tulemus = kysimus.tulemus
                tulemus.kood = obj.kood
                if is_copyarea and not tulemus1:
                    # selle maatriksi kopeerime teistele kysimustele
                    tulemus1 = tulemus
                    
    def include_edit(self):
        self.c.includes['raphael'] = True
        self.c.includes['dropzone'] = True
        self.c.includes['fancybox'] = True

    def include_view(self):
        self.c.includes['raphael'] = True

    def check(self, arvutihinnatav):
        rc = True
        li = []
        prkkysimus = self.block.get_baaskysimus(1)
        if len(prkkysimus.valikud) == 0:
            rc = False
            li.append(_("Puuduvad piirkonnad"))

        mo = self.block.taustobjekt
        if arvutihinnatav:
            if len(self.block.piltobjektid) == 0:
                rc = False
                li.append(_("Puuduvad lohistatavad pildid"))
            else:
                for rcd in self.block.piltobjektid:
                    li = [k for k in rcd.kysimused if k.tulemus]
                    if not li:
                        rc = False
                        li.append(_("Pildil {s} puudub hindamismaatriks").format(s=rcd.kood))

        if not mo or not mo.has_file and not mo.fileurl:
            rc = False
            li.append(_("Puudub taustobjekt"))
                
        return rc, li

    def set_valikvastused(self):
        prkkysimus = self.block.give_baaskysimus(1)
        for kysimus in self.block.pariskysimused:
            tulemus = kysimus.tulemus
            if tulemus:
                tulemus.set_valikvastus(prkkysimus.id, None, paarina=None)

class _positionTextInteractionController(BlockController):
    _TEMPLATE_NAME = 'itxpos'

    def include_edit(self):
        self.c.includes['ckeditor'] = True
        self.c.includes['raphael'] = True
        
    def include_view(self):
        self.c.includes['raphael'] = True
        self.c.includes['masonry'] = True
        
    def update(self, is_tr, not_locked):
        if not_locked:
            self._update_taustobjekt()

        bkysimus = self.block.kysimus
        bkysimus.rtf_old = bkysimus.rtf        
        if is_tr:
            self._tran_update_choices()
        elif not_locked:
            for r in self.form_result['v']:
                if not r['eraldi']:
                    r['eraldi'] = False
            l = self.form_result.get('l')
            if l:
                bkysimus.from_form(l)
                if bkysimus.min_vastus is None:
                    bkysimus.min_vastus = 1
            # update_choices teha peale bkysimus.from_form(), ette mitte yle kirjutada v_rtf
            self._update_choices()
            self._update_staatus()

        if not is_tr:
            # kas on vaja kopeerida
            is_copyarea = self.request.params.get('copyarea')
            # kust on vaja kopeerida
            tulemus1 = None
            # kysimuste koodid
            koodid = []
            for valik in bkysimus.valikud:
                t_valik = valik.tran(self.lang)
                koodid.append(valik.kood)
                kysimus = self.block.give_kysimus(kood=valik.kood)
                kysimus.min_vastus = valik.min_vastus
                kysimus.max_vastus = valik.max_vastus
                # +1 tuleb sellest, et sisuploki kysimus peab jääma seq=1
                kysimus.seq = valik.seq + 1
                if kysimus.id:
                    # varem olemas olnud kysimuse hindamismaatriks on ka postis
                    for n, am in enumerate(self.form_result['am']):
                        if am['kysimus_id'] == kysimus.id:
                            am['k_selgitus'] = valik.selgitus
                            self._update_mapping(kysimus, 
                                                 basetype=const.BASETYPE_POINT, 
                                                 prefix='am-%d' % n,
                                                 am=am,
                                                 copy_from_t=tulemus1)
                            tulemus = kysimus.tulemus
                            tulemus.kood = kysimus.kood = valik.kood
                            if is_copyarea and not tulemus1:
                                # selle maatriksi kopeerime teistele kysimustele
                                tulemus1 = tulemus
        model.Session.flush()
        if not is_tr and not_locked:
            for kysimus in self.block.kysimused:
                k_kood = kysimus.kood
                if kysimus.seq > 1 and k_kood not in koodid:
                    kysimus.delete()

    def check(self, arvutihinnatav):
        rc = True
        li = []
        bkysimus = self.block.kysimus
        if len(bkysimus.valikud) == 0:
            rc = False
            li.append(_("Valikuid on liiga vähe"))
        if arvutihinnatav:
            for valik in bkysimus.valikud:
                kysimus = self.block.get_kysimus(kood=valik.kood)
                if not kysimus or not kysimus.tulemus:
                    rc = False
                    li.append(_("Puudub küsimuse {s} hindamismaatriks").format(s=valik.kood) + '\n')
        mo = self.block.taustobjekt
        if not mo or not mo.has_file and not mo.fileurl:
            rc = False
            li.append(_("Puudub taustobjekt"))
                
        return rc, li

    def gen_selgitused(self, overwrite):
        """Genereeritakse valikute selgitused statistikute jaoks"""
        BlockController.gen_selgitused(self, overwrite)
        
        # kopeerime valikute selgitused kysimusele
        bkysimus = self.block.kysimus
        for valik in bkysimus.valikud:
            kysimus = self.block.give_kysimus(kood=valik.kood)
            kysimus.selgitus = valik.selgitus

class _txpos2InteractionController(BlockController):
    # tekstide lohistamine II
    _TEMPLATE_NAME = 'itxpos2'
    def update(self, is_tr, not_locked):
        bkysimus = self.block.give_baaskysimus(1, True)
        prkkysimus = self.block.give_baaskysimus(2, True)

        if not_locked:
            mo = self._update_taustobjekt()
            if not is_tr:
                # piirkonnad - prkkysimus
                self._update_hotspots_x(prkkysimus, mo)
                self._update_staatus()
                
        # valikute tekstid - bkysimus
        if is_tr:
            self._tran_update_choices(bkysimus)
        else:
            l = self.form_result.get('l')
            if l:
                bkysimus.min_vastus = l.get('min_vastus')
                bkysimus.max_vastus = l.get('max_vastus')

            self._update_choices(bkysimus)
            # kysimuste koodid
            koodid = []
            for valik in bkysimus.valikud:
                koodid.append(valik.kood)
                kysimus = self.block.give_kysimus(kood=valik.kood)
                kysimus.min_vastus = valik.min_vastus
                kysimus.max_vastus = valik.max_vastus
                kysimus.selgitus = valik.selgitus
                # +2 tuleb sellest, et baaskysimused on 1 ja 2
                kysimus.seq = valik.seq + 2
                if kysimus.id:
                    # varem olemas olnud kysimuse hindamismaatriks on ka postis
                    for n, am in enumerate(self.form_result['am']):
                        if am['kysimus_id'] == kysimus.id:
                            am['k_selgitus'] = valik.selgitus
                            self._update_mapping(kysimus, 
                                                 basetype=const.BASETYPE_IDENTIFIER, 
                                                 prefix='am-%d' % n,
                                                 am=am)
                            tulemus = kysimus.tulemus
                            tulemus.kood = kysimus.kood = valik.kood

            model.Session.flush()
            if not is_tr and not_locked:
                for kysimus in self.block.pariskysimused:
                    k_kood = kysimus.kood
                    if kysimus.seq > 2 and k_kood not in koodid:
                        kysimus.delete()

    def include_edit(self):
        self.c.includes['ckeditor'] = True
        self.c.includes['raphael'] = True

    def include_view(self):
        self.c.includes['raphael'] = True        
        self.c.includes['masonry'] = True
        
    def _export_files(self, exporter):
        exporter.export_hotspots(self.block.taustobjekt)

    def check(self, arvutihinnatav):
        rc = True
        li = []
        
        bkysimus = self.block.get_baaskysimus(1)
        prkkysimus = self.block.get_baaskysimus(2)
        pariskysimused = self.block.pariskysimused
        mo = self.block.taustobjekt
        if not mo or not mo.has_file and not mo.fileurl:
            rc = False
            li.append(_("Puudub taustobjekt"))
        if not bkysimus or not len(bkysimus.valikud) or not len(pariskysimused):
            rc = False
            li.append(_("Puuduvad lohistatavad tekstid"))
        if len(prkkysimus.valikud) == 0:
            rc = False
            li.append(_("Puuduvad piirkonnad"))
        return rc, li

    def gen_selgitused(self, overwrite):
        """Genereeritakse valikute selgitused statistikute jaoks"""
        bkysimus = self.block.give_baaskysimus(1)
        kysimused = {k.kood: k for k in self.block.pariskysimused}
        for valik in bkysimus.valikud:
            if valik.nimi and (overwrite or not valik.selgitus):
                if bkysimus.rtf:
                    selgitus = _html2txt(valik.nimi)
                else:
                    selgitus = valik.nimi
                valik.selgitus = selgitus[:255]
                k = kysimused.get(valik.kood)
                if k:
                    k.selgitus = valik.selgitus

    def set_valikvastused(self):
        prkkysimus = self.block.give_baaskysimus(2)
        for kysimus in self.block.pariskysimused:
            tulemus = kysimus.tulemus
            if tulemus:
                tulemus.set_valikvastus(prkkysimus.id, None, paarina=None)

class _txgapInteractionController(BlockController):
    # tekstide lohistamine kujunditele
    _TEMPLATE_NAME = 'itxgap'
    def update(self, is_tr, not_locked):
        bkysimus = self.block.give_baaskysimus(1, True)
        prkkysimus = self.block.give_baaskysimus(2, True)

        if not_locked:
            mo = self._update_taustobjekt()
            if not is_tr:
                # piirkonnad - prkkysimus
                self._update_hotspots(prkkysimus)
                self._update_staatus()
                
        # valikute tekstid - bkysimus
        if is_tr:
            self._tran_update_choices(bkysimus)
        else:
            l = self.form_result.get('l')
            if l:
                bkysimus.min_vastus = l.get('min_vastus')
                bkysimus.max_vastus = l.get('max_vastus')

            self._update_choices(bkysimus)
            # kysimuste koodid
            koodid = []
            for valik in bkysimus.valikud:
                koodid.append(valik.kood)
                kysimus = self.block.give_kysimus(kood=valik.kood)
                kysimus.min_vastus = valik.min_vastus
                kysimus.max_vastus = valik.max_vastus
                kysimus.selgitus = valik.selgitus
                # +2 tuleb sellest, et baaskysimused on 1 ja 2
                kysimus.seq = valik.seq + 2
                if kysimus.id:
                    # varem olemas olnud kysimuse hindamismaatriks on ka postis
                    for n, am in enumerate(self.form_result['am']):
                        if am['kysimus_id'] == kysimus.id:
                            am['k_selgitus'] = valik.selgitus
                            self._update_mapping(kysimus, 
                                                 basetype=const.BASETYPE_IDENTIFIER, 
                                                 prefix='am-%d' % n,
                                                 am=am)
                            tulemus = kysimus.tulemus
                            tulemus.kood = kysimus.kood = valik.kood

            model.Session.flush()
            if not is_tr and not_locked:
                for kysimus in self.block.pariskysimused:
                    k_kood = kysimus.kood
                    if kysimus.seq > 2 and k_kood not in koodid:
                        kysimus.delete()

    def include_edit(self):
        self.c.includes['ckeditor'] = True
        self.c.includes['raphael'] = True

    def include_view(self):
        self.c.includes['raphael'] = True        
        self.c.includes['masonry'] = True
        
    def _export_files(self, exporter):
        exporter.export_hotspots(self.block.taustobjekt)

    def check(self, arvutihinnatav):
        rc = True
        li = []
        
        bkysimus = self.block.get_baaskysimus(1)
        prkkysimus = self.block.get_baaskysimus(2)
        pariskysimused = self.block.pariskysimused
        mo = self.block.taustobjekt
        if not mo or not mo.has_file and not mo.fileurl:
            rc = False
            li.append(_("Puudub taustobjekt"))
        if not bkysimus or not len(bkysimus.valikud) or not len(pariskysimused):
            rc = False
            li.append(_("Puuduvad lohistatavad tekstid"))
        if len(prkkysimus.valikud) == 0:
            rc = False
            li.append(_("Puuduvad piirkonnad"))
        return rc, li

    def gen_selgitused(self, overwrite):
        """Genereeritakse valikute selgitused statistikute jaoks"""
        bkysimus = self.block.give_baaskysimus(1)
        kysimused = {k.kood: k for k in self.block.pariskysimused}
        for valik in bkysimus.valikud:
            if valik.nimi and (overwrite or not valik.selgitus):
                if bkysimus.rtf:
                    selgitus = _html2txt(valik.nimi)
                else:
                    selgitus = valik.nimi
                valik.selgitus = selgitus[:255]
                k = kysimused.get(valik.kood)
                if k:
                    k.selgitus = valik.selgitus

    def set_valikvastused(self):
        prkkysimus = self.block.give_baaskysimus(2)
        for kysimus in self.block.pariskysimused:
            tulemus = kysimus.tulemus
            if tulemus:
                tulemus.set_valikvastus(prkkysimus.id, None, paarina=None)

class _txassInteractionController(_txgapInteractionController):
    # tekstide seostamine kujunditega
    _TEMPLATE_NAME = 'itxass'

    def _update_taustobjekt(self):
        """Taustapildi salvestamine
        """
        t = super()._update_taustobjekt()
        if t.asend == model.Sisuobjekt.ASEND_PAREMAL and t.laius > 800:
            raise ValidationError(self.handler,
                                  {'mo.asend': _("Ülesanne on liiga lai, tekstid ei mahu pildiga kõrvuti!")})
        return t

class _drawingInteractionController(BlockController):
    _TEMPLATE_NAME = 'idraw'
    def update(self, is_tr, not_locked):
        kysimus = self.block.kysimus
        jo = self.form_result.get('jo')
        if not is_tr:
            arvutihinnatav = jo and jo.get('on_arvutihinnatav')
        else:
            arvutihinnatav = kysimus.give_joonistamine().on_arvutihinnatav

        if arvutihinnatav:
            self._update_arvutihinnatav(is_tr, not_locked)
        else:
            self._update_naidisvastus(is_tr, not_locked)

        if is_tr:
            self._tran_update_mapping(kysimus)
        else:
            self._update_mapping(kysimus,
                                 basetype=const.BASETYPE_POLYLINE,
                                 cardinality=const.CARDINALITY_MULTIPLE)
            self._unique_kysimus(kysimus)
           
        if not is_tr:
            self._update_staatus()
            
    def _update_arvutihinnatav(self, is_tr, not_locked):
        joonistamine = self.block.kysimus.give_joonistamine()
        if not_locked:
            joonistamine.on_arvutihinnatav = True
            self._update_taustobjekt()
            if not is_tr:
                l = self.form_result.get('l')
                if l:
                    self.block.kysimus.from_form(l)

            jo = self.form_result.get('jo')
            if not is_tr and jo:
                self._save_tools(joonistamine, jo)
                
    def _update_naidisvastus(self, is_tr, not_locked):
        kysimus = self.block.kysimus
        joonistamine = self.block.kysimus.give_joonistamine()

        if not_locked:
            joonistamine.on_arvutihinnatav = False
            self._update_taustobjekt()
            jo = self.form_result.get('jo')
            if not is_tr and jo:
                self._save_tools(joonistamine, jo)

            # näidispilt javascriptina
            skript = self.handler.request.params.get(self.block.get_result());
            self.block.sisuvaade = skript


    def _save_tools(self, joonistamine, jo):
        # joonistustarbed
        request = self.handler.request
        tarbed = jo.get('tarve')
        if tarbed:
            if isinstance(tarbed, list):
                # mitu tarvet
                joonistamine.tarbed = ';'.join(tarbed)
            else:
                # ainult yks tarve
                joonistamine.tarbed = tarbed
        else:
            joonistamine.tarbed = None
        
        joonistamine.on_seadistus = jo.get('on_seadistus')
        joonistamine.stroke_width = self.form_result.get('draw_width')
        joonistamine.stroke_color = self.form_result.get('draw_stroke')
        joonistamine.fill_none = self.form_result.get('draw_fill_none')
        joonistamine.fill_color = self.form_result.get('draw_fill')
        joonistamine.fill_opacity = self.form_result.get('draw_fill_opacity')
        joonistamine.fontsize = self.form_result.get('draw_fontsize')
        joonistamine.textfill_color = self.form_result.get('draw_textfill')

    def include_edit(self):
        self.c.includes['raphael'] = True

    def include_view(self):
        self.c.includes['raphael'] = True        

    def check(self, arvutihinnatav):
        rc = True
        li = []
        kysimus = self.block.kysimus
        mo = self.block.taustobjekt
        if not mo or not mo.has_file and not mo.fileurl:
            rc = False
            li.append(_("Puudub taustobjekt"))
        
        return rc, li

class _graphicGapMatchInteractionController(BlockController):
    _TEMPLATE_NAME = 'igrgap'
    def update(self, is_tr, not_locked):
        kysimus = self.block.give_kysimus(1)
        if not_locked:
            self._update_taustobjekt()
            if not is_tr:
                kysimus.from_form(self.form_result['l'])
                self._update_staatus()
            images = self.form_result['mod']
            self._update_drag_images(images, is_tr)           

            if not is_tr:
                self._update_hotspots(kysimus)

        if is_tr:
            self._tran_update_mapping(kysimus)
        else:
            if not_locked:
                max_vastus_arv = 0
                for obj in self.block.piltobjektid:
                    max_vastus_arv += obj.max_vastus or 1
                if kysimus.max_vastus is None or kysimus.max_vastus > max_vastus_arv or \
                       kysimus.max_vastus == 0:
                    # kui max_vastus on määramata või liiga suur või 0,
                    # siis kirjutame yle
                    kysimus.max_vastus = max_vastus_arv

            self._update_mapping(kysimus,
                                 basetype=const.BASETYPE_DIRECTEDPAIR,
                                 cardinality=const.CARDINALITY_MULTIPLE)
            self._unique_kysimus(kysimus)
            self._set_valikud_max_p(kysimus)

    def _set_valikud_max_p(self, kysimus):
        tulemus = kysimus.tulemus
        if tulemus:
            bkysimus2 = self.block.give_baaskysimus(2, True)
            self._set_valik_max_p(bkysimus2, tulemus, [(1, 1)], kysimus.max_vastus)
        
    def include_edit(self):
        self.c.includes['raphael'] = True
        self.c.includes['dropzone'] = True
        self.c.includes['fancybox'] = True

    def include_view(self):
        self.c.includes['raphael'] = True        

    def _update_drag_images(self, images, is_tr):
        """Lohistatavate piltide andmete salvestamine, piltide kustutamine
        Piltide lisamine vt piltobjektid.py
        """
        bkysimus2 = self.block.give_baaskysimus(2, True)
        piltvalikud = list(bkysimus2.valikud)

        def _give_piltvalik(kood):
            for v in piltvalikud:
                if v.kood == kood:
                    piltvalikud.remove(v)
                    return v
            v = model.Valik(kood=kood)
            bkysimus2.valikud.append(v)
            return v
        
        data = {r['id']: r for r in images}
        seq = 0
        for obj in list(self.block.piltobjektid):
            rcd = data.get(obj.id)
            if rcd:
                # muuta
                seq += 1
                obj.from_form(rcd, lang=self.lang)
                obj.seq = seq
                if not is_tr:
                    # loome valiku kirje, kus hoida selgitust
                    valik = _give_piltvalik(obj.kood)
                    valik.seq = seq
                    valik.selgitus = rcd['selgitus']
                    valik.max_vastus = obj.max_vastus
            elif is_tr:
                # kustutada tõlge
                tr_obj = obj.tran(self.lang, False)
                if tr_obj:
                    tr_obj.delete()
            else:
                # kustutada põhikirje
                obj.delete()

        if not is_tr:
            # eemaldame nende piltide selgitused, mida enam pole
            for v in piltvalikud:
                v.delete()

    def _export_files(self, exporter):
        exporter.export_hotspots(self.block.taustobjekt)
        for obj in self.block.piltobjektid:
            exporter.export_obj(obj)

    def check(self, arvutihinnatav):
        rc = True
        li = []
        kysimus = self.block.kysimus

        if len(self.block.piltobjektid) == 0:
            rc = False
            li.append(_("Puuduvad lohistatavad pildid"))
        mo = self.block.taustobjekt
        if not mo or not mo.has_file and not mo.fileurl:
            rc = False
            li.append(_("Puudub taustobjekt"))
        if len(kysimus.valikud) == 0:
            rc = False
            li.append(_("Puuduvad piirkonnad"))
        return rc, li

    def set_valikvastused(self):
        kysimus = self.block.give_kysimus(1)
        bkysimus2 = self.block.give_baaskysimus(2, True)
        tulemus = kysimus.tulemus
        if tulemus:
            tulemus.set_valikvastus(bkysimus2.id, kysimus.id, paarina=False)

class _colorareaController(BlockController):
    _TEMPLATE_NAME = 'icolorarea'
    def update(self, is_tr, not_locked):
        bkysimus = self.block.give_baaskysimus()
        if not_locked:
            self._update_taustobjekt()

            # salvestame värvid
            self._update_choices(bkysimus, is_tr=is_tr)

            if not is_tr:
                # salvestame piirkondade kysimused
                self._update_hotspots_k()
                self._update_staatus()

    def _update_choices(self, kysimus=None, rootdiv=True, is_tr=False):
        """Valikute salvestamine.
        """
        v = self.form_result['v']
        if not is_tr:
            self._unique_kood(v, 'v')
            self._valik_selgitus(v, kysimus.rtf)

            rtf_old = self.form_result.get('v_rtf_old')
            kysimus.rtf = self.form_result.get('v_rtf')
            if rtf_old and not kysimus.rtf:
                self._remove_rtf(kysimus, v)

        for ind, rcd in enumerate(v):
            if not rcd['varv']:
                errors = {'v-%d.varv' % ind: _("puudub")}
                raise ValidationError(self.handler, errors)                

        BaseGridController(kysimus.valikud, model.Valik).save(v, lang=self.lang)
        for v in kysimus.valikud:
            v.kysimus = kysimus

    def _update_hotspots_k(self):
        """Piirkond-kysimuste salvestamine.
        """
        # valikupiirkonnad
        rows = self.form_result['hs']
        # kui kohustuslikkuse märkeruut on valimata, siis ei ole kohustuslik
        for r in rows:
            if not r.get('min_vastus'):
                r['min_vastus'] = 0
            r['max_vastus'] = 1
            
        # ylesande teiste sisuplokkide kysimuste koodid
        ylesanne = self.ylesanne
        kkoodid = ylesanne.get_kysimus_koodid(self.block)
        # kontrollime, et valikupiirkondade koodid on kysimuse koodina unikaalsed
        self._unique_kood(rows, 'hs', kkoodid)

        # senised valikupiirkonnad
        valikupiirkonnad = [k.valikud[0] for k in self.block.pariskysimused if len(k.valikud)]

        class KValikGridController(BaseGridController):
            def create_subitem(self, rcd, lang=None):
                subitem = BaseGridController.create_subitem(self, rcd, lang)
                kysimus = model.Kysimus(sisuplokk=self.block,
                                        kood=subitem.kood)
                kysimus.valikud.append(subitem)
                subitem.kysimus = kysimus
                self.block.kysimused.append(kysimus)
                return subitem

            def delete_subitem(self, rcd):
                kysimus = rcd.kysimus
                kysimus.delete()
                self.block.kysimused.remove(kysimus)
                
        ctrl = KValikGridController(valikupiirkonnad, model.Valikupiirkond)
        ctrl.block = self.block
        ctrl.save(rows)

        # kysimuste järjekorranumbrid
        for k_seq, rcd in enumerate(rows):
            kood = rcd['kood']
            if kood:
                # leiame valiku
                for v in valikupiirkonnad:
                    if v.kood == kood:
                        v.kysimus.seq = k_seq + 1
                        break
                    
        # piirkond-kysimuste hindamismaatriksite salvestamine
        kysimused = {k.id:k for k in self.block.pariskysimused if k.id}
        for ind, am in enumerate(self.form_result['am']):
            kysimus = kysimused.get(am['kysimus_id'])
            if kysimus:
                valikupiirkond = kysimus.valikud[0]
                am['kood'] = valikupiirkond.kood
                kysimus.min_vastus = valikupiirkond.min_vastus
                kysimus.max_vastus = 1
                am['k_selgitus'] = valikupiirkond.selgitus
                kysimus.give_tulemus(True)
                self._update_mapping(kysimus,
                                     basetype=const.BASETYPE_IDENTIFIER,
                                     cardinality=const.CARDINALITY_SINGLE,
                                     prefix='am-%d' % ind,
                                     am=am)

    def include_edit(self):
        self.c.includes['raphael'] = True
        self.c.includes['spectrum'] = True
        
    def include_view(self):
        self.c.includes['raphael'] = True        

    def check(self, arvutihinnatav):
        rc = True
        li = []
        bkysimus = self.block.get_baaskysimus()
        if not bkysimus or len(bkysimus.valikud) == 0:
            rc = False
            li.append(_("Puuduvad värvid"))
        pariskysimused = list(self.block.pariskysimused)
        if not pariskysimused:
            rc = False
            li.append(_("Puuduvad piirkonnad"))
        for k in pariskysimused:
            if not k.valikud:
                rc = False
                li.append(_("Puuduvad piirkonnad"))
                break
        mo = self.block.taustobjekt
        if not mo or mo.filedata is None and mo.fileurl is None:
            rc = False
            li.append(_("Puudub taustobjekt"))
        return rc, li

    def set_valikvastused(self):
        bkysimus = self.block.give_baaskysimus()
        for kysimus in self.block.pariskysimused:
            if sa.inspect(kysimus).persistent:
                tulemus = kysimus.tulemus
                if tulemus:
                    tulemus.set_valikvastus(bkysimus.id, None, paarina=None)

    def gen_selgitused(self, overwrite):
        """Genereeritakse valikute selgitused statistikute jaoks"""
        kysimus = self.block.kysimus
        for valik in kysimus.valikud:
            if valik.nimi and (overwrite or not valik.selgitus):
                selgitus = valik.nimi
                valik.selgitus = selgitus[:255]

class _uncoverController(BlockController):
    _TEMPLATE_NAME = 'iuncover'
    def update(self, is_tr, not_locked):
        # baaskysimuse vastus on ABI-nupu kasutamise arv
        bkysimus = self.block.give_baaskysimus()
        if not_locked:
            if not is_tr:
                self._update_staatus()
                self._update_taustobjekt()
                ## salvestame min
                bkysimus.from_form(self.form_result['l'])
                bkysimus.ei_arvesta = True

            unc_data = self.form_result.get('unc') or {}
            cnt = self.block.laius and self.block.korgus and \
                  self.block.korgus * self.block.laius or 0
            cell_order = unc_data.get('cell_order') or []
            if cnt != len(cell_order):
                cell_order = list(range(1, cnt+1))
                random.shuffle(cell_order)
                unc_data['cell_order'] = cell_order
            if unc_data.get('evast_kasuta_muutmata'):
                unc_data['evast_kasuta'] = True
            self.block.set_json_sisu(unc_data, self.lang)
            self._update_kysimused(unc_data, bkysimus, is_tr)
            
    def _update_kysimused(self, unc_data, bkysimus, is_tr):
        """Valikute salvestamine.
        """
        if not self.block.korgus or not self.block.laius:
            return
        ylesanne = self.ylesanne
        
        # pildi ruutude juhusliku järjekorra genereerimine
        cnt = self.block.korgus * self.block.laius
        kysimused = {k.seq: k for k in self.block.kysimused if k.seq}

        if not is_tr:

            # loome ruudustiku iga ruudu jaoks yhe kysimuse
            k_cnt = (self.block.korgus or 0) * (self.block.laius or 0)
            for seq in range(1, k_cnt + 1):
                kysimus = kysimused.get(seq)
                if not kysimus:
                    def_kood = 'U%d' % (seq)
                    kood = ylesanne.gen_kysimus_kood(def_kood)
                    kysimus = model.Kysimus(sisuplokk=self.block,
                                            kood=kood,
                                            seq=seq)
                    self.block.kysimused.append(kysimus)
                    kysimused[seq] = kysimus

            # kustutame liigsed kysimused
            for k_seq in list(kysimused.keys()):
                if k_seq > k_cnt:
                    kysimus = kysimused[k_seq]
                    tulemus = kysimus.tulemus
                    if tulemus:
                        tulemus.delete()
                    kysimus.delete()
                    del kysimused[k_seq]

        # salvestame postitatud kysimuste sisu
        for ind, row in enumerate(self.form_result['unck']):
            prefix = 'unck-%d' % (ind)
            seq = row['seq']
            kysimus = kysimused.get(seq)
            if kysimus:
                kysimus.kood = row['kood']
                self._unique_kysimus(kysimus, prefix)
                valikud = list()
                kysimus.evast_edasi = unc_data.get('evast_edasi') and True or False
                kysimus.evast_kasuta = unc_data.get('evast_kasuta') and True or False
                kysimus.ei_arvesta = True

                for v_seq, v_kood in ((1, 'expr1'), (2, 'expr2')):
                    valik = kysimus.get_valik(v_kood)
                    if bkysimus.rtf:
                        v_nimi = row[v_kood + '_rtf']
                    else:
                        v_nimi = row[v_kood]
                    if v_nimi:
                        if is_tr:
                            if valik:
                                valik.give_tran(self.lang).nimi = v_nimi
                        else:
                            if valik:
                                valik.nimi = v_nimi
                                valik.seq = v_seq
                            else:
                                valik = model.Valik(kood=v_kood, nimi=v_nimi, seq=v_seq)
                                kysimus.valikud.append(valik)
                            valikud.append(valik)

                if not is_tr:
                    for valik in list(kysimus.valikud):
                        if valik not in valikud:
                            valik.delete()

                    # salvestame tulemuse kirje
                    tulemus = kysimus.give_tulemus()
                    tulemus.kood = kysimus.kood
                    tulemus.baastyyp = unc_data['baastyyp']
                    tulemus.kardinaalsus = const.CARDINALITY_SINGLE
                    tulemus.arvutihinnatav = True

                    value = row['expresp']
                    if tulemus.baastyyp == const.BASETYPE_INTEGER:
                        try:
                            int(value)
                        except:
                            raise ValidationError(self.handler, {}, _("Kõik vastused peavad olema täisarvud"))
                    elif tulemus.baastyyp == const.BASETYPE_FLOAT:
                        try:
                            float(value.replace(',','.'))
                        except:
                            raise ValidationError(self.handler, {}, _("Kõik vastused peavad olema reaalarvud"))

                    # salvestame 1 hindamismaatriksi kirje õige vastusega
                    rcd = {'id': None,
                           'kood1': str(value),
                           'kood2': None,
                           'oige': True,
                           'pallid': 1,
                           }
                    for hm in tulemus.hindamismaatriksid:
                        rcd['id'] = hm.id
                        break
                    g = BaseGridController(tulemus.hindamismaatriksid, model.Hindamismaatriks)
                    if is_tr:
                        g.update([rcd], lang=self.lang)
                    else:
                        g.save([rcd])
                
    def include_edit(self):
        self.c.includes['raphael'] = True
        self.c.includes['ckeditor'] = True        

    def include_view(self):
        self.c.includes['raphael'] = True        

class _trailInteractionController(BlockController):
    _TEMPLATE_NAME = 'itrail'
    def update(self, is_tr, not_locked):
        kysimus = self.block.kysimus
        if not_locked:
            self._update_taustobjekt()
            if not is_tr:
                kysimus.from_form(self.form_result['l'])
                kyslisa = kysimus.give_kyslisa()
                tl = self.form_result.get('tl')
                if tl:
                    kyslisa.from_form(tl)
                kysimus.max_vastus = 1
                self._update_staatus()
                errors = {}
                if not kysimus.ridu:
                    errors['l.ridu'] = _("Palun sisestada väärtus")
                if not kysimus.pikkus:
                    errors['l.pikkus'] = _("Palun sisestada väärtus")
                if errors:
                    raise ValidationError(self.handler, errors)
                self._update_choices()
                
        if not is_tr:
            self._update_mapping(kysimus,
                                 hm_key='ht',
                                 basetype=const.BASETYPE_IDLIST,
                                 cardinality=const.CARDINALITY_SINGLE)
            self._unique_kysimus(kysimus)        

    def include_edit(self):
        self.c.includes['raphael'] = True

    def include_view(self):
        self.c.includes['raphael'] = True        

    def _export_files(self, exporter):
        exporter.export_hotspots(self.block.taustobjekt)
        for obj in self.block.piltobjektid:
            exporter.export_obj(obj)

    def check(self, arvutihinnatav):
        rc = True
        li = []
        kysimus = self.block.kysimus

        mo = self.block.taustobjekt
        if not mo or not mo.has_file and not mo.fileurl:
            rc = False
            li.append(_("Puudub taustobjekt"))
        if len(kysimus.valikud) == 0:
            rc = False
            li.append(_("Puuduvad piirkonnad"))
        return rc, li

    def set_valikvastused(self):
        kysimus = self.block.give_kysimus()
        tulemus = kysimus.tulemus
        if tulemus:
            tulemus.set_valikvastus(kysimus.id, None, sisujarjestus=True, paarina=None)

class _hotspotInteractionController(BlockController):
    _TEMPLATE_NAME = 'ihotspot'
    def update(self, is_tr, not_locked):
        kysimus = self.block.kysimus
        if not_locked:
            self._update_taustobjekt()
            if not is_tr:
                self._update_staatus()
                kysimus.from_form(self.form_result['l'])        
                self._update_hotspots(kysimus)
                kysimus.max_vastus_arv = len(kysimus.valikud)
        if not is_tr:
            self._update_mapping(kysimus,
                                 basetype=const.BASETYPE_IDENTIFIER,
                                 cardinality=const.CARDINALITY_MULTIPLE)
            self._unique_kysimus(kysimus)

    def include_edit(self):
        self.c.includes['raphael'] = True

    def include_view(self):
        self.c.includes['raphael'] = True        

    def _export_files(self, exporter):
        exporter.export_hotspots(self.block.taustobjekt)
        for obj in self.block.piltobjektid:
            exporter.export_obj(obj)

    def check(self, arvutihinnatav):
        rc = True
        li = []
        kysimus = self.block.kysimus
        mo = self.block.taustobjekt
        if not mo or not mo.has_file and not mo.fileurl:
            rc = False
            li.append(_("Puudub taustobjekt"))
        if len(kysimus.valikud) == 0:
            rc = False
            li.append(_("Puuduvad piirkonnad"))                
        return rc, li

    def set_valikvastused(self):
        kysimus = self.block.give_kysimus()
        tulemus = kysimus.tulemus
        if tulemus:
            tulemus.set_valikvastus(kysimus.id, None, paarina=None)

class _graphicOrderInteractionController(BlockController):
    _TEMPLATE_NAME = 'igrorder'
    def update(self, is_tr, not_locked):
        kysimus = self.block.kysimus
        if not_locked:
            self._update_taustobjekt()
            if not is_tr:
                self._update_staatus()
                kysimus.from_form(self.form_result['l'])        
                self._update_hotspots(kysimus)

        if not is_tr:
            self._check_max_len_s(kysimus)
            self._update_mapping(kysimus,
                                 basetype=const.BASETYPE_IDENTIFIER,
                                 hm_key='hmx')
            self._unique_kysimus(kysimus)

    def _check_max_len_s(self, kysimus):
        # valikute selgituste kogupikkus koos semikoolonitega ei või ületada 255,
        # kuna nii suur on statvastus view selgituse väli
        MAX_LEN_S = 255
        selgitused = [v.selgitus or '' for v in kysimus.valikud]
        len_s = len(';'.join(selgitused))
        if len_s > MAX_LEN_S:
            err = _("Valikute selgitused on liiga pikad (kogupikkus ei või ületada {n1} sümbolit, praegu on {n2})").format(n1=MAX_LEN_S, n2=len_s)
            raise ValidationError(self.handler, {}, err)
        
    def include_edit(self):
        self.c.includes['raphael'] = True

    def include_view(self):
        self.c.includes['raphael'] = True        

    def _export_files(self, exporter):
        exporter.export_hotspots(self.block.taustobjekt)
        for obj in self.block.piltobjektid:
            exporter.export_obj(obj)

    def check(self, arvutihinnatav):
        rc = True
        li = []
        kysimus = self.block.kysimus
        mo = self.block.taustobjekt
        if not mo or not mo.has_file and not mo.fileurl:
            rc = False
            li.append(_("Puudub taustobjekt"))
        if len(kysimus.valikud) == 0:
            rc = False
            li.append(_("Puuduvad piirkonnad"))                
        return rc, li

    def set_valikvastused(self):
        kysimus = self.block.give_kysimus()
        tulemus = kysimus.tulemus
        if tulemus:
            tulemus.set_valikvastus(kysimus.id, None, sisujarjestus=True, paarina=None)

class _graphicOrdAssociateInteractionController(BlockController):
    _TEMPLATE_NAME = 'igrordass' # koolipsyhholoogi võrguylesanne
    def update(self, is_tr, not_locked):
        kysimus = self.block.kysimus
        if not_locked:
            self._update_taustobjekt()
            if not is_tr:
                self._update_staatus()
                self._update_hotspots(kysimus)
        
        if not is_tr:
            self._update_mapping(kysimus,
                                 basetype=const.BASETYPE_IDENTIFIER,
                                 cardinality=const.CARDINALITY_ORDERED_COR)

            self._unique_kysimus(kysimus)

            # valevastuseid ei lasta teha, kuid nende arv loetakse kokku ja hinnatakse
            kysimus2 = self.block.give_kysimus(seq=2)
            kysimus2.pseudo = True

            self._update_mapping(kysimus2,
                                 prefix='am2',
                                 basetype=const.BASETYPE_INTEGER,
                                 cardinality=const.CARDINALITY_MULTIPLE)
            
    def include_edit(self):
        self.c.includes['raphael'] = True

    def include_view(self):
        self.c.includes['raphael'] = True        

    def _export_files(self, exporter):
        exporter.export_hotspots(self.block.taustobjekt)
        for obj in self.block.piltobjektid:
            exporter.export_obj(obj)

    def check(self, arvutihinnatav):
        rc = True
        li = []
        kysimus = self.block.kysimus

        if arvutihinnatav:
            if not kysimus.tulemus:
                rc = False
                li.append(_("Puudub hindamismaatriks"))
        mo = self.block.taustobjekt
        if not mo or not mo.has_file and not mo.fileurl:
            rc = False
            li.append(_("Puudub taustobjekt"))
        if len(kysimus.valikud) == 0:
            rc = False
            li.append(_("Puuduvad piirkonnad"))                
        return rc, li

    def set_valikvastused(self):
        kysimus = self.block.give_kysimus()
        tulemus = kysimus.tulemus
        if tulemus:
            tulemus.set_valikvastus(kysimus.id, None, paarina=None)
           
class _selectPointInteractionController(BlockController):
    _TEMPLATE_NAME = 'iselect'
    def update(self, is_tr, not_locked):
        kysimus = self.block.kysimus
        if not_locked:
            self._update_taustobjekt()
            if not is_tr:
                self._update_staatus()
                kysimus.from_form(self.form_result['l'])        
                self._update_hotspots(kysimus)

        if not is_tr:
            self._update_mapping(kysimus,
                                 basetype=const.BASETYPE_POINT,
                                 cardinality=const.CARDINALITY_MULTIPLE)
            self._unique_kysimus(kysimus)
        
    def include_edit(self):
        self.c.includes['raphael'] = True

    def include_view(self):
        self.c.includes['raphael'] = True

    def check(self, arvutihinnatav):
        rc = True
        li = []
        kysimus = self.block.kysimus

        if arvutihinnatav:
            if not kysimus.tulemus:
                rc = False
                li.append(_("Puudub hindamismaatriks"))
        mo = self.block.taustobjekt
        if not mo or not mo.has_file and not mo.fileurl:
            rc = False
            li.append(_("Puudub taustobjekt"))
        return rc, li

class _select2PointInteractionController(BlockController):
    _TEMPLATE_NAME = 'iselect2'
    def update(self, is_tr, not_locked):
        prkkysimus = self.block.give_baaskysimus(1, True)
        kysimus = self.block.give_kysimus(2)
        if not_locked:
            mo = self._update_taustobjekt()
            if not is_tr:
                self._update_staatus()
                kysimus.from_form(self.form_result['l'])        
                self._update_hotspots_x(prkkysimus, mo)

                # iga piirkonda saab valida 1 korra
                for v in prkkysimus.valikud:
                    v.max_vastus = 1
                    
        if not is_tr:
            self._update_mapping(kysimus,
                                 basetype=const.BASETYPE_IDENTIFIER,
                                 cardinality=const.CARDINALITY_MULTIPLE)
            self._unique_kysimus(kysimus)
            self._set_valikud_max_p(prkkysimus, kysimus)
        
    def include_edit(self):
        self.c.includes['raphael'] = True

    def include_view(self):
        self.c.includes['raphael'] = True

    def check(self, arvutihinnatav):
        rc = True
        li = []
        prkkysimus = self.block.get_baaskysimus(1)
        kysimus = self.block.get_kysimus(seq=2)
        mo = self.block.taustobjekt
        if not mo or not mo.has_file and not mo.fileurl:
            rc = False
            li.append(_("Puudub taustobjekt"))
        if len(prkkysimus.valikud) == 0:
            rc = False
            li.append(_("Puuduvad piirkonnad"))

        if arvutihinnatav:
            if not kysimus.tulemus:
                rc = False
                li.append(_("Puudub hindamismaatriks"))
        return rc, li

    def _set_valikud_max_p(self, prkkysimus, kysimus):
        tulemus = kysimus.tulemus
        if tulemus:
            self._set_valik_max_p(prkkysimus, tulemus, [(1, 1)], kysimus.max_vastus)

    def set_valikvastused(self):
        prkkysimus = self.block.get_baaskysimus(1)
        kysimus = self.block.give_kysimus(2)
        tulemus = kysimus.tulemus
        if tulemus:
            # ES-1703: näitame statvastuses iga piirkonda eraldi kysimusena
            tulemus.set_valikvastus(prkkysimus.id, None, paarina=False)

class _graphicAssociateInteractionController(BlockController):
    _TEMPLATE_NAME = 'igrassociate'
    def update(self, is_tr, not_locked):
        kysimus = self.block.kysimus
        if not_locked:
            self._update_taustobjekt()
            if not is_tr:
                self._update_staatus()
                kysimus.from_form(self.form_result['l'])        
                self._update_hotspots(kysimus)
        
        if not is_tr:
            self._update_mapping(kysimus,
                                 basetype=const.BASETYPE_PAIR,
                                 cardinality=const.CARDINALITY_MULTIPLE)
            self._unique_kysimus(kysimus)
            self._set_valikud_max_p(kysimus)

    def _set_valikud_max_p(self, kysimus):
        tulemus = kysimus.tulemus
        if tulemus:
            self._set_valik_max_p(kysimus, tulemus, [(1, 1),(1,2)], kysimus.max_vastus)

    def include_edit(self):
        self.c.includes['raphael'] = True

    def include_view(self):
        self.c.includes['raphael'] = True        

    def _export_files(self, exporter):
        exporter.export_hotspots(self.block.taustobjekt)
        for obj in self.block.piltobjektid:
            exporter.export_obj(obj)

    def check(self, arvutihinnatav):
        rc = True
        li = []
        kysimus = self.block.kysimus

        if arvutihinnatav:
            if not kysimus.tulemus:
                rc = False
                li.append(_("Puudub hindamismaatriks"))
        mo = self.block.taustobjekt
        if not mo or not mo.has_file and not mo.fileurl:
            rc = False
            li.append(_("Puudub taustobjekt"))
        if len(kysimus.valikud) == 0:
            rc = False
            li.append(_("Puuduvad piirkonnad"))                
        return rc, li

    def set_valikvastused(self):
        kysimus = self.block.give_kysimus()
        tulemus = kysimus.tulemus
        if tulemus:
            tulemus.set_valikvastus(kysimus.id, kysimus.id, paarina=True)
           
#########################################################
# Faili laadimine

class _audioInteractionController(BlockController):
    _TEMPLATE_NAME = 'iaudio'

    def include_view(self):
        self.c.includes['audiorecorder'] = True

    def update(self, is_tr, not_locked):
        kysimus = self.block.kysimus
        if is_tr:
            self._tran_update_mapping(kysimus)            
        elif not_locked and not is_tr:
            self._update_staatus()

            auk = self.form_result['auk'] or {}
            kysimus.peida_start = auk.get('peida_start') or False
            kysimus.peida_paus = auk.get('peida_paus') or False
            kysimus.peida_stop = auk.get('peida_stop') or False
            kysimus.naita_play = auk.get('naita_play') or False
            kysimus.max_vastus = auk.get('max_vastus') or None
            kysimus.min_vastus = auk.get('min_vastus') and 1 or 0
            # kanalite arv
            kysimus.ridu = self.form_result.get('stereo') and 2 or None
            
            self._update_mapping(kysimus,
                                 basetype=const.BASETYPE_FILE,
                                 cardinality=const.CARDINALITY_SINGLE)
            self._unique_kysimus(kysimus)

            # autostardi valikud
            buf = ''
            opts = self.form_result.get('autostart')
            for key in (model.Sisuplokk.AUTOSTART_LOAD,
                        model.Sisuplokk.AUTOSTART_SEQ,
                        model.Sisuplokk.AUTOSTART_MEDIASTART,
                        model.Sisuplokk.AUTOSTART_MEDIA):
                if key in opts:
                    buf += key
            if not buf and kysimus.peida_start:
                errors = {'autostart_err': _("Kui alustamise nuppu ei kuvata, siis peab salvestamine algama automaatselt")}
                raise ValidationError(self.handler, errors)
            self.block.autostart_opt = buf

class _krattController(BlockController):
    _TEMPLATE_NAME = 'ikratt'

    def include_view(self):
        self.c.includes['kratt'] = True

    def update(self, is_tr, not_locked):
        krk = self.form_result['krk'] or {}
        on_kysimus = krk.get('krati_kuulamine_record') or False
        data = {}
        data['krati_kysimused'] = []
        for r in krk.get('kysimused'):
            d = {'speak': r['speak'] or None,
                 'text': r['text'] or None,
                 }
            for key in ('kordus', 'img_url', 'ooteaeg', 'vastamisaeg'):
                val = r.get(key)
                if val is not None:
                    d[key] = val
            data['krati_kysimused'].append(d)
        data['krati_kuulamine'] = {
            'record': on_kysimus,
            'audio_piiraeg': krk.get('krati_kuulamine_audio_piiraeg') or None,
            }
        outro = krk.get('outro')
        data['krati_outro'] = {
            'speak': outro['speak'] or None,
            'text': outro['text'] or None,
            }
        data['krati_hoiatus_piirajad'] = [60, 30, 10]
        data['audio_seadistamine'] = krk.get('audio_seadistamine') or False
        self.block.set_json_sisu(data, self.lang)
        log.debug(data)
        kysimus = self.block.get_kysimus()
        if is_tr:
            if kysimus:
                self._tran_update_mapping(kysimus)            
        elif not_locked:
            self._update_staatus()
            if on_kysimus:
                kysimus = self.block.give_kysimus()
                self._update_mapping(kysimus,
                                    basetype=const.BASETYPE_FILE,
                                    cardinality=const.CARDINALITY_SINGLE)
                self._unique_kysimus(kysimus)
            elif kysimus:
                kysimus.delete()
            
class _uploadInteractionController(BlockController):
    _TEMPLATE_NAME = 'iupload'
    def update(self, is_tr, not_locked):
        kysimus = self.block.kysimus
        if not_locked and not is_tr:
            self._update_staatus()
            kysimus.give_kyslisa().from_form(self.form_result['ul'])        

        if is_tr:
            self._tran_update_mapping(kysimus)
        else:
            self._update_mapping(kysimus,
                                 basetype=const.BASETYPE_FILE,
                                 cardinality=const.CARDINALITY_SINGLE)
            self._unique_kysimus(kysimus)
        

###########################################################
class _formulaController(BlockController):
    _TEMPLATE_NAME = 'formula'

    def update(self, is_tr, not_locked):
        kysimus = self.block.kysimus
        if not is_tr and not_locked:
            self.block.sisu = self.form_result['f_sisu']
            if not self.block.sisu:
                errors = {'f_sisu': _("Väärtus puudub")}
                raise ValidationError(self.handler, errors)

            kysimus.pseudo = True
        if not is_tr:
            self._update_mapping(kysimus,
                                 cardinality=const.CARDINALITY_SINGLE)
            self._unique_kysimus(kysimus)
        if not is_tr and not_locked:
            self._update_choices()

            # testime syntaksit
            errors = {}
            f_locals = {}
            for ind, v in enumerate(kysimus.valikud):
                try:
                    constant = eval(v.nimi, {}, {})
                except:
                    errors['v-%d.nimi' % ind] = _("Vigane väärtus")
                else:
                    f_locals[v.kood] = constant
            
            err = FormulaEnv(self.handler).test_formula(self.block, f_locals)
            if err:
                errors['f_sisu'] = err
            if errors:
                raise ValidationError(self.handler, errors)

class _randomController(BlockController):
    _TEMPLATE_NAME = 'random'

    def update(self, is_tr, not_locked):
        kysimus = self.block.kysimus
        if not is_tr:
            kysimus.pseudo = True
            kysimus.ei_arvesta = True
            kyslisa = kysimus.give_kyslisa()
            kyslisa.from_form(self.form_result['sl'])

            tulemus = self._update_mapping(kysimus,
                                           cardinality=const.CARDINALITY_SINGLE)
            tulemus.maatriksite_arv = 0
            tulemus.max_pallid = 0
            tulemus.max_vastus = 1
            tulemus.arvutihinnatav = True
            self._unique_kysimus(kysimus)

            ylesanne = self.ylesanne
            ylesanne.on_juhuarv = True
            
#########################################################
# Abifunktsioonid

def _getText(nodelist):
    rc = ""
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc = rc + node.data
    return rc

def _removeChildElements(node):
    for child in node.childNodes:
        if child.nodeType == node.ELEMENT_NODE:
            node.removeChild(child)

def _outer_xml(tree):
    "XML muudetakse stringiks"
    # enne eemaldame tyhjad divid, sest muidu
    # tostring('<div></div>') -> <div/>, millele brauser lisab ise </div> ja saab kahe lõpuga divi
    # alternatiiv oleks tostring(method='html'), aga see teeb <br/> -> <b>
    for field in tree.xpath('div[not(node())]|span[not(node())]'):
        parent = field.getparent()
        if parent is not None:
            text = field.tail
            if text is not None:
                previous = field.getprevious()
                if previous is not None:
                    previous.tail = (previous.tail or '') + text
                else:
                    parent.text = (parent.text or '') + text
            parent.remove(field)
    # tyhja iframe sisse paneme tyhiku, et tehtaks </iframe>
    for field in tree.xpath('//iframe'):
        if not field.text:
            field.text = ' '
    
    return etree.tostring(tree, encoding=str, with_tail=False).strip()

def _int_none(s):
    try:
        return int(s)
    except:
        return None

def _float_c(s):
    if isinstance(s,str):
        s = s.replace(',','.')
    return float(s)    

def _float_none(s):
    try:
        return _float_c(s)
    except:
        return None

def _add_field_class(field, add_cls, remove_cls):
    try:
        cls = field.attrib['class'] or ''
    except:
        cls = ''
    li = [c for c in cls.split(' ') if c]
    for c in remove_cls:
        if c in li:
            li.remove(c)
    if add_cls and add_cls not in li:
        li.append(add_cls)
    if cls or li:
        field.attrib['class'] = ' '.join(li)

class HTMLTextExtractor(html.parser.HTMLParser):
    def __init__(self):
        super(HTMLTextExtractor, self).__init__()
        self.result = [ ]

    def handle_data(self, d):
        self.result.append(d)

    def get_text(self):
        return ''.join(self.result)

def _html2txt(html):
    """Converts HTML to plain text (stripping tags and converting entities).
    _html2txt('<a href="#">Demo<!--...--> <em>(&not; \u0394&#x03b7;&#956;&#x03CE;)</em></a>')
    'Demo (\xac \u0394\u03b7\u03bc\u03ce)'

    "Plain text" doesn't mean result can safely be used as-is in HTML.
    _html2txt('&lt;script&gt;alert("Hello");&lt;/script&gt;')
    '<script>alert("Hello");</script>'

    Always use html.escape to sanitize text before using in an HTML context!

    HTMLParser will do its best to make sense of invalid HTML.
    _html2txt('x < y &lt z <!--b')
    'x < y < z '

    Unrecognized named entities are included as-is. '&apos;' is recognized,
    despite being XML only.
    _html2txt('&nosuchentity; &apos; ')
    "&nosuchentity; ' "
    """
    s = HTMLTextExtractor()
    s.feed(html)
    # asendame mitu tyhikut-tabi yhe tyhikuga
    return re.sub('\s+', ' ', s.get_text()).strip()
