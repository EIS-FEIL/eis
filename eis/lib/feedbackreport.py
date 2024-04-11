"""Tagasiside koostamine
"""
from lxml import etree
from lxml.builder import E
from chameleon import PageTemplate
import pickle
import sqlalchemy as sa
import base64
import json
import io
import requests
import urllib.parse
import weasyprint
import copy
import eiscore.const as const
from eis.lib.base import *
from eis.lib.helpers import fstr, literal
from eis.lib.block import _outer_xml
from eis.lib.feedbackdiag import FeedbackDiag
from eis.lib.feedbackpsyh import FeedbackPsyh
from eis.lib.feedbackopip import FeedbackOpip
from eis.lib.feedbackdgm import *

from eis.lib.pdf.psyhprofiilileht import PsyhprofiililehtDoc
from eis.lib.pdf.profiilileht import ProfiililehtDoc
from eis.lib.feedbacklocals import feedbacklocals_for_report, FeedbackStat
from . import npcalc

log = logging.getLogger(__name__)
_ = i18n._

class FeedbackReport(object):
    def __init__(self, handler, tvorm, test, template, liik, lang=None):
        self.tvorm = tvorm
        self.handler = handler
        self.test = test
        if template:
            template = template.replace('&nbsp;', ' ').strip()
        self.template = template
        self.liik = liik
        self.lang = lang
        self.can_xls = False
        
    @classmethod
    def init_kirjeldus(cls, handler, test, lang, kursus, check=False):
        "Kui testil on tagasisidevorm, siis tagastatakse FeedbackReport objekt"
        # kas on sisseehitatud mall
        if test.tagasiside_mall == const.TSMALL_NONE:
            return 
        liik = model.Tagasisidevorm.LIIK_KIRJELDUS
        tv = model.Tagasisidevorm.get_vorm(test.id, liik, lang, kursus)
        if check:
            return bool(tv)
        template = tv and tv.get_full_template()
        if template:
            return FeedbackReport(handler, tv, test, template, liik, lang)

    @classmethod
    def init_gruppidetulemused(cls, handler, test, lang, kursus, testimiskord=None, check=False):
        "Kui testil on tagasisidevorm, siis tagastatakse FeedbackReport objekt"
        # kas on sisseehitatud mall
        if test.tagasiside_mall == const.TSMALL_NONE:
            return
        if check:
            return True
        liik = model.Tagasisidevorm.LIIK_GRUPPIDETULEMUSED
        tv = model.Tagasisidevorm.get_vorm(test.id, liik, lang, kursus)
        template = tv and tv.get_full_template()
        if not template:
            # genereeritakse vaikimisi mall
            template = AutoFormGenerator.gen_template_gruppidetulemused(handler, test, kursus, testimiskord)
            tv = model.Tagasisidevorm.add_auto(test.id, liik, template, kursus, lang)
        return FeedbackReport(handler, tv, test, template, liik, lang)

    @classmethod
    def init_osalejatetulemused(cls, handler, test, lang, kursus, testimiskord=None, check=False):
        "Kui testil on tagasisidevorm, siis tagastatakse FeedbackReport objekt"
        # kas on sisseehitatud mall
        if test.tagasiside_mall == const.TSMALL_NONE:
            return
        liik = model.Tagasisidevorm.LIIK_OSALEJATETULEMUSED
        # kas on käsitsi mall
        tv = model.Tagasisidevorm.get_vorm(test.id, liik, lang, kursus)
        template = tv and tv.get_full_template()
        # kas saab genereerida d-testi malli, kui käsitsi mall puudub
        is_F2 = test.tagasiside_mall == const.TSMALL_DIAG
        if check:
            return is_F2 or bool(tv) or not test.pallideta
        if not template and not is_F2:
            # genereeritakse vaikimisi õpilaste tulemuse mall
            template = AutoFormGenerator.gen_template_osalejatetulemused(handler, test, kursus, testimiskord)
            tv = model.Tagasisidevorm.add_auto(test.id, liik, template, kursus, lang)            
        return FeedbackReport(handler, tv, test, template, liik, lang)

    @classmethod
    def init_valim(cls, handler, test, lang, kursus, testimiskord=None, check=False):
        "Kui testil on tagasisidevorm, siis tagastatakse FeedbackReport objekt"
        if test.tagasiside_mall == const.TSMALL_NONE:
            return
        liik = model.Tagasisidevorm.LIIK_VALIM
        # kas on käsitsi mall
        tv = model.Tagasisidevorm.get_vorm(test.id, liik, lang, kursus) 
        template = tv and tv.get_full_template()
        # kas saab genereerida d-testi malli, kui käsitsi mall puudub
        is_F3 = test.tagasiside_mall == const.TSMALL_DIAG        
        if check:
            return is_F3 or bool(tv)
        if is_F3 or template:
            return FeedbackReport(handler, tv, test, template, liik, lang)

    @classmethod
    def init_riiklik(cls, handler, test, lang, kursus, check=False):
        "Kui testil on tagasisidevorm, siis tagastatakse FeedbackReport objekt"
        if test.tagasiside_mall == const.TSMALL_NONE:
            return
        liik = model.Tagasisidevorm.LIIK_RIIKLIK
        # kas on käsitsi mall
        tv = model.Tagasisidevorm.get_vorm(test.id, liik, lang, kursus)
        template = tv and tv.get_full_template()
        # kas saab genereerida d-testi malli, kui käsitsi mall puudub
        is_F4 = test.tagasiside_mall == const.TSMALL_DIAG and test.testiliik_kood == const.TESTILIIK_TASEMETOO
        if check:
            return is_F4 or bool(tv)
        if is_F4 or template:
            return FeedbackReport(handler, tv, test, template, liik, lang)

    @classmethod
    def init_opilane(cls, handler, test, lang, kursus, check=False, opetajale=None):
        "Kui testil on tagasisidevorm, siis tagastatakse FeedbackReport objekt"
        # kas on olemas sisseehitatud mall
        if test.tagasiside_mall == const.TSMALL_NONE:
            return
        if check and not opetajale:
            # õpilasele saab alati midagi kuvada
            return True
        liik = model.Tagasisidevorm.LIIK_OPILANE
        tv = model.Tagasisidevorm.get_vorm(test.id, liik, lang, kursus)
        is_F1 = test.tagasiside_mall in (const.TSMALL_DIAG, const.TSMALL_PSYH, const.TSMALL_OPIP)
        if opetajale and tv and not tv.nahtav_opetajale:
            # vorm on, aga mitte õpetajale näitamiseks
            return
        if check:
            return True
        template = tv and tv.get_full_template()
        if not template and not is_F1:
            # genereeritakse vaikimisi mall 
            template = AutoFormGenerator.gen_template_opilane(handler, test, kursus)
            tv = model.Tagasisidevorm.add_auto(test.id, liik, template, kursus, lang)            
        return FeedbackReport(handler, tv, test, template, liik, lang)

    @classmethod
    def init_opetaja(cls, handler, test, lang, kursus, check=False):
        "Kui testil on tagasisidevorm, siis tagastatakse FeedbackReport objekt"
        # kas on olemas sisseehitatud mall
        if test.tagasiside_mall == const.TSMALL_NONE:
            return
        liik = model.Tagasisidevorm.LIIK_OPETAJA
        tv = model.Tagasisidevorm.get_vorm(test.id, liik, lang, kursus)
        template = tv and tv.get_full_template()
        is_F1 = test.tagasiside_mall == const.TSMALL_PSYH
        if check:
            return is_F1 or bool(tv)
        if template or is_F1:
            return FeedbackReport(handler, tv, test, template, liik, lang)

    @classmethod
    def leia_valimi_testimiskord(self, test_id, testimiskord_id):
        sis_valim_tk_id = None
        valimid_tk_id = []

        # objekt, mis hoiab valimite tulemuste avaldamise infot
        v_avaldet = FeedbackStat.new_avaldet()
        
        if isinstance(testimiskord_id, list) and len(testimiskord_id) == 1:
            testimiskord_id = int(testimiskord_id[0])

        if testimiskord_id:
            # kas leidub antud testimiskorrast eraldatud valimi testimiskord,
            # millel on märge statistikas arvestamise kohta?
            qtk = (model.SessionR.query(model.Testimiskord.id,
                                       model.Testimiskord.stat_valim,
                                       model.Testimiskord.alatestitulemused_avaldet,
                                       model.Testimiskord.ylesandetulemused_avaldet,
                                       model.Testimiskord.aspektitulemused_avaldet,
                                       model.Testimiskord.koondtulemus_avaldet)
                   .filter(model.Testimiskord.test_id==test_id)
                   )
            if isinstance(testimiskord_id, list):
                qtk = qtk.filter(model.Testimiskord.valim_testimiskord_id!=None)
            else:
                qtk = qtk.filter(model.Testimiskord.valim_testimiskord_id==testimiskord_id)

            qtk_avaldet = (qtk
                           .filter(model.Testimiskord.koondtulemus_avaldet==True)
                           .filter(model.Testimiskord.statistika_arvutatud==True)
                           .filter(model.Testimiskord.tulemus_kinnitatud==True)
                          )
            li = list(qtk_avaldet.all())
            valimid_tk_id = [r[0] for r in li if r[1]]
            # mittearvestatavad valimid
            v_avaldet.mittestat_valimid_tk_id = [r[0] for r in li if not r[1]]

            # arvestatavate valimite tulemuste avaldatus
            v_avaldet.alatestitulemused_avaldet = li and not [r for r in li if not r[2]]
            v_avaldet.ylesandetulemused_avaldet = li and not [r for r in li if not r[3]]
            v_avaldet.aspektitulemused_avaldet = li and not [r for r in li if not r[4]]
            v_avaldet.koondtulemus_avaldet = li and not [r for r in li if not r[5]]

            #log.info(f'valim={valimid_tk_id} mittestat={v_avaldet.mittestat_valimid_tk_id}; {v_avaldet.ylesandetulemused_avaldet}')
            # märge statistikas arvestamise kohta
            qtk = qtk.filter(model.Testimiskord.stat_valim==True)
            if not valimid_tk_id and qtk.count() == 0:
                # kui avaldatud eraldatud valimit ei ole, aga ilma avaldamata
                # arvestatav eraldatud valim on olemas
                # siis testimiskorrasisest valimit ei arvesta;
                if not isinstance(testimiskord_id, list):
                    # kontrollime, kas antud testimiskord on ise valim
                    q2 = (model.SessionR.query(model.Testimiskord.valim_testimiskord_id)
                          .filter_by(stat_valim=True)
                          .filter_by(id=testimiskord_id))
                    if q2.count():
                        valimid_tk_id = [testimiskord_id]

                if not valimid_tk_id:
                    # kui eraldatud arvestatavat valimit pole, siis vaatame, kas on testimiskorrasisene valim
                    qtk = (model.SessionR.query(model.Testimiskord.id)
                           .filter(model.Testimiskord.test_id==test_id)                   
                           .filter(model.Testimiskord.sisaldab_valimit==True)
                           .filter(model.Testimiskord.tulemus_kinnitatud==True)
                           )
                    if isinstance(testimiskord_id, list):
                        # mitu testimiskorra id (vana tulemuste vaade)
                        qtk = qtk.filter(model.Testimiskord.id.in_(testimiskord_id))
                    else:
                        qtk = qtk.filter(model.Testimiskord.id==testimiskord_id)
                    for r in qtk.all():
                        sis_valim_tk_id = r[0]
                        break

        log.debug(f'sis_valim_tk_id={sis_valim_tk_id},valimid_tk_id={valimid_tk_id}')
        return sis_valim_tk_id, valimid_tk_id, v_avaldet

    def generate(self, sooritaja, **kw):
        # tagasiside genereerimine
        # sooritaja - on olemas õpilase tagasiside korral (välja arvatud vormi salvestamise testimisel)
        # muud argumendid - grupi tagasiside korral kirjeldavad gruppi
        c = self.handler.c

        data = None
        self.can_xls = False
        if self.liik == model.Tagasisidevorm.LIIK_KIRJELDUS:
            # kirjeldus on staatiline, aga võib sisaldada pilte
            template = self._set_testimages_url(self.template)
            return None, template

        err, stat = self.make_stat(sooritaja, **kw)
        if err:
            return err, data
        c.is_pdf = stat.is_pdf

        env = self._get_locals(sooritaja, self.test, stat)
        if self.template:
            # Chameleoni vorm
            err, data = self._gen_by_template(env)
            # ES-3361 ajutine häkk
            if sooritaja and sooritaja.test_id == 9220 and sooritaja.testimiskord_id == 5735:
                q = (model.SessionR.query(sa.func.count(model.Hindamisolek.id))
                     .join(model.Hindamisolek.sooritus)
                     .filter(model.Sooritus.sooritaja_id==sooritaja.id)
                     .filter(model.Hindamisolek.hindamisprobleem==const.H_PROBLEEM_TOOPUUDU))
                if q.scalar() > 0:
                    data += '<p>Tehnilistel põhjustel polnud võimalik suulist osa hinnata.</p>'
                    
        elif self.liik == model.Tagasisidevorm.LIIK_OPILANE:
            # õpilase tagasiside F1
            template = None
            if self.test.tagasiside_mall == const.TSMALL_DIAG:
                data = FeedbackDiag(self.handler).gen_opilane(sooritaja)
            elif self.test.tagasiside_mall == const.TSMALL_OPIP:
                data = FeedbackOpip(self.handler).gen_opilane(sooritaja)
                self.can_xls = True

        elif self.liik == model.Tagasisidevorm.LIIK_OPETAJA:
            # õpetaja tagasiside F1
            template = None
            if self.test.tagasiside_mall == const.TSMALL_PSYH:
                data = FeedbackPsyh(self.handler).gen_opilane(sooritaja)
                self.can_xls = True
                
        elif self.liik == model.Tagasisidevorm.LIIK_OSALEJATETULEMUSED:
            if self.test.tagasiside_mall == const.TSMALL_DIAG:
                # grupi tagasiside, sisseehitatud mall F2
                tts = self.test.testitagasiside
                data = FeedbackDiag(self.handler).gen_grupp(tts, stat)

        elif self.liik == model.Tagasisidevorm.LIIK_VALIM:
            if self.test.tagasiside_mall == const.TSMALL_DIAG:
                # valimi tagasiside, sisseehitatud mall F3
                tts = self.test.testitagasiside
                data = FeedbackDiag(self.handler).gen_valim(tts, stat)

        elif self.liik == model.Tagasisidevorm.LIIK_RIIKLIK:
            if self.test.tagasiside_mall == const.TSMALL_DIAG and self.test.testiliik_kood == const.TESTILIIK_TASEMETOO:
                # valimi tagasiside, sisseehitatud mall F4
                tts = self.test.testitagasiside
                data = FeedbackDiag(self.handler).gen_riiklik(tts, stat)

        if data:
            h = self.handler.h
            lnk = h.javascript_link('/static/eis/feedbackreport.js')
            data += str(lnk)
            
            if stat.is_pdf:
                data = self._gen_header(env, stat) + data
            if self.is_empty_html(data):
                data = ''
        return err, data

    def is_empty_html(self, data):
        "Kas tagasiside on tühi (kui on ainult HTML märgendid ja teksti pole, siis on ka tühi)"
        if data:
            tag = None
            for ch in data:
                if tag:
                    if ch == '>':
                        if tag.lower().startswith('<img '):
                            # pilti sisaldav tagasiside ei ole tyhi (ES-3329)
                            return False
                        tag = None
                    else:
                        tag += ch
                elif ch == '<':
                    tag = ch
                elif ch.strip():
                    # sisaldab teksti, ei ole tyhi
                    return False
        return True
    
    def _gen_header(self, env, stat):
        "Testi nimetus PDFi päisesse"
        test = self.test
        buf = f'<h1>{_("Tulemused")} - {test.nimi}</h1><div>'
        data = [(_("ID"), test.id),
                (_("Õppeaine"), test.aine_nimi),
                (_("Toimumise aeg"), env.get('sooritamiskpv') or '')]
        if not test.pallideta:
            data.append((_("Max"), '%sp' % fstr(test.max_pallid)))
        if stat.kursus:
            kursus_nimi = model.Klrida.get_str('KURSUS', stat.kursus, test.aine_kood)
            data.append((_("Kursus"), kursus_nimi))
        for key, value in data:
            buf += f'<span style="padding-right:10px"><b>{key}</b> {value}</span> '
        buf += '</div>'
        return buf

    def make_stat(self, sooritaja, **kw):
        # stat objekti koostamine, mille kaudu tagasisidevormidele antakse tingimused
        stat = FeedbackStat(self.liik, self.lang, self.test.id, sooritaja, **kw)        

        r = self.leia_valimi_testimiskord(stat.test_id, stat.testimiskorrad_id)
        stat.sis_valim_tk_id, stat.valimid_tk_id, stat.v_avaldet = r

        if sooritaja:
            # õpilase tagasisidet saab kuvada ainult siis, kui töö on tehtud ja hinnatud
            if sooritaja.staatus != const.S_STAATUS_TEHTUD:
                log.debug('sooritaja.staatus=%s' % sooritaja.staatus)
                return _("Test ei ole lõpetatud"), None
            if sooritaja.hindamine_staatus != const.H_STAATUS_HINNATUD and sooritaja.pallid is None:
                log.debug('sooritaja.h_staatus=%s' % sooritaja.hindamine_staatus)
                return _("Testitöö ei ole hinnatud"), None

        return None, stat

    def _gen_by_template(self, env):
        "Genereeritakse vorm"
        try:
            template = self.template
            t = PageTemplate(template)
            data1 = t(**env)
            data2 = self._set_testimages_url(data1)
            data = self._fill_diagrams(data2, env)
            return None, data
        except Exception as e:
            self.handler._error(e, 'Malli viga', rollback=False)
            #log.error(e)
            err = repr(e)
            if self.handler.is_devel:
                raise
            return err, None

    def _set_testimages_url(self, template):
        "Testi tagasisidefailide URLile lisatakse testi ID"
        # Tagasiside koostamisel ei kirjutata testi ID urli sisse,
        # et tagasisidevorm oleks testi ID-st sõltumatu ja seda saaks kopeerida.
        # Siin lisatakse URLile testi ID, mille järgi leiab server pildifaili.
        pattern = r'src="/?testimages/'
        repl = 'src="testimages/%d/' % self.test.id
        template = re.sub(pattern, repl, template)
        return template

    def _gen_dgm_by_params(self, params, fbd_id, f_locals):
        "Diagrammi/tabeli sisu genereerimine"
        fl = f_locals['T']
        stat = fl.stat
        dname = params.get('dname')
        Dgm = get_feedbackdgm(dname)
        if Dgm:
            # kas diagramm on muu testi kohta (taustakysitlus)?
            tk_tahis = params.get('tk_tahis')
            if tk_tahis:
                fl = fl.TK(tk_tahis)
                if not fl:
                    # seotud testi keskkonda ei saa teha, testimiskord puudub
                    # diagrammi ei saa genereerida
                    return ''

            # reltest = params.get('reltest')
            # if reltest:
            #     li = list(reltest.split(','))
            #     if li[0] == 'PKTEST':
            #         aine = li[1]
            #         fl = fl.PKTEST(aine)
            #     if not fl:
            #         # seotud testi keskkonda ei saa teha (sooritused puuduvad),
            #         # diagrammi ei saa genereerida
            #         return ''

            
            # diagramm
            dgm = Dgm(self.handler, fl)
            data = dgm.data_by_params(params)
            if dgm.is_html:
                # HTML tabel
                if stat.is_xls:
                    self.xls_sheets_data.append(data)
                    return ''
                if data is None:
                    # ei ole midagi kuvada
                    buf = ''
                else:
                    body_only = params.get('gargs') is not None
                    buf = dgm.draw_html(data, fbd_id, body_only)
                    # kui vormil on tabel, siis on midagi Excelisse laadida
                    self.can_xls = True
                return buf

            # Diagramm
            fig = dgm.figure(*data)
            width = params.get('width')
            height = params.get('height')

            if fig is None:
                # ei ole midagi kuvada (vbl pole tulemused avaldatud)
                buf = ''
            elif stat.is_pdf:
                # asendatakse pildifailiga
                buf = '<img'
                style = ''
                if width:
                    buf += ' width="%dpx"' % width
                    style += 'width:%dpx;' % width
                if height:
                    buf += ' height="%dpx"' % height
                    style += 'height:%dpx;' % height
                if style:
                    buf += ' style="%s"' % style
                encoded_img = dgm.draw_inline(fig, width)
                buf += ' src="%s"/>' % encoded_img
            else:
                # javascripti diagramm
                style = ''
                if width:
                    style += 'width:%dpx;' % width
                if height:
                    style += 'height:%dpx;' % height

                json = fig.to_json()
                json = json[:-1] + ',config:{displayModeBar:false}}'
                self.ind_dgm += 1
                dgm_id = f'_dgm_{self.ind_dgm}'
                buf = f'<div id="{dgm_id}" style="{style}"></div>' + \
                      f'<script>Plotly.newPlot(document.getElementById("{dgm_id}"), {json});</script>'

            return buf

        raise Exception('tundmatu diagrammiliik %s' % dname)
        
    def _fill_diagrams(self, template, f_locals):
        "Genereeritakse malli sees olevad diagrammid ja tabelid"
        self.ind_dgm = 0
        self.xls_sheets_data = []

        def repl_attr(m):
            buf = m.groups()[0]
            res = re.findall(r' (\w+)="([^"]*)"', buf)
            di = {key.lower(): val for (key, val) in res}
            cls = di.get('class') or ''
            b64data = di.get('params')
            if 'fbdiagram' in cls:
                try:
                    txt = base64.b64decode(b64data)
                    params = json.loads(txt)
                except Exception as ex:
                    log.error(ex)
                    raise
                fbd_id = di.get('id')
                buf = self._gen_dgm_by_params(params, fbd_id, f_locals)
            return buf

        # igale diagrammi parameetrid salvestatatakse eraldi kirjes
        # ja tagasisidevormis asendatakse diagrammi URL, et see viitaks diagrammi kirjele
        pattern = r'(<div class="fbdiagram"[^>]+>[^<]*</div>)'
        template = re.sub(pattern, repl_attr, template)

        return template

    def generate_dgm(self, fbd_id, params, **kw):
        "Tabeli vormist eraldi genereerimine, vastavalt kasutaja valitud filtrile"
        # gargs - kasutaja dynaamiliselt valitud parameetrid
        sooritaja = None
        err, stat = self.make_stat(sooritaja, **kw)
        if err:
            return err, data
        env = self._get_locals(sooritaja, self.test, stat)
        fix_params = self._extract_dgm(fbd_id)
        if not fix_params:
            return f"ei leitud diagrammi {fbd_id}", None

        # kasutaja poolt antud tabeli juures antud filtri väljad
        gargs = {'sugu': params.get('sugu'),
                 'lng': params.get('lng'),
                 'alla': params.get('alla'),
                 'yle': params.get('yle'),
                 }

        fix_params['gargs'] = gargs
        html = self._gen_dgm_by_params(fix_params, fbd_id, env)
        return None, html

    def _extract_dgm(self, fbd_id):
        "Eraldame mallilt õige diagrammi"
        template = self.template
        pattern = r'(<div class="fbdiagram"[^>]+>)'
        for div in re.findall(pattern, template):
            res = re.findall(r' (\w+)="([^"]*)"', div)
            di = {key.lower(): val for (key, val) in res}            
            if di.get('id') == fbd_id:
                # leiti õige diagramm
                b64data = di.get('params')
                try:
                    txt = base64.b64decode(b64data)
                    params = json.loads(txt)
                except Exception as ex:
                    log.error(ex)
                else:
                    return params

    def generate_pdf(self, sooritaja, **kw):
        "Õpilase tagasiside PDF"
        filedata = None
        tsmall = self.test.tagasiside_mall
        if self.template or tsmall == const.TSMALL_DIAG:
            # genereeritakse HTML, siis teisendatakse PDFiks
            kw['format'] = 'pdf'
            err, data_html = self.generate(sooritaja, **kw)
            if err:
                self.handler.error(err)
            else:
                filedata = report2pdf(self.handler, data_html)
        elif sooritaja:
            # sisseehitatud profiililehe PDF
            if tsmall == const.TSMALL_PSYH:
                sooritus = sooritaja.sooritused[0]
                header, items, dgm_data = FeedbackPsyh(self.handler).prepare_sooritus(sooritus, 'pdf')
                doc = PsyhprofiililehtDoc(self, sooritus, header, items)
                filedata = doc.generate()
            elif tsmall == const.TSMALL_OPIP:
                sooritus = sooritaja.sooritused[0]
                header, items, dgm_data = FeedbackOpip(self.handler).prepare_sooritus(sooritus, 'pdf')
                doc = ProfiililehtDoc(self, sooritus, header, items)
                filedata = doc.generate()
        return filedata

    def generate_xls(self, sooritaja, **kw):
        "Tagasiside Excelis"

        data = None
        if self.liik == model.Tagasisidevorm.LIIK_KIRJELDUS:
            # kirjeldus on staatiline
            return None

        kw['format'] = 'xls'
        err, stat = self.make_stat(sooritaja, **kw)
        if err:
            return None

        if self.template:
            # Chameleoni vorm
            env = self._get_locals(sooritaja, self.test, stat)
            err, data = self._gen_by_template(env)

            xls_data = []
            for r in self.xls_sheets_data:
                if r:
                    header, items_with_attr = r[:2]
                    header_labels = [r[1] for r in header]
                    items = [item for (item, attr) in items_with_attr]
                    xls_data.append((header_labels, items, None))

            return utils.xls_multisheet_data(xls_data)

        elif sooritaja:
            # õpilase tagasiside F1
            template = None
            c = self.handler.c
            tsmall = self.test.tagasiside_mall
            if tsmall == const.TSMALL_PSYH:
                sooritus = sooritaja.sooritused[0]
                header, items, dgm_data = FeedbackPsyh(self.handler).prepare_sooritus(sooritus, 'xls')
                return utils.xls_data(header, items)
            elif tsmall == const.TSMALL_OPIP:
                sooritus = sooritaja.sooritused[0]
                header, items, dgm_data = FeedbackOpip(self.handler).prepare_sooritus(sooritus, 'xls')
                return utils.xls_data(header, items)
                

    def html2pdf(self, handler, html_data):
        return report2pdf(handler, html_data)

    def _get_locals(self, sooritaja, test, stat):
        "Tagasisidevormil kasutatavad muutujad ja funktsioonid"
        return feedbacklocals_for_report(self.handler, self.liik, test, sooritaja, stat, self.lang)

