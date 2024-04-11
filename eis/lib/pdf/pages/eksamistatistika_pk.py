"Eksami statistika raport avalikus vaates"

import io
import math

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const, sa
import eis.model as model
import eis.lib.helpers as h
from .eksamistatistikadgm import gen_dgm_confidence, gen_dgm_jaotus, gen_dgm_sugu, gen_dgm_ylesanded

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
      ]

def generate(story, test, qry):

    #title = u'%s - %s aastal %s' % (test.testiliik_nimi, test.nimi, qry.aasta)
    title = test.nimi
    if qry.kursus:
        kursus_nimi = model.Klrida.get_str('KURSUS', qry.kursus, test.aine_kood)
        title = '%s (%s)' % (title, kursus_nimi.lower())
        
    story.append(Paragraph(title, NH))
    
    if qry.aasta == 2020:
        story.append(Paragraph("2020. aastal toimus ainult eesti keel teise keelena põhikooli lõpueksam. Eksamil osalemine oli vabatahtlik.", N))
        story.append(Spacer(2*mm, 2*mm))

    buf = """
    <b>Selgitused</b>
    <br/> <br/>
    <b>Valim</b> - sooritajate arv;
    <br/>
    <b>Keskmine tulemus</b> - tulemuste protsentuaalne keskmine;
    <br/>
    <b>Keskmine</b> - tulemuste aritmeetiline keskmine (punktide kogusumma jagatud sooritajate arvuga);
    <br/>
    <b>Mediaan</b> - statistiline keskmine, mis jaotab sooritajad kaheks võrdseks rühmaks, millest pooltel
    sooritajatest jääb tulemus alla ja pooltel üle mediaani. Mediaan on aritmeetilise keskmisega
    võrreldes vähem mõjutatud üksikutest eriti tugevatest või nõrkadest tulemustest;
    <br/>
    <b>Min</b> - vähim saadud tulemus;
    <br/>
    <b>Max</b> - maksimaalne saadud tulemus;
    """

    if test.testiliik_kood == const.TESTILIIK_POHIKOOL:
        buf += """
        <br/>
        <b>Edukus</b> - õigesti lahendatud vähemalt 50% põhikooli lõpueksamitööst;
        <br/>
        <b>Kvaliteet</b> - õigesti lahendatud vähemalt 75% põhikooli lõpueksamitööst.
        """

    story.append(Paragraph(buf, N))

    _gen_yldandmed(story, 'Maakonna järgi', test, qry, is_maakond=True)
    oppekeeled = _gen_yldandmed(story, 'Õppekeele järgi', test, qry, is_oppekeel=True)
    _gen_yldandmed(story, 'Soo järgi', test, qry, is_sugu=True)

    oppekeeled.sort()
            
    p = Paragraph('Tulemuste jaotuse sagedustabel', NH1)
    p.keepWithNext = True
    story.append(p)
    _gen_jaotustabel(story, test, qry, oppekeeled)

    osad = []
    for testiosa in test.testiosad:
        on_alatestid = False
        for alatest in testiosa.alatestid:
            on_ylesanded = False
            for ty in alatest.testiylesanded:
                if ty.liik == const.TY_LIIK_Y:
                    on_ylesanded = True
                    break
            if on_ylesanded:
                osad.append(alatest)
            on_alatestid = True
        if not on_alatestid:
            osad.append(testiosa)
                
    if len(osad) > 1:
        for osa in osad:
            p = Paragraph(osa.nimi, NH1)            
            p.keepWithNext = True
            story.append(p)

            title = 'Osa tulemused õppekeele järgi'
            _gen_osa_yldandmed(story, title, osa, qry, is_oppekeel=True)

            title = 'Osa tulemused soo järgi'
            _gen_osa_yldandmed(story, title, osa, qry, is_sugu=True)
            
    y_data = list()
    story.append(KeepTogether([
        Paragraph('Ülesannete koondstatistika', NH2),
        _gen_ylesanded(test, qry, y_data, None) # soo järgi
        ]))
    if len(oppekeeled) > 1:
        # koondstatistika õppekeele järgi
        story.append(Spacer(2*mm, 2*mm))        
        story.append(_gen_ylesanded(test, qry, y_data, oppekeeled))

    _gen_diagramm_jaotus(story, test, qry)
    _gen_diagramm_sugu(story, test, qry)
    _gen_diagramm_ylesanded(story, y_data)
    if len(osad) > 1:
        for osa in osad:
            _gen_diagramm_osa(story, osa, qry)
            
