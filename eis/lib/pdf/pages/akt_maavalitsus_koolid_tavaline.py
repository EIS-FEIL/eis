# -*- coding: utf-8 -*- 
"Väljastuskottide koolidele üleandmise akt"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const

def generate(story, toimumisaeg, maakond_nimi, items):
    test = toimumisaeg.testimiskord.test
    testiosa = toimumisaeg.testiosa
    
    story.append(Paragraph('AKT', LBC))
    story.append(Paragraph('<b>(jääb eksameid korraldava asutuse ehk Haridus- ja Noorteameti esindajale)</b>', NC))

    story.append(Paragraph('<u>%s</u>' % maakond_nimi, LBI))
    story.append(Paragraph('(üleandja)', S))        

    data = [[[Paragraph('<u>%s %s (%s)</u>' % (toimumisaeg.tahised, test.nimi,testiosa.vastvorm_nimi.lower()), LBI),
              Paragraph('(eksami nimetus)', S)],
             #[Paragraph('<u>%s</u>' % date.today().strftime('%d.%m.%Y'), LBI),
             [Paragraph('.'*29, N),
              Paragraph('(kuupäev)', S)]]]
    story.append(Table(data, colWidths=(125*mm, 30*mm)))

    lang_data = {}
    langs = []
    for rcd in items:
        kotinr, lang, koht_nimi, ruum_tahis = rcd
        if ruum_tahis:
            # on_ruumiprotokoll
            koht_nimi = '%s, ruum %s' % (koht_nimi, ruum_tahis)
        if lang not in lang_data:
            langs.append(lang)
            lang_data[lang] = [['Nr', 'Kool', 'Turvakoti number', 'Allkiri']]
            n = 0
        n += 1
        lang_data[lang].append([n, koht_nimi, kotinr, ''])

    TS=TableStyle([('LINEBELOW',(0,0),(-1,0), 1,colors.black),
                   ('LINEABOVE',(0,1),(-1,-1),0.5, colors.black)])
    for lang in langs:
        story.append(Spacer(100*mm, 5*mm))
        story.append(Paragraph('<u>Eksamikeel: %s</u>' % const.LANG_NIMI.get(lang).lower(), N))
        story.append(Table(tp(lang_data[lang], N),
                           colWidths=(8*mm, 78*mm, 50*mm, 22*mm),
                           style=TS))

    story.append(PageBreak())

