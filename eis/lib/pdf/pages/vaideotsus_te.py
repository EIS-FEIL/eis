"Eesti keele tasemeeksami vaideotsus"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis.model import const
import eis.lib.helpers as h
import eis.lib.utils as utils
from .aadress import aadressikast
from .vaideotsus import vaide_allkirjad

def generate(story, vaie, allkirjastajad):
    sooritaja = vaie.sooritaja
    test = sooritaja.test

    k = sooritaja.kasutaja
    tase_nimi = test.keeletase_nimi

    font = ParagraphStyle(name='TEVaideOtsus',
                          parent=M,
                          fontSize=12,
                          alignment=TA_JUSTIFY,
                          spaceBefore=5,
                          spaceAfter=5)

    story.append(Spacer(1*mm,26*mm))
    story.append(aadressikast(k, on_kpv=False, font=font, on_lp=False))
    story.append(Spacer(2*mm, 7*mm))

    if allkirjastajad:
        story.append(Paragraph('<b>Vaidekomisjoni otsus nr %s</b>' % (vaie.vaide_nr), font))
    else:
        story.append(Paragraph('<b>Vaidekomisjoni otsuse eelnõu</b>', font))

    story.append(Spacer(6*mm,7*mm))

    story.append(Paragraph('Lugupeetud %s' % k.nimi, font))
    story.append(Spacer(1*mm,3*mm))

    tulemid = [] # osade tulemused
    nulliga_osa = False
    labikukutud = [] # läbikukutud osade alatestiliigikoodid
    muutused = [] # vaidega muudetud osade muudatused
    for s, osa, ylemsooritus in sooritaja.get_osasooritused():
        osatulem = osa.nimi.lower()
        if s and s.staatus == const.S_STAATUS_TEHTUD:
            osatulem += ' %s' % (h.fstr(s.pallid))
            if s.tulemus_protsent < test.lavi_pr:
                labikukutud.append(osa.alatest_kood)
            if s.tulemus_protsent == 0:
                nulliga_osa = True
            if s.pallid is not None and s.pallid_enne_vaiet is not None:
                vahe = s.pallid - s.pallid_enne_vaiet
                if vahe:
                    muutused.append((osa, vahe))
        elif s and s.staatus == const.S_STAATUS_PUUDUS:
            # mõnest osast puuduja on läbi kukkunud
            osatulem += ' 0'
            nulliga_osa = True
            labikukutud.append(osa.alatest_kood)
        else:
            osatulem += ' ' + (s and s.staatus_nimi or ylemsooritus.staatus_nimi)
        tulemid.append(osatulem)

    # JIRA EH-145:
    # - Kui tulemust tõstetakse ja lõpptulemus on üle 60%, 
    # siis ei tule alatestide kirjeldusi
    # ja kuvatakse muutused alatestide kaupa.
    # - Kui tulemust ei tõsteta või kui lõpptulemus on alla 60%, 
    # siis tulevad nende osaoskuste kirjeldused, mis jäävad alla 60%. 
    if vaie.muutus > 0 and sooritaja.tulemus_protsent >= test.lavi_pr and not nulliga_osa:
        labikukutud = []

    kpv = utils.str_date_aastal(sooritaja.algus)
    buf = 'Vastavalt keeleseaduse § 25 lõikele 2 vaatas Haridus- ja Noorteameti peadirektori 23.08.2023 käskkirjaga nr 1.1-1/23/98 „Eesti keele tasemeeksami tulemuste vaidekomisjoni koosseisu kinnitamine“ kinnitatud eesti keele tasemeeksamite vaidekomisjon läbi Teie %s sooritatud eesti keele %s-taseme eksami tulemuse vaidlustamise avalduse. ' % (kpv, tase_nimi)

    buf += 'Komisjon, tutvunud avalduses esitatud põhjendustega, analüüsinud hindajate tegevust ning suunanud eksamitöö ekspertidele uuesti hindamiseks, otsustas '

    if labikukutud:
        # hiljem kuvatakse alatestide kirjeldused
                
        if vaie.muutus > 0:
            s_otsus = 'tõsta Teie eksamitulemust'
        elif vaie.muutus < 0:
            s_otsus = 'langetada Teie eksamitulemust'
        else:
            s_otsus = 'jätta Teie eksamitulemuse muutmata'

        buf += s_otsus + '.'

    else:
        # ei ole vaja alatestide kirjeldusi kuvada
        
        data = []
        teieeksamitoo = 'Teie eksamitöö '
        for (osa, vahe) in muutused:
            muuta = vahe > 0 and 'tõsta' or 'langetada'
            osad = {const.ALATEST_RK_KIRJUTAMINE: 'kirjutamisosa',
                    const.ALATEST_RK_LUGEMINE: 'lugemisosa',
                    const.ALATEST_RK_RAAKIMINE: 'rääkimisosa',
                    const.ALATEST_RK_KUULAMINE: 'kuulamisosa',
                    }
            misosa = osad.get(osa.alatest_kood) or 'osa "%s"' % osa.nimi.lower()
            s = '%s %s%s tulemust %s punkti võrra' % (muuta, teieeksamitoo, misosa, h.fstr(abs(vahe)))
            teieeksamitoo = ''
            data.append(s)

        if not data:
            buf += 'jätta Teie eksamitulemuse muutmata'
        elif len(data) == 1:
            buf += data[0]
        else:
            buf += ', '.join(data[:-1]) + ' ja ' + data[-1]
        buf += '.'       
        buf += ' Komisjoni otsusel hinnati Teie eksamitööd järgmiselt:'

    story.append(Paragraph(buf, font))

    buf = '<b>Teie eksamitulemus on %s punkti ' % h.fstr(vaie.pallid_parast)
    buf += '(' + ', '.join(tulemid) + ' punkti).</b>'
    story.append(Paragraph(buf, font))

    story.append(Paragraph('Keeleseaduse § 23 lõike 3 kohaselt võetakse kohustusliku keeleoskustaseme määramisel aluseks Euroopa Nõukogu koostatud Euroopa keeleõppe raamdokumendis määratletud keeleoskustasemed. Eesti keele %s-taseme eksam tugineb Euroopa keeleõppe raamdokumendi keeleoskustaseme %s kirjeldusele.' % (tase_nimi, tase_nimi), font))

    if labikukutud:
        tase = test.keeletase_kood
        if tase == const.KEELETASE_A2:
            buf = _asjatunne_A2(labikukutud)
        elif tase == const.KEELETASE_B1:
            buf = _asjatunne_B1(labikukutud)
        elif tase == const.KEELETASE_B2:
            buf = _asjatunne_B2(labikukutud)
        elif tase == const.KEELETASE_C1:
            buf = _asjatunne_C1(labikukutud)

        for line in buf.split('\n'):
            story.append(Paragraph(line, font))

        buf = ' <br/>Lähtudes haridus- ja teadusministri 13. juuni 2011. aasta määruse nr 24 „Eesti keele tasemeeksamite ülesehitus ja läbiviimise kord“ § 4 lõike 2 alusel kinnitatud hindamisjuhendist analüüsis vaidekomisjon Teie tööd ja hindajate tegevust ning leidis järgmist:'
        story.append(Paragraph(buf, font))

        if allkirjastajad:
            # otsus
            pohjendus = vaie.otsus_pohjendus
        else:
            # eelnõu
            pohjendus = vaie.eelnou_pohjendus

        if pohjendus:
            pohjendus = pohjendus.strip()
            if pohjendus and pohjendus[-1] not in '.!?':
                pohjendus += '.'
            for line in pohjendus.split('\n'):
                story.append(Paragraph(line, font))

        buf = 'Eelnimetatud põhjusel otsustas komisjon '
        if vaie.muutus < 0:
            buf += 'langetada Teie eksamitöö tulemust %s punkti võrra.' % (h.fstr(0-vaie.muutus))
        elif vaie.muutus > 0:
            buf += 'tõsta Teie eksamitöö tulemust %s punkti võrra.' % (h.fstr(vaie.muutus))        
        else:
            buf += 'jätta Teie eksamitulemuse muutmata.'
        story.append(Paragraph(buf, font))

    if allkirjastajad:
        story.append(Paragraph('Käesolevat vaidekomisjoni otsust on võimalik vaidlustada 30 päeva jooksul teatavaks tegemisest, esitades kaebuse Tartu Halduskohtusse halduskohtumenetluse seadustikus sätestatud korras.', font))

        story.append(Spacer(9*mm, 20*mm))
        story.append(vaide_allkirjad(allkirjastajad))
 
