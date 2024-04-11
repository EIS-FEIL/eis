"Põhikooli lõpueksami toimumise protokoll"

from datetime import date
import re
from .pdfutils import *
from .stylesheet import *
import eis.model as model
from eis.model.usersession import _

def generate(story, testikoht, toimumisprotokoll):
    testimiskord = toimumisprotokoll.testimiskord
    if not testimiskord.prot_tulemusega:
        # kui testimiskorra juures pole määratud, et soovitakse uut tyypi protokolli
        return generate_vana(story, testikoht, toimumisprotokoll)

    koht = toimumisprotokoll.koht

    buf = _('Protokoll põhikooli lõpueksami kohta')
    story.append(Paragraph(buf, NC))
    story.append(Paragraph(koht.nimi, NC))
    story.append(Spacer(3*mm, 3*mm))

    testikohad = list(toimumisprotokoll.testikohad)

    pais(story, toimumisprotokoll, testimiskord, testikohad, koht)
    story.append(Spacer(5*mm, 5*mm))
    lvdata = get_labiviijad(toimumisprotokoll, testikohad)
    story.append(labiviijad(lvdata, False))    
    osalejad(story, toimumisprotokoll, testikohad)
    erivajadused(story, toimumisprotokoll, testikohad)    

    story.append(Spacer(3*mm, 3*mm))
    story.append(Paragraph(_('Kooli käskkirja number, eksamikomisjoni liikmete eriarvamused, märkused'), N))
    if toimumisprotokoll.markus:
        story.append(Paragraph(toimumisprotokoll.markus, N))
    else:
        for n in range(3):
            story.append(Paragraph('.'*198, DOT))
    cnt = len(toimumisprotokoll.ruumifailid)
    if cnt:
        story.append(Paragraph(_('Protokollile on lisatud {n} faili.').format(n='<b>%d</b>' % cnt), N))

    story.append(Spacer(3*mm, 5*mm))
    
    story.append(labiviijad(lvdata, True))
    story.append(PageBreak())
    
def get_labiviijad(toimumisprotokoll, testikohad):
    esimehed = set()
    liikmed = set()

    for testikoht in testikohad:
        for lv in testikoht.labiviijad:
            log.info('   lv %s' % lv.id)
            k = lv.kasutaja
            if k:
                if lv.kasutajagrupp_id == const.GRUPP_KOMISJON_ESIMEES:
                    esimehed.add(k.nimi)
                elif lv.kasutajagrupp_id == const.GRUPP_KOMISJON:
                    liikmed.add(k.nimi)

    punktiir = '.' * 80
    if len(esimehed) < 1:
        esimehed.add(punktiir)
    if len(liikmed) < 1:
        liikmed = [punktiir] * 3

    lvdata = [(_('Lõpueksamikomisjoni esimees'), esimehed),
              (_('Lõpueksamikomisjoni liikmed'), liikmed),
              ]
    return lvdata

def labiviijad(lvdata, allkiri):
    data = []
    TS = []
    n = 0
    for title, names in lvdata:
        for name in names:
            if allkiri:
                if name.startswith('...'):
                    s_allkiri = ''
                else:
                    s_allkiri = '.'*50
                data.append((Paragraph(title, DOT), Paragraph(name, DOT), Paragraph(s_allkiri, DOT)))
                data.append(('', Paragraph('(%s)' % _("nimi ja allkiri"), S), ''))
                TS.append(('BOTTOMPADDING', (0, n*2), (-1,n*2), 0))
                TS.append(('TOPPADDING', (0, n*2+1), (-1, n*2+1), 0))
            else:
                data.append((Paragraph(title, DOT), Paragraph(name, DOT)))
                if name.startswith('...'):
                    data.append((Paragraph('', S), Paragraph('', S)))                    
            title = ''
            n += 1

    data, col_widths, vaba, TS = calc_table_width(data, max_width=190*mm, nice_width=180*mm, style=TS)
    if vaba > 0:
        d = min(vaba, 53*mm - col_widths[0])
        col_widths[0] += d
        vaba -= d
        col_widths[1] += vaba
    if allkiri:
        TS.append(('RIGHTPADDING', (1,0),(1,-1), 0))
        TS.append(('LEFTPADDING', (-1,0),(-1,-1), 0))            
            
    #col_widths=(53*mm, 127*mm)
    return Table(data,
                 style=TS,
                 colWidths=col_widths)
    
