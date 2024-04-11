# -*- coding: utf-8 -*- 
"Soorituskoha teade sisseastumiseksamile registreerunule"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const
import eis.lib.helpers as h

def generate(story, sooritaja, sooritused, taiendavinfo):

    story.append(Paragraph('', NBC))
    story.append(Paragraph('', NBC))
    story.append(Spacer(3*mm,3*mm))
    story.append(Paragraph('Sisseastumiseksami toimumise teade', NC))

    kasutaja = sooritaja.kasutaja
    #aadress: vahemikus 4-6 cm ülalt, vähemalt 2 cm vasakust äärest
    li = [kasutaja.nimi] 
    if kasutaja.aadress:
        li.extend(kasutaja.aadress.li_print_aadress(kasutaja))
    aadress = '<br/>'.join(li)

    story.append(Table([[Paragraph(aadress, N), 
                            Paragraph(h.str_from_date(date.today()), N)]],
                        colWidths=(130*mm,30*mm),
                        style=TableStyle([('VALIGN', (0,0),(-1,-1), 'TOP'),
                                        ]) 
                        ))    

    story.append(Spacer(5*mm, 5*mm))

    story.append(Paragraph('Lp %s' % kasutaja.nimi, N))
    story.append(Spacer(5*mm,5*mm))

    story.append(Paragraph('Teatame sisseastumiseksami toimumise aja ja koha.', N))
    for s in sooritused:
        if s.testiosa.oma_kavaaeg:
            kavaaeg = s.kavaaeg
        else:
            tpr = s.testiprotokoll
            kavaaeg = tpr and tpr.algus or s.testiruum.algus

        if kavaaeg:
            buf = kavaaeg.strftime('<b>%d.%m.%Y kell %H.%M</b>') + ' - '
        elif s.testiruum.algus:
            buf = s.testiruum.algus.strftime('<b>%d.%m.%Y</b>') + ' - '
        else:
            buf = ''

        buf += '%s (%s); ' % (s.testiosa.test.nimi, s.testiosa.nimi)
        buf += s.testikoht.koht.nimi
        if s.testiruum.ruum and s.testiruum.ruum.tahis:
            buf += ', ruum %s' % s.testiruum.ruum.tahis

        tais_aadress = s.testikoht.koht.tais_aadress
        if tais_aadress:
            buf += '; %s' % (tais_aadress or '')
        buf += '.'
        
        story.append(Paragraph(buf, N))

    if taiendavinfo:
        story.append(Spacer(2*mm, 2*mm))
        story.append(Paragraph(taiendavinfo, N))        

    story.append(Spacer(2*mm, 2*mm))

    story.append(Paragraph("Sisseastumiseksamit viiakse läbi e-testide keskkonnas, kuhu saab sisse logida kasutades ID-kaarti, mobiil-ID'd või Smart-ID'd ning vastava autentimisvahendi PIN1.", N))

    story.append(Paragraph("Eksamile palume kohale tulla 15 minutit enne eksami algust ning kaasa võtta pass või ID-kaart.", N))

    story.append(Paragraph("Mobiiltelefoni on lubatud kasutada üksnes ja ainult eksamisüsteemi mobiil-ID või Smart ID-ga sisselogimiseks. Ühelgi muul eesmärgil (kaasa arvatud kella või kalkulaatorina) mobiiltelefoni eksamil kasutada ei ole lubatud.", N))

    story.append(PageBreak())