def _asjatunne_A2(alatestid):
    buf = ''
    if const.ALATEST_RK_RAAKIMINE in alatestid:
        buf += """

Raamdokumendis kirjeldatakse A2-taseme rääkimisoskuse asjatundlikkuse näitajaid järgmiselt:
1. Oskab lihtsal viisil ning üldsõnaliselt väljenduda igapäevateemadel või oma huvivaldkonna teemade piires.
2. Oskab kasutada sagedasemaid sõnu ning käibefraase.
3. Oskab jutustava või kirjeldava teksti moodustamiseks kasutada sidumata lauseid või seob oma jutu lihtsate sidesõnade abil.
4. Oskab vahetada lühikesi lauseid, kuid ei suuda vestlust ülal hoida. Saab vestluspartnerist aru, kui   too soostub selle nimel vaeva nägema ning öeldut lihtsustama.
5. Kõne on takerduv, esineb hääldusvigu ning võõras aktsent on märgatav.
6. Kõnes esineb palju ebasobivaid alustusi.
"""
    if const.ALATEST_RK_KIRJUTAMINE in alatestid:
        buf += """

Raamdokumendis kirjeldatakse A2-taseme kirjutamisoskuse asjatundlikkuse näitajaid järgmiselt:
1. Oskab kirjutada igapäevastel teemadel lihtsamaid fraase ja lauseid, ühendades neid lihtsate sidesõnadega.
2. Oskab lihtsate fraaside ja lausetega kirjutada oma perekonnast, elutingimustest, haridusest ning praegusest ja eelmisest tööst.
3. Oskab kirjutada lühikesi ja lihtsaid lugusid inimestest, asjadest ja oma igapäevaelust.
4. Oskab üle küsida lihtsat faktiteavet.
5. Oskab häälduspäraselt (kuigi mitte õigesti) kirjutada lühikesi sõnu, mis kuuluvad tema suulisesse sõnavarasse.
6. Oskab kirjutada lühikesi lihtsaid sõnumeid, mis puudutavad igapäevaelu.
7. Oskab kirjutada väga lihtsaid isiklikke kirju.
8. Oskab täita lihtsaid isikuandmeid nõudvaid formulare.
9. Oskab enda jaoks igapäevases teemavaldkonnas infot küsida ja infopärimisele vastata.
"""
    if const.ALATEST_RK_LUGEMINE in alatestid:
        buf += """

Raamdokumendis kirjeldatakse A2-taseme lugemisoskuse asjatundlikkuse näitajaid järgmiselt:
1. Mõistab lühikesi, lihtsaid tekste, mis sisaldavad sagedasti kasutatavaid ja rahvusvahelise levikuga sõnu.
2. Oskab leida eeldatavat faktiinfot lihtsatest igapäevatekstidest.
3. Oskab leida kindlat harjumuspärast teavet igapäevatekstidest.
4. Oskab nimestikest leida ja muust eristada vajalikku teavet.
5. Mõistab lühikesi ja lihtsaid isiklikke kirju.
6. Mõistab lihtsaid igapäevaseid juhiseid ning silte ja teateid avalikes kohtades.
"""
    if const.ALATEST_RK_KUULAMINE in alatestid:
        buf += """

Raamdokumendis kirjeldatakse A2-taseme kuulamisoskuse asjatundlikkuse näitajaid järgmiselt:
1. Mõistab selgelt ja aeglaselt hääldatud fraase ja lauseid, mis seostuvad oluliste eluvaldkondadega (nt info perekonna kohta, sisseostude tegemine, kodukoht, töö).
2. Mõistab ennustatava sisuga, lühikesi, lihtsaid ja selgelt hääldatud ütluseid.
3. Suudab tabada enda jaoks tuttava valdkonna mõttevahetuse teema ja mõista mõnesid detaile, kui räägitakse aeglaselt ja selgelt.
4. Mõistab lühikeste, lihtsate ja selgelt esitatud tekstide põhisisu.
5. Saab aru igapäevaseid asju puudutavast ja selgelt esitatud numbri- jm faktiinfost.
6. Mõistab lihtsaid juhiseid.
7. Mõistab põhimises lühikesi, aeglaselt ja selgelt esitatud salvestisi, mis puudutavad ennustatava sisuga igapäevaseid asju.
8. Suudab tabada lihtsamat faktiinfot teleuudistes.
9. Suudab tabada telesaadete teemavahetust ja põhisisu, mis esitatakse piltide või muu tugimaterjali taustal.
"""
    return buf

