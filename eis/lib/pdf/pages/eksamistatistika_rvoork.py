"Eksami statistika raport avalikus vaates"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const, sa
import eis.model as model
import eis.lib.helpers as h

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
                    fontSize=16,
                    spaceBefore=16,
                    spaceAfter=10,
                    textColor='#4472C4')
NH1 = ParagraphStyle(name='NormalHeader1',
                     parent=NH,
                     fontSize=14)
NH2 = ParagraphStyle(name='NormalHeader2',
                     parent=NH,
                     fontSize=12)

GREY = '#B5B2AA'
TS = [('GRID',(0,0),(-1,-1), 0.5, GREY),
      ('LINEABOVE', (0,0), (-1,0), 1, GREY),
      ('LINEBELOW',(0,-1),(-1,0),1, GREY),
      ('FONTNAME', (0,-1),(-1,0),'Times-Bold'),
      ('ALIGN', (0,0), (0,-1), 'RIGHT'),
      ('VALIGN', (0,0), (-1,-1), 'TOP'),
      ('LEFTPADDING', (0,0), (-1,-1), 3),
      ('RIGHTPADDING', (0,0), (-1,-1), 3),
      ]

def generate(story, test, qry):

    title = test.nimi
    story.append(Paragraph(title, NH))
    
    buf = """
    <b>Selgitused</b>
    <br/> <br/>
    <b>N</b> - sooritajate arv;
    <br/>
    """
    buf += """
    <b>Taseme mitte saavutanud</b> - sooritajad, kes ületasid 1-pallise lävendi, kuid ei saavutanud keeletaset.
    """

    story.append(Paragraph(buf, N))

    qry.field_pallid = model.Sooritaja.pallid
    
    title = 'Gümnaasiumi statsionaarne õpe maakondade lõikes'
    rc1 = _gen_tbl(story, title, qry, const.OPPEVORM_STATS, True)

    title = 'Gümnaasiumi mittestatsionaarne õpe maakondade lõikes'
    rc2 = _gen_tbl(story, title, qry, const.OPPEVORM_MITTESTATS, True)    

    if not rc1 and not rc2:
        # õppevormide andmed puuduvad
        title = 'Gümnaasiumiõpe maakondade lõikes'
        _gen_tbl(story, title, qry, [], True)

    #if qry.aasta < 2022:
    if True: # ES-3280 piirangu eemaldas ES-3315
        # alates 2022 ei kuvata koolide lõikes andmeid (ES-3280)        
        title = 'Gümnaasiumi statsionaarne õpe koolide lõikes'
        rc1 = _gen_tbl(story, title, qry, const.OPPEVORM_STATS, False)

        title = 'Gümnaasiumi mittestatsionaarne õpe koolide lõikes'
        rc2 = _gen_tbl(story, title, qry, const.OPPEVORM_MITTESTATS, False)    

        if not rc1 and not rc2:
            title = 'Gümnaasiumiõpe koolide lõikes'
            _gen_tbl(story, title, qry, [], False)
            
def _gen_tbl(story, title, qry, oppevorm, is_maakond):
    qry.oppevorm = oppevorm
    qry.hinnatud = True

    select_fields = [sa.func.count(model.Sooritaja.id),
                     sa.func.avg(model.Sooritaja.tulemus_protsent),
                     sa.func.stddev(model.Sooritaja.tulemus_protsent),
                     ]
    q_total = qry._gen_query1(select_fields)

    r_total = q_total.first()
    total, total_avg, total_stddev = r_total[:3]
    if total == 0:
        # sooritajaid pole
        return

    q_aadress = (q_total.outerjoin(
        (model.Aadresskomponent,
         sa.and_(model.Aadresskomponent.kood==model.Sooritaja.kool_aadress_kood1,
                 model.Aadresskomponent.tase==1)))
                )
    data = []
    header = ['', 'N', 'Taseme mitte saavutanud (%)', 'B1 (%)', 'B2 (%)', 'C1 (%)', 'C2 (%)']

    row = [Paragraph(s, NB) for s in header]
    data.append(row)

    # 5-st väiksema eksaminandide arvuga read koos
    koos_id = list()

    def _gen_row(loige_kood, row_title, item, q, koos_kuni=False):
        row_total, res_avgpr, res_stddev = item[:3]
        
        if koos_kuni and row_total < 5:
            koos_id.append(loige_kood)
            return
        
        tasemeta = qry.query_tasemeta(q, row_total)
        b1 = qry.query_tase(q, const.KEELETASE_B1, row_total)
        b2 = qry.query_tase(q, const.KEELETASE_B2, row_total)
        c1 = qry.query_tase(q, const.KEELETASE_C1, row_total)
        c2 = qry.query_tase(q, const.KEELETASE_C2, row_total)

        row = [row_title or 'Määramata',
               str(row_total),
               fstr(tasemeta),
               fstr(b1),
               fstr(b2),
               fstr(c1),
               fstr(c2),
               ]

        if loige_kood and res_avgpr is not None:
            # kui pole kokku-rida, siis läheb graafikule
            aup, yup = qry.query_confidence(row_total, res_stddev, res_avgpr)            
            if aup is None or yup is None:
                error = 0
            else:
                error = (yup - aup) / 2
            
        return [Paragraph(r or '', N) for r in row]

    select_fields = [sa.func.count(model.Sooritaja.id)]
    if is_maakond:
        # maakonna kaupa
        group_fields = [model.Aadresskomponent.kood, model.Aadresskomponent.nimetus]
        q_all = (q_aadress.add_columns(*group_fields)
                 .group_by(*group_fields)
                 .order_by(model.Aadresskomponent.nimetus)
                 )
    else:
        # kooli kaupa
        group_fields = [model.Sooritaja.koolinimi_id, model.Koolinimi.nimi]
        q_all = (q_total.add_columns(*group_fields)
                 .join(model.Sooritaja.koolinimi)
                 .group_by(*group_fields)
                 .order_by(model.Koolinimi.nimi)
                 )

    for item in q_all.all():
        row_total, res_avgpr, res_stddev, loige_kood, loige_title = item
        if is_maakond:
            q = q_aadress.filter(model.Sooritaja.kool_aadress_kood1==loige_kood)
        else:
            q = q_total.filter(model.Sooritaja.koolinimi_id==loige_kood)
        row = _gen_row(loige_kood, loige_title, item, q, True)
        if row:
            data.append(row)

    def _filter_null(field, values):
        if None not in values:
            return field.in_(values)
        else:
            values = [r for r in values if r is not None]
            if values:
                return model.sa.or_(field.in_(values), field==None)
            else:
                return field==None

    ignored_rows = bool(koos_id)
        
    # kokku-rida
    row = _gen_row(None, 'Kokku', r_total, q_total)
    data.append(row)

    # veergude laiused
    data, col_widths, vaba = calc_table_width(data, nice_width=180*mm, min_extra=6)
    if vaba > 0:
        d = 40*mm - col_widths[0]
        if d > 0:
            d = min(d, vaba)
            col_widths[0] += d
            vaba -= d
        cnt = len(col_widths)
        for n in range(cnt):
            col_widths[n] += vaba/cnt

    li = [Paragraph(title, NH2),
          Table(data, 
                colWidths=col_widths,
                style=TS,
                hAlign='LEFT',
                repeatRows=1)
          ]
    if ignored_rows:
        li.append(Paragraph('Statistikat ei kuvata, kui otsitavas grupis on vähem kui 5 sooritajat', N))
    story.append(KeepTogether(li))
    return True

def fstr(value):
    return h.fstr(value, 1)

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
