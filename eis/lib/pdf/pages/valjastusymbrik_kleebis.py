"Väljastusümbriku kleebis"

from eis.model import const
from .pdfutils import *
from .stylesheet import *

def generate(story, toimumisaeg, rcd, sooritusi, 
             cnt, ymbrikearv,
             cnt_paketis, ymbrikearv_paketis, algus):

    ymbrik, yliik, truum_algus, truum_tahis, ruum_tahis, testipakett, koht = rcd
    test = toimumisaeg.testimiskord.test

    if koht.piirkond:
        story.append(Paragraph(koht.piirkond.get_nimi_ylematega(), MC))
    koht_nimi = koht.nimi
    story.append(Paragraph(koht_nimi, MC))
    test_nimi = test.nimi
    kursus_nimi = ymbrik.kursus_nimi
    if kursus_nimi:
        test_nimi += ' (%s)' % kursus_nimi.lower()   
    story.append(Paragraph(test_nimi, MBC))
    story.append(Paragraph(yliik.nimi, MBC))
    if not yliik.keeleylene:
        story.append(Paragraph('Eksamikeel: %s' % testipakett.lang_nimi.lower(), MC))
    if algus:
        buf = 'AVADA %s' % (algus.strftime('%d.%m.%Y'))
        if algus.hour:
            buf += ' KELL %s' % (algus.strftime('%H.%M'))
        story.append(Paragraph(buf, MBC))

    buf = ruum_tahis and 'Ruum %s - ' % ruum_tahis or ''
    buf += '%d %s' % (sooritusi, sooritusi == 1 and 'töö' or 'tööd')
    buf += ', ümbrik %d (%d)' % (cnt, ymbrikearv)
    if ymbrikearv_paketis > ymbrikearv:
        # kui on mitu ruumi, siis kuvame ka testipaketi loenduri
        buf += ' / %d (%d)' % (cnt_paketis, ymbrikearv_paketis)

    story.append(Paragraph(buf, MC))

    story.append(PageBreak())