def _gen_yldandmed(story, title, test, qry, is_maakond=False, is_oppekeel=False, is_sugu=False):
    
    data = []
    header = ['', 'Valim', 'Keskmine tulemus (%)', 'Min', 'Keskmine', 'Mediaan', 'Max']
    if test.testiliik_kood == const.TESTILIIK_POHIKOOL:
        header = header + ['Edukus', 'Kvaliteet', 'Edukus (%)', 'Kvaliteet (%)']
    row = [Paragraph(s, NB) for s in header]
    data.append(row)

    def _set_qry_loige(loige_kood):
        if is_maakond:
            qry.maakond_kood = loige_kood
        elif is_oppekeel:
            qry.oppekeel = loige_kood
        elif is_sugu:
            qry.sugu = loige_kood

    koos_id = list()
    dgm_data = []

    def _gen_row(loige_kood, loige_nimi, item):
        total, res_avgpr, res_min, res_avg, res_max, res_stddevpr = item        
        if total < 5 and loige_kood:
            # 5-st väiksema eksaminandide arvuga read koos
            koos_id.append(loige_kood)
            return
        
        mediaan = qry.query_mediaan()
        if test.testiliik_kood == const.TESTILIIK_POHIKOOL:        
            q = (qry._gen_query1([sa.func.count(model.Sooritaja.id)])
                 .filter(model.Sooritaja.staatus==const.S_STAATUS_TEHTUD)
                 )
            edukus, edukus_pr = qry.query_max(q, 49.995, total)
            kvaliteet, kvaliteet_pr = qry.query_max(q, 74.995, total)

        if loige_kood and res_avgpr is not None:
            # kui pole kokku-rida, siis läheb graafikule
            aup, yup = qry.query_confidence(total, res_stddevpr, res_avgpr)
            if aup is None or yup is None:
                error = 0
            else:
                error = (yup - aup)/2
            dgm_item = (loige_nimi, res_avgpr, error)
            dgm_data.append(dgm_item)
            #dgm_data.insert(0, dgm_item)
        
        row = [Paragraph(loige_nimi or '-', N),
               Paragraph(str(total), N),
               Paragraph(fstr(res_avgpr), N),
               Paragraph(fstr(res_min), N),
               Paragraph(fstr(res_avg), N),
               Paragraph(fstr(mediaan) or '', N),
               Paragraph(fstr(res_max), N),
               ]
        if test.testiliik_kood == const.TESTILIIK_POHIKOOL:
            row = row + [
                Paragraph(fstr(edukus), N),
                Paragraph(fstr(kvaliteet), N),
                Paragraph(fstr(edukus_pr), N),
                Paragraph(fstr(kvaliteet_pr), N),
                ]
        return row

    select_fields = [sa.func.count(model.Sooritaja.id),
                     sa.func.avg(model.Sooritaja.tulemus_protsent),
                     sa.func.min(model.Sooritaja.pallid),
                     sa.func.avg(model.Sooritaja.pallid),
                     sa.func.max(model.Sooritaja.pallid),
                     sa.func.stddev(model.Sooritaja.tulemus_protsent),
                     ]

    if is_maakond:
        group_fields = [model.Aadresskomponent.kood, model.Aadresskomponent.nimetus]
        q_all = (qry._gen_query1(group_fields + select_fields,
                                 join_maakond=True)
                 .group_by(*group_fields)
                 .order_by(group_fields[1])
                 )
    elif is_oppekeel:
        group_fields = [model.Sooritaja.oppekeel, model.Sooritaja.oppekeel]
        q_all = (qry._gen_query1(group_fields + select_fields)
                 .group_by(*group_fields)
                 .order_by(group_fields[1])
                 )
    elif is_sugu:
        group_fields = [model.Kasutaja.sugu, model.Kasutaja.sugu]
        q_all = (qry._gen_query1(group_fields + select_fields,
                                 join_kasutaja=True)
                 .group_by(*group_fields)
                 .order_by(group_fields[1])
                 )

    leitud_loiked = []
    for item in q_all.all():
        loige_kood, loige_nimi = item[:2]
        leitud_loiked.append(loige_kood)
        if is_oppekeel:
            loige_nimi = get_oppekeel(loige_kood)
        elif is_sugu:
            loige_nimi = get_sugu(loige_kood)

        _set_qry_loige(loige_kood or qry.NULL)
        row = _gen_row(loige_kood, loige_nimi, item[2:])
        if row:
            data.append(row)

    ignored_rows = bool(koos_id)
    # ES-2790 kaotati grupeeriv rida, kus oli 5-st väiksemate sooritajate arvuga read kokku

    # kokku-rida
    _set_qry_loige(None)
    q_all = qry._gen_query1(select_fields)
    item = q_all.first()
    row = _gen_row(None, 'Kokku', item)
    data.append(row)
    total_avg = item[1]
    
    # veergude laiused
    data, col_widths, vaba = calc_table_width(data, max_width=275*mm, nice_width=265*mm)
    if vaba > 0:
        d = 40*mm - col_widths[0]
        if d > 0:
            col_widths[0] += d
            vaba -= d

        cnt = len(col_widths)
        for n in range(1, cnt):
            col_widths[n] += vaba/cnt

    tbl = Table(data, 
                colWidths=col_widths,
                style=TS,
                hAlign='LEFT',
                repeatRows=1)

    li = []
    if is_maakond:
        # maakond on esimene jaotus, enne seda kuvame yldpealkirja
        p = Paragraph('Üldandmed', NH1)
        li.append(p)
    li.extend([Paragraph(title, NH2), tbl])
    if ignored_rows:
        li.append(Paragraph('Statistikat ei kuvata, kui otsitavas grupis on vähem kui 5 sooritajat', N))
    if dgm_data and total_avg is not None:
        li2 = gen_dgm_confidence(dgm_data, total_avg, False)
        li.extend(li2)

    story.append(KeepTogether(li))
    return leitud_loiked

