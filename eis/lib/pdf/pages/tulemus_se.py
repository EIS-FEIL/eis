"Seaduse tundmise eksami tulemuse teavitus"

from .pdfutils import *
from .stylesheet import *
from datetime import date
import eis.model as model
from eis.model import const, sa
import eis.lib.helpers as h
from .aadress import aadressikast

def generate(story, sooritaja, taiendavinfo):

    story.append(Paragraph('Haridus- ja Noorteamet', LBC))
    story.append(HRFlowable(width="80%", thickness=0.5, spaceBefore=1, spaceAfter=1, hAlign='CENTER', vAlign='CENTER', color=colors.black))
    story.append(Paragraph('Lõõtsa 4, 11415 Tallinn, tel 7350 500', SBC))
    story.append(Spacer(3*mm,3*mm))

    kasutaja = sooritaja.kasutaja
    story.append(aadressikast(kasutaja))
    story.append(Spacer(15*mm, 15*mm))

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

    if sooritaja.tulemus_piisav:
        gen_sooritusteade(story, sooritaja, N, NB)
    else:
        gen_mittesooritusteade(story, sooritaja, N, NB)
    
    if taiendavinfo:
        story.append(Spacer(2*mm, 2*mm))
        story.append(Paragraph(taiendavinfo, N))         
    story.append(PageBreak())

def gen_sooritusteade(story, sooritaja, N, NB):
    test = sooritaja.test

    buf = 'Teatame Teile, et olete %s edukalt sooritanud Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse tundmise eksami.' % h.str_from_date(sooritaja.algus)
    story.append(Paragraph(buf, NB))
    
    buf = 'Teie eksamitulemus on %s punkti %s-st.' % (int(round(sooritaja.pallid)), int(round(sooritaja.max_pallid)))
    story.append(Paragraph(buf, NB))

    tunnistus = model.SessionR.query(model.Tunnistus).\
                join(model.Tunnistus.testitunnistused).\
                filter(model.Tunnistus.staatus>const.N_STAATUS_KEHTETU).\
                filter(model.Testitunnistus.sooritaja_id==sooritaja.id).\
                first()
    if tunnistus:
        buf = 'TEIE EESTI VABARIIGI PÕHISEADUSE JA KODAKONDSUSE SEADUSE TUNDMISE TUNNISTUSE NUMBER ON %s.' % tunnistus.tunnistusenr
        story.append(Paragraph(buf, NB))
    
    buf = 'Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse tundmise tunnistus on elektrooniline. Paberil tunnistusi ei väljastata.'
    story.append(Paragraph(buf, N))

    buf = 'Te saate oma tunnistust soovi korral vaadata, alla laadida ning välja trükkida riigiportaalis www.eesti.ee, kasutades teenust "EV Põhiseaduse ja Kodakondsuse seaduse tundmise eksami e-tunnistuse allalaadimine". '
    story.append(Paragraph(buf, N))

    buf = 'E-tunnistus on kättesaadav ka Eksamite Infosüsteemis (EIS) eis.ekk.edu.ee.'
    story.append(Paragraph(buf, N))
    
    buf = 'Portaali saate siseneda ID-kaardi, Mobiil-ID või Smart-ID abil. Juhised leiab riigiportaalist vastava teenuse juurest või www.harno.ee. Lisainfot saate tel 7350 500 ja EISi kasutajatoest: e-post eis@tugi.edu.ee, tel 7302 135 (E-R 9-17).'
    story.append(Paragraph(buf, N))

    buf = 'NB! Elektroonilise tunnistuse allalaadimine ja välja trükkimine ei ole kohustuslik. Ametiasutuste ja -isikutega suhtlemisel piisab, kui edastate oma isikukoodi ja tunnistuse unikaalse numbri.'
    story.append(Paragraph(buf, N))

    buf = 'Teie poolt sooritatud Eesti Vabariigi Põhiseaduse ja Kodakondsuse seaduse tundmise eksami tulemust on võimalik vaidlustada 30 päeva jooksul pärast selle teatavaks tegemist, esitades Haridus- ja Teadusministeeriumile vaide oma eksamitulemuse läbivaatamiseks.'
    story.append(Paragraph(buf, N))

    story.append(HRFlowable(width="100%", thickness=0.5, spaceBefore=1, spaceAfter=1, color=colors.black))    

    buf = 'Э-свидетельство о сдаче экзамена на уровень владения эстонским языком стало электронным. Бумажные свидетельства больше не выдаются.'
    story.append(Paragraph(buf, N))

    buf = 'При желании Вы сможете посмотреть свое свидетельство, скачать его на свой компьютер и распечатать, воспользовавшись услугой государственного портала www.eesti.ee „Скачивание э-свидетельств о сдаче экзамена на знание Конституции Эстонской Республики и Закона о гражданстве“ или Eksamite Infosüsteem (EIS) eis.ekk.edu.ee.'
    story.append(Paragraph(buf, N))

    buf = 'На портал можно входить с помощью ID-карты, Mobiil ID или Smart ID. Технические инструкции можно найти рядом с соответствующей услугой или на www.harno.ee; э-почта eis@tugi.edu.ee; тел 7302 135 (Пн-Пт 9-17).'
    story.append(Paragraph(buf, N))

    buf = 'NB! Скачивание и распечатка электронного свидетельства при ходатайстве о гражданстве не являются обязательными.'
    story.append(Paragraph(buf, N))

    if tunnistus:
        buf = 'НОМЕР ВАШЕГО СВИДЕТЕЛЬСТВА О СДАЧЕ ЭКЗАМЕНА НА ЗНАНИЕ КОНСТИТУЦИИ ЭСТОНСКОЙ РЕСПУБЛИКИ И ЗАКОНА О ГРАЖДАНСТВЕ %s.' % tunnistus.tunnistusenr
        story.append(Paragraph(buf, NB))

def gen_mittesooritusteade(story, sooritaja, N, NB):

    test = sooritaja.test
    buf = 'Käesolevaga teatame, et Te ei sooritanud %s Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse tundmise eksamit.' % (h.str_from_date(sooritaja.algus))
    story.append(Paragraph(buf, NB))
    
    buf = 'Teie eksamitulemus on %s punkti vajalikust %s-st.' % (int(round(sooritaja.pallid)), int(round(test.lavi_pr*sooritaja.max_pallid/100.)))
    story.append(Paragraph(buf, NB))

    story.append(HRFlowable(width="100%", thickness=0.5, spaceBefore=1, spaceAfter=1, color=colors.black))    

    buf = 'Kui soovite registreeruda korduseksamile, tuleb Teil esitada uus avaldus Haridus- ja Noorteametile.'
    story.append(Paragraph(buf, N))

    story.append(Spacer(10*mm, 10*mm))

    buf = 'Edu edaspidiseks!'
    story.append(Paragraph(buf, N))

    story.append(Spacer(10*mm, 10*mm))

    buf = 'Haridus- ja Noorteamet'
    story.append(Paragraph(buf, N))
