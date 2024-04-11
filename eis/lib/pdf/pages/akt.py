# -*- coding: utf-8 -*- 
# $Id: akt.py 533 2016-03-30 11:31:19Z ahti $
"Mitmesugused üleandmisaktid"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const

def generate(story, toimumisaeg, prk_nimi, items, suund, kullerile):
    """Kasutatakse erinevatel juhtudel:
    EKK -> kuller (suund=VALJA, kullerile=True)
    kuller -> maavalitsus (suund=VALJA, kullerilt=True)
    maavalitsus -> kuller (suund=TAGASI, kullerile=True)
    kuller -> Haridus- ja Noorteamet (suund=TAGASI, kullerilt=True)
    """

    REKK = 'Haridus- ja Noorteamet'
    KULLER = 'Kullerfirma esindaja'

    if suund == const.SUUND_VALJA:
        if kullerile:
            # REKK -> kuller
            yleandja = REKK
            vastuvotja = KULLER
            sihtkoht = prk_nimi
        else:
            # kuller -> maavalitsus
            yleandja = KULLER
            vastuvotja = prk_nimi
            sihtkoht = None
    else:
        if kullerile:
            # maavalitsus -> kuller
            yleandja = prk_nimi
            vastuvotja = KULLER
            sihtkoht = REKK
        else:
            # kuller -> REKK
            yleandja = KULLER
            vastuvotja = REKK
            sihtkoht = None


    test = toimumisaeg.testimiskord.test
    testiosa = toimumisaeg.testiosa
    
    # akti nimi
    story.append(Paragraph('AKT', LBC))
    if sihtkoht:
        story.append(Paragraph('<b>Eksamimaterjalide kinniste turvakottide üleandmise ja vastuvõtmise kohta toimetamiseks sihtkohta</b>', N))


    # sihtkoha andmed
    if sihtkoht:
        story.append(Paragraph('<u>%s</u>' % (sihtkoht), LBI))
        story.append(Paragraph('(sihtkoht)', S))        
    else:
        story.append(Paragraph('<u>%s</u>' % (vastuvotja), LBI))
        story.append(Paragraph('(vastuvõtja)', S))


    # eksami andmed
    data = [[[Paragraph('<u>%s %s (%s)</u>' % (toimumisaeg.tahised, test.nimi,testiosa.vastvorm_nimi.lower()), LBI),
              Paragraph('(eksami nimetus)', S)],
             #[Paragraph('<u>%s</u>' % date.today().strftime('%d.%m.%Y'), LBI),
             [Paragraph('.'*29, N),             
              Paragraph('(kuupäev)', S)]]]
    story.append(Table(data, colWidths=(125*mm, 30*mm)))


    # turvakottide loetelu
    lang_data = {}
    langs = []
    for rcd in items:
        kotinr, lang, koht_nimi, ruum_tahis = rcd
        if ruum_tahis:
            # on_ruumiprotokoll
            koht_nimi = '%s, ruum %s' % (koht_nimi, ruum_tahis)
        if lang not in lang_data:
            langs.append(lang)
            lang_data[lang] = [['Nr', 'Kool', 'Turvakoti number']]
            n = 0
        n += 1
        lang_data[lang].append([n, koht_nimi, kotinr])

    TS=TableStyle([('LINEBELOW',(0,0),(2,0), 1,colors.black)])
    for lang in langs:
        story.append(Spacer(100*mm, 5*mm))
        story.append(Paragraph('<u>Eksamikeel: %s</u>' % const.LANG_NIMI.get(lang).lower(), N))
        story.append(Table(tp(lang_data[lang], N),
                           colWidths=(8*mm, 78*mm, 72*mm),
                           style=TS))

    story.append(Spacer(50*mm, 10*mm))


    # yleandja ja vastuvõtja andmed
    data = [['<i>Andis üle</i>', '<i>Võttis vastu</i>'],
            [Spacer(50*mm,10*mm), Spacer(50*mm, 10*mm)],
            ]

    data.append([Paragraph(yleandja + '<br/>(esindaja nimi ja allkiri)', SC),
                 Paragraph(vastuvotja + '<br/>(esindaja nimi ja allkiri)', SC)])

    story.append(Table(tp(data, N),
                       colWidths=(79*mm, 79*mm),
                       style=TableStyle([('LINEBELOW', (0,1),(1,1), 1, colors.black)])))


    story.append(PageBreak())

