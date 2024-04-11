"""Tagasisidevormi diagramm
"""
import sqlalchemy as sa
import base64
import json
import io
import decimal
import requests
from eis.lib.base import *
from eis.lib.helpers import fstr, literal
from eis.lib.block import _outer_xml
from .feedbackdgm import FeedbackDgm

log = logging.getLogger(__name__)
_ = i18n._

class FeedbackDgmOpyltbl(FeedbackDgm):
    "Õpilase vaikimisi tulemuste tabel ülesannete kaupa"
    is_html = True
    
    def data_by_params(self, data):
        return self.data()

    def data(self):
        from eis.lib.examsaga import ExamSaga

        is_pdf = self.handler.c.is_pdf
        is_preview = self.handler.c.is_preview
        stat = self.stat
        sooritaja = stat.sooritaja
        if not sooritaja:
            # tagasisidevormi salvestamine
            return []
        test = sooritaja.test
        test_pallideta = test.test_pallideta
        testimiskord = sooritaja.testimiskord
        yhisosa = testimiskord and test.yhisosa_max_pallid

        if testimiskord:
            permitted = False
            if testimiskord.ylesandetulemused_avaldet:
                permitted = True
            else:
                # Ylesannete tulemusi ei ole avaldatud
                eeltest = test.eeltest
                if eeltest and (eeltest.tagasiside_sooritajale or eeltest.tagasiside_koolile):
                    # kui on lubatud ainult yhele neist, siis toimib makos olev kontroll
                    permitted = True
            if not permitted:
                return []

        items = []
        sooritused = list(sooritaja.sooritused)
        mitu_testiosa = len(sooritused) > 1
        
        def _add_row_ty(osa, ty, yv):
            "Ülesande rida tabelis"
            item = []
            if mitu_testiosa:
                item.append(osa.tahis)

            label = ty.tahis or ''
            if ty.nimi and ty.nimi != ty.tahis:
                label += ' ' + ty.nimi
            item.append(label)

            if test_pallideta:
                item.append('')
            if yv:
                value = not test_pallideta and yv.get_tulemus() or ''
                item.append(value)

                values = []
                for yh in yv.ylesandehinded:
                    if yh.markus and yh.hindamine.loplik:
                        values.append(yh.markus.replace('\n', '<br/>'))
                item.append('<br/>'.join(values))
                # märkused
                item.append('')
                if yhisosa:
                    value = yv.get_yhisosa_tulemus()
                    item.append(value or '')
            else:
                item.extend(['',''])
            items.append((item, {'type':'ty'}))

        def _get_aspektimarkused(yv, hindamisaspekt_id, punktid):
            markused = []
            # kui ylesande hindamisaspektil on kirjeldatud märkused selle punktide arvu kohta,
            # siis leitakse see
            if punktid is not None:
                q = (model.SessionR.query(model.Punktikirjeldus.kirjeldus)
                     .filter_by(hindamisaspekt_id=hindamisaspekt_id)
                     .filter_by(punktid=punktid)
                     )
                for kirjeldus, in q.all():
                    markused.append(kirjeldus)
            return markused
            
        def _add_row_had(osa, ty, yv):
            "Hindamisaspektide read tabelis"
            if yv and (not testimiskord or testimiskord.aspektitulemused_avaldet):
                for va in yv.vastusaspektid:
                    item = []
                    ha = va.hindamisaspekt
                    if mitu_testiosa:
                        item.append('')
                    item.append(ha.aspekt_nimi)
                    if test_pallideta:
                        item.append('')
                    value = va.get_tulemus((ha.max_pallid or 0) * ha.kaal)
                    item.append(value or '')

                    values = []
                    for markus in _get_aspektimarkused(yv, ha.id, va.pallid):
                        values.append(markus.replace('\n', '<br/>'))
                    item.append('<br/>'.join(values))
                    items.append((item, {'type': 'ha'}))

        def _add_rows_formula(osa, ty, yv):
            "Vastuste read tabelis"
            for kv in yv.kysimusevastused:
                kysimus = kv.kysimus
                sp = kysimus.sisuplokk
                if not kysimus.ei_arvesta:
                    item = []
                    if mitu_testiosa:
                        item.append(osa.tahis)

                    value = ty.tahis or ''
                    if ty.nimi and value != ty.nimi:
                        value += ' ' + ty.nimi
                    item.append(value)

                    value = utils.html2plain(sp.nimi or '') + ' ' + kysimus.kood
                    item.append(value)

                    values = []
                    for kvs in kv.kvsisud:
                        value = kvs.as_string(False)
                        values.append(value)
                    item.append('<br/>'.join(values))
                    item.append('')
                    items.append((item, {'type': 'f'}))

        for tos in sooritused:
            osa = tos.testiosa
            kursus = sooritaja.kursus_kood
            prev_alatest_id = None
            for ty in osa.testiylesanded:
                if (not kursus or ty.alatest and ty.alatest.kursus_kood == kursus) and ty.liik == const.TY_LIIK_Y:
                    ylesandevastused = ExamSaga(self.handler).sooritus_ylesandevastused(tos, ty.id)
                    for yv in ylesandevastused or [None]:
                        if not test_pallideta:
                            _add_row_ty(osa, ty, yv)
                            _add_row_had(osa, ty, yv)
                        if yv and test_pallideta:
                            _add_rows_formula(osa, ty, yv)
    
        header = []
        if mitu_testiosa:
            header.append(_("Testiosa"))
        header.append(_("Ülesanne"))
        if test_pallideta:
            header.append(_("Küsimus"))
        header.append(_("Tulemus"))
        header.append(_("Märkused"))
        if yhisosa:
            header.append(_("Ühisosa"))

        return header, items, None

    def draw_html(self, data, fbd_id, body_only=False):
        if not data:
            return ''
        header, items, dummy = data
        buf = '<div class="fbtbl fbtbl-opyltbl">' +\
              '<div style="overflow-x:auto">' +\
              '<table class="table table-striped">' +\
              '<thead><tr>'
        for ind, name in enumerate(header):
            buf += f'<th>{name}</th>'
        buf += '</tr></thead>\n<tbody>'
        for row, attrs in items:
            buf += '<tr>'
            for ind, value in enumerate(row):
                tdatt = ''
                if attrs.get('type') == 'ha' and ind == 0:
                    tdatt = 'style="text-align:right"'
                buf += f'<td {tdatt}>{value}</td>'
            buf += '</tr>\n'
        buf += '</tbody></table></div></div>'
        return buf

