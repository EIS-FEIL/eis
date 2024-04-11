"Akt kooli kohta"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const

def generate(story, toimumisaeg, maakond_nimi, testikoht, testipakett, valjastuskotid, tagastuskotid):
    # items on kotinumbrid
    test = toimumisaeg.testimiskord.test
    testiosa = toimumisaeg.testiosa
    
    story.append(Paragraph('ÜLEANDMISE JA VASTUVÕTMISE AKT', LBC))
    story.append(Paragraph('<b>(tagastatakse Haridus- ja Noorteametile koos turvakottidega)<br/>MITTE PAKKIDA TURVAKOTTI!</b>', NC))

    story.append(Paragraph('<u>%s</u>' % maakond_nimi, LBI))
    story.append(Paragraph('(linn/haridusosakond)', S))        

    koht_nimi = testikoht.koht.nimi
    if testipakett.testiruum and testipakett.testiruum.ruum:
        koht_nimi = '%s, ruum %s' % (koht_nimi, testipakett.testiruum.ruum.tahis)

    story.append(Paragraph('<u>%s</u>' % koht_nimi, LBI))
    story.append(Paragraph('(kooli nimetus)', S))        

    data = [[[Paragraph('<u>%s %s (%s)</u>' % (toimumisaeg.tahised, test.nimi,testiosa.vastvorm_nimi.lower()), LBI),
              Paragraph('(eksami nimetus)', S)],
             #[Paragraph('<u>%s</u>' % date.today().strftime('%d.%m.%Y'), LBI),
             [Paragraph('.'*30, N),             
              Paragraph('(kuupäev)', S)]]]
    story.append(Table(data, colWidths=(125*mm, 30*mm)))

    story.append(Spacer(100*mm, 5*mm))
    story.append(Paragraph('<u>Eksamikeel: %s</u>' % testipakett.lang_nimi.lower(), N))
    story.append(Spacer(100*mm, 5*mm))

    testiliik = toimumisaeg.testiosa.test.testiliik_kood
    if testiliik == const.TESTILIIK_RIIGIEKSAM:
        s_vaatlejad = 'riigieksami välisvaatleja(d)'
    elif testiliik == const.TESTILIIK_TASE:
        s_vaatlejad = 'tasemeeksami vaatleja(d)'
    else:
        s_vaatlejad = 'vaatleja(d)'

    mitu = len(valjastuskotid) > 1

    story.append(Paragraph('1. Käesolevaga kinnitan eksamimaterjalide rikkumata, %s nr %s vastuvõtmist Haridus- ja Noorteameti esindajalt:' % (mitu and 'kinniste turvakottide' or 'kinnise turvakoti', ', '.join(valjastuskotid)), N))

    story.append(Spacer(100*mm, 18*mm))
    story.append(Table([[Paragraph('kooli eksamikomisjoni esimees (nimi ja allkiri)', SC)]],
                       style=TableStyle([('LINEABOVE', (0,0),(-1,-1), 1,colors.black)]),
                       colWidths=(160*mm)))

    story.append(Paragraph('kooli eksamikomisjoni esimehelt:', N))
    story.append(Spacer(100*mm, 18*mm))
    story.append(Table([[Paragraph('%s (nimi ja allkiri)' % s_vaatlejad, SC)]],
                       style=TableStyle([('LINEABOVE', (0,0),(-1,-1), 1,colors.black)]),
                       colWidths=(160*mm)))

    
    story.append(Spacer(100*mm, 20*mm))


    mitu = len(tagastuskotid) > 1
    story.append(Paragraph('2. Käesolevaga kinnitan tagastatavate eksamimaterjalide rikkumata, %s nr %s üleandmist' % (mitu and 'kinniste turvakottide' or 'kinnise turvakoti', ', '.join(tagastuskotid)), N))

    story.append(Paragraph('kooli eksamikomisjoni esimehele:', N))
    story.append(Spacer(100*mm, 18*mm))
    story.append(Table([[Paragraph('%s (nimi ja allkiri)' % s_vaatlejad, SC)]],
                       style=TableStyle([('LINEABOVE', (0,0),(-1,-1), 1,colors.black)]),
                       colWidths=(160*mm)))


    story.append(Paragraph('Haridus- ja Noorteameti esindajale:', N))
    story.append(Spacer(100*mm, 18*mm))
    story.append(Table([[Paragraph('kooli eksamikomisjoni esimees (nimi ja allkiri)', SC)]],
                       style=TableStyle([('LINEABOVE', (0,0),(-1,-1), 1,colors.black)]),
                       colWidths=(160*mm)))


    story.append(PageBreak())

