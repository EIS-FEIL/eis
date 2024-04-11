"Vastuste statistika (tehtud eeltestide statistika jäädvustamiseks)"

from datetime import date
from eis.lib.pdf.pages.pdfutils import *
from eis.lib.pdf.pages.stylesheet import *
import eis.lib.helpers as h
import eis.model as model

def generate(story, args):
    test, testiosa, testimiskord, q, prepare_items_y, prepare_items_k, is_y_perm, opt = args
    eraldi = testimiskord and testimiskord.analyys_eraldi
    buf = 'Testi %s vastuste statistika' % test.id
    story.append(Paragraph(buf, H1))
    
    if testimiskord and testiosa:
        toimumisaeg = testimiskord.get_toimumisaeg(testiosa)
        toimumisajad = {testiosa.id: toimumisaeg}
    elif testimiskord:
        toimumisaeg = None
        toimumisajad = {ta.testiosa_id: ta for ta in testimiskord.toimumisajad}
    else:
        toimumisaeg = None
        toimumisajad = {}
        
    if eraldi and toimumisaeg:
        buf = 'Toimumisaeg %s' % toimumisaeg.tahised
    elif eraldi:
        buf = 'Testimiskord %s' % testimiskord.tahis
    elif testimiskord:
        buf = 'Testimiskorraga sooritused'
    else:
        buf = 'Testimiskorrata sooritused'
    story.append(Paragraph(buf, NBC))
    story.append(Paragraph(test.nimi, NC))
    if testiosa and len(test.testiosad) > 1:
        story.append(Paragraph(testiosa.nimi, NC))
    #story.append(Paragraph(u'Seisuga %s' % h.str_from_date(date.today()), N))
    
    # kõigi komplektide andmed
    komplektid = []
    if toimumisaeg:
        ta_komplektid = list(toimumisaeg.komplektid) or []
    elif testimiskord:
        ta_komplektid = []
        for ta in toimumisajad.values():
            ta_komplektid += list(ta.komplektid) or []

    if testiosa:
        testiosad = [testiosa]
    else:
        testiosad = list(test.testiosad)
    for testiosa in testiosad:
        for kv in testiosa.komplektivalikud:
            for k in kv.komplektid:
                if not testimiskord or k in ta_komplektid:
                    komplektid.append(k)
    for k in komplektid:
        q1 = q.filter(model.Valitudylesanne.komplekt_id==k.id)
        story.append(Spacer(5*mm, 5*mm))
    
        header, items = prepare_items_y(q1, True)
        story.append(KeepTogether([Paragraph('Komplekti %s ülesanded' % k.tahis, H1),
                                   _gen_table(header, items, True)]))

    for rcd in q.all():
        ylesanne, vy, ty, yst = rcd
        if not is_y_perm(ylesanne):
            continue
        komplektis = yst and yst.valitudylesanne_id is not None
        if testimiskord:
            toimumisaeg = toimumisajad.get(ty.testiosa_id)
        else:
            toimumisaeg = None
        r = _gen_yl(testiosa, toimumisaeg, ylesanne, vy, ty, yst, opt, eraldi, komplektis)
        story.append(r)
                                   
    story.append(PageBreak())
        
def _gen_table(header, items, on_y):
    # koostame tabeli päised
    headerrow = [Paragraph(isinstance(s, tuple) and s[1] or s, SI) for s in header]
    data = [headerrow]

    textrows = []
    rowind = 0
    # koostame tabeli sisu
    for item in items:
        row = []
        for s in item:
            if s is None:
                s = ''
            elif isinstance(s, list):
                s = '<br/>'.join(s)
            else:
                s = str(s)
            row.append(Paragraph(s, S))
        rowind += 1
        data.append(row)

    data, col_widths, vaba = calc_table_width(data, max_width=190*mm, nice_width=180*mm)

    # kui jääb vaba ruumi
    if vaba > 0 and on_y:
        col_widths[-1] += vaba

    # joonistame tabeli
    ts = [('GRID', (0,0), (-1,-1), 0.5, colors.black),
          ('VALIGN', (0,0), (-1,-1), 'TOP'),
          ('LEFTPADDING', (0,0), (-1,-1), 2),
          ('RIGHTPADDING', (0,0), (-1,-1), 2),
          ]
    for rowind in textrows:
        ts.append(('SPAN', (1, rowind), (-1, rowind)))

    tbl = Table(data,
                colWidths=col_widths,
                style=TableStyle(ts),
                hAlign='LEFT',
                repeatRows=1)
    return tbl