class AutoFormGenerator:
    "Vaikimisi tagasisidevormide genereerimine siis, kui kehtivat vormi pole"
    
    @classmethod
    def gen_template_osalejatetulemused(cls, handler, test, kursus, testimiskord=None):
        "Genereeritakse vaikimisi osalejate tulemuste mall"
        fbd_seq = 0

        def gen_tbls_cols(test, kursus):
            "Tabelite veergude genereerimine, igale alatestile/testiosale oma tabel"
            testiosad = {osa.seq: osa for osa in test.testiosad}
            mitu_osa = len(testiosad) > 1
            on_tase = len(test.testitasemed) > 0
            KEY_TEST = '%s.' % const.FBC_TEST
            KEY_OSA1 = '%s.1' % const.FBC_TESTIOSA
            curr_osa = curr_ala = None
            data = {}
            # kõik võimalikud valikud veergude jaoks
            opt_expr = FeedbackDgmGtbl.get_opt_expr(handler, test, kursus)
            for r in opt_expr:
                expr, label = r
                fbctype, fbcid = expr.split('.', 1)
                if fbctype == const.FBC_TEST:
                    key = mitu_osa and KEY_TEST or KEY_OSA1
                    # kogu testi tulemus koos testiosade tulemustega
                    data[key] = [(expr, label, const.FBD_TULEMUS)]
                    if on_tase:
                        data[key].append((expr, _("Tase"), const.FBD_TASE))
                elif fbctype == const.FBC_TESTIOSA:
                    # testiosa tulemus
                    osa = testiosad.get(int(fbcid))
                    if mitu_osa:
                        # kogu testi tulemuse tabel
                        data[KEY_TEST].append((expr, label, const.FBD_TULEMUS))
                        # testiosa tabel
                        data[expr] = [(expr, label, const.FBD_TULEMUS)]

                    # kirjaliku e-testi korral lisame osa ajakulu
                    on_ajakulu = osa and osa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE)
                    if on_ajakulu:
                        data[expr].append((expr, _("Kasutatud aeg"), const.FBD_AJAKULU))

                    curr_osa = expr
                    curr_ala = None
                elif fbctype == const.FBC_ALATEST:
                    data[curr_osa].append((expr, label, const.FBD_TULEMUS))
                    data[expr] = [(expr, label, const.FBD_TULEMUS)]
                    curr_ala = expr
                elif fbctype == const.FBC_YLESANNE:
                    if curr_ala:
                        data[curr_ala].append((expr, label, const.FBD_TULEMUS))
                    else:
                        data[curr_osa].append((expr, label, const.FBD_TULEMUS))
                elif fbctype == const.FBC_ASPEKT:
                    if curr_ala:
                        data[curr_ala].append((expr, label, const.FBD_TULEMUS))
                    else:
                        data[curr_osa].append((expr, label, const.FBD_TULEMUS))
            return data
        
        def gen_avg(test, testimiskord):
            "Tabelitele lisatavad keskmiste read"
            avg = [const.FBR_SOORITAJA, const.FBR_GRUPP]
            if not test.protsendita:
                avg.append(const.FBR_GRUPP_PR)
            avg.extend([const.FBR_KOOL, const.FBR_LINN, const.FBR_MAAKOND])
            avg.append(const.FBR_RIIK)
            if not test.protsendita:
                avg.append(const.FBR_RIIK_PR)
            return avg

        def gen_osa_gtbl(key, li_expr, avg, fbd_seq):
            "Testiosa/alatesti tabel"
            heading = li_expr[0][1]
            tcol = []
            for expr, label, fbdtype in li_expr:
                tcol.append({
                    'name': label,
                    'expr': expr,
                    'displaytype': fbdtype,
                    })
            dname = 'gtbl'
            js = {
                'dname': dname,
                'width': None,
                'height': None,
                'tcol': tcol,
                'avg_row': avg,
                'heading': heading,
                #'cmp_valim': True,
                }
            buf = json.dumps(js).encode('utf-8')
            params = base64.b64encode(buf).decode('ascii')
            txt = handler.c.opt.title_feedbackdgm(dname)
            fbd_id = f'fbd_{fbd_seq}'
            buf = f'<div class="fbdiagram" contenteditable="false" fbtype="{dname}" params="{params}" id="{fbd_id}">{txt}</div> <br/>'
            return buf

        # tabelite veerud
        data = gen_tbls_cols(test, kursus)
        # igale tabelile lisatavad keskmiste read
        avg = gen_avg(test, testimiskord)
        
        # tabelite lisamine mallile
        template = ''
        for key, li_expr in data.items():
            fbd_seq += 1
            template += gen_osa_gtbl(key, li_expr, avg, fbd_seq)

        if not test.pallideta:
            # lisame klassi tulemuste tulpdiagrammi
            dname = 'klassyl'
            js = {
                'dname': dname,
                'width': 900,
                }
            buf = json.dumps(js).encode('utf-8')
            params = base64.b64encode(buf).decode('ascii')
            txt = handler.c.opt.title_feedbackdgm(dname)
            fbd_seq += 1
            fbd_id = f'fbd_{fbd_seq}'            
            buf = f'<div class="fbdiagram" contenteditable="false" fbtype="{dname}" params="{params}" id="{fbd_id}">{txt}</div> '
            template += buf
        return template

    @classmethod
    def gen_template_gruppidetulemused(cls, handler, test, kursus, testimiskord=None):
        "Genereeritakse vaikimisi gruppide tulemuste mall"
        template = ''
        opt_expr = FeedbackDgmKtbl.get_opt_expr(handler, test)
        tcol = [key for (key, label) in opt_expr if key not in ('lang','sugu')]
            
        # tabelitele lisatavad keskmiste read    
        avg = [const.FBR_KOOL,
               const.FBR_KLASS,
               const.FBR_OPETAJA,
               const.FBR_LINN,
               const.FBR_MAAKOND]

        avg.append(const.FBR_RIIK)

        js = {
            'dname': 'ktbl',
            'tcol2': tcol,
            'avg_row': avg,
            }
        buf = json.dumps(js).encode('utf-8')
        params = base64.b64encode(buf).decode('ascii')
        txt = handler.c.opt.title_feedbackdgm(js['dname'])
        buf_img = f'<div class="fbdiagram" contenteditable="false" fbtype="ktbl" id="fbd_1" params="{params}">{txt}</div> '        
        template += buf_img
        return template

    @classmethod
    def gen_template_opilane(cls, handler, test, kursus):
        "Genereeritakse vaikimisi õpilase tagasiside mall"
        template = ''
        js = {
            'dname': 'opyltbl',
            }
        buf = json.dumps(js).encode('utf-8')
        params = base64.b64encode(buf).decode('ascii')
        txt = handler.c.opt.title_feedbackdgm(js['dname'])
        buf_img = f'<div class="fbdiagram" contenteditable="false" fbtype="opyltbl" params="{params}" id="fbd_1">{txt}</div> '        
        template += buf_img
        return template
       

