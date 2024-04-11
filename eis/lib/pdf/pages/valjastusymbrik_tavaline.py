"Väljastusümbrik C4"

from eis.model import const
from .pdfutils import *
from .stylesheet import *

def generate(story, toimumisaeg, rcd, sooritusi, 
             cnt, ymbrikearv,
             cnt_paketis, ymbrikearv_paketis, algus):

    ymbrik, yliik, truum_algus, truum_tahis, ruum_tahis, testipakett, koht = rcd
    test = toimumisaeg.testimiskord.test

    story.append(Spacer(50*mm,50*mm))
    
    if koht.piirkond:
        story.append(Paragraph(koht.piirkond.get_nimi_ylematega(), LC))
    koht_nimi = koht.nimi
    story.append(Paragraph(koht_nimi, LC))

    test_nimi = test.nimi
    kursus_nimi = ymbrik.kursus_nimi
    if kursus_nimi:
        test_nimi += ' (%s)' % kursus_nimi.lower()       
    story.append(Paragraph(test_nimi, LBC))
    story.append(Paragraph(yliik.nimi, LBC))
    if not yliik.keeleylene:
        story.append(Paragraph('Eksamikeel: %s' % testipakett.lang_nimi.lower(), LC))
    if algus:
        buf = 'AVADA %s' % (algus.strftime('%d.%m.%Y'))
        if algus.hour:
            buf += ' KELL %s' % (algus.strftime('%H.%M'))
        story.append(Paragraph(buf, MBC))

    buf = ruum_tahis and 'Ruum %s - ' % ruum_tahis or ''
    buf += '%d %s' % (sooritusi, sooritusi == 1 and 'töö' or 'tööd')
    # ümbriku jrk nr ruumis, sulgudes ümbrike koguarv ruumis
    buf += ', ümbrik %d (%d)' % (cnt, ymbrikearv)
    if ymbrikearv_paketis > ymbrikearv:
        # kui on mitu ruumi, siis kuvame ka testipaketi loenduri
        buf += ' / %d (%d)' % (cnt_paketis, ymbrikearv_paketis)

    story.append(Paragraph(buf, LC))

    story.append(PageBreak())