def _gen_yl(testiosa, toimumisaeg, ylesanne, vy, ty, yst, opt, eraldi, komplektis):
    story = []
    story.append(Paragraph(ylesanne.nimi, H1))
    story.append(Paragraph('Ülesande ID %d' % ylesanne.id, NBC))
    for block in ylesanne.sisuplokid:
        for kysimus in block.kysimused:
            if kysimus.tulemus_id:
                story.append(Spacer(3*mm, 3*mm))
                r = _gen_ky(testiosa, toimumisaeg, kysimus, yst, opt, eraldi, komplektis)
                story.append(r)
    return KeepTogether(story)

def _gen_ky(testiosa, toimumisaeg, kysimus, yst, opt, analyys_eraldi, komplektis):
    vy_id = komplektis and yst and yst.valitudylesanne_id or None
    if analyys_eraldi:
        kst = toimumisaeg.get_kysimusestatistika(kysimus.id, vy_id)
    elif toimumisaeg:
        kst = testiosa.get_kysimusestatistika(kysimus.id, vy_id, True)
    else:
        kst = testiosa.get_kysimusestatistika(kysimus.id, vy_id, False)

    story = []
    story.append(Paragraph('Küsimus %s' % kysimus.kood, NB))
    if kysimus.selgitus:
        story.append(Table([[Paragraph(kysimus.selgitus, SB)]], colWidths=(180*mm,), hAlign='LEFT'))
    if not kst:
        story.append(Paragraph('Statistikat pole arvutatud', S))
    else:
        s_arv = str(kst.vastajate_arv)
        if kst.test_hinnatud_arv and kst.test_hinnatud_arv != kst.vastajate_arv:
            s_arv += ' (test hinnatud %d sooritajal)' % kst.test_hinnatud_arv
        data = [[Paragraph('Sooritajate arv', S),
                 Paragraph(s_arv, S)],
                [Paragraph('Vastuste arv', S),
                 Paragraph(str(kst.vastuste_arv), S)],
                [Paragraph('Keskmine lahendusprotsent', S),
                 Paragraph('%s%%' % h.fstr(kst.klahendusprotsent or 0), S)],
                [Paragraph('Rit', S),
                 Paragraph(h.fstr(kst.rit, 2) or '', S)],
                [Paragraph('Rir', S),
                 Paragraph(h.fstr(kst.rir, 2) or '', S)],
                [Paragraph('Soorituste arv', S),
                 Paragraph(str(kst.vastajate_arv or ''), S)],
                ]
        data, col_widths, vaba = calc_table_width(data, max_width=190*mm, nice_width=180*mm)
        if vaba > 0:
            lisa1 = min(vaba, 36*mm - col_widths[0])
            if lisa1 > 0:
                vaba -= lisa1
                col_widths[0] += lisa1
            col_widths[1] += vaba

        ts = []
        tbl = Table(data,
                    colWidths=col_widths,
                    style=TableStyle(ts),
                    hAlign='LEFT')
        story.append(tbl)

        r = _kysimus_stat_resp(kysimus, kst, opt)
        if r:
            story.append(r)

        story.append(Spacer(3*mm, 3*mm))
        r = _kysimus_stat_point(kysimus, kst, opt)
        if r:
            story.append(r)            
        
    return KeepTogether(story)

