"Tasemeeksami tulemuse teavitus"

from .pdfutils import *
from .stylesheet import *
from datetime import date
import eis.model as model
from eis.model import const, sa
import eis.lib.helpers as h
from .aadress import aadressikast

def generate(story1, sooritaja, taiendavinfo):
    story = []
    story.append(Paragraph('Haridus- ja Noorteamet', LBC))
    story.append(HRFlowable(width="80%", thickness=0.5, spaceBefore=1, spaceAfter=1, hAlign='CENTER', vAlign='CENTER', color=colors.black))
    story.append(Paragraph('Lõõtsa 4, 11415 Tallinn, tel 7350 500', SBC))
    story.append(Spacer(3*mm,3*mm))

    kasutaja = sooritaja.kasutaja
    story.append(aadressikast(kasutaja))
    story.append(Spacer(10*mm, 10*mm))

    N = ParagraphStyle(name='TimesRoman',
                       fontName='Times-Roman',
                       fontSize=10,
                       leading=11,
                       spaceBefore=7,
                       spaceAfter=7)
    NB = ParagraphStyle(name='TimesBold',
                       fontName='Times-Bold',
                       fontSize=10,
                       leading=11,
                       spaceBefore=7,
                       spaceAfter=7)

    test = sooritaja.test
    keeletase_nimi = test.keeletase_nimi
    if keeletase_nimi[-1].isdigit():
        # A2,B1,B2,C1
        taseme = '%s-taseme' % keeletase_nimi
    else:
        # alg, kesk, kõrg
        taseme = '%staseme' % keeletase_nimi

    if sooritaja.tulemus_piisav:
        gen_sooritusteade(story, sooritaja, taseme, N, NB)
    else:
        gen_mittesooritusteade(story, sooritaja, taseme, N, NB)
    
    if taiendavinfo:
        story.append(Spacer(2*mm, 2*mm))
        story.append(Paragraph(taiendavinfo, N))      
    story.append(PageBreak())
    story1.extend(avoid_too_large(story))
    