def _asjatunne_B1(alatestid):
    buf = ''
    if const.ALATEST_RK_RAAKIMINE in alatestid:
        buf += """

Raamdokumendis kirjeldatakse B1-taseme rääkimisoskuse asjatundlikkuse näitajaid järgmiselt:
1. Tuleb lihtsat keelt kasutades toime enamikus praktilistes olukordades, nagu info küsimine, selgituse palumine, oma arvamuse avaldamine, ettepanekute tegemine.
2. Oskab esitada võrdlemisi ladusaid, kuid üldsõnalisi kirjeldusi oma huvivaldkonna teemade piires.
3. On võimeline lihtsaid keelevahendeid kasutades kirjeldama, analüüsima ja võrdlema ka ebatavalisi sündmusi ja nähtusi.
4. Oskab oma arvamust, nõustumist ja mittenõustumist viisakalt väljendada.
5. Oskab ilma ettevalmistuseta alustada, jätkata ja lõpetada lihtsat silmast silma vestlust, kui kõneaine on talle tuttav või pakub huvi.
6. Kõnes esineb küll pause ja katkestusi, aga suudab vestlust jätkata.
"""
    if const.ALATEST_RK_KIRJUTAMINE in alatestid:
        buf += """

Raamdokumendis kirjeldatakse B1-taseme kirjutamisoskuse asjatundlikkuse näitajaid järgmiselt:
1. Oskab kirjutada tuttaval teemal lihtsamaid üldsõnalisi tekste, ühendades lühemaid lauseid lihtsa järjendina.
2. Oskab kirjutada isiklikke kirju ja teateid ning anda edasi uudiseid.
3. Oskab kirjeldada tegelikku või kujuteldavat sündmust, oma kogemusi ja elamusi lihtsa tekstina, seejuures tuttavatel teemadel ka üksikasjalikult.
4. Keelekasutus ei takista üldiselt teksti mõistmist, kuid emakeele interferents on ilmne ning tekstis esineb palju eri tüüpi vigu.
"""
    if const.ALATEST_RK_LUGEMINE in alatestid:
        buf += """

Raamdokumendis kirjeldatakse B1-taseme lugemisoskuse asjatundlikkuse näitajaid järgmiselt:
1. Saab rahuldavalt aru otsesõnalistest faktipõhistest tekstidest, kui teema kuulub tema huvivaldkonda.
2. Suudab lugeda lühemaid tekste erinevatel teemadel (ajaleheartiklid, brošüürid, kasutusjuhendid, lihtne ilukirjandus).
3. On võimeline mõistma ka pikemate tekstide peamist mõtet ja otsima neist konkreetset infot, kui teema on talle oluline või tuttav.
"""
    if const.ALATEST_RK_KUULAMINE in alatestid:
        buf += """

Raamdokumendis kirjeldatakse B1-taseme kuulamisoskuse asjatundlikkuse näitajaid järgmiselt:
1. Suudab üldjoontes jälgida lühikest otsesõnalist juttu tuttaval teemal, kui kõneldakse kirjakeeles ja hääldus on selge.
2. Mõistab olulisemat ka pikemast kirjakeelsest jutust, kui räägitakse tavapärasest aeglasemalt. Paremaks mõistmiseks vajab ajuti kordamist või üleküsimise võimalust.
3. Saab aru tuttaval teemal raadiouudiste ja ennustatava sisuga (st oodatud või rutiinsete) telefonikõnede põhisisust, kui jutt on suhteliselt aeglane ja selge.
4. Suudab järgida üksikasjalikke juhiseid.
5. Mõistab faktiteavet igapäevaelu või tööga seotud teemadel.
"""
    return buf