def osalejad(story, toimumisprotokoll, testikohad):
    story.append(Paragraph(_('Põhikooli lõpueksami tulemused:'), DOT))
    story.append(Spacer(3*mm, 3*mm))

    test = toimumisprotokoll.testimiskord.test
    is_hinne = len(test.testihinded) > 0

    # sooritajate loetelu tabel
    header = [Paragraph(_('Jrk nr'), NC),
              Paragraph(_('Õpilase ees- ja perekonnanimi'), NC),
              Paragraph(_('Punktide arv'), NC),
              Paragraph(_('Tulemus protsentides'), NC),
              ]
    if is_hinne:
        header.append(Paragraph(_('Lõpueksami hinne'), NC))
    header.append(Paragraph(_('Märkused'), NC))

    testiosad = test.testiosad
    mitu_testiosa = len(testiosad)
    if mitu_testiosa > 1:
        header_testiosa = [Paragraph(testiosa.tahis, NC) for testiosa in testiosad]
        header[2:2] = header_testiosa
    
    data = [header]
    nimi_width = 120

    q = (model.SessionR.query(model.Sooritaja,
                             model.Sooritus.tahis)
         .filter(model.Sooritaja.testimiskord_id==toimumisprotokoll.testimiskord_id)
         .join(model.Sooritaja.sooritused)
         .filter(model.Sooritus.testikoht_id==toimumisprotokoll.testikoht_id)
         .filter(model.Sooritaja.staatus>const.S_STAATUS_REGAMATA)
         .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
         )
    nimi_jrk = toimumisprotokoll.testikoht.toimumisaeg.nimi_jrk
    if nimi_jrk:
        q = q.order_by(model.Sooritaja.perenimi, model.Sooritaja.eesnimi)
    else:
        q = q.order_by(model.Sooritus.tahis)        

    n = 0
    table_style = [('GRID', (0,0), (-1,-1), 0.5, colors.black)]
    for sooritaja, tahis in q.all():
        n += 1
        t = Paragraph('XX' + sooritaja.nimi.replace(' ','X'), N)
        nimi_width = max(nimi_width, t.minWidth())
        
        row = [Paragraph('%s.' % n, N),
               Paragraph(sooritaja.nimi, N),
               ]
        taidetud = sooritaja.staatus > const.S_STAATUS_POOLELI
        if taidetud:
            # eeltäidetud
            if mitu_testiosa > 1:
                for testiosa in testiosad:
                    tos = sooritaja.get_sooritus(testiosa_id=testiosa.id)
                    if tos.staatus == const.S_STAATUS_TEHTUD:
                        buf = model.fstr(tos.pallid) or ''
                    else:
                        buf = tos.staatus_nimi
                    row.append(Paragraph(buf, N))
            if sooritaja.staatus == const.S_STAATUS_TEHTUD:
                tulemus = model.fstr(sooritaja.pallid) or ''
                prot = sooritaja.tulemus_protsent
                if prot is not None:
                    prot = str(round(prot)) + '%'
                else:
                    prot = ''
            else:
                tulemus = sooritaja.staatus_nimi
                prot = ''
                # yhendame pallide, protsendi ja hinde lahtri
                table_style.append(('SPAN', (2,n),(is_hinne and 4 or 3, n))) 
            row.append(Paragraph(tulemus, N))
            row.append(Paragraph(prot, N))
            if is_hinne:
                row.append(Paragraph(str(sooritaja.hinne or ''), N))
            row.append(Paragraph(sooritaja.markus or '', N))
        else:
            # käsitsi täitmiseks
            if mitu_testiosa > 1:
                row.extend([Paragraph('', N)] * mitu_testiosa)
            row.extend([Paragraph('', N),
                        Paragraph('', N),
                        Paragraph('', DOT),                   
                        ])
        data.append(row)

    TS = TableStyle(table_style)
    data, col_widths, vaba, TS = calc_table_width(data, max_width=190*mm, nice_width=175*mm, style=TS)
    
    # kui jääb vaba ruumi
    if vaba > 0:
        # märkuste veeru laiuseks 52 mm
        d = min(vaba, 52*mm - col_widths[-1])
        col_widths[-1] += d
        vaba -= d

        # nime veerg nii, et nimed yhel real
        d = min(vaba, nimi_width - col_widths[1])
        col_widths[1] += d
        vaba -= d

        # muu jagamisele
        col_widths[2] += vaba/2
        col_widths[3] += vaba/2        
        
    story.append(Table(data, 
                       colWidths=col_widths,
                       style=TS))

