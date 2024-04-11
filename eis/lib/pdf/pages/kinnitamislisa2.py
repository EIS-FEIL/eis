# -*- coding: utf-8 -*- 
"TE,SE testitulemuste kinnitamise käskkirja lisa 2"

from eis.lib.pdf.pages.pdfutils import *
from eis.lib.pdf.pages.stylesheet import *
import eis.lib.helpers as h
import eis.model as model

def generate(story, testimiskord, items, staatus_jrk, headers):
    test = testimiskord.test

    if test.testiliik_kood == const.TESTILIIK_TASE:
        buf = 'Lisa 2. %s toimunud eesti keele %s-taseme eksami mittesooritanud isikute nimekiri ja eksamitulemused' % \
              (testimiskord.millal, test.keeletase_nimi)
    elif test.testiliik_kood == const.TESTILIIK_SEADUS:
        buf = 'Lisa 2. %s toimunud Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse tundmise eksami mittesooritanud isikute nimekiri ja eksamitulemused' % (testimiskord.millal)
        
    story.append(Paragraph(buf, N))

    row = [Paragraph('Nr', SB),
           Paragraph('Ees- ja perekonnanimi', SB),
           Paragraph('Isikukood', SB),
           Paragraph('Eksami sooritamise koht', SB),
           ]
    if test.testiliik_kood == const.TESTILIIK_TASE:    
        row.append(Paragraph('Eksamitulemus (% võimalikust punktisummast)', SB))
    else:
        row.append(Paragraph('Eksamitulemus', SB))
        
    for s in headers:
        row.append(Paragraph(s, SB))
    data = [row]
    style = []
    
    for n_row, item in enumerate(items):
        sooritaja_id, eesnimi, perenimi, isikukood, synnikpv, aadress_kood2, aadress_kood1 = item[:7]
        pallid, tulemus_protsent = item[-2:]
        # if pallid is None or tulemus_protsent is None:
        #     # tulemust hetkel ei ole, sest on vaidlustatud
        #     sooritaja = model.Sooritaja.get(sooritaja_id)
        #     vaie = sooritaja.vaie
        #     pallid = vaie.pallid_enne
        #     tulemus_protsent = vaie.tulemus_protsent_enne

        koht_nimi = None
        if aadress_kood2:
            koht_nimi = model.Aadresskomponent.get_str_by_tase_kood(2, aadress_kood2, True)
        elif aadress_kood1:
            koht_nimi = model.Aadresskomponent.get_str_by_tase_kood(1, aadress_kood1, True)
        
        row = [Paragraph(str(n_row+1),S),
               Paragraph('%s %s' % (eesnimi, perenimi), S),
               Paragraph(isikukood or h.str_from_date(synnikpv), S),
               Paragraph(koht_nimi or '', S),
               ]
        if test.testiliik_kood == const.TESTILIIK_TASE:
            row.append(Paragraph(h.fstr(round(tulemus_protsent)), S))
        else:
            row.append(Paragraph(h.fstr(round(pallid)), S))

        #log.debug('%s %s' % (n_row, item))
        
        n = 7
        while n < len(item) - 2:
            r = item[n]
            if n not in staatus_jrk:
                # ei ole oleku veerg
                # st on protokoll või protsent
                if r is None:
                    # tegemata
                    r = ''
                elif isinstance(r, float):
                    # protsent
                    n_vahemik, algus, lopp = test.get_vahemik_by_protsent(r)
                    r = '%s (%s-%s%%)' % (const.VAHEMIK[n_vahemik], algus, lopp)
                else:
                    # protokollinr
                    r = str(r)
                #log.debug('LISAN: %s' % r)
                row.append(Paragraph(r, S))

            elif r != const.S_STAATUS_TEHTUD:
                # oleku väli ja olek "ei ole tehtud" -
                # järgnevate tulemuste väljade asemel tuleb kuvada olek
                ignore = staatus_jrk[n] 
                colspan = (ignore - len([k for k in range(n+1, n+ignore+1) if k in staatus_jrk]))/2+1
                n_cell = len(row)
                style.append(('SPAN', (n_cell,n_row+1),(n_cell+colspan-1,n_row+1)))
                
                n += ignore                
                s = model.usersession.get_opt().S_STAATUS.get(r)
                row.append(Paragraph(s, S))
                #log.debug('LISAN:%s' % s)
                # lisame ignoreeritavad väljad (mis ühendatakse oleku väljaga)
                for i in range(colspan-1):
                    #log.debug('IGNO')
                    row.append(Paragraph('',S))
            n += 1

        data.append(row)

    data, col_widths, vaba, style = calc_table_width(data, max_width=275*mm, style=style)

    # kui jääb vaba ruumi
    if vaba > 0:
        cnt = len(col_widths)
        for n in range(cnt):
            col_widths[n] += vaba/cnt

    # joonistame tabeli
    style += [('GRID', (0,0), (-1,-1), 0.5, colors.black),
              ('VALIGN', (0,0), (-1,-1), 'TOP'),
              ]

    tbl = Table(data,
                colWidths=col_widths,
                style=TableStyle(style),
                hAlign='LEFT',
                repeatRows=1)
    story.append(tbl)

    story.append(Spacer(3*mm,3*mm))

    punktiir = 37 * '_'
    if test.testiliik_kood == const.TESTILIIK_TASE:
        data = [[Paragraph('Keelekeskuse juhataja Kersti Sõstar ' + punktiir, S),
                 Paragraph('Hindamisagentuuri juht Margus Tõnissaar ' + punktiir, S),
                 ]]
    elif test.testiliik_kood == const.TESTILIIK_SEADUS:
        data = [[Paragraph('', S),
                 Paragraph('Hindamisagentuuri juht Margus Tõnissaar ' + punktiir, S),
                 ]]        
    
    tbl = Table(data, colWidths=(sum(col_widths)/2,)*2)
    story.append(tbl)

    story.append(PageBreak())

