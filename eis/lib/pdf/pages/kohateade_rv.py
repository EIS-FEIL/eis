"Soorituskoha teade rahvusvahelisele eksamile registreerunule"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const
import eis.lib.helpers as h

def generate(story, kasutaja, sooritused, taiendavinfo):

    story.append(Paragraph('Haridus- ja Noorteamet', NBC))
    story.append(Paragraph('Lõõtsa 4, 11415 Tallinn, tel 7350 500', NBC))
    story.append(Spacer(3*mm,3*mm))
    story.append(Paragraph('RAHVUSVAHELISTE EKSAMITE TEADE', NC))

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

    story.append(Paragraph('Teatame rahvusvahelise eksami toimumise aja ja koha.', N))
    testid_id = []
    delf = False
    notdelf = False
    for s in sooritused:
        sooritaja = s.sooritaja
        test = sooritaja.test
        if test.id not in testid_id:
            testid_id.append(test.id)
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

        buf += '%s (%s)' % (test.nimi, s.testiosa.nimi)
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

        story.append(Paragraph(buf, N))
        
        testi_nimi = test.nimi
        if 'DELFscolaire' in testi_nimi:
            delf = True
        else:
            notdelf = True

    if taiendavinfo:
        story.append(Spacer(2*mm, 2*mm))
        story.append(Paragraph(taiendavinfo, N))        

    story.append(Spacer(2*mm, 2*mm))
    if delf and not notdelf:
        story.append(Paragraph('Infot eksami sisu ja korralduse kohta leiate Haridus- ja Noorteameti koduleheküljelt www.harno.ee.', N))
        story.append(Paragraph('NB! Suulise eksami puhul on ära toodud selle kuupäeva kõige esimese õpilase soorituse kellaaeg. Täpse ajagraafiku koostab kool ning informeerib sellest kõiki registreerinud õpilasi.', N))
        story.append(Paragraph('Kui sooritate eksami mõnes teises koolis, toimub suuline eksam samal päeval kirjaliku eksamiga vastavalt kas enne (A1 ja A2 eksamitel) või pärast (B1 ja B2 eksamitel) seda.', N))
        story.append(Paragraph('Eksamikoolis tuleb kohal olla hiljemalt 30 minutit enne eksami algust ning kaasa võtta kehtiv pildiga isikut tõendav dokument (pass, ID-kaart või autojuhiluba) ja sinine või must pastakas. Hariliku pliiatsiga eksamitööle märkmete tegemine või mis tahes kustutusvahendite kasutamine on keelatud. Oma vastuste sõnastamiseks saate kasutada mustandipaberit. Samuti ei ole eksamil lubatud kasutada elektroonikaseadmeid (mobiiltelefon, (tahvel)arvuti, nutikell, kalkulaator) ükskõik mis eesmärgil.', N))

    elif not delf and notdelf:
        story.append(Paragraph('Infot eksamite sisu ja korralduse kohta leiate Haridus- ja Noorteameti koduleheküljelt www.harno.ee.', N))    

        story.append(Spacer(2*mm, 2*mm))
        story.append(Paragraph('Eksamile palume kohale tulla 15 minutit enne eksami algust ning kaasa võtta kehtiv pildiga isikut tõendav dokument (pass, ID-kaart või autojuhiluba). Eksamil ei ole lubatud kasutada mobiiltelefoni ükskõik mis eesmärgil (kaasa arvatud kella või kalkulaatorina).', N))

        if not (len(testid_id) == 1 and test.testiliik_kood == const.TESTILIIK_RV and test.aine_kood == const.AINE_EN):
            # kui on ainult ingl k rv eksam, siis ei kuvata lause "Kui ei soovi..."
            story.append(Spacer(2*mm, 2*mm))
            story.append(Paragraph('Kui Te ei soovi eksamil osaleda, siis palume saata teade hiljemalt seitse (7) päeva enne eksami toimumise kuupäeva aadressile info@harno.ee.', N))
    elif delf and notdelf:
        story.append(Paragraph('Infot eksami sisu ja korralduse kohta leiate Haridus- ja Noorteameti koduleheküljelt www.harno.ee.', N))
        story.append(Paragraph('***', N))
        story.append(Paragraph('Eksamile palume kohale tulla 15 minutit enne eksami algust ning kaasa võtta kehtiv pildiga isikut tõendav dokument (pass, ID-kaart või autojuhiluba). Eksamil ei ole lubatud kasutada mobiiltelefoni ükskõik mis eesmärgil (kaasa arvatud kella või kalkulaatorina).', N))
        if not (len(testid_id) == 1 and test.testiliik_kood == const.TESTILIIK_RV and test.aine_kood == const.AINE_EN):
            # kui on ainult ingl k rv eksam, siis ei kuvata lause "Kui ei soovi..."
            story.append(Spacer(2*mm, 2*mm))
            story.append(Paragraph('Kui Te ei soovi eksamil osaleda, siis palume saata teade hiljemalt seitse (7) päeva enne eksami toimumise kuupäeva aadressile info@harno.ee.', N))

        story.append(Paragraph('Eksamikoolis tuleb kohal olla hiljemalt 30 minutit enne eksami algust ning kaasa võtta kehtiv pildiga isikut tõendav dokument (pass, ID-kaart või autojuhiluba) ja sinine või must pastakas. Hariliku pliiatsiga eksamitööle märkmete tegemine või mis tahes kustutusvahendite kasutamine on keelatud. Oma vastuste sõnastamiseks saate kasutada mustandipaberit. Samuti ei ole eksamil lubatud kasutada elektroonikaseadmeid (mobiiltelefon, (tahvel)arvuti, nutikell, kalkulaator) ükskõik mis eesmärgil.', N))


    story.append(Spacer(5*mm,5*mm))
    story.append(Paragraph('Haridus- ja Noorteamet', N))
    story.append(Paragraph('Lõõtsa 4, 11415 Tallinn', N))
    story.append(Paragraph('Tel: 7350 500', N))
    story.append(Paragraph('https://www.harno.ee', N))

    story.append(PageBreak())
