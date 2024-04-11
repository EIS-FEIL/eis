"Eksami statistika raport avalikus vaates"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const, sa
import eis.model as model
import eis.lib.helpers as h
from .eksamistatistikadgm import gen_dgm_confidence

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
    if qry.kursus:
        kursus_nimi = model.Klrida.get_str('KURSUS', qry.kursus, test.aine_kood)
        title = '%s (%s)' % (title, kursus_nimi.lower())

    story.append(Paragraph(title, NH))
    qry.test = test
    on_c1 = qry.test.aine_kood == const.AINE_ET2 and qry.aasta > 2014

    buf = """
    <b>Selgitused</b>
    <br/> <br/>
    <b>N</b> - sooritajate arv;
    <br/>
    <b>Keskmine</b> - tulemuste aritmeetiline keskmine; (punktide kogusumma jagatud sooritajate arvuga).
    <br/>
    <b>Mediaan</b> - statistiline keskmine, mis jaotab sooritajad kaheks võrdseks rühmaks, milles pooltel
    sooritajatest jääb tulemus alla ja pooltel üle mediaani. Mediaan on aritmeetilise keskmisega
    võrreldes vähem mõjutatud üksikutest eriti tugevatest või nõrkadest tulemustest.
    <br/>
    <b>Min</b> - vähim saadud tulemus.
    <br/>
    <b>Max</b> - maksimaalne saadud tulemus.
    <br/>
    <b>St. hälve</b> - standardhälve.
    <br/>
    <b>AUP</b> - alumine usalduspiir.
    <br/>
    <b>ÜUP</b> - ülemine usalduspiir.
    <br/>
    AUP ja ÜUP tähistavad keskväärtuse usaldusintervalli usaldusnivool 95%. Kui kahe võrreldava grupi 
    usaldusvahemikul on olemas ühisosa, siis ei saa öelda, et keskmiste erinevus on statistiliselt oluline
    """
    if on_c1:
        buf += "<br/>*Eesti keele teise keelena eksamist on vabastatud lõpetajad, kes on eesti keele tasemeeksamil saavutanud C1-keeletaseme. Tunnistuse esitanute arv on ära toodud tabeli viimases veerus."
        
    story.append(Paragraph(buf, N))

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
            # õppevormide andmed puuduvad
            title = 'Gümnaasiumiõpe koolide lõikes'
            _gen_tbl(story, title, qry, [], False)
        
    qry.oppevorm = None
    title = 'Tulemuste sagedustabel (kõik eksaminandid)'
    _gen_sagedustabel(story, title, test, qry)
            
