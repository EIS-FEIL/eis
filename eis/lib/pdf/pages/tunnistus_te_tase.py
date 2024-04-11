"Riigikeele tasemeeksami tunnistus"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis import model
from eis.model import const
import eis.lib.helpers as h

def generate(story, tunnistusenr, valjastamisaeg, nimi, kasutaja, sessioon, q_sooritajad, sooritaja):
    # q_sooritajad on alati None

    N10 = ParagraphStyle(name='N10',
                         fontName='Times-Roman',
                         fontSize=10,
                         leading=12,
                         alignment=TA_CENTER)                         
    N12 = ParagraphStyle(name='N12',
                         fontName='Times-Roman',
                         fontSize=12,
                         leading=18,
                         alignment=TA_CENTER)                                                  
    NL10 = ParagraphStyle(name='NL10',
                         fontName='Times-Roman',
                         fontSize=10,
                         leading=14,
                         alignment=TA_LEFT)                         
    NL12 = ParagraphStyle(name='NL12',
                         fontName='Times-Roman',
                         fontSize=12,
                         leading=16,
                         alignment=TA_LEFT)                                                  
    N14 = ParagraphStyle(name='N14',
                         fontName='Times-Roman',
                         fontSize=14,
                         leading=18,
                         alignment=TA_CENTER)                                                  
    NR12 = ParagraphStyle(name='NR12',
                          fontName='Times-Roman',
                          fontSize=12,
                          leading=16,
                          alignment=TA_RIGHT)
    NB12 = ParagraphStyle(name='NB12',
                          fontName='Times-Bold',
                          fontSize=12,
                          leading=16,
                          alignment=TA_CENTER)                                                   
    NB16 = ParagraphStyle(name='NB16',
                          fontName='Times-Bold',
                          fontSize=16,
                          leading=18,
                          alignment=TA_CENTER)                                                   

    test = sooritaja.test
    keeletase_kood = test.keeletase_kood
    keeletase_nimi = test.keeletase_nimi

    story.append(Spacer(5*mm, 37*mm))
    story.append(Paragraph('EESTI VABARIIK', N12))
    story.append(Spacer(5*mm, 2*mm))    
    fn_img = os.path.join(IMAGES_DIR,  'eestivapp.jpg')
    story.append(Image(fn_img, width=72, height=72))
    story.append(Spacer(5*mm, 2*mm))    

    story.append(Paragraph('EESTI KEELE TASEMETUNNISTUS', N12))
    story.append(Paragraph('NR %s' % tunnistusenr, N12))
    #story.append(Spacer(5*mm,5*mm))
    story.append(Paragraph(nimi.upper(), NB16))
    story.append(Paragraph('(ees- ja perekonnanimi)', N10))
    story.append(Spacer(5*mm, 4*mm))

    story.append(Paragraph(kasutaja.isikukood or kasutaja.synnikpv.strftime('%d.%m.%Y'), NB16))
    story.append(Paragraph('(isikukood või sünniaeg)', N10))    
    story.append(Spacer(5*mm, 4*mm))

    if keeletase_kood in (const.KEELETASE_ALG, const.KEELETASE_KESK, const.KEELETASE_KORG):
        buf = 'on sooritanud eesti keele %staseme eksami' % keeletase_nimi
    else:
        buf = 'on sooritanud eesti keele %s-taseme eksami' % keeletase_nimi
    if sooritaja.vabastet_kirjalikust:
        buf += ' kodakondsuse taotlejale.'
    else:
        buf += '.'
    story.append(Paragraph(buf, NB12))

    story.append(Spacer(5*mm, 7*mm))
    
    story.append(Table([[Paragraph('Tema keeleoskust hinnati järgmiselt:', NL12),]],
                       colWidths=(149*mm,)))

    # Ei kuva kogu testi tulemust, vaid alatestide tulemusi
    # või kui testiosas pole alateste, siis testiosa tulemusi
   
    osasooritused = []
    for (item, osa, ylemsooritus) in sooritaja.get_osasooritused():    
        try:
            alatest_kood = osa.alatest_kood
        except:
            alatest_kood = None
        r = [osa.nimi,
             osa.vastvorm_kood,
             item and item.staatus or ylemsooritus.staatus,
             item and item.staatus_nimi or ylemsooritus.staatus_nimi,
             item and item.pallid or None,
             item and item.tulemus_protsent or None,
             alatest_kood]
        osasooritused.append(r)

    #sooritaja.vabastet_kirjalikust = True
    #osasooritused[1][2] = const.S_STAATUS_VABASTATUD
    
    if test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
        # riigieksami osaoskuseid näidatakse tasemeeksami oskustena
        osasooritused = _convert_osasooritused(osasooritused)

    rows = []
    for osa_nimi, vastvorm_kood, staatus, staatus_nimi, pallid, tulemus_protsent, alatest_kood in osasooritused:
        if staatus == const.S_STAATUS_TEHTUD and tulemus_protsent is not None:
            if keeletase_kood in (const.KEELETASE_ALG, const.KEELETASE_KESK, const.KEELETASE_KORG):
                # tulemused on punktides
                selgitus = '%s p' % (h.fstr(pallid))
                protsent = ''
            else:
                # tulemused on protsendivahemikuga
                vahemik_id, algus, lopp = test.get_vahemik_by_protsent(tulemus_protsent)
                selgitus = const.VAHEMIK[vahemik_id]
                protsent = '(%d-%d%%)' % (algus, lopp)
        else:
            selgitus = staatus_nimi.lower()
            if staatus == const.S_STAATUS_VABASTATUD and sooritaja.vabastet_kirjalikust \
                   and alatest_kood == const.ALATEST_RK_KIRJUTAMINE:
                selgitus += '*'
            protsent = ''
        rows.append([Paragraph(osa_nimi, NL12),
                     Paragraph(selgitus, NL12),
                     Paragraph(protsent, NL12),
                     ])

    story.append(Table(rows,
                       colWidths=(60*mm, 60*mm, 25*mm),
                ))    

    story.append(Spacer(5*mm, 5*mm))
    story.append(Table([[Paragraph('Keeleoskustaseme iseloomustus', N10),]],
                       colWidths=(155*mm,)))
    story.append(Spacer(5*mm, 3*mm))

    if keeletase_kood == const.KEELETASE_A2:
        buf = """A2-tasemel keelekasutaja mõistab lauseid ja sageli kasutatavaid väljendeid, mis seostuvad talle oluliste valdkondadega (näiteks info enda ja pere kohta, sisseostude tegemine, kodukoht, töö). Ta tuleb toime igapäevastes suhtlusolukordades, mis nõuavad otsest ja lihtsat infovahetust tuttavatel rutiinsetel teemadel, oskab lihtsate fraaside ja lausete abil kirjeldada oma perekonda, teisi inimesi ja elutingimusi ning väljendada oma vajadusi."""
    elif keeletase_kood == const.KEELETASE_B1:
        buf = """B1-tasemel keelekasutaja mõistab kõike olulist endale tuttaval teemal, nagu töö, kool, vaba aeg või muu, saab enamasti hakkama välisriigis, kus vastavat keelt räägitakse, oskab koostada lihtsat teksti tuttaval või enda jaoks huvipakkuval teemal, oskab kirjeldada kogemusi, sündmusi, unistusi ja eesmärke ning lühidalt põhjendada-selgitada oma seisukohti ja plaane."""
    elif keeletase_kood == const.KEELETASE_B2:
        buf = """B2-tasemel keelekasutaja mõistab keerukate abstraktsel või konkreetsel teemal tekstide ning erialase mõttevahetuse tuuma, suudab spontaanselt ja ladusalt vestelda sama keele emakeelse kõnelejaga, oskab paljudel teemadel luua selget, üksikasjalikku teksti ning selgitada oma vaatenurka, kaaluda kõnealuste seisukohtade tugevaid ja nõrku külgi."""
    elif keeletase_kood == const.KEELETASE_C1:
        buf = """C1-tasemel keelekasutaja mõistab pikki ja keerukaid tekste, tabab ka varjatud tähendust, oskab end spontaanselt ja ladusalt mõistetavaks teha, väljendeid eriti otsimata, oskab kasutada keelt paindlikult ja tulemuslikult nii avalikes, õpi- kui ka tööolukordades, oskab luua selget, loogilist, üksikasjalikku teksti keerukatel teemadel, kasutades sidusvahendeid ja sidusust loovaid võtteid."""

    elif keeletase_kood == const.KEELETASE_ALG:
        buf = 'eesti keele piiratud suuline ja elementaarne kirjalik oskus'
    elif keeletase_kood == const.KEELETASE_KESK:
        buf = 'eesti keele suuline ja piiratud kirjalik oskus'
    elif keeletase_kood == const.KEELETASE_KORG:
        buf = 'eesti keele suuline ja kirjalik oskus'
    elif not keeletase_kood:
        raise Exception('Testile %s ei ole märgitud keeleoskuse taset' % test.id)
    else:
        raise Exception('Testil %s on tundmatu keeleoskuse tase %s' % (test.id, keeletase_kood))

    story.append(Table([[Paragraph(buf, NL10),]],
                       colWidths=(155*mm,)))
    story.append(Spacer(5*mm, 3*mm))

    for sooritus in sooritaja.sooritused:
        if sooritus.staatus == const.S_STAATUS_TEHTUD:
            aadress = sooritus.testikoht.koht.aadress
            kohas = aadress and aadress.vald_liigita or ''
            if kohas:
                kohas = model.Asukohamaarus.get_for(kohas)
            break
    buf = 'Eksam on sooritatud %s %s' % (kohas, sooritus.algus.strftime('%d.%m.%Y'))
    protokollid = [s.testiprotokoll.tahised for s in sooritaja.sooritused if s.testiprotokoll]
    # TSEISist imporditud protokollides esineb korduvaid numbreid, 
    # mis on EISi paigutamiseks tähistatud lõpuga .1 - eemaldame selle lõpu
    protokollid = [x.endswith('.1') and x[:-2] or x for x in protokollid]
    if len(protokollid) == 1:
        buf += ', eksamiprotokoll %s.' % protokollid[0]
    elif len(protokollid) > 1:
        buf += ', eksamiprotokollid %s.' % ', '.join(protokollid)
    else:
        buf += '.'
    story.append(Table([[Paragraph(buf, NL12),]],
                       colWidths=(155*mm,)))

    story.append(Spacer(5*mm, 8*mm))

    buf = 'Haridus- ja Noorteamet<br/>ALLKIRJASTATUD DIGITAALSELT'
    story.append(Table([[Paragraph(buf, NR12)]], 
                       colWidths=(120*mm),
                       ))    

    # if sooritaja.vabastet_kirjalikust:
    #     buf = u'* Kodakondsuse seaduse § 34 lõike 1 kohaselt on vähemalt 65-aastane Eesti kodakondsust taotlev isik'+\
    #           '<br/>' + '&nbsp;'*4 + \
    #           u'keeleeksamil vabastatud kodakondsusseaduse § 8 2. lõike punktis 4 sätestatud nõuete täitmisest'+\
    #           '<br/>' + '&nbsp;'*6 + \
    #           u'(oskus koostada lihtsat teksti tuttaval või enda jaoks huvipakkuval teemal), st kirjutamistestist.'
    #     story.append(Paragraph(buf, NL10))
        
    story.append(PageBreak())

