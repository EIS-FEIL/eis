"Paketi tagastusümbrik, mis pole seotud protokollirühmaga ja millele kirjutatakse eksamitööde koodid käsitsi"
import math
from .pdfutils import *
from .stylesheet import *
from . import tagastusymbrikupais_t

# märge, et seda ümbrikku ei trükita iga protokollirühma kohta
# ja sellist ümbrikku ei saa süsteemisiseselt hindajatele suunata
# kuna testitööd kirjutatakse ümbriku peale käsitsi
# ja süsteem ei tea, milliste sooritajate testitööd ümbriku sees on
paketiymbrik = True

def generate(story, toimumisaeg, testikoht, testipakett, ymbrikuliik, y_toodearv, n_y, ymbrikearv):
    test = toimumisaeg.testiosa.test
    tagastusymbrikupais_t.header(story, toimumisaeg, testipakett, None, ymbrikuliik)

    # tabelite stiilid
    TB = TableStyle([('BOX',(0,0),(-1,-1), 1,colors.black),                         
                     ])

    TS = TableStyle([('FONTSIZE',(0,0),(-1,-1), 8),
                     ('GRID',(0,0),(-1,-1), 0.5,colors.black),                         
                     ])        

    buf = """
    Ümbrikusse on pandud täidetud eksamitööd, mille koodid on kirjutatud ümbrikule.
    <br/>
    Tühje ja eksamilt kõrvaldatud eksaminandide eksamitöid ümbrikusse mitte panna.
    <br/>
    """
    if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
        buf += """
    Eraldi spetsiaalsesse ümbrikusse panna protokoll riigieksamitööde paketi avamise kohta,
    protokoll riigieksami toimumise kohta ning riigieksamitöö üleandmisprotokoll(id).
    """
    else:
        buf += """
    Eraldi spetsiaalsesse ümbrikusse panna protokoll eksamitööde paketi avamise kohta,
    protokoll eksami toimumise kohta ning eksamitöö üleandmisprotokoll(id).
    """

    buf += """
    <br/>
    Ümbrikusse on pandud ......... eksamitööd.
    <br/>
    Ümbrik on komplekteeritud nõuetekohaselt.
    <br/>
    <br/>
    <b>
    Nimi: ............................................................
    <br/>
    <br/>
    Allkiri: .........................................................
    </b>
    """

    if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
        taitja = 'Täidab välisvaatleja'
    else:
        taitja = 'Täidab eksamikomisjoni esimees'
        
    vaatleja = Table([[Paragraph(taitja, NBC)],
                      [Paragraph(buf, N)]],
                     style=TB, colWidths=(89*mm))

    data = [['Jrk', 'SISESTAJA'],
            ['1.', ''],
            ['2.', '']]

    sisestaja = Table([[Paragraph('Täidetakse Haridus- ja Noorteametis', NBC)],
                       [Table(tp([['HINDAJA KOOD', '', '']], NBC),
                              style=TS,
                              colWidths=(48*mm, 19*mm, 19*mm))],
                       [Table(tp(data,N), 
                              style=TS, 
                              colWidths=(19*mm,67*mm))]],
                      colWidths=(89*mm), style=TB)


    # parempoolne osa
    TS = [('FONTSIZE',(0,0),(-1,-1), 8),
          ('VALIGN', (0,0), (-1,-1), 'TOP'),
          ]        
    data = []
    maht = ymbrikuliik.maht or 20
    veergudearv = 5
    ridadearv = min(y_toodearv, math.ceil(maht / veergudearv))
    veerud = []
    for n in range(veergudearv):
        veerg = [n * ridadearv + 1 + i for i in range(ridadearv)]
        veerud.append(veerg)
    for n in range(ridadearv):
        row = []
        max_x = veergudearv
        for m in range(veergudearv):
            jrk = veerud[m][n]
            if jrk <= y_toodearv:
                row.append(Paragraph('%d.' % jrk, NL))
            else:
                max_x = min(m, max_x)
                row.append(Paragraph('', NL))
        data.append(row)
        TS.append(('GRID', (0, n), (max_x - 1, n), .5, colors.black))

    sooritused = [Paragraph('Ümbrikus on järgmiste koodidega eksamitööd:', N),
                  Table(data,
                        style=TableStyle(TS),
                        colWidths=(37*mm, 37*mm, 37*mm, 37*mm, 37*mm),
                        rowHeights=(9.81*mm,)*len(data)),
                  Paragraph('NB! ÜHTE ÜMBRIKUSSE TOHIB PANNA KUNI %d EKSAMITÖÖD.' % maht, M),
                  Paragraph('ENNE SAMA VARIANDI ÜMBRIKU TÄITMIST PALUN VEENDU, ET EELMISES ON %d EKSAMITÖÖD!' % maht, M), 
                  Paragraph('PALUME TAGASI SAATA KA TÜHJAD TRIIPKOODIDEGA ÜMBRIKUD.', M)
                  ]

    jrknr = Paragraph('%d (%d)' % (n_y, ymbrikearv), M)
  
    # terve tabel
    data = [[[jrknr, vaatleja, sisestaja], '', sooritused]]
    t = Table(data, 
              colWidths=(90*mm,8*mm, 185*mm),
              style=TableStyle([('VALIGN', (0,0),(0,0), 'TOP'),
                                ('VALIGN', (1,0),(1,0), 'BOTTOM'),
                                ('VALIGN', (-1,0),(-1,0), 'TOP'),
                                ('ALIGN', (-1,-1),(-1,-1), 'LEFT'),
                                ('TOPPADDING', (0,0), (-1,-1), 0),
                                ('LEFTPADDING', (0,0), (-1,-1), 3),
                                ('RIGHTPADDING', (0,0), (-1,-1), 3),
                                ]))

    story.append(t)

    story.append(PageBreak())

