"STANDARD2. Tagastusümbrik alatestile, kus hindajad märgivad punktid otse tööle või töö on masinhinnatav"

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

    buf = """
    Ümbrikusse panna ainult täidetud eksamitööd, mille koodid on antud ümbriku paremas servas.
    <br/>
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

    # keskmine osa (ES-1444)
    tbl_kesk = tbl_hindamiskogumid(tpr, ymbrikuliik)
    
    # parempoolne osa
    sooritused = tagastusymbrikupais_t.sooritused(tpr.sooritused)

    # terve tabel
    tagastusymbrikupais_t.body(story, [vaatleja, sisestaja], tbl_kesk, sooritused)
    story.append(PageBreak())

def tbl_hindamiskogumid(tpr, ymbrikuliik):
    # tabel, kus iga hindamiskogumi kohta on rida:
    # hindamiskogumi ülesanded; hindaja 1; hindaja 2
    TS = TableStyle([('FONTSIZE',(0,0),(-1,-1), 8),
                     ('GRID',(0,0),(-1,-1), 0.5,colors.black),                         
                     ])        

    kursus = tpr.kursus_kood
    hindamiskogumid = [hk for hk in ymbrikuliik.hindamiskogumid if hk.kursus_kood == kursus]
    if hindamiskogumid:
        # järjestame hindamiskogumid ylesannete järjekorras
        # ja leiame iga hindamiskogumi ylesannete loetelu
        hk_list = []
        for hk in hindamiskogumid:
            key = (0, 0)
            tahised = []
            for ind, ty in enumerate(hk.testiylesanded):
                if ind == 0:
                    key = (ty.alatest_seq, ty.seq)
                tahis = ty.nimi or ty.tahis
                if tahis:
                    tahised.append(tahis)
            hk_list.append((key, tahised))
        sorted_hk_list = sorted(hk_list, key=lambda r: r[0])

        # teeme tabeli, kus iga hindamiskogumi kohta eraldi rida
        yl_rows = [[Paragraph('Ül', N),
                    Paragraph('Hindaja 1', N),
                    Paragraph('Hindaja 2', N)]]
        for key, tahised in sorted_hk_list:
            value = tahised and ', '.join(tahised) or ''
            row = [Paragraph(value, N),
                   Paragraph('', N),
                   Paragraph('', N)]
            yl_rows.append(row)
        yltbl = Table(yl_rows, style=TS, colWidths=(25*mm, 37*mm, 37*mm))
        tbl_kesk = Table([[Paragraph('Täidab hindaja', NBC)],
                          [yltbl]])
    else:
        tbl_kesk = Paragraph('', NBC)
    return tbl_kesk