def _asjatunne_B2(alatestid):
    buf = ''
    if const.ALATEST_RK_RAAKIMINE in alatestid:
        buf += """

Raamdokumendis kirjeldatakse B2-taseme rääkimisoskuse asjatundlikkuse näitajaid järgmiselt:
1. Oskab esitada selgeid, üksikasjalikke kirjeldusi ja ettekandeid mitmesugustel oma huvivaldkonna teemadel. Oskab kommentaaride ja asjakohaste näidete toel mõttekäike laiendada ja põhjendada.
2. Oskab esitada selgesõnalisi põhjendusi, laiendades ja toetades arutluskäike kommentaaride ja asjakohaste näidetega.
3. Oskab selgitada oma vaatenurka, kaaluda kõnealuste seisukohtade tugevaid ja nõrku külgi.
4. Oskab ettevalmistanuna selgesõnaliselt esineda. Oskab põhjendada poolt- ja vastuväiteid, kaaluda eri seisukohtade tugevaid ja nõrku külgi. Oskab esinemisjärgsetele küsimustele vastata ladusalt, sundimatult ja pingutuseta, ilma et kuulajatel tekiks mõistmisraskusi.
5. Suudab emakeelsete kõnelejatega suhelda küllaltki ladusalt ja spontaanselt, ilma et kumbki pool peaks pingutama. Oskab rõhutada toimunu või kogetu olulisust, selgitada ja põhjendada oma vaateid.
6. Oskab keelt piisavalt, et sõnu otsimata selgesõnaliselt kirjeldada vajalikku, väljendada seisukohti ja esitada põhjendusi.
"""
    if const.ALATEST_RK_KIRJUTAMINE in alatestid:
        buf += """

Raamdokumendis kirjeldatakse B2-taseme kirjutamisoskuse asjatundlikkuse näitajaid järgmiselt:
1. Oskab kirjutada selgeid, üksikasjalikke tekste oma huvivaldkonna teemade piires, sünteesides ja hinnates mitmest allikast pärit infot ja arutluskäike.
2. Oskab kirjutada kirju, mis vahendavad tundeid või kirjutajale tähtsaid sündmusi ja kogemusi.
3. Oskab kirjutada argumenteeritud arvamuskirjutist vm teksti, esitades põhjendatud poolt- või vastuväiteid ning selgitades võimalike seisukohtade eeliseid ja puudusi. Suudab sünteesida eri allikatest pärit infot ja arutluskäike.
4. Valdab üldiste kõneainete ja oma tegevusala piires ulatuslikku sõnavara.
5. Sõnakasutus on üldjoontes täpne; aeg-ajalt võib küll sõnavalikul eksida, kuid see ei takista suhtlust.
6. Valdab grammatikat küllaltki hästi. Ei tee vääritimõistmist põhjustavaid vigu.
7. Oskab kirjutada selgelt ja arusaadavalt, järgides teksti paigutamise ja liigendamise tavasid.
8. Kirjutamine ja kirjavahemärgistus on üsna korrektne, ehkki vahel on märgata emakeele mõju.
"""
    if const.ALATEST_RK_LUGEMINE in alatestid:
        buf += """

Raamdokumendis kirjeldatakse B2-taseme lugemisoskuse asjatundlikkuse näitajaid järgmiselt:
1. Loeb suuresti iseseisvalt, kohandades lugemise viisi ja kiirust sõltuvalt tekstist ja lugemise eesmärgist. Tal on suur aktiivne lugemissõnavara, kuid raskusi võib olla haruldaste idioomide mõistmisega.
2. Suudab kiiresti hõlmata pikki ja keerukaid tekste, keskendudes asjakohastele detailidele.
3. Mõistab kaasaegseid probleemartikleid ja ülevaateid, kus autorid väljendavad lahknevaid hoiakuid ja eriarvamusi.
"""
    if const.ALATEST_RK_KUULAMINE in alatestid:
        buf += """

Raamdokumendis kirjeldatakse B2-taseme kuulamisoskuse asjatundlikkuse näitajaid järgmiselt:
1. Mõistab suhteliselt pika ja keeruka üldkeelse jutu põhisisu nii konkreetse kui ka abstraktse teema puhul.
2. Suudab jälgida pikka juttu ja keeruka sisuga vaidlust juhul, kui teema on tuttav ja vestluse suunda toetavad selged märksõnad
3. Suudab jälgida keeruka arutluskäigu ja keelekasutusega loengute, aruannete ja muus vormis teaduslike või erialaste esinemiste põhisisu.
4. Mõistab normaalse kiirusega edastatud üldkeelseid teadaandeid ja sõnumeid konkreetsetel ja abstraktsetel teemadel.
5. Mõistab enamikku asjalikest raadiosaadetest ning salvestatud ja ringhäälingus levivast materjalist, mis on üldkeelne ja lubab kõneleja meeleolu, tooni vms tabada.
"""
    return buf

