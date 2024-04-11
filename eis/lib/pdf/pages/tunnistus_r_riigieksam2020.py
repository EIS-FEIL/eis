"Riigieksamitunnistus 2020"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis import model
from eis.model import const
import eis.lib.helpers as helpers
from .tunnistus_r_riigieksam2014 import tulemus_rida

def get_doctemplate(output):
    doc = SimpleDocTemplate(output, 
                            leftMargin=14*mm,
                            rightMargin=11*mm,
                            topMargin=0*mm,
                            bottomMargin=1*mm)
    return doc

def generate(story, tunnistusenr, valjastamisaeg, nimi, kasutaja, sessioon, q_sooritajad, sooritaja1):
    # riigieksami tunnistuse korral on parameeter "sooritaja" alati None
    N10 = ParagraphStyle(name='N10',
                         fontName='Times-Roman',
                         fontSize=10,
                         leading=16)
    N12 = ParagraphStyle(name='N12',
                         fontName='Times-Roman',
                         fontSize=12,
                         leading=15)
    NC12 = ParagraphStyle(name='NC12',
                          fontName='Times-Roman',
                          fontSize=12,
                          leading=15,
                          alignment=TA_CENTER)
    NB12 = ParagraphStyle(name='NB12',
                          fontName='Times-Bold',
                          fontSize=12,
                          leading=18)
    NB18 = ParagraphStyle(name='NB18',
                          fontName='Times-Bold',
                          fontSize=18,
                          leading=22)
    NBC12 = ParagraphStyle(name='NBC12',
                           fontName='Times-Bold',
                           fontSize=12,
                           alignment=TA_CENTER,
                           leading=18)

    S1 = ParagraphStyle(name='S',
                        fontName='Times-Roman',
                        fontSize=15,
                        leading=21,
                        alignment=TA_CENTER)
    S2 = ParagraphStyle(name='S',
                        fontName='Times-Bold',
                        fontSize=26,
                        leading=32,
                        spaceBefore=3,
                        alignment=TA_CENTER)

    story.append(Paragraph('EESTI VABARIIK', S1))

    fn_img = os.path.join(IMAGES_DIR,  'eestivapp.jpg')
    story.append(Image(fn_img, width=48, height=48))

    story.append(Paragraph('RIIGIEKSAMITUNNISTUS', S2))
    story.append(Spacer(20*mm, 5*mm))

    story.append(Paragraph('Nr: %s' % tunnistusenr, NBC12))
    story.append(Spacer(20*mm,20*mm))

    story.append(Paragraph('Selle tunnistuse omanik %s' % nimi.upper(), N12))
    story.append(Spacer(20*mm, 5*mm))

    story.append(Paragraph('isikukood %s' % kasutaja.isikukood, N12))
    story.append(Spacer(20*mm, 5*mm))

    story.append(Paragraph('sooritas järgmised riigieksamid:', N12))
    story.append(Spacer(20*mm, 5*mm))

    def get_kpv(sooritaja_id):
        "Leiame testi kuupäeva. Kui toimub mitmel päeval, siis kasutame kirjaliku osa kuupäeva."
        algus = None
        q_kpv = model.SessionR.query(model.Sooritus.algus, model.Testiosa.vastvorm_kood).\
                join(model.Sooritus.testiosa).\
                filter(model.Sooritus.sooritaja_id==sooritaja_id)
        for algus, vastvorm_kood in q_kpv.all():
            if vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_KP):
                break
        return algus
    
    # eksamitulemuste loetelu tabel

    # sordime sooritused ainete kindlas järjekorras,
    # et inglise keel jääks viimaseks
    jrk = (const.AINE_ET, const.AINE_ET2, const.AINE_M, const.AINE_EN)
    eksamid = sorted(q_sooritajad.all(),
                     key=lambda r: r[1].aine_kood in jrk and jrk.index(r[1].aine_kood) + 1 or 0)

    #story.append(Paragraph(u'õ', NB11))
    
    # paigutame sooritused tabelisse
    data = [[Paragraph('Kuupäev', NB11),
             Paragraph('Õppeaine', NB11),
             Paragraph('Tulemus / Maksimum', NB11)]]
    merge = []
    ingl_tase_kood = None # saavutatud inglise keele taseme kood
    iOK = False # kas on mõni individuaalse õppekavaga aine

    for sooritaja, test in eksamid:
        kpv, aine_nimi, tulemus, r_iOK, ingl_tase_kood = tulemus_rida(sooritaja, test, ingl_tase_kood)
        if r_iOK:
            iOK = True
        data.append((Paragraph(kpv, N11),
                     Paragraph(aine_nimi, N11),
                     Paragraph(tulemus, N11)))

        if test.aine_kood == const.AINE_ET2:
            # Eesti keel teise keelena korral kuvatakse loetelu vabastatud osaoskustest
            vabastatud = []
            for osasooritus, osa, sooritus in sooritaja.get_osasooritused():
                if osasooritus.staatus == const.S_STAATUS_VABASTATUD:
                    vabastatud.insert(0, osa.nimi.lower())
            if vabastatud:
                buf1 = '' # nimetav
                buf2 = '' # seestytlev
                sep = ''
                for nimi in vabastatud:
                    buf1 = nimi + sep + buf1
                    if buf2 is not None:
                        # kui kõik osad on ...mine lõpuga, siis kasutame seestytlevat
                        if nimi.endswith('mine'):
                            buf2 = nimi[:-2] + 'sosast' + sep + buf2
                        else:
                            buf2 = None
                    if sep:
                        sep = ', '
                    else:
                        sep = ' ja '
                if buf2 is not None:
                    # kõik osad lõpevad ...mine
                    buf = 'Vabastatud ' + buf2
                elif len(vabastatud) == 1:
                    # ei kääna, yks osa
                    buf = 'Vabastatud osast: ' + buf1
                else:
                    # ei kääna, mitu osa
                    buf = 'Vabastatud osadest: ' + buf1
                merge.append(len(data))
                data.append((Paragraph(buf, NR11), '', ''))

        elif test.aine_kood == const.AINE_EN:
            # inglise keele korral kuvatakse osaoskused
            for osasooritus, osa, sooritus in sooritaja.get_osasooritused():
                if osasooritus.staatus == const.S_STAATUS_VABASTATUD:
                    tulemus = '%s vabastatud' % (osa.nimi)
                elif osasooritus.staatus == const.S_STAATUS_TEHTUD:
                    tulemus = '%s %s%%' % (osa.nimi, helpers.fstr(osasooritus.tulemus_protsent, 2))
                elif osasooritus.staatus == const.S_STAATUS_PUUDUS:
                    tulemus = '%s %s%%' % (osa.nimi, '0')  
                else:
                    tulemus = osa.nimi
                taand = '&nbsp;' * 13
                data.append(('', '', Paragraph(taand + tulemus, N11)))
                
            buf = 'Inglise keele riigieksami terviktööst moodustab kirjutamisosa 25%, kuulamisosa 25%, lugemisosa 30%, suuline osa 20%.'
            merge.append(len(data))
            data.append((Paragraph(buf, N), '', ''))
                

    style = []
    for n in merge:
        style.append(('SPAN', (0, n), (-1, n)))
    TS = TableStyle(style)

    story.append(Table(data, 
                       colWidths=(30*mm, 90*mm, 61*mm),
                       style=TS,
                       repeatRows=1))


    if ingl_tase_kood:
        desc = {const.KEELETASE_A2:
                """A2-tasemel keelekasutaja mõistab lauseid ja sageli kasutatavaid väljendeid, mis seostuvad talle oluliste valdkondadega (näiteks info enda ja pere kohta, sisseostude tegemine, kodukoht, töö). Ta tuleb toime igapäevastes suhtlusolukordades, mis nõuavad otsest ja lihtsat infovahetust tuttavatel rutiinsetel teemadel, oskab lihtsate fraaside ja lausete abil kirjeldada oma perekonda, teisi inimesi ja elutingimusi ning väljendada oma vajadusi.""",
                const.KEELETASE_B1:
                """B1-tasemel keelekasutaja mõistab kõike olulist endale tuttaval teemal, nagu töö, kool, vaba aeg või muu, saab enamasti hakkama välisriigis, kus vastavat keelt räägitakse, oskab koostada lihtsat teksti tuttaval või enda jaoks huvipakkuval teemal, oskab kirjeldada kogemusi, sündmusi, unistusi ja eesmärke ning lühidalt põhjendada-selgitada oma seisukohti ja plaane.""",
                const.KEELETASE_B2:
                """B2-tasemel keelekasutaja mõistab keerukate abstraktsel või konkreetsel teemal tekstide ning erialase mõttevahetuse tuuma, suudab spontaanselt ja ladusalt vestelda sama keele emakeelse kõnelejaga, oskab paljudel teemadel luua selget, üksikasjalikku teksti ning selgitada oma vaatenurka, kaaluda kõnealuste seisukohtade tugevaid ja nõrku külgi.""",
                const.KEELETASE_C1:
                """C1-tasemel keelekasutaja mõistab pikki ja keerukaid tekste, tabab ka varjatud tähendust, oskab end spontaanselt ja ladusalt mõistetavaks teha, väljendeid eriti otsimata, oskab kasutada keelt paindlikult ja tulemuslikult nii avalikes, õpi- kui ka tööolukordades, oskab luua selget, loogilist, üksikasjalikku teksti keerukatel teemadel, kasutades sidusvahendeid ja sidusust loovaid võtteid.""",
                }
        buf = desc.get(ingl_tase_kood)
        if buf:
            story.append(Paragraph(buf, NI))


    if iOK:
        story.append(Spacer(5*mm, 35*mm))
        story.append(Paragraph('*Vastavalt gümnaasiumi õppekava <b>§ 13 lõikele 2</b> võib gümnaasium teha muudatusi õpilase taotletavates õpitulemustes. Kui muudatuste või kohandustega kaasneb riikliku või kooli õppekavaga võrreldes nädalakoormuse või õppe intensiivsuse oluline kasv või kahanemine, tuleb muudatuste rakendamiseks koostada individuaalne õppekava (IÕK). Kooli taotlusel koostatakse õpilasele tema IÕK-st lähtuv riigieksamitöö.', S))

    story.append(PageBreak())

    story.append(Spacer(5*mm, 9*mm))

    buf_et = """Käesoleva tunnistuse väljaandmise ajal ei olnud  riigieksamite sooritamine gümnaasiumis lõpetamise tingimuseks. Soovi korral võis vabatahtlikult sooritada eesti keele / eesti keele kui  teise keele, matemaatika ja rahvusvaheliselt tunnustatud võõrkeele eksami.  

Eesti keele teise keelena eksamil vähemalt 60% maksimumtulemusest saavutanutele on väljastatud eesti keele B2-taseme tunnistus. 

Matemaatikas sai sooritada kas kitsa matemaatika (kaheksa 35-tunnist kursust) või laia matemaatika (neliteist 35-tunnist kursust) riigieksami.  

Võõrkeeles sai sooritada rahvusvaheliselt tunnustatud võõrkeeleeksami inglise, prantsuse, saksa või vene keeles.  

Inglise, prantsuse, saksa ja vene keeles sai sooritada riigi korraldatud eksamina järgmised rahvusvaheliselt tunnustatud eksamid:  
<u><b>inglise keel</b></u>: <i>Cambridge English: C1 Advanced (CAE)</i>; <u><b>prantsuse keel</b></u>: <i>Diplôme d'études en langue française B1, Diplôme d'études en langue française B2</i>; <u><b>saksa keel</b></u>: <i>Goethe-Zertifikat B1, Goethe-Zertifikat B2, Deutsches Sprachdiplom II B2, Deutsches Sprachdiplom II C1, Deutschprufung der Allgemeinen deutschen Hochschulreife</i>; <u><b>vene keel</b></u>: <i>Тест по русскому языку как иностранному B1, Тест по русскому языку как иностранному B2</i>. 
Eksaminandile väljastatakse rahvusvaheline tasemetunnistus või teade eksamitulemustega. 

Lisaks tunnustab Eesti Vabariik võõrkeele riigieksamit asendava eksamina järgmiste rahvusvaheliste eksamite sooritamist:
<u><b>inglise keel</b></u>: <i>Cambridge English: B1 Preliminary (PET); Cambridge English: B2 First (FCE); Cambridge English: C1 Advanced (CAE); Cambridge English: C2 Proficiency (CPE); The International English Language Testing System (IELTS); Test of English as a Foreign Language (TOEFL) iBT; Pearson Test of English General (PTE General)</i>; <u><b>prantsuse keel</b></u>: <i>Diplôme approfondi en langue française (DALF C1)</i>; <u><b>saksa keel</b></u>: <i>Goethe-Zertifikat C1, Goethe-Zertifikat C2, TestDaf (TDN3), TestDaF (TDN4), TestDaF (TDN5); Osterreichisches Sprachdiplom Zertifikat B1, Osterreichisches Sprachdiplom B2 Mittelstufe Deutsch, Osterreichisches Sprachdiplom C1 Oberstufe Deutsch; Deutsches Sprachdiplom I B1</i>.

At the time of issuing the present certificate, it was not mandatory to take state examinations in order to graduate from upper secondary school. Students had the option of voluntarily taking Estonian/Estonian as a second language, mathematics and internationally recognised foreign language examinations.  
 
Examinees who have achieved at least 60% of the maximum result at the Estonian as a second language examination have been issued a level B2 certificate.  
  
In mathematics, it was possible to take a state examination in narrow mathematics (eight 35-hour courses) or broad mathematics (fourteen 35-hour courses). 
  
In a foreign language, it was possible to take an internationally recognised foreign language examination in English, French, German or Russian. 
<u><b>English</b></u>: <i>Cambridge English: C1 Advanced (CAE)</i>; <u><b>French</b></u>: <i>Diplôme d'études en langue française B1, Diplôme d'études en langue française B2</i>; <u><b>German</b></u>: <i>Goethe-Zertifikat B1, Goethe- Zertifikat B2, Deutsches Sprachdiplom II B2,Deutsches Sprachdiplom II C1, Deutschprufung der Allgemeinen deutschen Hochschulreife</i>; <u><b>Russian</b></u>: <i>Тест по русскому языку как иностранному B1, Тест по русскому языку как иностранному B2</i>.  

<i>An international language level certificate or a notice of examination results will be issued for an examinee.</i>  
  
In addition to that, the Republic of Estonia recognises the following international examinations as replacements for the state examination in a foreign language:  
<u><b>English</b></u>: <i>Cambridge English: B1 Preliminary (PET); Cambridge English: B2 First (FCE); Cambridge English: C1 Advanced (CAE); Cambridge English: C2 Proficiency (CPE); The International English Language Testing System (IELTS); Test of English as a Foreign Language (TOEFL) iBT; Pearson Test of English General (PTE General)</i>; <u><b>French</b></u>: <i>Diplôme approfondi en langue française (DALF C1)</i>; <u><b>German</b></u>: <i>Goethe-Zertifikat C1, Goethe-Zertifikat C2, TestDaF (TDN3), TestDaF (TDN4), TestDaF (TDN5); Osterreichisches Sprachdiplom Zertifikat B1, Osterreichisches Sprachdiplom B2 Mittelstufe Deutsch, Osterreichisches Sprachdiplom C1 Oberstufe Deutsch; Deutsches Sprachdiplom I B1</i>."""

    MJ = ParagraphStyle(name='NormalJustified',
                        fontName='Times-Roman',
                        fontSize=10,
                        leading=14,
                        spaceBefore=1,
                        spaceAfter=1,
                        alignment=TA_JUSTIFY)
    for line in buf_et.splitlines():
        if not line.strip():
            story.append(Spacer(2*mm, 2*mm))
        else:
            story.append(Paragraph(line, MJ))
    
    story.append(PageBreak())