def _gen_jaotustabel(story, test, qry, oppekeeled):

    # soo järgi tabelid
    header = ['', 'Poisid', 'Tüdrukud', 'Kokku']
    row_s = [Paragraph(s, NB) for s in header]

    # õppekeele järgi tabelid
    if len(oppekeeled) == 1:
        # ainsa keele järgi pole mõtet jaotust vaadata
        oppekeeled = []
    header = ['']
    for value in oppekeeled:
        text = get_oppekeel(value) or value
        header.append(text.capitalize())
    row_k = [Paragraph(s, NB) for s in header]
    
    max_pallid = test.max_pallid
    field = model.Sooritaja.pallid

    q = (qry._gen_query1([sa.func.count(field)],
                         join_kasutaja=True)
         )
    total = q.scalar()

    def proc(value):
        if total:
            return fstr(value * 100. / total)
        else:
            return '0'

    # soo järgi absoluutarvudes
    data_sn = [row_s]
    # soo järgi protsentides
    data_sp = [row_s]
    # keele järgi absoluutarvutdes
    data_kn = [row_k]
    # keele järgi protsentides
    data_kp = [row_k]

    # mitmes veerg välja jätta, kuna on alla 5 osaleja
    ignore_col_s = []
    ignore_col_k = []
    
    # testi pallid jagatakse vahemikeks 20%,50%,75% ja 90% järgi
    steps = sorted(set([round(max_pallid*r/100.) for r in (20, 50, 75, 90)])) +\
            [max_pallid+1, None]    
    min_p = 0
    for max_p in steps:
        if max_p:
            q1 = q.filter(field < max_p - 0.5)
            if min_p:
                q1 = q1.filter(field >= min_p)
            row_title = '%d-%dp' % (min_p, max_p-1) 
            min_p = max_p
        else:
            q1 = q
            row_title = 'Kokku'
            
        row_total = q1.scalar()

        # soo järgi
        row_sn = [row_title]
        row_sp = [row_title]
        sugu_m = q1.filter(model.Kasutaja.sugu == const.SUGU_M).scalar()
        sugu_n = q1.filter(model.Kasutaja.sugu == const.SUGU_N).scalar()
        for value in [sugu_m, sugu_n, row_total]:
            if not max_p and value < 5:
                # kokku-rida, kus on alla 5 osaleja
                ignore_col_s.append(len(row_sn))
            row_sn.append(str(value))
            row_sp.append(proc(value))
        
        # õppekeele järgi
        row_kn = [row_title]
        row_kp = [row_title]
        for value in oppekeeled:
            keel_v = q1.filter(model.Sooritaja.oppekeel == value).scalar()
            if not max_p and keel_v < 5:
                # kokku-rida, kus on alla 5 osaleja
                ignore_col_k.append(len(row_kn))
            row_kn.append(str(keel_v))
            row_kp.append(proc(keel_v))

        data_sn.append([Paragraph(v, N) for v in row_sn])
        data_sp.append([Paragraph(v, N) for v in row_sp])
        data_kn.append([Paragraph(v, N) for v in row_kn])
        data_kp.append([Paragraph(v, N) for v in row_kp])

    # eemaldame veerud, mille Kokku-real on alla 5 osaleja
    if ignore_col_s:
        data_sn = [[p for (i,p) in enumerate(row) if i not in ignore_col_s] for row in data_sn]
        data_sp = [[p for (i,p) in enumerate(row) if i not in ignore_col_s] for row in data_sp]
    if ignore_col_k:
        data_kn = [[p for (i,p) in enumerate(row) if i not in ignore_col_k] for row in data_kn]
        data_kp = [[p for (i,p) in enumerate(row) if i not in ignore_col_k] for row in data_kp]        
        if len(data_kn[0]) < 2:
            # õppekeelte tabeleid ei kuva
            oppekeeled = []
            
    def draw_tbl(title, data):
        # veergude laiused
        data, col_widths, vaba = calc_table_width(data, max_width=275*mm, nice_width=265*mm)
        if vaba > 0:
            cnt = len(col_widths)
            for n in range(cnt):
                col_widths[n] += vaba/cnt

        tbl = Table(data, 
                    colWidths=col_widths,
                    style=TS,
                    hAlign='LEFT',
                    repeatRows=1)
        if title:
            story.append(KeepTogether([Paragraph(title, NH2), tbl]))
        else:
            story.append(Spacer(2*mm, 2*mm))
            story.append(tbl)

    draw_tbl('Absoluutarvudena', data_sn)
    if oppekeeled:
        draw_tbl(None, data_kn)

    draw_tbl('Protsentides', data_sp)
    if oppekeeled:
        draw_tbl(None, data_kp)