def erivajadused(story, toimumisprotokoll, testikohad):
    test = toimumisprotokoll.testimiskord.test
    testiosad = list(test.testiosad)
    mitu_testiosa = len(testiosad) > 1
    
    for testiosa in testiosad:
        Sooritus2 = model.sa.orm.aliased(model.Sooritus)
        q = (model.SessionR.query(model.Sooritaja, Sooritus2)
             .filter(model.Sooritaja.testimiskord_id==toimumisprotokoll.testimiskord_id)
             .join(model.Sooritaja.sooritused)
             .filter(model.Sooritus.testikoht_id==toimumisprotokoll.testikoht_id)
             .join((Sooritus2, Sooritus2.sooritaja_id==model.Sooritaja.id))
             .filter(Sooritus2.testiosa_id==testiosa.id)
             .filter(Sooritus2.staatus.in_((const.S_STAATUS_TEHTUD,
                                            const.S_STAATUS_KATKESPROT,
                                            const.S_STAATUS_VABASTATUD,
                                            const.S_STAATUS_EEMALDATUD)))
             .filter(model.sa.or_(
                 Sooritus2.erivajadused.any(
                     model.sa.and_(
                         model.Erivajadus.erivajadus_kood==model.Klrida.kood,
                         model.Klrida.klassifikaator_kood=='ERIVAJADUS',
                         model.Klrida.kinnituseta==True,
                         model.Erivajadus.kasutamata==False
                         )
                     ),
                 model.sa.and_(
                         Sooritus2.on_erivajadused_kinnitatud==True,
                         model.sa.or_(
                             Sooritus2.staatus==const.S_STAATUS_VABASTATUD,
                             sa.exists().where(sa.and_(
                                 Sooritus2.id==model.Alatestisooritus.sooritus_id,
                                 model.Alatestisooritus.staatus==const.S_STAATUS_VABASTATUD
                                 )),
                             Sooritus2.erivajadused.any(
                                 model.sa.and_(
                                     model.Erivajadus.kinnitus==True,
                                     model.Erivajadus.kasutamata==False))
                             )
                     )
                 ))
             .order_by(model.Sooritus.tahis)
             )
        if q.count() > 0:
            if mitu_testiosa:
                buf = _('Testiosas "{s}" võimaldatud eritingimused').format(s=testiosa.nimi)
            else:
                buf = _('Eksamitöö tegemisel võimaldatud eritingimused')
            story.append(Paragraph(buf, DOT))
            _erivajadused_testiosas(story, toimumisprotokoll, test, testikohad, q)
            
def _erivajadused_testiosas(story, toimumisprotokoll, test, testikohad, q):
    story.append(Spacer(3*mm, 3*mm))
    
    # sooritajate loetelu tabel
    header = [Paragraph(_('Õpilase ees- ja perekonnanimi'), NC),
              Paragraph(_('Eritingimused'), NC),
              ]
    
    data = [header]
    nimi_width = 120
    
    n = 0
    table_style = [('GRID', (0,0), (-1,-1), 0.5, colors.black)]
    for sooritaja, sooritus in q.all():
        n += 1
        t = Paragraph('XX' + sooritaja.nimi.replace(' ','X'), N)
        nimi_width = max(nimi_width, t.minWidth())

        li = []
        if sooritus.staatus == const.S_STAATUS_VABASTATUD:
            li.append(_('Vabastatud testiosast: {s}').format(s=sooritus.testiosa.nimi))
        else:
            for atos in sooritus.alatestisooritused:
                if atos.staatus == const.S_STAATUS_VABASTATUD:
                    li.append(_('Vabastatud alatestist: {s}').format(s=atos.alatest.nimi))

        for r in sooritus.erivajadused:
            if r.erivajadus_kood:
                if (r.kinnitus or r.taotlus and r.ei_vaja_kinnitust(test)) and not r.kasutamata:
                    li.append(r.erivajadus_nimi)
        
        row = [Paragraph(sooritaja.nimi, N),
               Paragraph('<br/>'.join(li), N),
               ]
        data.append(row)

    TS = TableStyle(table_style)
    data, col_widths, vaba, TS = calc_table_width(data, max_width=190*mm, nice_width=175*mm, style=TS)
    
    # kui jääb vaba ruumi
    if vaba > 0:
        # nime veerg nii, et nimed yhel real
        d = min(vaba, nimi_width - col_widths[0])
        col_widths[0] += d
        col_widths[1] += vaba - d
    story.append(Table(data, 
                       colWidths=col_widths,
                       style=TS))

