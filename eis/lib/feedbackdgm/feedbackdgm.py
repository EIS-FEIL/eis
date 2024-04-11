"""Tagasisidevormi diagramm
"""
from lxml import etree
from lxml.builder import E
from chameleon import PageTemplate
import pickle
import math
import sqlalchemy as sa
import base64
import json
import io
import requests
import plotly.graph_objects as go
import plotly.express as px
import plotly.io
from eis.lib.base import *
from eis.lib.helpers import fstr, literal
from eis.lib.block import _outer_xml

log = logging.getLogger(__name__)
_ = i18n._

class FeedbackDgm:
    is_html = False

    # #https://disain.edu.ee/?path=/story/hariduse-e-teenuste-disainis%C3%BCsteem-01-baaselemendid--colours
    # välja pakutud värvid vt
    # https://projektid.edu.ee/pages/viewpage.action?spaceKey=EIS2&title=Testi+tagasiside+disain
    # pikk2 
    default_colors = ('#E8384F', '#20AAEA', '#FD9A00', '#8E47E6', '#62D26F',
                      '#FC91AD', '#4186E0', '#D9E300', '#EA4E9D', '#FF784A')
    # siniroheline valgus
    #default_colors = ('#13254B','#1756AF','#2770D3','#01B6E6','#A0DCF8',
    #                  '#206A32','#17A548','#60E447','#A9EBB4','#D4FAAE')
    # sinimustvalge
    #default_colors = ('#B9D9EB','#90C8E8','#41B6E6','#009CDE','#0072CE','#003087','#041E42')

    def __init__(self, handler, fl):
        self.handler = handler
        self.stat = fl.stat
        self.fl = fl

    def draw_inline(self, fig, width=None):
        "inline-pildi sisu genereerimine"
        if fig is not None:
            try:
                if width:
                    fdata = fig.to_image(format='png', width=width)
                else:
                    fdata = fig.to_image(format='png')
            except ValueError as ex:
                # ValueError: Image export using the "kaleido" engine requires the kaleido package
                log.error('plotly to_image: ' + str(ex))
                return ''
            buf = base64.b64encode(fdata).decode('ascii')        
            return 'data:image/png;base64,' + buf

    def draw_params(self, encoded_params, width, height=None):
        "Etteantud json parameetrite põhjal joonistatakse diagramm"
        try:
            params = pickle.loads(bytes.fromhex(encoded_params))
        except:
            params = None
        if params:
            fdata = ''
            try:
                fig = plotly.io.from_json(params)
                fdata = fig.to_image(format='png')
            except ValueError as ex:
                fdata = b''
            return fdata


    def tbl_col_filter(self, header):
        "Tabeli väljade kuvamise/peitmise filtri moodustamine"
        if self.stat.is_pdf:
            # PDFis pole filtrit vaja
            return ''
        
        # filtri peitmise nupp
        close_btn =  '<div class="text-right">' +\
            f'<button type="button" class="close" aria-label="{_("Sule")}">' +\
            '<i class="mdi mdi-close" aria-hidden="true"></i>' +\
            '</button>' +\
            '</div>'

        # filtri avamise nupp
        open_btn = '<div class="text-right">' +\
              f'<div class="mdi mdi-chevron-down open-filter mr-2" aria-hidden="true" title="{_("Tabeli veergude valimine")}">{_("Rohkem valikuid")}</div>' +\
              '</div>'

        inputs = self.tbl_col_filter_items(header)

        # z-index peab yletama graafilise protsendi, kus z-index=100
        fstyle = "display:none;background-color:#fff;z-index:101;position:absolute;right:10px"
        div = f'<div class="fbtbl-filter rounded border p-3" style="{fstyle}">' +\
              '<div class="d-flex">' +\
              '<div class="flex-grow-1">' + inputs + '</div>' +\
              close_btn +\
              '</div></div>' +\
              open_btn
        return div

    def tbl_col_filter_items(self, header):
        "Tabeli väljade valimise märkeruudud"
        h = self.handler.h
        items = []
        for (ind, (key, label)) in enumerate(header):
            if key and label:
                cb = h.checkbox1(key,
                                 1,
                                 checked=True,
                                 label=label,
                                 class_="fbtbl-hide-filter",
                                 ronly=False)
                buf = '<div>' + str(cb) + '</div>'
                items.append(buf)

        buf = self.tbl_col_filter_layout(items)
        wrapper = '<div class="d-flex flex-wrap">' + buf + '</div>'
        return wrapper

    def tbl_col_filter_layout(self, items, cnt1=0):
        "Filtri väljad jagatakse nelja veergu"
        # väljade arv
        cnt = len(items)
        # väljade arv veerus
        if cnt1:
            # esimese veeru väljad on juba välja valitud
            rows_in_col = max(1, math.ceil((cnt - cnt1) / 3))
        else:
            rows_in_col = max(1, math.ceil(cnt / 4))

        # jagame väljad 4 veergu
        cols = []
        n = 0
        for i in range(4):
            if i == 0 and cnt1:
                n_end = cnt1
            else:
                n_end = n + rows_in_col
            cols.append(items[n:n_end])
            if n_end > cnt:
                break
            n = n_end
            
        buf = ''
        for n, col in enumerate(cols):
            if n == 0 and cnt1 and cnt > cnt1:
                # kui esimene veerg on grupeerimistingimused, siis
                # need eraldatakse joonega teistest veergudest
                cls = 'border-right mr-2'
            else:
                cls = ''
            buf += f'<div class="pr-2 {cls}">' + ' '.join(col) + '</div>\n'
        return buf

