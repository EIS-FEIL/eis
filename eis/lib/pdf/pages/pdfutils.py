# -*- coding: utf-8 -*- 
"Abifunktsioonid ja ReportLabi moodulite importimine"

import io
import sys
import os
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import StyleSheet1, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import *
from reportlab.platypus.doctemplate import NextFrameFlowable
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.utils import ImageReader

from eis.model import const

import logging
log = logging.getLogger(__name__)

IMAGES_DIR = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'static'), 'images_pdf')

class TableTooWideException(Exception):
    "Mida visata, kui tabel ei mahu lehele ära"
    def __init__(self):
        pass
    
def p(value, style):
    return Paragraph(value, style)

def tp(data, style):
    """Tabeli sisuks mõeldud listi veergudeks antud stringid tehakse paragrahvideks
    """
    for n in range(len(data)):
        for j in range(len(data[n])):
            if isinstance(data[n][j], str):
                data[n][j] = Paragraph(data[n][j], style)
    return data 

def avoid_too_large(story):
    # KeepTogether on vajalik, et ei tuleks LayoutError: ... too large on page...
    # vt ES-2177, ES-2178, ES-3773
    for n in range(len(story)):
        r = story[n]
        if isinstance(r, (Paragraph, Spacer, HRFlowable)):
            story[n] = KeepTogether(r)        
    return story

def calc_table_width(data, max_width=190*mm, nice_width=None, extra=0, min_extra=20, style=None, raise_table_too_wide=False, nice_widths=None):
    "Arvutame tabeli veergude laiused"
    # data - tabeli read, mille põhjal arvutatakse vajalik laius
    # max_width - maksimaalne lubatud tabeli laius
    # nice_width - kena tabeli laius (kena oleks selle mahutada, kui ei mahu, siis kasutatakse max_width)
    # extra - kui jääb ruumi üle, siis igale veerule lisatakse see juurde
    # min_extra - igale veerule lisatakse see alati juurde
    # nice_widths - kenad veerulaiused (nendele veergudele None, mille kohta pole teada)
    # leiame, kui palju ruumi on iga veeru jaoks minimaalselt vaja
    orig_col_cnt = col_cnt = len(data[0])
    col_widths = [min_extra] * col_cnt
    for row in data:
        for n, p in enumerate(row):
            if p != '':
                w = p.minWidth() + min_extra
                col_widths[n] = max(col_widths[n], w)
                #log.debug('%s - %s' % (p.text, p.minWidth()))

    #log.debug('calc_table_width before %s = %s' % \
    #          (int(sum(col_widths)), str([int(r) for r in col_widths])))
    
    # jätame välja need veerud paremas otsas, mis ei mahu ära
    total_width = 0
    
    for n in range(col_cnt):
        w = total_width + col_widths[n]
        #log.debug('%d. kokku %s, max %s' % (n, w, max_width))
        if w > max_width:
            # kõik veerud ei mahu ära, lõikame parempoolsed veerud maha
            if raise_table_too_wide:
                raise TableTooWideException()
            n -= 1
            break
        else:
            # see veerg mahub ära küll
            total_width = w

    if n + 1 < col_cnt:
        # kõik veerud ei mahtunud ära
        col_cnt = n + 1
        data = [row[:col_cnt] for row in data]
        col_widths = col_widths[:col_cnt]

        # võtame stiilist liigsed veerud maha
        log.debug('uus veergude arv: %s (oli %s)' % (col_cnt, orig_col_cnt))
        if style is not None:
            style2 = []
            for r in style:
                #log.debug('STIIL:%s' % str(r))
                if r[0] == 'SPAN':
                    x1, y1 = r[1]
                    x2, y2 = r[2]
                    if x1 >= col_cnt:
                        continue
                    if x2 >= col_cnt:
                        x2 = col_cnt - 1
                        r = ('SPAN', (x1, y1), (x2, y2))
                        #log.debug('STIILIMUUTUS: uus %s' % str(r))                        
                style2.append(r)
            style = style2

    vaba = (nice_width or max_width) - total_width
    #log.debug('calc_table_width: nice=%s, max=%s, total=%s, vaba=%s, extra=%s' % (nice_width, max_width, total_width, vaba, extra))
    if vaba > 0 and extra:
        # kui jäi ruumi yle, siis lisame igale veerule extra
        for n in range(col_cnt):
            if vaba >= extra:
                col_widths[n] += extra
                vaba -= extra
            else:
                break

    # kui on teada soovitud kenad veerulaiused ja on vaba ruumi, siis teeme need veerud nii laiaks
    for n, width in enumerate(nice_widths or []):
        if vaba <= 0:
            break
        if width and col_widths[n] < width:
            dx = min(vaba, width - col_widths[n])
            col_widths[n] += dx
            vaba -= dx

    #log.debug('calc_table_width after  %s = %s' % \
    #          (int(sum(col_widths)), str([int(r) for r in col_widths])))

    # tagastame:
    # tabeli andmed - vajadusel parempoolsed veerud ära võetud
    # tabeli veergude laiused
    # kasutamata ruum (mida saaks veergude vahel jagada)
    if style is None:
        return data, col_widths, vaba
    else:
        return data, col_widths, vaba, style