def _gen_osa_yldandmed(story, title, osa, qry, is_oppekeel=False, is_sugu=False):
    data = []
    header = ['', 'Valim', 'Keskmine tulemus (%)', 'Min', 'Keskmine', 'Mediaan', 'Max']
    row = [Paragraph(s, NB) for s in header]
    data.append(row)

    if isinstance(osa, model.Testiosa):
        testiosa_id = osa.id
        alatest_id = None
    else:
        testiosa_id = None
        alatest_id = osa.id

    koos_id = list()
        
    def _set_qry_loige(loige_kood):
        if is_oppekeel:
            qry.oppekeel = loige_kood
        elif is_sugu:
            qry.sugu = loige_kood

    def _gen_row(loige_kood, loige_nimi, item):
        total, res_avgpr, res_min, res_avg, res_max = item
        if total < 5 and loige_kood:
            # 5-st väiksema eksaminandide arvuga read koos
            koos_id.append(loige_kood)
            return
        mediaan = qry.query_mediaan(testiosa_id=testiosa_id, alatest_id=alatest_id)
        
        row = [Paragraph(loige_nimi or '', N),
               Paragraph(str(total), N),
               Paragraph(fstr(res_avgpr), N),
               Paragraph(fstr(res_min), N),
               Paragraph(fstr(res_avg), N),
               Paragraph(fstr(mediaan) or '', N),
               Paragraph(fstr(res_max), N),
               ]
        data.append(row)

    if isinstance(osa, model.Testiosa):        
        select_fields = [sa.func.count(model.Sooritus.id),
                         sa.func.avg(model.Sooritus.tulemus_protsent),
                         sa.func.min(model.Sooritus.pallid),
                         sa.func.avg(model.Sooritus.pallid),
                         sa.func.max(model.Sooritus.pallid),
                         ]
    else:
        select_fields = [sa.func.count(model.Alatestisooritus.id),
                         sa.func.avg(model.Alatestisooritus.tulemus_protsent),
                         sa.func.min(model.Alatestisooritus.pallid),
                         sa.func.avg(model.Alatestisooritus.pallid),
                         sa.func.max(model.Alatestisooritus.pallid),
                         ]
        
    if is_oppekeel:
        group_fields = [model.Sooritaja.oppekeel]
        q_all = (qry._gen_query1(group_fields + select_fields,
                                 testiosa_id=testiosa_id,
                                 alatest_id=alatest_id)
                 .group_by(*group_fields)
                 .order_by(group_fields[0])
                 )
    elif is_sugu:
        group_fields = [model.Kasutaja.sugu]
        q_all = (qry._gen_query1(group_fields + select_fields,
                                 testiosa_id=testiosa_id,
                                 alatest_id=alatest_id,
                                 join_kasutaja=True)
                 .group_by(*group_fields)
                 .order_by(group_fields[0])
                 )

    for item in q_all.all():
        loige_kood = item[0]
        if is_oppekeel:
            loige_nimi = get_oppekeel(loige_kood)
        elif is_sugu:
            loige_nimi = get_sugu(loige_kood)
        _set_qry_loige(loige_kood or qry.NULL)
        _gen_row(loige_kood, loige_nimi, item[1:])

    ignored_rows = bool(koos_id)
    
    # kokku-rida
    _set_qry_loige(None)
    q_all = qry._gen_query1(select_fields, testiosa_id=testiosa_id, alatest_id=alatest_id)
    item = q_all.first()
    _gen_row(None, 'Kokku', item)

    # veergude laiused
    data, col_widths, vaba = calc_table_width(data, max_width=275*mm, nice_width=265*mm)
    if vaba > 0:
        d = 40*mm - col_widths[0]
        if d > 0:
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
                repeatRows=1),
          ]
    if ignored_rows:
        li.append(Paragraph('Statistikat ei kuvata, kui otsitavas grupis on vähem kui 5 sooritajat', N))

    story.append(KeepTogether(li))