def gen_sooritusteade(story, sooritaja, taseme, N, NB):

    story.append(Paragraph('SOORITUSTEADE', MBC))

    buf = 'Teatame, et Te sooritasite %s %s eksami. Teie eksamitulemus on %s%% võimalikust punktisummast.' % \
        (h.str_from_date(sooritaja.algus),
         taseme,
         int(round(sooritaja.tulemus_protsent)))
    story.append(Paragraph(buf, NB))
    
    pallid, vahemikud = _pallid_vahemikud(sooritaja)

    buf = 'Teie keeleoskusele anti järgmine hinnang (protsentides võimalikust punktisummast): '
    buf += ', '.join(vahemikud) + '.'
    story.append(Paragraph(buf, N))

    tunnistus = model.SessionR.query(model.Tunnistus).\
                join(model.Tunnistus.testitunnistused).\
                filter(model.Tunnistus.staatus>const.N_STAATUS_KEHTETU).\
                filter(model.Testitunnistus.sooritaja_id==sooritaja.id).\
                first()
    if not tunnistus:
        kasutaja = sooritaja.kasutaja
        raise Exception(_("Sooritaja {ik} tunnistus puudub!").format(ik=kasutaja.isikukood))
    
    buf = 'TEIE EESTI KEELE OSKUSE TUNNISTUSE NUMBER ON %s.' % (tunnistus.tunnistusenr)
    story.append(Paragraph(buf, NB))

    buf = 'Eesti keele oskuse tunnistus on elektrooniline. Paberil tunnistusi ei väljastata.'
    story.append(Paragraph(buf, N))

    buf = 'Te saate oma tunnistust vaadata, alla laadida ning välja trükkida riigiportaalis www.eesti.ee, kasutades teenust "Eesti keele tasemeeksami e-tunnistuse allalaadimine". E-tunnistus on kättesaadav ka testide andmekogus (EIS) eis.ekk.edu.ee.'
    story.append(Paragraph(buf, NB))

    buf = 'Portaali saate siseneda ID-kaardi, Mobiil-ID või Smart-ID abil. Juhised leiab riigiportaalist vastava teenuse juurest või www.harno.ee. Lisainfot saate tel 7350 500 ja EISi kasutajatoest: e-post eis@tugi.edu.ee, tel 7302 135 (E-R 9-17).'
    story.append(Paragraph(buf, N))

    buf = 'NB! Elektroonilise tunnistuse allalaadimine ja väljatrükkimine ei ole kohustuslik. Keeleoskuse tõendamiseks tööandjale või ametiisikule piisab, kui edastate talle oma isikukoodi ja tunnistuse numbri.'
    story.append(Paragraph(buf, NB))

    buf = 'Eksaminandil on õigus 30 päeva jooksul pärast tasemeeksami tulemuse teatavaks tegemist esitada oma eksamitulemuse läbivaatamiseks vaie Haridus- ja Noorteameti vaidekomisjonile.  Vaide saab esitada testide andmekogus EIS: <a href="https://eis.ekk.edu.ee">eis.ekk.edu.ee</a>. NB! Vaide esitamiseks on vaja avaldus digitaalselt allkirjastada! Palun veenduge, et teil on olemas digiallkirjastamise võimalus, enne kui alustate avalduse täitmist. Täpsemalt eksamitulemuste vaidlustamise kohta on võimalik lugeda Haridus- ja Noorteameti <a href="https://harno.ee/eesti-keele-tasemeeksamid#tutvumine">kodulehelt</a>.'

    story.append(Paragraph(buf, N))

    if sooritaja.test.keeletase_kood in (const.KEELETASE_A2, const.KEELETASE_B1):
        # venekeelne osa, ainult A2 ja B1 tasemete korral
        story.append(HRFlowable(width="100%", thickness=0.5, spaceBefore=1, spaceAfter=1, color=colors.black))

        buf = 'НОМЕР ВАШЕГО СВИДЕТЕЛЬСТВА О ВЛАДЕНИИ ЭСТОНСКИМ ЯЗЫКОМ %s.' % (tunnistus.tunnistusenr)
        story.append(Paragraph(buf, NB))

        buf = 'Свидетельство о владении эстонским языком является электронным. Свидетельства на бумажном носителе не выдаются.'
        story.append(Paragraph(buf, N))
        buf = 'При желании Вы сможете посмотреть свое свидетельство, скачать его на компьютер и распечатать, воспользовавшись услугой государственного портала www.eesti.ee „Скачивание э-свидетельств об уровне владения эстонским языком.“ Э-свидетельство также доступно в Собрании данных по тестам EIS eis.ekk.edu.ee.' 
        story.append(Paragraph(buf, N))
        buf = 'На портал можно входить с помощью ID-карты, Mobiil-ID или Smart-ID. Технические инструкции можно найти на государственном портале рядом с соответствующей услугой или на www.harno.ee. Дополнительную информацию можно получить по телефону 7350 500 и через поддержку пользователя EIS по э-почте eis@tugi.edu.ee и телефону 7302 135 (Пн-Пт 9-17).'
        story.append(Paragraph(buf, N))
        buf = 'NB! Скачивание и распечатка электронного свидетельства не являются обязательными. Чтобы доказать свое знание языка работодателю или должностному лицу, достаточно предоставить им свой личный код и номер свидетельства.'
        story.append(Paragraph(buf, N))
        buf = 'Экзаменуемый имеет право в течение 30 дней после получения сведений о результатах экзамена представить возражение для пересмотра результатов экзамена в комиссию по рассмотрению возражений Департамента по делам образования и молодежи. Возражение можно подать через Собрание данных по тестам EIS: eis.ekk.edu.ee. NB! Для подачи возражения необходимо поставить цифровую подпись на заявлении! Пожалуйста, прежде чем начать заполнять заявление, убедитесь, что у вас есть возможность цифровой подписи. Подробнее об оспаривании результатов экзамена можно прочитать на сайте Департамента по делам образования и молодежи.'
        story.append(Paragraph(buf, N))

        # ingl k osa, ainult A2 ja B1 tasemete korral
        story.append(HRFlowable(width="100%", thickness=0.5, spaceBefore=1, spaceAfter=1, color=colors.black))

        buf = 'YOUR ESTONIAN LANGUAGE CERTIFICATE NUMBER IS %s.' % (tunnistus.tunnistusenr)
        story.append(Paragraph(buf, NB))

        buf = 'The Estonian language proficiency certificate is electronic. Certificates are not issued on paper. You can view, download, and print your certificate on the state portal www.eesti.ee using the service "Estonian proficiency exam e-certificate download." The e-certificate is also available in the Test Database (EIS) eis.ekk.edu.ee.'
        story.append(Paragraph(buf, N))
        buf = 'You can enter the website using an ID card, Mobile ID or Smart ID. Instructions can be found on the state portal at the corresponding service or www.harno.ee. You can get additional information by tel. 7350 500 and from the EIS user support: e-mail eis@tugi.edu.ee, tel. 7302 135 (Mon-Fri 9-17).'
        story.append(Paragraph(buf, N))
        buf = 'NB! Downloading and printing the electronic certificate is not mandatory. To prove your language skills to an employer or an official, it is enough to provide them with your personal identification number and certificate number.'
        story.append(Paragraph(buf, N))
        buf = 'The examinee has the right, within 30 days after the announcement of the results of the proficiency exam, to file a challenge with the Education and Youth Board challenge committee for the review of their examination result. Challenges can be submitted in the Test Database EIS: eis.ekk.edu.ee. NB! To submit the challenge, you need to digitally sign the form! Please make sure you have the digital signature option before you start filling out the application. You can read more about challenging exam results on the Education and Youth Board website.'
        story.append(Paragraph(buf, N))

    story.append(HRFlowable(width="100%", thickness=0.5, spaceBefore=1, spaceAfter=1, color=colors.black))
    buf = 'NB! Positiivselt sooritatud eksami korral on Teil võimalus taotleda eesti keele õppe kulude hüvitamist. Info ja tingimused: www.harno.ee.'
    story.append(Paragraph(buf, N))
    if sooritaja.test.keeletase_kood in (const.KEELETASE_A2, const.KEELETASE_B1):
        buf = 'В случае положительной сдачи экзамена, у Вас есть возможность ходатайствовать о возмещении затрат на изучение эстонского языка. Информация и условия: www.harno.ee.'
        story.append(Paragraph(buf, N))    
        buf = 'NB! In the case of a positive result, you have the opportunity to apply for compensation for the costs of learning the Estonian language. Information and conditions: www.harno.ee.'
        story.append(Paragraph(buf, N))
        