def pais(story, toimumisprotokoll, testimiskord, testikohad, koht):
    test = testimiskord.test
    kuupaev = toimumisprotokoll.millal or date.today().strftime('%d.%m.%Y')
    tahised = list()
    keeled = list()
    for testikoht in testikohad:
        if testikoht.tahis not in tahised:
            tahised.append(testikoht.tahis)
        q = (model.SessionR.query(model.Sooritaja.lang).distinct()
             .join(model.Sooritaja.sooritused)
             .filter(model.Sooritus.testikoht_id==testikoht.id))
        for lang, in q.all():
            if lang not in keeled:
                keeled.append(lang)

    s_tahised = ', '.join(tahised)
    s_keeled = ', '.join([const.LANG_NIMI.get(lang) for lang in keeled]).capitalize()

    data = [[Paragraph('%s' % kuupaev, N),
             Paragraph('%s' % s_tahised, NR)],
            [Paragraph('(%s)' % _("kuupäev"), S),
             Paragraph('(%s)' % _("kooli kood"), SR)],
            [Paragraph('%s' % (test.nimi), N),
             Paragraph('%s' % koht.nimi, NR)],
            [Paragraph('(%s)' % _("eksam"), S),
             Paragraph('(%s)' % _("kooli nimi"), SR)],
            [Paragraph('%s' % s_keeled, N),
             Paragraph('',N)],
            [Paragraph('(%s)' % _("eksami sooritamise keel"), S),
             Paragraph('',S)],
            ]
    TS = [('ALIGN',(0,0),(0,-1), 'LEFT'),
          ('ALIGN',(1,0),(1,-1), 'RIGHT'),
          ('LEFTPADDING', (0,0),(-1,-1), 0),
          ]        
    for n in range(3):
        TS.append(('BOTTOMPADDING', (0, n*2), (-1,n*2), 0))
        TS.append(('TOPPADDING', (0, n*2+1), (-1, n*2+1), 0))
    
    story.append(Table(data, 
                       colWidths=(83*mm, 83*mm),
                       style=TS,
                       hAlign='LEFT')) 


