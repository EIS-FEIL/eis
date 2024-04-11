"VARIANT. Tagastusümbrik töödele, mis on kirjutatud ümbrikuliigile vastavas variandis"

from .pdfutils import *
from .stylesheet import *
from . import tagastusymbrikupais_t

def generate(story, toimumisaeg, testikoht, testipakett, tpr, ymbrikuliik):
    test = toimumisaeg.testiosa.test
    tagastusymbrikupais_t.header(story, toimumisaeg, testipakett, tpr, ymbrikuliik)

    # tabelite stiilid
    TB = TableStyle([('BOX',(0,0),(-1,-1), 1,colors.black),                         
                     ])

    TS = TableStyle([('FONTSIZE',(0,0),(-1,-1), 8),
                     ('GRID',(0,0),(-1,-1), 0.5,colors.black),                         
                     ])        

    # vasak osa

    buf = """
    Ümbrikusse panna ainult täidetud eksamitööd, mis on kirjutatud ümbrikul märgitud variandis ning
    mille koodid on antud ümbriku paremas servas.
    Eksamitööde olemasolu ümbrikus märkida ära plussi ja miinusega.
    <br/>
    Tühje ja eksamilt kõrvaldatud eksaminandide eksamitöid ümbrikusse mitte panna.
    <br/>
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

    if toimumisaeg.vaatleja_maaraja:
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
    sooritused = tagastusymbrikupais_t.sooritused(tpr.sooritused)

    # terve tabel
    tagastusymbrikupais_t.body(story, [vaatleja, sisestaja], '', sooritused)
    story.append(PageBreak())