def _kysimus_stat_resp(kysimus, kst, opt):
    tulemus = kysimus.tulemus 
    sp_tyyp = kysimus.sisuplokk.tyyp
    basetype = tulemus and tulemus.baastyyp or None
    if sp_tyyp == const.INTER_DRAW:
        # vastuseid ei kuvata
        return 

    #order = request.params.get('kvst_order')
    #kvst_order = 'kvstatistika.oige desc,Kvstatistika.vastuste_arv desc,kvstatistika.kood1,kvstatistika.kood2,kvstatistika.sisu'              
    kvst_order = 'kvstatistika.vastuste_arv desc,kvstatistika.kood1,kvstatistika.kood2,kvstatistika.sisu'
    kvstatistikad = (model.SessionR.query(model.Kvstatistika)
                     .filter_by(kysimusestatistika_id=kst.id)
                     .order_by(model.sa.text(kvst_order)).all())
    if not len(kvstatistikad):
        return Paragraph('Küsimuse statistika pole arvutatud', S)
    else:
        header = ["Jrk"]
        if basetype in (const.BASETYPE_PAIR, const.BASETYPE_DIRECTEDPAIR):
            header.append("Kood 1")
            header.append("Kood 2")
        elif sp_tyyp == const.INTER_GAP and kysimus.seq == 0:
            header.append("Vastus")
            header.append("Positsioon")
        else:
            header.append("Vastus")
        header.append("Selgitus")
        header.append("Esinemiste arv")
        header.append("Sagedus")
        header.append("Õige")
        data = [[Paragraph(s, SI) for s in header]]

        ts = [('GRID', (0,0), (-1,-1), 0.5, colors.black),
              ('VALIGN', (0,0), (-1,-1), 'TOP'),
              ('LEFTPADDING', (0,0), (-1,-1), 2),
              ('RIGHTPADDING', (0,0), (-1,-1), 2),
              ]
        di_vv = {}
        for n_rcd, rcd in enumerate(kvstatistikad):
            if rcd.oige == const.C_OIGE:
                color = '#DBFFE6'
            elif rcd.oige == const.C_VALE:
                color = '#f0f0f0'
            else:
                color = '#ffffff'
            ts.append(('BACKGROUND', (0, n_rcd+1), (-1, n_rcd+1), color))
                
            row = [Paragraph(str(n_rcd+1), S)]
            if rcd.tyyp == const.RTYPE_CORRECT:
                row.append(Paragraph('Vastuseid pole sisestatud', SI))
            else:
                rtf = False
                if basetype == const.BASETYPE_MATH:
                    sisu = rcd.sisu or ''
                else:
                    sisu = rcd.kood1 or rcd.sisu or ''
                    rtf = kysimus.rtf
                if not rtf:
                    sisu = sisu.replace('<', '&lt;').replace('>','&gt;')
                try:
                    S.wordWrap = 'CJK'
                    p = Paragraph(sisu, S)
                except Exception as ex:
                    # vigane rtf, pilt pole kättesaadav vms
                    p = Paragraph('Vastus, mida ei saa kuvada', SI)
                if len(sisu) > 90:
                    # anname ette lubatud laiuse
                    p = Table([[p]], colWidths=(90*mm,), hAlign='LEFT')
                row.append(p)

            if basetype in (const.BASETYPE_PAIR, const.BASETYPE_DIRECTEDPAIR):
                if rcd.tyyp == const.RTYPE_CORRECT:
                    row.append(Paragraph('Vastuseid pole sisestatud', SI))
                else:
                    sisu = rcd.kood2 or ''
                    row.append(Paragraph(sisu, S))
            elif sp_tyyp == const.INTER_GAP and kysimus.seq == 0:
                if rcd.tyyp == const.RTYPE_CORRECT:
                    row.append(Paragraph('Vastuseid pole sisestatud', SI))
                else:
                    sisu = rcd.sisu or ''
                    row.append(Paragraph(sisu, S))                

            # vastuse selgitus
            vv = di_vv.get(rcd.maatriks)
            if not vv:
                vv = di_vv[rcd.maatriks] = model.Valikvastus.get_by_tulemus(kysimus.tulemus_id, rcd.maatriks)
            selgitus = vv and vv.get_selgitus(rcd) or None
            row.append(Paragraph(selgitus or '', S))

            row.append(Paragraph(str(rcd.vastuste_arv) or '', S))
            if kst.vastajate_arv:
                pro = rcd.vastuste_arv * 100. / kst.vastajate_arv
                row.append(Paragraph('%s%%' % h.fstr(pro), S))
            else:
                row.append(Paragraph('', S))

            row.append(Paragraph(opt.C_CORRECT.get(rcd.oige) or '', S))
            data.append(row)

        data, col_widths, vaba = calc_table_width(data, max_width=190*mm, nice_width=180*mm)
        if vaba > 0:
            if len(col_widths) > 2:
                col_widths[1] += vaba/2
                col_widths[2] += vaba/2
            else:
                col_widths[0] += vaba
        tbl = Table(data,
                    colWidths=col_widths,
                    style=TableStyle(ts),
                    hAlign='LEFT')
        return tbl