def _gen_ylesanded(test, qry, y_data, oppekeeled):
    
    def _get_aspektid(ty):
        set_aspektid = set()
        aspektid = []
        for vy in ty.valitudylesanded:
            y = vy.ylesanne
            if y:
                for ha in y.hindamisaspektid:
                    if ha.kuvada_statistikas and ha.aspekt_kood not in set_aspektid and ha.max_pallid:
                        set_aspektid.add(ha.aspekt_kood)
                        aspekt_nimi = 'Aspekt %s' % ha.aspekt_nimi
                        aspektid.append((ha.aspekt_kood, aspekt_nimi, ha.max_pallid))
        return aspektid

    # kui on mitu testiosa, siis kuvame testiosa veeru
    on_testiosa = len(test.testiosad) > 1
    # kui on alatestid, siis kuvame alatesti veeru
    on_alatest = False
    for testiosa in test.testiosad:
        if testiosa.on_alatestid:
            on_alatest = True

            
    header = ['Ülesanne']
        
    if oppekeeled:
        # õppekeelte kaupa
        for value in oppekeeled:
            text = get_oppekeel(value) or value
            header.append(text.capitalize())
    else:
        # keskmine ja soo kaupa
        header.extend(['Keskmine', 'Keskmine protsent', 'Poisid', 'Tüdrukud'])

    if on_alatest:
        header.insert(0, 'Alatest')
    if on_testiosa:
        header.insert(0, 'Testiosa')
    
    row = [Paragraph(s, NB) for s in header]
    data = [row]   
            
    for testiosa in test.testiosad:
        for ty in testiosa.testiylesanded:
            # ylesande pallide rida
            if not ty.max_pallid:
                continue
            row_pref = []
            if on_testiosa:
                row_pref.append(Paragraph(testiosa.nimi, N))
            if on_alatest:
                row_pref.append(Paragraph(ty.alatest and ty.alatest.nimi or '', N))
            row = _gen_ylesanne_ty(test, qry, ty, y_data, oppekeeled)
            data.append(row_pref + row)

            # aspektide kaupa eraldi read
            aspektid = _get_aspektid(ty)
            for a_kood, a_nimi, a_max_pallid in aspektid:
                row = _gen_ylesanne_aspekt(test, qry, ty, y_data, a_kood, a_nimi, a_max_pallid, oppekeeled)
                data.append(row_pref + row)

    # veergude laiused
    data, col_widths, vaba = calc_table_width(data, max_width=275*mm, nice_width=265*mm)
    
    if vaba > 0:
        cnt = len(col_widths)
        for n in range(cnt):
            col_widths[n] += vaba/cnt

    tbl = Table(data, 
                colWidths=col_widths,
                style=TS,
                hAlign='LEFT',
                repeatRows=1)
    return tbl
        
