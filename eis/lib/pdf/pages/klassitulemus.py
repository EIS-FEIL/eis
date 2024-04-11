# -*- coding: utf-8 -*- 
"Klassi tulemus testikaupa vaates"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const, Klrida
import eis.model as model
import eis.lib.helpers as h

def generate(story, header, footer, items, c, img_buf, is_landscape):
    N = ParagraphStyle(name='Normal',
                       fontName='Times-Roman',
                       fontSize=11,
                       leading=12,
                       spaceBefore=3,
                       spaceAfter=3)
    N10 = ParagraphStyle(name='Normal10',
                        parent=N,
                        fontSize=10)
    N9 = ParagraphStyle(name='Normal9',
                        parent=N,
                        fontSize=9)
    N8 = ParagraphStyle(name='Normal8',
                        parent=N,
                        fontSize=8)
    N7 = ParagraphStyle(name='Normal7',
                        parent=N,
                        fontSize=7)        
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

    q = model.SessionR.query(model.Testiruum.algus).filter(model.Testiruum.id.in_(c.testiruumid_id)).order_by(model.Testiruum.algus)
    paevad = list()
    for algus, in q.all():
        s_algus = h.str_from_date(algus)
        if s_algus not in paevad:
            paevad.append(s_algus)
    title += ' ' + ', '.join(paevad)
    if c.kursus:
        kursus_nimi = Klrida.get_str('KURSUS', c.kursus, ylem_kood=c.test.aine_kood)
        title += ' (%s)' % kursus_nimi.lower()

    story.append(Paragraph(title, NH))
    story.append(Paragraph(c.user.koht.nimi, NH))
    if c.opetaja_nimi:
        klass = 'Õpetaja %s õpilased' % c.opetaja_nimi
    else:
        klass = '%s%s klass' % (c.klass, c.paralleel or '')
    story.append(Paragraph(klass, NH))
    story.append(Spacer(5*mm,5*mm))

    nice_width = 272*mm
    if img_buf is not None:
        img_buf.seek(0)
        img = Image(img_buf)
        img.drawWidth = img.imageWidth / 3
        img.drawHeight = img.imageHeight / 3        
        story.append(img)
        story.append(Spacer(5*mm, 5*mm))

    # proovime erinevaid kirjasuurusi, kuni tabel ära mahub
    table = None
    for pstyle in (N, N10, N9, N8):
        try:
            table = _gen_table(header, footer, items, pstyle, True, c.header_osa)
            break
        except:
            continue
    if table is None:
        table = _gen_table(header, footer, items, N7, False, c.header_osa)        
        
    story.append(table)

def _gen_table(header, footer, items, N, raise_table_too_wide, header_osa):
    max_width = 280*mm
    nice_width = 272*mm

    data = []
    row = [Paragraph('<b>%s</b>' % s, N) for s in header]
    data.append(row)

    grey = '#B5B2AA'
    TS = [('GRID',(0,0),(-1,-1), 0.5, grey),
          ('LINEABOVE', (0,0), (-1,0), 1, grey),
          ('LINEBELOW',(0,-1),(-1,0),1, grey),
          ('FONTNAME', (0,-1),(-1,0),'Times-Bold'),
          ('VALIGN', (0,0), (-1,-1), 'TOP'),
          ('LEFTPADDING', (0,0), (-1,-1), 2),
          ('RIGHTPADDING', (0,0), (-1,-1), 2),          
          ]

    if header_osa:
        # testiosade pealkirjad esimesse ritta (rvaade korral)
        row = []
        x = 0
        for title, colspan in header_osa:
            if colspan:
                row.append(Paragraph('<b>%s</b>' % title, N))
                for ind in range(1, colspan):
                    row.append(Paragraph('', N))
                if colspan > 1:
                    TS.append(('SPAN', (x,0), (x+colspan-1, 0)))
                x += colspan
        data = [row] + data
        body_start = 2
    else:
        body_start = 1
    cnt = 0
    for item in footer:
        cnt += 1
        row = []
        for s in item[1:]:
            row.append(Paragraph(s is not None and str(s) or '', N))
        data.append(row)
    TS.append(('BACKGROUND', (0, body_start), (-1, cnt + body_start - 1), '#e9e9e9'))

    backs = []
    for item in items:
        cnt += 1
        if cnt % 2:
            # tulemused vahelduva halli taustaga
            backs.append(cnt + body_start - 1)
        row = []
        for s in item[1:]:
            row.append(Paragraph(s is not None and str(s) or '', N))
        data.append(row)

    for cnt in backs:
        TS.append(('BACKGROUND', (0, cnt), (-1, cnt), '#e9e9e9'))


    data, col_widths, vaba, TS = calc_table_width(data,
                                                  max_width=max_width,
                                                  nice_width=nice_width,
                                                  min_extra=5,
                                                  style=TS,
                                                  raise_table_too_wide=raise_table_too_wide)
    # kui jääb vaba ruumi
    if vaba > 0:
        col_widths[0] += vaba/2
        cnt = len(col_widths)
        for n in range(1, cnt):
            col_widths[n] += vaba/2/(cnt-1)

    return Table(data,
                 colWidths=col_widths,
                 style=TS,
                 hAlign='LEFT',
                 repeatRows=1)

def first_page(canvas, doc, pdoc):
    "Esimese lehekülje jalus"
    canvas.saveState()
    fn_img = os.path.join(IMAGES_DIR,  'haridus_ja_noorteamet_logo.png')
    logo = ImageReader(fn_img)

    # landscape
    x_logo = 226*mm
    y_logo = 183*mm
    x_footer = 12*mm

    # portrait
    #x_logo = 135*mm
    #y_logo = 272*mm
    #x_footer = 20*mm
    canvas.drawImage(logo, x_logo, y_logo, width=140, height=51)        

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