def _asjatunne_C1(alatestid):
    buf = ''
    if const.ALATEST_RK_RAAKIMINE in alatestid:
        buf += """

Raamdokumendis kirjeldatakse C1-taseme rääkimisoskuse asjatundlikkuse näitajaid järgmiselt:
1. Oskab keerukal teemal esitada selgeid, üksikasjalikke kirjeldusi ja ettekandeid. Oskab siduda allteemasid, arendada seisukohti ja lõpetada sobiva kokkuvõttega.
2. Väljendub ladusalt ja loomulikult, peaaegu pingutuseta. Sõnavara on rikkalik ja lubab lünki ületada kaudsel viisil.
3. Võib raskusteta kaasa lüüa väitluses, isegi kui tegu on abstraktse ja keeruka võõra teemaga. Oskab esindaja rollis veenvalt kaitsta ametlikke seisukohti. Oskab ladusalt, sundimatult ja olukohaselt vastata küsimustele, märkustele ja keerukatele vastuväidetele..
4. Tunneb paljusid idioome ja argikeeleväljendeid, tajub registrivahetusi.
5. Kasutab keelt paindlikult ja tulemuslikult enamikul suhtluseesmärkidel, valdab emotsionaalset ja vihjelist keelepruuki.
"""
    if const.ALATEST_RK_KIRJUTAMINE in alatestid:
        buf += """

Raamdokumendis kirjeldatakse C1-taseme kirjutamisoskuse asjatundlikkuse näitajaid järgmiselt:
1. Oskab keerukal teemal kirjutada selgeid, hea ülesehitusega tekste, rõhutada seejuures olulist, toetada oma seisukohti selgituste, põhjenduste ja asjakohaste näidetega ning lõpetada sobiva kokkuvõttega.
2. Oskab kirjutada selgeid, üksikasjalikke, hea ülesehitusega ja väljaarendatud kirjeldusi või loovtekste isikupärases ja loomulikus stiilis, mis arvestab lugejat.
3. Oskab kirjutada selgeid hea ülesehitusega tekste keerukatel teemadel, tõstes tähtsaima esile. Oskab laiendada ja põhjendada oma seisukohti ning esitada asjakohaseid näiteid.
4. Valdab rikkalikku sõnavara ning kasutab ka idioome ja argikeeleväljendeid.
5. Kasutab grammatiliselt õiget keelt, teksti õigekiri on korrektne.
6. Teksti paigutus, liigendus ja kirjavahemärgistus on järjekindel ning toetab lugemist.
"""
    if const.ALATEST_RK_KUULAMINE in alatestid:
        buf += """

Raamdokumendis kirjeldatakse C1-taseme kuulamisoskuse asjatundlikkuse näitajaid järgmiselt:
1. Mõistab keelt piisavalt, et saada aru pikemast jutust abstraktsel ja keerukal teemal, mis ei pruugi olla tuttav; võib siiski küsida mõnd üksikasja, eriti kui hääldus on võõrapärane. Suudab laias ulatuses mõista idiomaatilisi ja argiväljendeid, tabades ära registrivahetuse. On võimeline jälgima pikka juttu isegi siis, kui selle ülesehitus ei ole selge ja kõiki mõtteseoseid ei panda sõnadesse.
2. Suudab millise tahes, k.a keeruka abstraktse teema juures raskusteta jälgida ülejäänute keerukat koostööd rühma mõttevahetustes ja väitlustes.
3. Suudab suhteliselt hõlpsasti jälgida enamikku loengutest, mõttevahetustest ja väitlustest.
4. Suudab info kätte saada isegi kehva kvaliteedi ja moonutatud heliga avalikest teadaannetest, nagu rongijaamas, staadionil jm.
5. Mõistab keerukamat tehnilist või suunavat infot, näiteks tegevusjuhiseid, tuttavate toodete ja teenuste tutvustusi jms.
6. Mõistab vägagi erinevat laadi salvestatud materjali ja saateid, sealhulgas keelekasutuse poolest ebatavalisi, tabades ka peenemaid nüansse, nagu varjatud hoiakud ja kõnelejate omavahelised suhted.
7. On osav tegema kontekstis, grammatikas ja sõnavalikus peituvate vihjete toel järeldusi hoiakute, meeleolu ja kavatsuste kohta ning ennustama, mida on järgmisena oodata.
"""
    if const.ALATEST_RK_LUGEMINE in alatestid:
        buf += """

Raamdokumendis kirjeldatakse C1-taseme lugemisoskuse asjatundlikkuse näitajaid järgmiselt:
1. Mõistab üksikasjalikult pikki ja keerukaid tekste olenemata sellest, kas need kuuluvad tema asjatundmuse valdkonda või mitte, kui vaid on võimalik raskeid kohti üle lugeda.
2.Mõistab üksikasjalikult suuremat osa pikki keerukaid tekste, mis tulevad ette avalikus, töö- ja hariduselus; tabab pisimaidki detaile, k.a hoiakud ning arvamuste sõnastamata nüansid.
3. Mõistab üksikasjalikult pikki keerukaid kasutusjuhendeid ja tegevusjuhiseid, olenemata sellest, kas need on tema asjatundmusega seotud või mitte, kui vaid on võimalik raskeid osi üle lugeda.
4. Valdab rikkalikku sõnavara ja oskab sõnavaralünkadest üle saada kaudse väljenduse abil; sõnade otsimist või mõne väljendi vältimist tuleb ette harva. Kasutab ka idioome ja argikeeleväljendeid.
5. Mõistab kirju, kui on võimalik aeg-ajalt sõnaraamatut kasutada.
6. Suudab kiiresti hõlmata pikki ja keerukaid tekste, keskendudes asjakohastele detailidele. Tabab kiiresti laia erialast teemaringi käsitlevate uudiste, artiklite, ülevaadete sisu ja asjakohasuse ning oskab otsustada, kas tasub süveneda.
"""
    return buf