def report2pdf(handler, html_data):
    "Aruande HTMLi teisendamine PDFiks"

    def url_fetcher(url):
        "Tagasisidefailide piltide lisamine"
        m = re.match(r'graph:testimages/(\d+)/(.+)', url)
        if m:
            test_id, fn = m.groups()
            fn = urllib.parse.unquote(fn)
            q = (model.SessionR.query(model.Tagasisidefail)
                 .filter_by(test_id=test_id)
                 .filter_by(filename=fn)
                 )
            item = q.first()
            if item:
                return dict(string=item.filedata, mime_type=item.mimetype)
        return weasyprint.default_url_fetcher(url)

    # lisame piltide URLi ette "graph:", et antaks url_fetcherile
    html_data = re.sub(r'src="testimages/',
                       'src="graph:testimages/',
                       html_data)
    doc = weasyprint.HTML(string=html_data, url_fetcher=url_fetcher)

    # stiil:
    # - kiri Arial 10pt
    # - tabelile äär ymber
    # - lehekyljenumbrid
    # - stiilid failist avalik/tagasiside/tagasiside.css
    style = """
    body {
      font-family: Arial;
      font-size:10pt;
    }
    table.list {
      background: #e4882a;
      border-spacing: 2px;
    }
    table.list td {
      color: #444;
      background: #fff;
    }
    table.list th {
      color: #fff;
      background: #f7a047;
      font-weight: normal;
    }
    @page {
      @bottom-center {
        content: counter(page) "/" counter(pages);
        font-family: Arial;
        font-size: 8pt;
      }
      size:A4 landscape;
    }
    tr.total-row > td {
    background-color: #e6ddc5;
    }
    tr.city-row > td {
    background-color:#f6f2da;
    }
    font.v-mv-diff {
    color: #ff0000;
    }
    tr.v-mv-diff > td {
    background-color:#fcdcec;
    }
    """
    stylesheets = [weasyprint.CSS(string=style)]
    filedata = doc.write_pdf(stylesheets=stylesheets)
    return filedata
