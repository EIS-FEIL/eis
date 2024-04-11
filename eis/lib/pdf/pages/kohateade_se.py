"Eksamikutse seaduse tundmise eksamile registreerunule"

from .pdfutils import *
from .stylesheet import *
from datetime import date
import eis.model as model
from eis.model import const, sa
import eis.lib.helpers as h

def generate(story, sooritaja, sooritused, taiendavinfo):

    story.append(Paragraph('Haridus- ja Noorteamet', LBC))
    story.append(HRFlowable(width="80%", thickness=0.5, spaceBefore=1, spaceAfter=1, hAlign='CENTER', vAlign='CENTER', color=colors.black))
    story.append(Paragraph('Lõõtsa 4, 11415 Tallinn, tel 7350 500', NBC))
    story.append(Spacer(3*mm,3*mm))

    kasutaja = sooritaja.kasutaja
    # aadress: vahemikus 4-6 cm ülalt, vähemalt 2 cm vasakust äärest
    li = ['Lp %s' % kasutaja.nimi] 
    if kasutaja.aadress:
        li.extend(kasutaja.aadress.li_print_aadress(kasutaja))
    aadress = '<br/>'.join(li)

    story.append(Table([[Paragraph(aadress, N), 
                         Paragraph(h.str_from_date(date.today()), N)]],
                       colWidths=(130*mm,30*mm),
                       style=TableStyle([('VALIGN', (0,0),(-1,-1), 'TOP'),
                                         ]) 
                       ))    

    story.append(Spacer(10*mm, 10*mm))

    sooritused = list(sooritused)
    sooritused.sort(key=lambda s: s.kavaaeg or s.algus or s.testiruum.algus)

    for s in sooritused:
        algus = s.kavaaeg or s.algus or s.testiruum.algus
        if algus:
            aeg = algus.strftime('%d.%m.%Y kell %H.%M')
        else:
            aeg = ''
        koht_nimi = s.testikoht.koht.nimi
        ruum_tahis = s.testiruum.ruum and s.testiruum.ruum.tahis
        if ruum_tahis:
            koht_nimi += ', ruum %s' % ruum_tahis
        tais_aadress = s.testikoht.koht.tais_aadress
        if tais_aadress:
            koht_aadress = ' (%s)' % tais_aadress
        else:
            koht_aadress = ''
        break
    
    buf = 'Teatame Teile, et olete registreeritud Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse tundmise eksamile, mis toimub %s asukohaga %s%s.' % (aeg, koht_nimi, koht_aadress)
    story.append(Paragraph(buf, NB))

    if not ruum_tahis:
        buf = 'Eksamiruumi numbri saate teada kohapeal olevast nimekirjast.'
        story.append(Paragraph(buf, NB))


    buf = 'Palume eksamile tulles kaasa võtta isikut tõendav dokument (pass, ID-kaart või elamisluba). NB! Autojuhiluba ei ole isikut tõendav dokument! Isikut tõendava dokumendita eksamile ei lubata.'
    story.append(Paragraph(buf, NB))  

    li = list()
    for (r_algus, koht, r_tahis) in sooritaja.get_konsultatsiooniruumid():
        if not r_algus:
            msg = "Konsultatsiooni alguse aeg on määramata ({koht}, {ruum})".format(koht=koht.nimi, ruum=r_tahis)                
            raise Exception(msg)
        aeg = r_algus.strftime('%d.%m.%Y kell %H.%M')
        k_nimi = koht.nimi
        if r_tahis:
            k_nimi += ', ruum %s' % r_tahis
        tais_aadress = koht.tais_aadress
        if tais_aadress:
            k_nimi += ', %s' % tais_aadress
        li.append('%s %s' % (aeg, k_nimi))
    if len(li):
        if len(li) == 1:
            buf = 'Eksamieelne konsultatsioon toimub:'
        else:
            buf = 'Eksamieelsed konsultatsioonid toimuvad järgmistel kuupäevadel:'
        story.append(Paragraph(buf, NI))
        for s_kons in li:
            story.append(Paragraph(s_kons, N))
        if len(li) > 1:
            buf = 'Konsultatsioonil osalemiseks palun valige antud aegade seast endale sobivaim!'
            story.append(Paragraph(buf, NI))
        buf = 'Konsultatsioon kestab kuni 1,5 tundi.'
        story.append(Paragraph(buf, NI))

    if taiendavinfo:
        story.append(Spacer(2*mm, 2*mm))
        story.append(Paragraph(taiendavinfo, N))        

    story.append(HRFlowable(width="100%", thickness=0.5, spaceBefore=10, spaceAfter=8, color=colors.black))

    buf = """
Teadmiseks Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse tundmise eksami sooritajale!
<br/>
1. Eksamile lubatakse ainult isikut tõendava dokumendi esitamisel (pass, ID-kaart või elamisluba). 
<br/>
2. Hilinejaid eksamiruumi ei lubata.
<br/>
3. Eksami sooritamiseks on aega 45 minutit.
<br/>
4. Eksam sooritatakse eksamipunktis, kus eksamitöö täidetakse elektrooniliselt ehk arvutil eesti keeles.
<br/>
5. Eksami ajal ei ole lubatud eksamiruumist lahkuda.
<br/>
6. Eksamitöö koosneb 24 valikvastusega küsimusest. 
<br/>
7. Eksamil on võimalik kasutada Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse eestikeelset teksti ning sõnaraamatut, mis on eksamiruumis olemas. 
<br/>
8. Eksamineeritaval palutakse eksamilt lahkuda, kui eksaminand kirjutab maha, üritab seda teha või aitab sellele kaasa; eksaminandi käitumine häirib teisi eksaminande või takistab eksami läbiviimist ja/või eksaminand ei allu eksamikomisjoni korraldusele.
<br/>
9. Eksam loetakse sooritatuks, kui eksamineeritav on vastanud õigesti vähemalt 18 küsimusele. 
<br/>
10. Eksamil osalejatele saadetakse 14 päeva jooksul teade eksami tulemuse kohta.
<br/>
11. Kui eksamikutse saanud isik loobub eksamist või ei soorita eksamit, tuleb tal vajadusel ise  uuesti eksamile registreeruda. 
registreeruma. 
<br/>
12. Eksamitulemust saab vaidlustada 30 päeva jooksul pärast tulemuse teadasaamist. Selleks tuleb
esitada avaldus Haridus-ja Teadusministeeriumile.
"""
    story.append(Paragraph(buf, N))

    story.append(Spacer(30*mm,30*mm) )
    story.append(Paragraph('Soovime Teile edu eksamiks!', L))

    story.append(PageBreak())

