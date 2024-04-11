"Eksamikutse tasemeeksamile registreerunule"

from .pdfutils import *
from .stylesheet import *
from datetime import date
import eis.model as model
from eis.model import const, sa
import eis.lib.helpers as h

def generate(story, sooritaja, sooritused, taiendavinfo):
    N = ParagraphStyle(name='Normal',
                       fontName='Arial-Narrow',
                       fontSize=12,
                       leading=15,
                       #backColor='#FFFF00',
                       spaceBefore=4,
                       spaceAfter=4)

    NB = ParagraphStyle(name='NormalBold',
                        parent=N,
                        fontName='Arial-Narrow-Bold')
    NBC = ParagraphStyle(name='NormalBoldCentred',
                         parent=NB,
                         alignment=TA_CENTER)
    NI = ParagraphStyle(name='NormalItalic',
                        parent=N,
                        fontName='Times-Italic')

    S = ParagraphStyle(name='Small',
                       parent=N,
                       fontSize=10,
                       leading=11,
                       spaceBefore=4,
                       spaceAfter=4)

    SB = ParagraphStyle(name='SmallBold',
                        parent=S,
                        fontName='Arial-Narrow-Bold')
    SBC = ParagraphStyle(name='NormalBoldCentred',
                         parent=SB,
                         alignment=TA_CENTER)

    story.append(Paragraph('Haridus- ja Noorteamet', LBC))
    story.append(HRFlowable(width="80%", thickness=0.5, spaceBefore=1, spaceAfter=1, hAlign='CENTER', vAlign='CENTER', color=colors.black))
    story.append(Paragraph('Lõõtsa 4, 11415 Tallinn, tel 7350 500', SBC))
    story.append(Spacer(1,3*mm))

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

    story.append(Spacer(1, 5*mm))

    keeletase_kood = sooritaja.test.keeletase_kood
    keeletase_nimi = sooritaja.test.keeletase_nimi

    sooritused = list(sooritused)
    sooritused.sort(key=lambda s: s.kavaaeg or s.algus or s.testiruum.algus or const.MAX_DATETIME)

    kuupaevad = set()
    algused = []
    for s in sooritused:
        osa = s.testiosa.nimi
        algus = s.kavaaeg or s.algus or s.testiruum.algus
        if algus:
            aeg = algus.strftime('%d.%m.%Y kell %H.%M')
        else:
            aeg = ''
        koht = s.testikoht.koht
        r_tahis = s.testiruum.ruum and s.testiruum.ruum.tahis or None
        koht_aadress = get_aadress(koht, r_tahis)
        algused.append((osa, aeg, koht_aadress))
        if algus:
            kuupaevad.add(algus.date())

    if len(kuupaevad) == 1:
        # kui kõik testiosad toimuvad samal kuupäeval,
        # siis antakse teada ainult esimese testiosa algus        
        osa, aeg, koht_aadress = algused[0]
        story.append(Paragraph('Teatame, et eesti keele %s-taseme eksam toimub %s asukohaga %s.' % \
                               (keeletase_nimi,
                                aeg,
                                koht_aadress),
                            NB))
    else:
        story.append(Paragraph('Teatame, et eesti keele %s-taseme eksam toimub:' % (keeletase_nimi), NB))
        for osa, aeg, koht_aadress in algused:
            story.append(Paragraph(f'{osa} - {algus} asukohaga {koht_aadress}', NB))
            
    if sooritaja.soovib_konsultatsiooni:
        li = list()
        for (r_algus, koht, r_tahis) in sooritaja.get_konsultatsiooniruumid():
            if not r_algus:
                msg = "Konsultatsiooni alguse aeg on määramata ({koht})".format(koht=koht_aadress)
                raise Exception(msg)
            aeg = r_algus.strftime('%d.%m.%Y kell %H.%M')
            koht_aadress = get_aadress(koht, r_tahis)
            s = '%s asukohaga %s' % (aeg, koht_aadress)
            li.append(s)

        if len(li):
            s_konsultatsioonid = '; '.join(li)
            story.append(Paragraph('Eksamieelne konsultatsioon toimub %s.' % '; '.join(li), NI))
            story.append(Paragraph('Konsultatsioon kestab kuni 4,5 tundi (kuni 6 akadeemilist tundi).', NI))

    if taiendavinfo:
        story.append(Spacer(1, 2*mm))
        story.append(Paragraph(taiendavinfo, N))        
    
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph('Isik, kes puudub eksamilt mõjuva põhjuseta või kelle eksamitulemus jääb alla 45 protsendipunkti võimalikust punktisummast, ei saa eksamit uuesti sooritada varem kui kuue kuu möödumisel eksami toimumisest.', SB))
    story.append(Paragraph('Piirangut ei kohaldata, kui isik tühistab eksamile registreerumise hiljemalt <b>neli (4) tööpäeva</b> enne eksami toimumise kuupäeva! Registreeringut saab tühistada ööpäevaringselt, kirjutades aadressile info@harno.ee (kindlasti lisada isikukood!) või helistades E–R 9.00–17.00 telefonil +372 735 0500.', S))
    story.append(Paragraph('Isikul, kes puudus eksamilt mõjuval põhjusel ning kes soovib eksamit sooritada enne 6 kuu möödumist, tuleb 30 päeva jooksul esitada vabas vormis selgitus puudumise põhjuse kohta koos tõendiga Haridus- ja Noorteametile. Dokumentidele tuleb lisada eksamile registreerumise avaldus.', S))

    story.append(HRFlowable(width="100%", thickness=0.5, spaceBefore=4, spaceAfter=2, color=colors.black))

    story.append(Paragraph('Palume eesti keele tasemeeksamile tulles meeles pidada järgmist.', S))
    story.append(Paragraph('1. Eesti keele tasemeeksam algab täpselt kell 10.00. Hilinejaid eksamile ei lubata. Soovitame olla eksamipunktis kohal 15-20 minutit enne eksami algust. Eksamiruumi numbri saab teada seinal olevatest nimekirjadest. ', S))
    story.append(Paragraph('2. Eksamile lubatakse järgmiste dokumentide alusel: ID-kaart, pass või elamisluba. NB! Autojuhiluba ei ole isikut tõendav dokument. ', S))
    story.append(Paragraph('3. Enne eksami algust tuvastab eksami läbiviija eksaminandi isiku ja kontrollib esitatud dokumente. Kui eksami läbiviijal ei õnnestu eksaminandi isikut tuvastada või tekib dokumente kontrollides kahtlus, et eksamil on vale isik või dokument pole ehtne, tuvastab isiku politsei.', S))
    story.append(Paragraph('4.	Käekell (mehhaaniline; elektrooniline; nuti vmt)  tuleb eksami ajaks käelt ära võtta!', S))
    story.append(Paragraph('5. Eksamitöö täitmisel:', S))
    story.append(Paragraph('• tuleb kirjutada loetava käekirjaga, käekirja tõttu ebaselged kohad loetakse veaks;', S))
    story.append(Paragraph('• tuleb kirjutada musta või sinise tindi või pastakaga, hariliku pliiatsiga kirjutatud ja tindi või pastakaga ülekirjutatud eksamitööd loetakse kehtetuks;', S))
    story.append(Paragraph('• laual tohib olla ainult kirjutusvahend;', S))
    story.append(Paragraph('• parandused eksamitöös tuleb teha selgelt, tõmmates maha terve sõna, sümboli või numbri;', S))
    story.append(Paragraph('• ei ole lubatud kasutada korrektorpliiatsit;', S))
    story.append(Paragraph('• ei ole lubatud kasutada abimaterjale (sõnastikud, õpikud vms);', S))
    story.append(Paragraph('• ei ole lubatud kasutada eksamitöö tegemisel kellegi teise abi;', S))
    story.append(Paragraph('• ei ole lubatud kasutada mobiiltelefoni; ', S))
    story.append(Paragraph('• ei ole lubatud häirida eksamit;', S))
    story.append(Paragraph('• ei ole lubatud eksamitööde üleandmise ajal eksamitööd lehitseda või sinna midagi kirjutada.', S))
    story.append(Paragraph('6. Kui eksamitöö hindamise käigus tuvastatakse kõrvalise abi kasutamine, hinnatakse eksamitöö 0 punktiga.', S))
    story.append(Paragraph('7. Valikvastuste kirjutamisel tuleb kasutada suuri trükitähti (A, B, C jne). I ja J, C ja G peavad selgelt eristuma. Kui eksaminand on valikülesannetes ära märkinud mitu vastust, loetakse vastus valeks.', S))
    story.append(Paragraph('8. Eksamikorra rikkumisel kõrvaldatakse eksaminand eksamilt ette hoiatamata.', S))
    story.append(Paragraph('9. Reeglina ei ole eksami ajal lubatud ruumist lahkuda; erandkorras võib eksami ajal ruumist lahkuda üksnes eksami läbiviija loal.', S))
    story.append(Paragraph('10. Eksam koosneb kirjalikust ja suulisest osast. Eksam algab kirjutamisosaga. Järgnevad kuulamis- ning lugemisosa.', S))
    buf = '11. Eesti keele %s-taseme eksami kirjalik osa kestab ' % keeletase_nimi
    if keeletase_kood=='A2':
        buf += '1 tund ja 50 min (kirjutamine 30 min, kuulamine 30 min, lugemine 50 min).'        
    elif keeletase_kood=='B1':
        buf += '2 tundi (kirjutamine 35 min, kuulamine 35 min, lugemine 50 min).'
    elif keeletase_kood=='B2':
        buf += '3 tundi ja 5 min (kirjutamine 80 min, kuulamine 35 min, lugemine 70 min).'
    elif keeletase_kood=='C1':
        buf += '3 tundi ja 15 min (kirjutamine 90 min, kuulamine 45 min, lugemine 60 min).'
    story.append(Paragraph(buf, S))
    story.append(Paragraph('12. Eksami suuline osa algab umbes 15-20 minutit pärast kirjaliku osa lõppu juhul, kui suuline osa toimub samal päeval. Eksami suulise osa läbivad eksaminandid paarikaupa nimekirja järgi. Kõikide eksaminandide suuline vastus salvestatakse ja seda hinnatakse hiljem salvestise järgi. ', S))

    story.append(Paragraph('13. Eksam on sooritatud, kui eksaminand on kogunud vähemalt 60% võimalikust punktisummast, ühegi osaoskuse tulemus ei tohi olla 0 punkti.', S))
    story.append(Paragraph('14. Eksamitulemused teatatakse hiljemalt 40 päeva pärast eksamit kirja või e-posti teel registreerimisavaldusel märgitud aadressil. Telefoni teel eksamitulemuste kohta informatsiooni ei anta.', S))
    story.append(Paragraph('15. Eksami sooritanud isikule vormistatakse eesti keele tasemeeksami elektrooniline tunnistus. Tunnistust saab soovi korral vaadata, alla laadida ning välja trükkida riigiportaalis https://www.eesti.ee ja testide andmekogus (EIS) https://eis.ekk.edu.ee/eis/.', S))
    story.append(Paragraph('16. Kui eksaminand ei ole rahul tasemeeksami tulemusega, on tal õigus 30 päeva jooksul pärast selle teatavaks tegemist <b>esitada põhjendatud vaie</b>. Vaide saab esitada <b>ainult elektroonselt</b> testide andmekogus EIS: https://eis.ekk.edu.ee/eis. Pärast sisse logimist valige "Minu tulemused" ja leidke õige eksam. Seejärel vajutage nupule "Esita vaie" ja täitke kõik vajalikud väljad. <b>Selleks, et vaie saaks esitatud, tuleb see kindlasti digitaalselt allkirjastada.</b> ',S))

    story.append(Spacer(1,5*mm))
    story.append(Paragraph('Soovime Teile edu eksamiks!', L))

    story.append(PageBreak())
    
def get_aadress(koht, r_tahis):
    buf = koht.nimi
    if r_tahis:
        buf += ' ruum %s' % r_tahis
    tais_aadress = koht.tais_aadress
    if tais_aadress:
        buf += ', %s' % (tais_aadress or '')
    return buf
