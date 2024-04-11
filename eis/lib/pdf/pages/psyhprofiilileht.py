"Psühholoogilise testi soorituse profiilileht"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const
import eis.lib.helpers as h

def generate(story, handler, sooritus, header, items):

    sooritaja = sooritus.sooritaja
    test = sooritaja.test
    kasutaja = sooritaja.kasutaja
    aastad, kuud = kasutaja.get_vanus(sooritaja.algus)
    testija = sooritaja.esitaja_kasutaja and sooritaja.esitaja_kasutaja.nimi or ''
    if sooritaja.kool_koht:
        klass = 'Klass: %s%s &nbsp; Kool: %s' % (sooritaja.klass or '',
                                            sooritaja.paralleel or '',
                                            sooritaja.kool_koht.nimi)
    else:
        klass = ''
    data = [[Paragraph(test.nimi, NB),
             Paragraph('Profiilileht', NB)],
            [Paragraph('Nimi: %s' % sooritaja.nimi, N),
             Paragraph('Testimise aeg: %s' % sooritaja.millal, N)],
            [Paragraph(klass, N),
             Paragraph('Sünniaeg: %s' % h.str_from_date(kasutaja.synnikpv), N)],
            [Paragraph('Testija: %s' % testija, N),
             Paragraph('Vanus: %sa %sk' % (aastad, kuud), N)],
            ]
    table = Table(data, colWidths=(100*mm, 60*mm), hAlign='LEFT')
    story.append(table)
    story.append(Spacer(3*mm, 3*mm))

    row = [Paragraph(value, NB) for value in header]
    data = [row]
    grouprows = []
    for n_item, item in enumerate(items):
        if len(item) == 1:
            # alatestide grupi nimetus
            grouprows.append(n_item+1)

        row = [Paragraph(value, N) for value in item]
        data.append(row)

    TS = [('VALIGN', (0,0), (-1,-1), 'TOP'),
          ('GRID', (1,0), (4,-1), 0.5, colors.black),
          ('LINEABOVE', (0,0), (-1,-1), 0.5, colors.black),
          ('LINEBELOW', (0,-1), (-1,-1), 0.5, colors.black),                    
          ]

    group_end = -1
    is_grey = len(grouprows) % 2 # esimesele grupile hall taust
    for group_begin in reversed(grouprows):
        # grupi nimi üle kõigi lahtrite
        TS.append(('SPAN', (0, group_begin), (-1, group_begin)))
        if is_grey:
            # gruppide taust kordamööda helehall
            TS.append(('BACKGROUND', (0, group_begin + 1), (-1, group_end), colors.HexColor(0xE3E3E3)))
        is_grey = not is_grey
        # 50 protsentiil tumehall
        TS.append(('BACKGROUND', (7, group_begin + 1), (7, group_end), colors.HexColor(0xC3C3C3)))                
        group_end = group_begin - 1
    
    data, col_widths, vaba = calc_table_width(data, max_width=180*mm, nice_width=180*mm, min_extra=5*mm)
    # kui jääb vaba ruumi
    if vaba > 0:
        col_widths[0] += vaba

    table = Table(data, colWidths=col_widths, style=TS, repeatRows=1, hAlign='LEFT')
    story.append(table)
    story.append(Spacer(2*mm, 2*mm))
    buf = """*Summaskoor või täpsuse skoor testides Näo leidmine ja AKI leidmine või aeg võrgutestis. Kahe sõnarea meenutamise summaskoor on valitud õiged pluss mittevalitud valed.<br/>
    V - valed vastused, Õ - õiged vastused<br/>
    """
    story.append(Paragraph(buf, N))

def first_page(canvas, doc, pdoc):
    "Esimese lehekülje jalus"
    fn_img = os.path.join(IMAGES_DIR,  'logo_eea_grants.jpg')
    logo = ImageReader(fn_img)
    canvas.drawImage(logo, 175*mm, 275*mm, width=70, height=50)

def later_pages(canvas, doc, pdoc):
    "Teise ja järgmiste lehekülgede jalus"
    return first_page(canvas, doc, pdoc)

