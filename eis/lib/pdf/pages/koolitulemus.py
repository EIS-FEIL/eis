# -*- coding: utf-8 -*- 
"Kooli tulemus testikaupa vaates"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const, Klrida
import eis.lib.helpers as h

def generate(story, header, items, c):

    N = ParagraphStyle(name='Normal',
                       fontName='Times-Roman',
                       fontSize=11,
                       leading=12,
                       spaceBefore=3,
                       spaceAfter=3)
    NB = ParagraphStyle(name='NormalBold',
                        parent=N,
                        fontName='Times-Bold')
    NH = ParagraphStyle(name='NormalHeader',
                        parent=NB,
                        fontSize=14,
                        textColor='#4472C4')
    
    if c.test.testiliik_kood == const.TESTILIIK_TASEMETOO:
        aasta = date.today().year
        title = '%d %s e-tasemetöö tulemuste statistika' % (aasta, c.test.aine_nimi)
    else:
        title = c.test.nimi

    paevad = list()
    for tk in c.testimiskorrad:
        millal = tk.millal
        if millal not in paevad:
            paevad.append(millal)
    kuupaevad = ', '.join(paevad)
    title += ' ' + kuupaevad
    if c.kursus:
        kursus_nimi = Klrida.get_str('KURSUS', c.kursus, ylem_kood=c.test.aine_kood)
        title += ' (%s)' % kursus_nimi.lower()
    
    story.append(Spacer(3*mm, 3*mm))
    story.append(Paragraph(title, NH))
    if c.user.koht.id != const.KOHT_EKK:
        story.append(Paragraph(c.user.koht.nimi, NH))

    story.append(Spacer(5*mm,5*mm))

    data = []
    row = [Paragraph(s, NB) for s in header]
    data.append(row)
    grey = '#B5B2AA'
    TS = [('GRID',(0,0),(-1,-1), 0.5, grey),
          ('LINEABOVE', (0,0), (-1,0), 1, grey),
          ('LINEBELOW',(0,-1),(-1,0),1, grey),
          ('FONTNAME', (0,-1),(-1,0),'Times-Bold'),
          ('VALIGN', (0,0), (-1,-1), 'TOP'),
          ]

    cnt = 0
    spans = []
    backs = []
    for title, k_class, k_url, r_items in items:
        cnt_items = len(r_items)
        if cnt_items > 1:
            # yhendame esimese veeru
            spans.append((cnt+1, cnt+cnt_items))

        for r_cnt, (r_item, d_url, d_title) in enumerate(r_items):
            cnt += 1
            if cnt % 2:
                # tulemused vahelduva halli taustaga
                backs.append(cnt)

            row = [Paragraph(r_cnt == 0 and title or '', N)]
            for s in r_item:
                row.append(Paragraph(s is not None and str(s) or '', N))
            data.append(row)

    for k_start, k_end in spans:
        # yhendame esimese veeru lahtrid, milles on sama pealkiri
        TS.append(('SPAN', (0,k_start),(0, k_end)))
    # kui on mitu rida sama tiitliga, siis alustame värvimist teisest veerust
    grey_start = spans and 1 or 0
    for cnt in backs:
        TS.append(('BACKGROUND', (grey_start, cnt), (-1, cnt), '#e9e9e9'))
        
    data, col_widths, vaba = calc_table_width(data, max_width=175*mm, nice_width=165*mm)
    # kui jääb vaba ruumi
    if vaba > 0:
        col_widths[0] += vaba/2
        cnt = len(col_widths)
        for n in range(1, cnt):
            col_widths[n] += vaba/2/(cnt-1)

    story.append(Table(data, 
                       colWidths=col_widths,
                       style=TS,
                       hAlign='LEFT',
                       repeatRows=1))

def first_page(canvas, doc, pdoc):
    "Esimese lehekülje jalus"
    canvas.saveState()
    fn_img = os.path.join(IMAGES_DIR,  'haridus_ja_noorteamet_logo.png')
    logo = ImageReader(fn_img)
    canvas.drawImage(logo, 135*mm, 272*mm, width=140, height=51)

    grey = colors.HexColor('#b5b2aa')
    canvas.setFillColor(grey) # font color
    canvas.setStrokeColor(grey) # line color
    
    x_footer = 20*mm
    y_footer = 23*mm
    canvas.setLineWidth(0.1)
    canvas.line(0, y_footer, 152*mm, y_footer)
    
    canvas.setFont('Times-Roman', 8)
    canvas.drawString(x_footer, 19*mm, 'Haridus- ja Noorteamet / Lõõtsa 4, 11415 Tallinn / Telefon 735 0500 / Registrikood 77001292')
    canvas.drawString(x_footer, 14*mm, 'E-post: info@harno.ee / www.harno.ee')
    canvas.restoreState()

def later_pages(canvas, doc, pdoc):
    "Teise ja järgmiste lehekülgede jalus"
    return first_page(canvas, doc, pdoc)