def first_page(canvas, doc, pdoc):
    "Esimese lehekülje jalus"
    canvas.saveState()
    canvas.setFont('Times-Roman', 12)

    canvas.drawString(15*mm, 48*mm, 'Tallinn %s' % (helpers.str_from_date(pdoc.valjastamisaeg)))
    canvas.drawString(15*mm, 43*mm, 'Allkirjastatud digitaalselt')
    canvas.drawString(15*mm, 30*mm, 'Selgitused teisel leheküljel')    
    canvas.drawString(22*mm, 17*mm, 'TUNNISTUS ON KEHTIV KOOS KESKHARIDUST TÕENDAVA LÕPUTUNNISTUSEGA.')
    canvas.setFont('Times-Roman', 11)
    canvas.drawString(101*mm, 12*mm, '1(2)')    
    canvas.restoreState()

def later_pages(canvas, doc, pdoc):
    "Teise ja järgmiste lehekülgede jalus"
    canvas.saveState()
    canvas.setFont('Times-Roman', 11)
    canvas.drawString(55*mm, 17*mm, 'Riigieksamitunnistus Nr: %s Tallinn, %s' % (pdoc.tunnistusenr, helpers.str_from_date(pdoc.valjastamisaeg)))
    canvas.drawString(101*mm, 12*mm, '2(2)')    
    canvas.restoreState()