def _convert_osasooritused(osasooritused):
    "Riigieksami osasooritused teisendatakse tasemeeksami osasooritusteks"

    # Riigikeele eksamil (REIS) on osad: kirjutamine, kuulamine, lugemine, keele struktuur ja suuline;
    # riigikeele eksamil (EIS) on osad: kirjalik (kirjutamine, kuulamine, lugemine, keele struktuur) ja suuline;
    # B2 tasemeeksamil on osad: kirjalik (kirjutamine, kuulamine, lugemine) ja kõnelemine;
    # riigikeele eksami põhjal tunnistust väljastades tuleb lugemise ja keele struktuuri tulemust
    # näidata ühe osaoskusena, nagu oleks B2 tasemeeksam.
    # Eeldame, et lugemise ja keele struktuuri osad saame siis, kui võtame kaks viimast kirjalikku osaoskust
    
    # leiame viimased kaks kirjalikku osaoskust
    n_lugemine = n_struktuur = None
    for n in range(len(osasooritused)-1,-1,-1):
        r = osasooritused[n]
        vastvorm_kood = r[1]
        if vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_KP):
            if n_struktuur is None:
                n_struktuur = n
            elif n_lugemine is None:
                n_lugemine = n
                break

    if n_lugemine is not None:
        # kui leidsime, siis liidame viimase tulemuse eelviimasele ja eemaldame jadast viimase
        lugemine = osasooritused[n_lugemine]
        struktuur = osasooritused[n_struktuur]
        if lugemine[1] == const.S_STAATUS_TEHTUD and struktuur[1] == const.S_STAATUS_TEHTUD:
            # liidame kokku
            pallid = lugemine[4] + struktuur[4]
            protsent = (lugemine[5] + struktuur[5])/2
        elif lugemine[1] == const.S_STAATUS_VABASTATUD and struktuur[1] == const.S_STAATUS_TEHTUD:
            # võtame struktuuri tulemuse
            pallid = struktuur[4]
            protsent = struktuur[5]
        else:
            # ei muuda
            pallid = lugemine[4]
            protsent = lugemine[5]

        osasooritused[n_lugemine][4] = pallid
        osasooritused[n_lugemine][5] = protsent
        del osasooritused[n_struktuur]

    return osasooritused

def first_page(canvas, doc, pdoc):
    "Esimese lehekülje jalus"

    if pdoc.sooritaja.vabastet_kirjalikust:
        buf1 = '* Kodakondsuse seaduse § 34 lõike 1 kohaselt on vähemalt 65-aastane Eesti kodakondsust taotlev isik'
        buf2 = 'keeleeksamil vabastatud kodakondsusseaduse § 8 2. lõike punktis 4 sätestatud nõuete täitmisest'
        buf3 = '(oskus koostada lihtsat teksti tuttaval või enda jaoks huvipakkuval teemal), st kirjutamistestist.'

        canvas.saveState()
        canvas.setFont('Times-Roman', 10)

        canvas.line(28*mm, 34*mm, 178*mm, 34*mm)
        canvas.drawString(30*mm, 29*mm, buf1)
        canvas.drawString(35*mm, 24*mm, buf2)
        canvas.drawString(36*mm, 19*mm, buf3)
        canvas.restoreState()

def later_pages(canvas, doc, pdoc):
    "Teise ja järgmiste lehekülgede jalus"
    return