def first_page(canvas, doc, pdoc):
    "Tasemeeksami korral on esimene lehekülg plangil"
    canvas.saveState()

    image = os.path.join(IMAGES_DIR,  'Harno_logo_plangil.jpg')
    canvas.drawImage(image, 8*mm, 258*mm, 85*mm, 28*mm)

    # juurdepääsupiirang 75 aastat
    if pdoc.allkirjastajad:
        dt = pdoc.vaie.otsus_kp
    else:
        # eelnõu
        dt = date.today()

    dt_end = utils.add_months(dt, 75*12)
    canvas.setFont('Times-Bold', 10)    
    x = 136*mm
    y = 278*mm
    lines = ('ASUTUSESISESEKS',
             'KASUTAMISEKS',
             'Märge tehtud: %s' % utils.str_date(dt),
             'Kehtib kuni: %s' % utils.str_date(dt_end),
             'Alus: 75 aastat - AvTS § 35 lg 1 p 12',
             'Teabevaldaja: Haridus- ja',
             'Noorteamet')
    for ind, text in enumerate(lines):
        if ind < 2:
            canvas.setFont('Times-Bold', 10)
        else:
            canvas.setFont('Times-Roman', 10)
        canvas.drawString(x, y, text)
        y -= 4*mm

    # kontaktandmed
    canvas.setFont('Times-Roman', 10)
    buf = 'Lõõtsa 4 / 11415 Tallinn / Tel 735 0500 / info@harno.ee / www.harno.ee'
    canvas.drawString(30*mm, 17*mm, buf)

    buf = 'Registrikood 77001292'
    canvas.drawString(30*mm, 13*mm, buf)   
    
    canvas.restoreState()