def _gen_ylesanne_aspekt(test, qry, ty, y_data, a_kood, a_nimi, a_max_pallid, oppekeeled):
    def proc(value):
        if value is None:
            return '-'
        else:
            return value * 100. / ty.max_pallid
    def fproc(value):
        return fstr(proc(value))

    q1 = qry._gen_query1([sa.func.avg(model.Vastusaspekt.pallid)],
                         join_kasutaja=True,
                         testiylesanne_id=ty.id,
                         aspekt_kood=a_kood)
    
    row_title = a_nimi
    row = [row_title]
    if oppekeeled:
        # õppekeelte kaupa
        for value in oppekeeled:
            keel_v = q1.filter(model.Sooritaja.oppekeel == value).scalar()
            row.append(fproc(keel_v))
    else:
        # soo kaupa
        avg = q1.scalar()
        sugu_m = q1.filter(model.Kasutaja.sugu == const.SUGU_M).scalar()
        sugu_n = q1.filter(model.Kasutaja.sugu == const.SUGU_N).scalar()
        row.extend([fstr(avg),
                    fproc(avg),
                    fproc(sugu_m),
                    fproc(sugu_n),
                    ])
        if avg is not None:
            y_data.append((row_title, proc(avg))) # diagrammi jaoks
    return [Paragraph(v, N) for v in row]

def _gen_ylesanne_ty(test, qry, ty, y_data, oppekeeled):
    def proc(value):
        if value is None:
            return '-'
        else:
            return value * 100. / ty.max_pallid
    def fproc(value):
        return fstr(proc(value))

    q1 = qry._gen_query1([sa.func.avg(model.Ylesandevastus.pallid)],
                         join_kasutaja=True,
                         testiylesanne_id=ty.id)
    
    row_title = 'ül %s' % (ty.tahis or '')
    row = [row_title]
    if oppekeeled:
        # õppekeelte kaupa
        for value in oppekeeled:
            keel_v = q1.filter(model.Sooritaja.oppekeel == value).scalar()        
            row.append(fproc(keel_v))
    else:
        # soo kaupa
        avg = q1.scalar()
        sugu_m = q1.filter(model.Kasutaja.sugu == const.SUGU_M).scalar()
        sugu_n = q1.filter(model.Kasutaja.sugu == const.SUGU_N).scalar()
        row.extend([fstr(avg),
                    fproc(avg),
                    fproc(sugu_m),
                    fproc(sugu_n),
                    ])
        if avg is not None:
            y_data.append((row_title, proc(avg))) # diagrammi jaoks
    return [Paragraph(v, N) for v in row]

def _gen_diagramm_jaotus(story, test, qry):
    field = model.Sooritaja.pallid
    max_pallid = test.max_pallid
    #field = model.Sooritaja.tulemus_protsent
    #max_pallid = 100
    q = (qry._gen_query1([sa.func.count(field),
                          sa.func.avg(field),
                          sa.func.stddev(field)])
         )
    total, res_avg, res_stddev = q.first()
    buf = 'Valimi maht: %d, keskmine: %s, st.hälve: %s' % (total, fstr(res_avg), fstr(res_stddev))

    q = (qry._gen_query1([sa.func.round(field),
                          sa.func.count(field)])
         .group_by(sa.func.round(field))
         )
    items = {}
    for pallid, cnt in q.all():
        if cnt:
            items[pallid] = cnt
            #items[pallid] = int(cnt*100./total)            

    if items:
        story.append(KeepTogether([
            Paragraph('Tulemuste jaotus', NH1),
            Paragraph(buf, N),
            gen_dgm_jaotus(items, max_pallid)
            ]))