def gen_mittesooritusteade(story, sooritaja, taseme, N, NB):

    story.append(Spacer(20*mm, 20*mm))
    buf = 'Teatame, et Te ei sooritanud %s %s eksamit. Teie eksamitulemus on %s%% võimalikust punktisummast.' % \
        (h.str_from_date(sooritaja.algus),
         taseme,
         int(round(sooritaja.tulemus_protsent)))
    story.append(Paragraph(buf, NB))

    pallid, vahemikud = _pallid_vahemikud(sooritaja)

    buf = 'Teie keeleoskusele anti järgmine hinnang (protsentides võimalikust punktisummast): '
    buf += ', '.join(vahemikud) + '.'
    story.append(Paragraph(buf, N))

    buf = 'Eesti keele tasemeeksami tööga tutvumiseks tuleb esitada avaldus meie infolauda (avatud esmaspäevast reedeni kell 9.00–17.00), saata Haridus- ja Noorteameti postiaadressile Lõõtsa 4, 11415 Tallinn või digitaalselt e-posti teel aadressile <a href="mailto:info@harno.ee">info@harno.ee</a>.'
    story.append(Paragraph(buf, N))

    buf = 'Eksaminandil on õigus 30 päeva jooksul pärast tasemeeksami tulemuse teatavaks tegemist esitada oma eksamitulemuse läbivaatamiseks vaie Haridus- ja Noorteameti vaidekomisjonile.  Vaide saab esitada testide andmekogus EIS: <a href="https://eis.ekk.edu.ee">eis.ekk.edu.ee</a>. NB! Vaide esitamiseks on vaja avaldus digitaalselt allkirjastada! Palun veenduge, et teil on olemas digiallkirjastamise võimalus, enne kui alustate avalduse täitmist. Täpsemalt eksamitulemuste vaidlustamise kohta on võimalik lugeda Haridus- ja Noorteameti <a href="https://harno.ee/eesti-keele-tasemeeksamid#tutvumine">kodulehelt</a>.'
    story.append(Paragraph(buf, N))

    story.append(HRFlowable(width="100%", thickness=0.5, spaceBefore=1, spaceAfter=1, color=colors.black))
    
    buf = 'Для ознакомления с экзаменационной работой уровневого экзамена по эстонскому языку, необходимо подать заявление через информационный стол Haridus- ja Noorteamet (открыт с понедельника по пятницу с 9:00 до 17:00), либо отправив его по адресу Haridus- ja Noorteamet, Lõõtsa tn 4, 11415 Tallinn, либо отправив дигитально на электронную почту <a href="mailto:info@harno.ee">info@harno.ee</a>.'
    story.append(Paragraph(buf, N))

    buf = 'Экзаменуемый имеет право в течение 30 дней после получения сведений о результатах экзамена представить возражение для пересмотра результатов экзамена в комиссию по рассмотрению возражений Департамента по делам образования и молодежи. Возражение можно подать через Собрание данных по тестам EIS: <a href="https://eis.ekk.edu.ee">eis.ekk.edu.ee</a>. NB! Для подачи возражения необходимо поставить цифровую подпись на заявлении! Пожалуйста, прежде чем начать заполнять заявление, убедитесь, что у вас есть возможность цифровой подписи. Подробнее об оспаривании результатов экзамена можно прочитать на сайте Департамента по делам образования и молодежи.'
    story.append(Paragraph(buf, N))

    story.append(HRFlowable(width="100%", thickness=0.5, spaceBefore=1, spaceAfter=1, color=colors.black))
    
    buf = 'To review your Estonian language proficiency exam papers, you can submit an application either to our information desk (open from Monday to Friday from 9:00 a.m. to 5:00 p.m.), send it by post to the Education and Youth Board at Lõõtsa 4, 11415 Tallinn, or send it by e-mail to <a href="mailto:info@harno.ee">info@harno.ee</a>.'
    story.append(Paragraph(buf, N))
    buf = 'The examinee has the right, within 30 days after the announcement of the results of the proficiency exam, to file a challenge with the Education and Youth Board challenge committee for the review of their examination result. Challenges can be submitted in the Test Database EIS: <a href="https://eis.ekk.edu.ee">eis.ekk.edu.ee</a>. NB! To submit the challenge, you need to digitally sign the form! Please make sure you have the digital signature option before you start filling out the application. You can read more about challenging exam results on the Education and Youth Board website.'
    story.append(Paragraph(buf, N))        

