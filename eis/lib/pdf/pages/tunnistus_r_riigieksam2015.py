# -*- coding: utf-8 -*- 
"Riigieksamitunnistus 2015-2016"

from .pdfutils import *
from .stylesheet import *
from datetime import date
from eis import model
from eis.model import const
import eis.lib.helpers as helpers
from .tunnistus_r_riigieksam2014 import tulemus_rida

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

        elif test.aine_kood == const.AINE_M:
            # matemaatika korral kuvatakse yhisosa eraldi real
            if test.yhisosa_max_pallid:
                if sooritaja.staatus == const.S_STAATUS_TEHTUD:
                    pallid = sooritaja.yhisosa_pallid
                else:
                    pallid = 0
                max_pallid = test.yhisosa_max_pallid
                tulemus = '%s punkti / %s punkti' % (helpers.fstr(pallid, 2), helpers.fstr(max_pallid, 2))
                data.append(('',
                             Paragraph('sh kitsa ja laia matemaatika ühisosa', N11),
                             Paragraph(tulemus, N11)))

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

    buf = """Käesoleva tunnistuse väljaandmise ajal on gümnaasiumi lõpetamiseks kohustuslikud riigieksamid eesti keel / eesti keel teise keelena, matemaatika ja võõrkeel. Eesti keele teise keelena eksamil vähemalt 60% maksimumtulemusest saavutanutele on väljastatud eesti keele B2-taseme tunnistus. Eesti keele C1-taseme tunnistuse omanikud on eesti keele teise keelena riigieksamist vabastatud.
Matemaatikas võib õpilane sooritada kas kitsa matemaatika (8 35-tunnist kursust) või laia matemaatika (14 35-tunnist kursust) riigieksami.
Võõrkeeles võib õpilane sooritada inglise keele riigieksami või rahvusvaheliselt tunnustatud võõrkeeleeksami inglise, prantsuse, saksa või vene keeles. Riiklik õppekava eeldab gümnaasiumi lõpuks võõrkeeles B-taseme omandamist.
Prantsuse, saksa ja vene keele riigieksam on asendatud järgmiste rahvusvaheliste eksamitega: <u>prantsuse keel</u> <i>DELF B1</i> ja <i>B2</i>; <u>saksa keel</u> <i>Goethe-Zertifikat B1</i>, <i>Goethe-Zertifikat B2</i>, <i>Deutsches Sprachdiplom II B2, Deutsches Sprachdiplom II C1</i>, <i>Deutschprüfung der Allgemeinen deutschen Hochschulreife</i>; <u>vene keel</u>: <i>Тест по русскому языку как иностранному</i> B1, <i>Тест по русскому языку как иностранному</i> B2. Eksaminandile väljastatakse rahvusvaheline tasemetunnistus või teade eksamitulemustega.
Lisaks tunnustab Eesti Vabariik võõrkeele riigieksamit asendava eksamina järgmiste rahvusvaheliste eksamite sooritamist vähemalt B1-tasemel:
<u>Inglise keel:</u> <i>Preliminary English Test (PET)</i>, <i>First Certificate in English (FCE)</i>, <i>Certificate in Advanced English (CAE)</i>, <i>Certificate of Proficiency in English (CPE)</i>, <i>International English Language Testing System (IELTS)</i> (min 4,0 p), <i>Test of English as a Foreign Language (TOEFL) iBT</i> (min 57 p), <i>Pearson Test of English General (PTE General)</i> (min Level 2); <u>prantsuse keel:</u> <i>DALF C1</i>; <u>saksa keel:</u> <i>Goethe-Zertifikat</i> C1, <i>Goethe-Zertifikat</i> C2, <i>TestDaF (TDN3), TestDaF (TDN4), TestDaF (TDN5); Österreichisches Sprachdiplom Zertifikat B1, Österreichisches Sprachdiplom B2 Mittelstufe Deutsch, Österreichisches Sprachdiplom C1 Oberstufe Deutsch; Deutsches Sprachdiplom I B1.</i>
<i>At the time of issuing the present certificate, the mandatory examinations for graduating from upper secondary school are Estonian/Estonian as a second language, mathematics and foreign language. Examinees who have achieved at least 60% of the maximum result at the Estonian as a second language examination shall be issued a level B2 certificate. Persons who have obtained a level C1 certificate in Estonian are exempt from the Estonian as a second language state examination.</i>
<i>In mathematics a student may either take a state examination in narrow mathematics (8 35-hour courses) or broad mathematics (14 35-hour courses).</i>
<i>In foreign language a student may take a state examination in English or an internationally acknowledged foreign language examination in English, French, German or Russian. The national curriculum assumes that level B is obtained in a foreign language by the end of upper secondary school.</i>
<i>State examinations in French, German and Russian have been replaced with the following international examinations:</i>
<i><u>French:</u> DELF B1 and B2; <u>German:</u> Goethe-Zertifikat B1, Goethe-Zertifikat B2, Deutsches Sprachdiplom II B2, Deutsches Sprachdiplom II C1, Deutschprüfung der Allgemeinen deutschen Hochschulreife; <u>Russian</u>: Тест по русскому языку как иностранному B1, Тест по русскому языку как иностранному B2. An international language level certificate or a notice of examination results will be issued for an examinee.</i>
<i>As a replacement for the foreign language state examination, the Republic of Estonia also recognises the certificates of the following international examinations at least at level B1:</i>
<i><u>English:</u> Preliminary English Test (PET), First Certificate in English (FCE), Certificate in Advanced English (CAE), Certificate of Proficiency in English (CPE), International English Language Testing System (IELTS) (min 4.0 p), Test of English as a Foreign Language (TOEFL) iBT (min 57 p), Pearson Test of English General (PTE General)</i>(min Level 2);<i> <u>French</u>: DALF C1; <u>German:</u> Goethe-Zertifikat C1, Goethe-Zertifikat C2, TestDaF (TDN3), TestDaF (TDN4), TestDaF (TDN5); Österreichisches Sprachdiplom Zertifikat B1, Österreichisches Sprachdiplom B2 Mittelstufe Deutsch, Österreichisches Sprachdiplom C1 Oberstufe Deutsch; Deutsches Sprachdiplom I B1.</i>"""

    MJ = ParagraphStyle(name='NormalJustified',
                        parent=M,
                        spaceBefore=6,
                        alignment=TA_JUSTIFY)
    for line in buf.splitlines():
        story.append(Paragraph(line, MJ))
        
    story.append(PageBreak())

def first_page(canvas, doc, pdoc):
    "Esimese lehekülje jalus"
    canvas.saveState()
    canvas.setFont('Times-Roman', 12)

    canvas.drawString(15*mm, 50*mm, 'Tallinnas %s' % (helpers.str_from_date(pdoc.valjastamisaeg)))
    canvas.drawString(15*mm, 45*mm, 'Allkirjastatud digitaalselt')
    canvas.drawString(22*mm, 19*mm, 'TUNNISTUS ON KEHTIV KOOS KESKHARIDUST TÕENDAVA LÕPUTUNNISTUSEGA.')
    canvas.restoreState()

def later_pages(canvas, doc, pdoc):
    "Teise ja järgmiste lehekülgede jalus"
    return
    #canvas.saveState()
    #canvas.setFont('Times-Roman', 12)
    #canvas.drawString(15*mm, 280*mm, u'Riigieksamitunnistuse nr %s lisa' % pdoc.tunnistusenr)
    #canvas.restoreState()

