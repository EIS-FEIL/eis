"Kirjaliku osa peaümbrik"

from .pdfutils import *
from .stylesheet import *
from . import tagastusymbrikupais_t

def generate(story, toimumisaeg, testikoht, testipakett):
    tagastusymbrikupais_t.header(story, toimumisaeg, testipakett)

    buf = ''
    aadress = testikoht.koht.aadress
    if aadress and aadress.kood1:
        buf = aadress.maakond + '<br/>'
    buf += testikoht.koht.nimi
    testiosa = toimumisaeg.testiosa
    test = testiosa.test

    data = [[Paragraph(test.testiliik_nimi + \
                       '<br/>Eksamikeel: ' + testipakett.lang_nimi.lower(), LB),
             Paragraph(testiosa.nimi, LBC),
             Paragraph(buf, LBR)]]
    story.append(Table(data,
                       colWidths=(90*mm, 105*mm, 90*mm),
                       ))

    story.append(Spacer(100*mm, 14*mm))

    story.append(Paragraph('Ümbrikusse panna kirjaliku eksami läbiviimise protokollid:', L))
    story.append(Paragraph('Märkida "X"', S))
    
    if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
        story.append(Paragraph('_ Protokoll riigieksamitööde paketi avamise ja riigieksami toimumise kohta', L))
        story.append(Paragraph('_ Riigieksamitöö üleandmisprotokoll(id)', L))
    else:
        story.append(Paragraph('_ Protokoll eksamitööde paketi avamise ja toimumise kohta', L))
        story.append(Paragraph('_ Eksamitööde üleandmisprotokoll(id)', L))

    story.append(Spacer(100*mm, 3*mm))
    story.append(Paragraph('Muud materjalid olemasolul:', L))
    story.append(Paragraph('_ Eksamilt kõrvaldatud eksaminandide eksamitööd', L))
    story.append(Paragraph('_ Erakorraliselt eksamit sooritanud (luba Haridus- ja Noorteametilt) eksaminandi eksamitöö koos avaldusega', L))
    story.append(Paragraph('_ Muud dokumendid, mille saatmist eksamikomisjon või välisvaatleja peab vajalikuks', L))

    story.append(PageBreak())