def first_page(canvas, doc, pdoc):
    "Esimese lehekülje jalus"
    canvas.saveState()
    canvas.setFont('Times-Roman', 10)

    canvas.drawString(18*mm, 17*mm, 'Haridus- ja Noorteamet')
    canvas.drawString(74*mm, 17*mm, 'Lõõtsa 4, 11415 Tallinn')
    canvas.drawString(74*mm, 13*mm, 'telefon 735 0500')
    canvas.drawString(131*mm, 17*mm, 'registrikood 77001292')
    canvas.drawString(131*mm, 13*mm, 'www.harno.ee,')
    canvas.drawString(131*mm, 9*mm, 'e-post:info@harno.ee')
    canvas.restoreState()

def later_pages(canvas, doc, pdoc):
    "Teise ja järgmiste lehekülgede jalus"
    return first_page(canvas, doc, pdoc)

def _pallid_vahemikud(sooritaja):
    vahemikud = []
    pallid = []
    test = sooritaja.test
    for sooritus, osa, ylemsooritus in sooritaja.get_osasooritused():
        if sooritus and sooritus.staatus == const.S_STAATUS_TEHTUD and sooritus.pallid != None:
            n, vahemik_algus, vahemik_lopp = test.get_vahemik_by_protsent(sooritus.tulemus_protsent)
            buf = '%s %s (%d-%d%%)' % (osa.nimi.lower(),
                                        test.get_vahemiknimi_by_protsent(sooritus.tulemus_protsent),
                                        vahemik_algus,
                                        vahemik_lopp)
            vahemikud.append(buf)
            buf = '%s %d (%d-st)' % (osa.nimi.lower(), int(round(sooritus.pallid)), int(round(sooritus.max_pallid)))
            pallid.append(buf)
        elif sooritus and sooritus.staatus == const.S_STAATUS_VABASTATUD:
            vahemikud.append('%s vabastatud' % (osa.nimi.lower()))
            pallid.append('%s vabastatud' % (osa.nimi.lower()))
        elif not sooritus and ylemsooritus.staatus == const.S_STAATUS_VABASTATUD:
            vahemikud.append('%s vabastatud' % (osa.nimi.lower()))
            pallid.append('%s vabastatud' % (osa.nimi.lower()))            
    return pallid, vahemikud
