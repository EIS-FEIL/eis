# -*- coding: utf-8 -*- 
"ERI1. Tagastusümbrik alatestile, mille iga ülesande kohta märgitakse hindaja"

from .pdfutils import *
from .stylesheet import *
from . import tagastusymbrikupais_t

def generate(story, toimumisaeg, testikoht, testipakett, tpr, ymbrikuliik):
    # hindajate tabelis peaks olema ümbrikuliigile vastava alatesti 
    # iga ülesande kohta üks rida, aga kuna ümbrikuliigid ja alatestid
    # ei ole süsteemis seotud, siis ei saa täpset arvu kasutada
    hindajad_len = min(9, len(toimumisaeg.testiosa.testiylesanded))
    generate_eri(story, toimumisaeg, testikoht, testipakett, tpr, ymbrikuliik, hindajad_len)

def generate_eri(story, toimumisaeg, testikoht, testipakett, tpr, ymbrikuliik, hindajad_len):
    test = toimumisaeg.testiosa.test
    tagastusymbrikupais_t.header(story, toimumisaeg, testipakett, tpr, ymbrikuliik)

    # tabelite stiilid
    TB = TableStyle([('BOX',(0,0),(-1,-1), 1,colors.black),                         
                     ])

    TS = TableStyle([('FONTSIZE',(0,0),(-1,-1), 8),
                     ('GRID',(0,0),(-1,-1), 0.5,colors.black),
                     ])        

    # vasak ylemine osa
    buf = """
    Ümbrikusse panna ainult täidetud eksamitööd, mille koodid on antud ümbriku paremas servas.
    <br/>
    Eksamitööde olemasolu ümbrikus märkida ära plussi ja miinusega.
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
        taitja = 'Täidetakse eksamil välisvaatleja poolt'
    else:
        taitja = 'Täidetakse eksamikomisjoni esimehe poolt'

    vaatleja = Table([[Paragraph(taitja, NBC)],
                      [Paragraph(buf, S)]],
                     style=TB, colWidths=(89*mm))

    # vasak alumine osa
    data = [['Jrk', 'SISESTAJA'],
            ['1.', ''],
            ['2.', '']]

    sisestaja = Table([[Paragraph('Täidetakse Haridus- ja Noorteametis', NBC)],
                       [Table(tp(data,S), style=TS, colWidths=(19*mm,67*mm))]],
                      colWidths=(89*mm), style=TB)


    # keskmine osa

    data = [['Nr', 'Hindaja kood', 'Hindaja', 'Allkiri', 'Kuupäev']]
    for n in range(1,hindajad_len+1):
        data.append(['%d' % n, '', '', '', ''])

    hindaja = [Paragraph('Täidetakse Haridus- ja Noorteametis', NBC),
               Table(tp(data,N), 
                     style=TS, 
                     colWidths=(9*mm,16*mm,36*mm,20*mm,20*mm))]


    # parempoolne osa
    sooritused = tagastusymbrikupais_t.sooritused(tpr.sooritused)

    # terve tabel
    tagastusymbrikupais_t.body(story, [vaatleja, sisestaja], hindaja, sooritused)

    story.append(PageBreak())