def _gen_tbl(story, title, qry, oppevorm, is_maakond):
    qry.oppevorm = oppevorm
    qry.hinnatud = True
 
    select_fields = [sa.func.count(model.Sooritaja.id),
                     sa.func.avg(model.Sooritaja.pallid),
                     sa.func.min(model.Sooritaja.pallid),
                     sa.func.max(model.Sooritaja.pallid),
                     sa.func.stddev(model.Sooritaja.pallid),
                     ]
   
    q_total = qry._gen_query1(select_fields)
    
    r_total = q_total.first()
    total = r_total[0]
    if total == 0:
        # sooritajaid pole
        return

    data = []
    header = ['', 'N', 'N (%)', 'AUP', 'Keskmine', 'ÜUP', 'Mediaan', 'Min', 'Max', 'St. hälve']

    on_b2 = qry.test.aine_kood == const.AINE_ET2 and qry.aasta > 2014
    if on_b2:
        header.append('B2 tase (%)')

    on_c1 = on_b2 and (not oppevorm or oppevorm == const.OPPEVORM_STATS)
    if on_c1:
        header.append('Lisaks C1 tasemetunnistuse esitanuid*')
        
    row = [Paragraph(s, NB) for s in header]
    data.append(row)

    # 5-st väiksema eksaminandide arvuga koolid yhel real
    koos_id = list()

    # usalduspiiride diagrammi andmed
    dgm_data = []

    def _gen_row(loige_kood, row_title, item, koos_kuni=False):
        row_total, res_avg, res_min, res_max, res_stddev = item
       
        if koos_kuni and row_total < 5:
            # 5-st väiksema eksaminandide arvuga koolid kuvatakse koos yhel real
            koos_id.append(loige_kood)
            return
        
        if is_maakond:
            qry.maakond_kood = loige_kood
        else:
            qry.koolinimi_id = loige_kood
            
        mediaan = qry.query_mediaan()
        aup, yup = qry.query_confidence(row_total, res_stddev, res_avg)

        row_total_pr = row_total * 100. / total
        row = [row_title or 'Määramata',
               str(row_total),
               fstr(row_total_pr),
               fstr(aup),
               fstr(res_avg),
               fstr(yup),
               fstr(mediaan),
               fstr(res_min),
               fstr(res_max),
               fstr(res_stddev),
               ]
        if on_b2:
            # B2 taseme saanute protsent
            q_b2 = qry._gen_query1([sa.func.count(model.Sooritaja.id)])
            b2 = qry.query_tase(q_b2, const.KEELETASE_B2, row_total)
            row.append(fstr(b2))

        if on_c1:
            # C1 taseme sooritanute arv (tasemeeksamilt)
            c1 = qry.query_c1_tunnistus(qry.aasta)
            row.append(str(c1))

        if loige_kood and res_avg is not None:            
            # kui pole kokku-rida, siis läheb graafikule
            max_pallid = qry.test.max_pallid
            if aup is None or yup is None:
                error = 0
            else:
                error = (yup - aup) / 2
            errorpr = error * 100 / max_pallid
            res_avgpr = res_avg * 100 / max_pallid
            dgm_item = (row_title, res_avgpr, errorpr)
            if koos_kuni:
                dgm_data.append(dgm_item)
            else:
                dgm_data.insert(0, dgm_item)
            
        return [Paragraph(r or '', N) for r in row]
    
    if is_maakond:
        # maakonna kaupa
        group_fields = [model.Aadresskomponent.kood, model.Aadresskomponent.nimetus]
        q_all = (qry._gen_query1(group_fields + select_fields,
                                 join_maakond=True)
                 .group_by(*group_fields)
                 .order_by(model.Aadresskomponent.nimetus)
                 )
    else:
        # kooli kaupa
        group_fields = [model.Sooritaja.koolinimi_id, model.Koolinimi.nimi]
        q_all = (qry._gen_query1(group_fields + select_fields,
                                 join_koolinimi=True)
                 .group_by(*group_fields)
                 .order_by(model.Koolinimi.nimi)
                 )

    for item in q_all.all():
        loige_kood, loige_title = item[:2]
        row = _gen_row(loige_kood, loige_title, item[2:], True)
        if row:
            data.append(row)

    ignored_rows = bool(koos_id)

    # kokku-rida
    row = _gen_row(None, 'Kokku', r_total, False)
    data.append(row)

    # Eesti keskmine
    total_avg = r_total[1] * 100 / qry.test.max_pallid
    
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

    if dgm_data:
        li2 = gen_dgm_confidence(dgm_data, total_avg, True)
        for r in li2:
            story.append(r)
    return True

def _gen_sagedustabel(story, title, test, qry):
    
    header = ['Tulemus', 'Eksaminande']
    row = [Paragraph(s, NB) for s in header]
    data = [row]
    
    q = (qry._gen_query1([sa.func.count(model.Sooritaja.pallid),
                          sa.func.round(model.Sooritaja.pallid)])
         .group_by(sa.func.round(model.Sooritaja.pallid))
         .order_by(sa.func.round(model.Sooritaja.pallid))
         )
    for cnt, pallid in q.all():
        if cnt:
            data.append([Paragraph(fstr(pallid), N),
                         Paragraph(str(cnt), N)])

    col_widths = [30*mm, 30*mm]
    story.append(KeepTogether(
            [Paragraph(title, NH2),
             Table(data, 
                   colWidths=col_widths,
                   style=TS,
                   hAlign='LEFT',
                   repeatRows=1)]))

def fstr(value):
    return h.fstr(value, 1)

def first_page(canvas, doc, pdoc):
    "Esimese lehekülje jalus"
    canvas.saveState()
    fn_img = os.path.join(IMAGES_DIR,  'haridus_ja_noorteamet_logo.png')
    logo = ImageReader(fn_img)
    # fail on 215x78
    canvas.drawImage(logo, 158*mm, 272*mm, width=108, height=39)

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