def _gen_diagramm_osa(story, osa, qry):
    if isinstance(osa, model.Testiosa):
        field = model.Sooritus.pallid
        testiosa_id = osa.id
        alatest_id = None
    else:
        field = model.Alatestisooritus.pallid
        testiosa_id = None
        alatest_id = osa.id
    max_pallid = osa.max_pallid

    q = (qry._gen_query1([sa.func.round(field),
                          sa.func.count(field)],
                         testiosa_id=testiosa_id,
                         alatest_id=alatest_id)
         .group_by(sa.func.round(field))
         )
    items = {}
    for pallid, cnt in q.all():
        if cnt:
            items[pallid] = cnt

    if items:
        story.append(KeepTogether([
            Paragraph(osa.nimi, NH1),            
            gen_dgm_jaotus(items, max_pallid)
            ]))

def _gen_diagramm_sugu(story, test, qry):
    max_pallid = test.max_pallid
    field = model.Sooritaja.pallid
    
    q = qry._gen_query1([sa.func.count(field)],
                        join_kasutaja=True)
    total_m = q.filter(model.Kasutaja.sugu == const.SUGU_M).scalar()
    total_n = q.filter(model.Kasutaja.sugu == const.SUGU_N).scalar()    
    if not total_m or not total_n:
        return
    data_m = []
    data_n = []
    # testi pallid jagatakse vahemikeks 20%,50%,75% ja 90% järgi
    steps = sorted(set([round(max_pallid*r/100.) for r in (20, 50, 75, 90)])) +\
            [max_pallid+1]
    x_tickvals = []
    x_ticktext = []
    min_p = 0
    for x, max_p in enumerate(steps):
        q1 = q.filter(field < max_p - 0.5)
        if min_p:
            q1 = q1.filter(field >= min_p)
        row_title = '%d-%dp' % (min_p, max_p-1)
        x_tickvals.append(x)
        x_ticktext.append(row_title)
        
        min_p = max_p
            
        sugu_m = q1.filter(model.Kasutaja.sugu == const.SUGU_M).scalar()
        sugu_n = q1.filter(model.Kasutaja.sugu == const.SUGU_N).scalar()

        data_m.append((x, int(sugu_m * 100. / total_m)))
        data_n.append((x, int(sugu_n * 100. / total_n)))

    img = gen_dgm_sugu(data_m, data_n, x_tickvals, x_ticktext)
    
    story.append(KeepTogether([
        Paragraph('Tulemused sooti', NH1),
        img,
        ]))

def _gen_diagramm_ylesanded(story, y_data):
    x_ticktext = []
    y_values = []
    x_tickvals = []
    for x, (row_title, pallid) in enumerate(y_data):
        x_tickvals.append(x)
        x_ticktext.append(row_title)
        y_values.append(pallid)
    if not y_values:
        return
    img = gen_dgm_ylesanded(x_tickvals, x_ticktext, y_values)

    story.append(KeepTogether([
        Paragraph('Ülesannete keskmised protsentides', NH1),
        img,
        ]))

def get_oppekeel(kood):
    value = const.EHIS_LANG_NIMI.get(kood)
    if value:
        return value.capitalize()

def get_sugu(kood):
    sugu_map = {const.SUGU_M: 'Poisid',
                const.SUGU_N: 'Tüdrukud'}
    return sugu_map.get(kood)

def fstr(value):
    return h.fstr(value, 1) or '-'

def first_page(canvas, doc, pdoc):
    "Esimese lehekülje jalus"
    canvas.saveState()
    fn_img = os.path.join(IMAGES_DIR,  'haridus_ja_noorteamet_logo.png')
    logo = ImageReader(fn_img)

    # landscape
    x_logo = 245*mm
    y_logo = 183*mm
    x_footer = 12*mm

    # portrait
    #x_logo = 135*mm
    #y_logo = 272*mm
    #x_footer = 20*mm
    # fail on 215x78
    canvas.drawImage(logo, x_logo, y_logo, width=108, height=39)        

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
