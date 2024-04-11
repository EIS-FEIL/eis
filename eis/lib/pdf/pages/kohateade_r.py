"Soorituskoha teade riigieksamile registreerunule"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const
import eis.lib.helpers as h

def generate(story, kasutaja, sooritused, taiendavinfo):

    story.append(Paragraph('Haridus- ja Noorteamet', NBC))
    story.append(Paragraph('Lõõtsa 4, 11415 Tallinn, tel 7350 500', NBC))
    story.append(Spacer(3*mm,3*mm))
    story.append(Paragraph('RIIGIEKSAMITE TEADE', NC))

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

    story.append(Paragraph('Teatame riigieksami toimumise aja ja koha.', N))
    for s in sooritused:
        sooritaja = s.sooritaja
        test = sooritaja.test
        if s.testiosa.oma_kavaaeg:
            kavaaeg = s.kavaaeg
        else:
            kavaaeg = s.testiruum.algus

        if kavaaeg:
            buf = kavaaeg.strftime('<b>%d.%m.%Y kell %H.%M</b>') + ' - '
        elif s.testiruum.algus:
            buf = s.testiruum.algus.strftime('<b>%d.%m.%Y</b>') + ' - '
        else:
            buf = ''

        buf += '%s (%s)' % (s.testiosa.test.nimi, s.testiosa.nimi)
        if sooritaja.kursus_kood:
            buf += ', %s' % sooritaja.kursus_nimi
        if test.aine_kood == const.AINE_M and test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
            buf += ', %ses' % sooritaja.lang_nimi.lower()
        buf += '; ' + s.testikoht.koht.nimi
        if s.testiruum.ruum and s.testiruum.ruum.tahis:
            buf += ', ruum %s' % s.testiruum.ruum.tahis

        tais_aadress = s.testikoht.koht.tais_aadress
        if tais_aadress:
            buf += '; %s' % (tais_aadress or '')
        buf += '.'
        
        if not kavaaeg:
            buf += ' Vastamise kellaaja saate teada kirjalikul eksamil.'

        story.append(Paragraph(buf, N))

    if taiendavinfo:
        story.append(Spacer(2*mm, 2*mm))
        story.append(Paragraph(taiendavinfo, N))        
    
    story.append(Spacer(2*mm, 2*mm))
    story.append(Paragraph('Infot eksamite sisu ja korralduse kohta leiate Haridus- ja Noorteameti koduleheküljelt www.harno.ee.', N))

    story.append(Spacer(2*mm, 2*mm))
    story.append(Paragraph('Eksamile palume kohale tulla 15 minutit enne eksami algust ning kaasa võtta kehtiv pildiga isikut tõendav dokument (pass, ID-kaart või autojuhiluba). Eksamil ei ole lubatud kasutada mobiiltelefoni ükskõik mis eesmärgil (kaasa arvatud kella või kalkulaatorina).', N))

    story.append(Spacer(2*mm, 2*mm))
    story.append(Paragraph('Elektroonilised riigieksamitunnistused avaldatakse riigiportaalis <a href="https://www.eesti.ee">www.eesti.ee</a>.', N))

    story.append(Spacer(5*mm,5*mm))
    story.append(Paragraph('Haridus- ja Noorteamet', N))
    story.append(Paragraph('Lõõtsa 4, 11415 Tallinn', N))
    story.append(Paragraph('Tel: 7350 500', N))
    story.append(Paragraph('https://www.harno.ee', N))

    story.append(PageBreak())
