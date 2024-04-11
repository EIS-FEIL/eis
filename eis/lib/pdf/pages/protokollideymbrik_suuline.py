"Suulise osa peaümbrik"

from .pdfutils import *
from .stylesheet import *
from . import tagastusymbrikupais_t

def generate(story, toimumisaeg, testikoht, testipakett):
    tagastusymbrikupais_t.header(story, toimumisaeg, testipakett)

    # kahe joone vaheline osa
    testiosa = toimumisaeg.testiosa
    if testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_KP):
        vastvorm_nimi = 'Kirjalik osa'
    else:
        vastvorm_nimi = 'Suuline osa'

    data = [[Paragraph('Eksamikeel: ' + testipakett.lang_nimi.lower(), LB),
             Paragraph(vastvorm_nimi, LBC),
             Paragraph(testiosa.nimi, LBR)]]        

    story.append(Table(data,
                       colWidths=(90*mm,105*mm,90*mm),
                       style=TableStyle([('LINEBELOW', (0,0),(-1,-1), 1,colors.black),
                                        ])
                       ))


    # piirkonna nimi
    if testikoht.koht.piirkond:
        story.append(Paragraph(testikoht.koht.piirkond.nimi, LR))

    # kooli nimi
    story.append(Paragraph(testikoht.koht.nimi, LR))
    story.append(Spacer(100*mm, 14*mm))

    story.append(Paragraph('Ümbrikusse panna suulise eksami läbiviimise ja hindamise protokollid:', L))
    story.append(Paragraph('Märkida "X"', S))

    if testiosa.test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
        story.append(Paragraph('_ Protokoll riigieksamitööde paketi avamise ja riigieksami toimumise kohta', L))
        story.append(Paragraph('_ Riigieksamitöö üleandmisprotokoll(id)', L))
        story.append(Paragraph('_ Hindamisprotokoll(id)', L))
        
        story.append(Spacer(100*mm, 3*mm))
        story.append(Paragraph('Muud materjalid olemasolul:', L))
        story.append(Paragraph('_ Hindaja/intervjueerija töövõtulepingud', L))
        story.append(Paragraph('_ Muud dokumendid, mille saatmist eksamikomisjon või välisvaatleja peab vajalikuks', L))

    else:
        story.append(Paragraph('_ Protokoll eksamitööde paketi avamise ja toimumise kohta', L))
        story.append(Paragraph('_ Eksamitööde üleandmisprotokoll(id)', L))
        story.append(Paragraph('_ Hindamisprotokoll(id)', L))
        
        story.append(Spacer(100*mm, 3*mm))
        story.append(Paragraph('Muud materjalid olemasolul:', L))
        story.append(Paragraph('_ Hindaja/intervjueerija töövõtulepingud', L))
        story.append(Paragraph('_ Muud dokumendid, mille saatmist eksamikomisjon peab vajalikuks', L))

    story.append(Spacer(100*mm, 25*mm))
    story.append(Paragraph('Eksamimaterjalid saata tagasi turvakotis.', L))


    story.append(PageBreak())