def generate_vana(story, testikoht, toimumisprotokoll):
    "Vana tüüpi põhikooliprotokoll - ühe toimumisaja ja ühe testikoha kohta"

    toimumisaeg = testikoht.toimumisaeg
    testiosa = toimumisaeg.testiosa
    test = testiosa.test
    koht_nimi = testikoht.koht.nimi

    aine_nimi = test.aine_nimi.lower()
    if re.search(r'[aeiouõäöü]$', aine_nimi):
        # lõpeb täishäälikuga
        aine_nime = aine_nimi
    else:
        # viimane täht enne sulgusid on kaashäälik, mille järgi võib panna e
        aine_nime = re.sub(r'([a-z])( \(|$)', '\\1e\\2', aine_nimi)
    
    story.append(Paragraph(_('PROTOKOLL'), LC))
    story.append(Paragraph(_('{subject} põhikooli lõpueksami kohta').format(subject=aine_nime), LC))
    story.append(Spacer(3*mm, 3*mm))
    story.append(Paragraph(koht_nimi, LC))
    story.append(Spacer(3*mm, 5*mm))

    esimehed = []
    eksamineerijad = []
    liikmed = []

    for lv in testikoht.labiviijad:
        k = lv.kasutaja
        if k:
            if lv.kasutajagrupp_id == const.GRUPP_KOMISJON_ESIMEES:
                esimehed.append(k.nimi)
            elif lv.kasutajagrupp_id == const.GRUPP_KOMISJON:
                liikmed.append(k.nimi)

    punktiir = '.' * 80
    if len(esimehed) < 1:
        esimehed.append(punktiir)
    if len(eksamineerijad) < 1:
        eksamineerijad.append(punktiir)
    while len(liikmed) < 3:
        liikmed.append(punktiir)

    lvdata = [(_('Lõpueksamikomisjoni esimees'), esimehed),
              (_('Eksamineeriv õpetaja lõpueksamil'), eksamineerijad),
              (_('Lõpueksamikomisjoni liikmed'), liikmed),
              ]

    def labiviijad(lvdata, allkiri):
        data = []
        TS = []
        n = 0
        for title, names in lvdata:
            for name in names:
                if allkiri:
                    data.append((Paragraph(title, DOT), Paragraph(name, DOT), Paragraph('.'*50, DOT)))
                    data.append(('', Paragraph('(%s)' % _("nimi ja allkiri"), S), ''))
                else:
                    data.append((Paragraph(title, DOT), Paragraph(name, DOT)))
                    data.append((Paragraph('', S), Paragraph('(%s)' % _("ees- ja perekonnanimi"), S)))                    
                title = ''
                TS.append(('BOTTOMPADDING', (0, n*2), (-1,n*2), 0))
                TS.append(('TOPPADDING', (0, n*2+1), (-1,n*2+1), 0))                
                n += 1

        data, col_widths, vaba, TS = calc_table_width(data, max_width=190*mm, nice_width=180*mm, style=TS)
        if vaba > 0:
            d = min(vaba, 53*mm - col_widths[0])
            col_widths[0] += d
            vaba -= d
            col_widths[-1] += vaba
        if allkiri:
            TS.append(('RIGHTPADDING', (1,0),(1,-1), 0))
            TS.append(('LEFTPADDING', (-1,0),(-1,-1), 0))            
            
        return Table(data,
                     style=TS,
                     colWidths=col_widths)
    
    story.append(labiviijad(lvdata, False))

    story.append(Spacer(3*mm, 3*mm))
    punktiir = '.' * 20
    story.append(Paragraph(_('Põhikooli lõpueksam algas kell {dt1}, lõppes kell {dt2}').format(dt1=punktiir, dt2=punktiir), DOT))
    story.append(Paragraph(_('Põhikooli lõpueksamile tuli {n} õpilast.').format(n=punktiir), DOT))
    story.append(Paragraph(_('Eksamile lubatud õpilastest jäi tulemata (tuua ära nende ees- ja perekonnanimi)'), DOT))
    for n in range(3):
        story.append(Paragraph('.'*200, DOT))
    story.append(Paragraph(_('Põhikooli lõpueksami tulemused:'), DOT))
    
    # sooritajate loetelu tabel
    header = [Paragraph(_('Jrk nr'), NC),
              Paragraph(_('Õpilase ees- ja perekonnanimi'), NC),
              Paragraph(_('Punktide arv'), NC),
              Paragraph(_('Lõpueksami hinne'), NC),
              Paragraph(_('Märkused'), NC),
              ]
    data = [header]
    nimi_width = 120
    n = 0
    for tpr in testipakett.testiprotokollid:
        q = (model.SessionR.query(model.Sooritaja, model.Sooritus.tahis)
             .join(model.Sooritaja.sooritused)
             .filter(model.Sooritus.testiprotokoll_id==tpr.id)
             .filter(model.Sooritaja.staatus>const.S_STAATUS_REGAMATA)
             .filter(model.Sooritus.staatus!=const.S_STAATUS_VABASTATUD)
             )
        nimi_jrk = toimumisaeg.nimi_jrk
        if nimi_jrk:
            q = q.order_by(model.Sooritaja.perenimi, model.Sooritaja.eesnimi)
        else:
            q = q.order_by(model.Sooritus.tahis)        

        for sooritaja, tos in q.all():
            n += 1
            t = Paragraph('XX' + sooritaja.nimi.replace(' ','X'), N)
            nimi_width = max(nimi_width, t.minWidth())
        
            row = [Paragraph('%s.' % n, N),
                   Paragraph(sooritaja.nimi, N),
                   Paragraph('', N),
                   Paragraph('', N),
                   Paragraph('', DOT),                   
                   ]
            data.append(row)

    TS = TableStyle([('GRID',(0,0),(-1,-1), 0.5, colors.black),
                     ])
    data, col_widths, vaba, TS = calc_table_width(data, max_width=190*mm, nice_width=175*mm, style=TS)
    
    # kui jääb vaba ruumi
    if vaba > 0:
        # märkuste veeru laiuseks 52 mm
        d = min(vaba, 52*mm - col_widths[-1])
        col_widths[-1] += d
        vaba -= d

        # nime veerg nii, et nimed yhel real
        d = min(vaba, nimi_width - col_widths[1])
        col_widths[1] += d
        vaba -= d

        # muu jagamisele
        col_widths[2] += vaba/2
        col_widths[3] += vaba/2        
        
    story.append(Table(data, 
                       colWidths=col_widths,
                       style=TS))


    story.append(Paragraph(_('Eksamikomisjoni liikmete eriarvamused'), N))
    for n in range(3):
        story.append(Paragraph('.'*198, DOT))

    cnt = len(toimumisprotokoll.ruumifailid)
    if cnt:
        story.append(Paragraph(_('Protokollile on lisatud {n} faili.').format(n='<b>%d</b>' % cnt), N))

    if testikoht.alates:
        kpv = testikoht.alates.strftime('%d.%m.%Y')
    else:
        kpv = '.' * 20
    story.append(Paragraph(_('Lõpueksami kuupäev {d}').format(d=kpv), DOT))

    story.append(labiviijad(lvdata, True))
    
    story.append(PageBreak())