def _kysimus_stat_point(kysimus, kst, opt):
    tulemus = kysimus.tulemus 
    khstatistikad = list(kst.khstatistikad)
    if not len(khstatistikad):
        return Paragraph('Saadud tulemuste statistika puudub', S)
    else:
        header = ["Jrk",
                  "Toorpunktid",
                  "Pallid",
                  "Null punkti põhjus",
                  "Esinemiste arv",
                  "Sagedus"]
        data = [[Paragraph(s, SI) for s in header]]

        ts = [('GRID', (0,0), (-1,-1), 0.5, colors.black),
              ('VALIGN', (0,0), (-1,-1), 'TOP'),
              ('LEFTPADDING', (0,0), (-1,-1), 2),
              ('RIGHTPADDING', (0,0), (-1,-1), 2),
              ]
        for n_rcd, rcd in enumerate(khstatistikad):
            if rcd.pallid:
                color = '#DBFFE6'
            elif rcd.nullipohj_kood:
                color = '#FFFFFF'
            else:
                color = '#f0f0f0'
            ts.append(('BACKGROUND', (0, n_rcd+1), (-1, n_rcd+1), color))

            if kst.vastajate_arv:
                pro = rcd.vastuste_arv * 100. / kst.vastajate_arv
                pro = '%s%%' % (h.fstr(pro))
            else:
                pro = ''
            row = [Paragraph(str(n_rcd+1), S),
                   Paragraph(h.fstr(rcd.toorpunktid) or '', S),
                   Paragraph(h.fstr(rcd.pallid) or '', S),
                   Paragraph(rcd.nullipohj_nimi or '', S),
                   Paragraph(str(rcd.vastuste_arv), S),
                   Paragraph(str(pro), S),
                   ]
            data.append(row)

        data, col_widths, vaba = calc_table_width(data, max_width=190*mm, nice_width=180*mm)
        # if vaba > 0:
        #   col_widths[1] += vaba
        tbl = Table(data,
                    colWidths=col_widths,
                    style=TableStyle(ts),
                    hAlign='LEFT')
        return tbl

        
def first_page(canvas, doc, pdoc):
    "Esimese lehekülje jalus"
    canvas.saveState()
    canvas.setFont('Times-Roman', 10)

    canvas.drawString(12*mm, 286*mm, doc.title)
    canvas.drawString(180*mm, 286*mm, h.str_from_date(date.today()))
    canvas.line(12*mm, 285*mm, 197*mm, 285*mm)
    canvas.restoreState()

def later_pages(canvas, doc, pdoc):
    "Teise ja järgmiste lehekülgede jalus"
    return first_page(canvas, doc, pdoc)
