Subject: Sooritusteade
Lp ${isik_nimi}

<b>Teatame Teile, et olete ${sooritaja.algus.strftime('%d.%m.%Y')} edukalt sooritanud Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse tundmise eksami.

Teie eksamitulemus on ${int(round(sooritaja.pallid))} punkti ${int(round(sooritaja.max_pallid))}-st.</b>

% if tunnistus:
<b>TEIE EESTI VABARIIGI PÕHISEADUSE JA KODAKONDSUSE SEADUSE TUNDMISE TUNNISTUSE NUMBER ON ${tunnistus.tunnistusenr}.</b>
% endif

Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse tundmise tunnistus on elektrooniline. Paberil tunnistusi ei väljastata.

Te saate oma tunnistust soovi korral vaadata, alla laadida ning välja trükkida riigiportaalis <a href="https://www.eesti.ee">www.eesti.ee</a>, kasutades teenust "EV Põhiseaduse ja Kodakondsuse seaduse tundmise eksami e-tunnistuse allalaadimine".

E-tunnistus on kättesaadav ka Eksamite Infosüsteemis (EIS) <a href="https://eis.ekk.edu.ee/eis">eis.ekk.edu.ee</a>.

Portaali saate siseneda ID-kaardi, Mobiil-ID või Smart-ID abil. Juhised leiab riigiportaalist vastava teenuse juurest või <a href="https://www.harno.ee">www.harno.ee</a>. Lisainfot saate tel 7350 500 ja EISi kasutajatoest: e-post <a href="mailto:eis@tugi.edu.ee">eis@tugi.edu.ee</a>, tel 7302 135 (E-R 9-17).

NB! Elektroonilise tunnistuse allalaadimine ja välja trükkimine ei ole kohustuslik. Ametiasutuste ja -isikutega suhtlemisel piisab, kui edastate oma isikukoodi ja tunnistuse unikaalse numbri.

Teie poolt sooritatud Eesti Vabariigi Põhiseaduse ja Kodakondsuse seaduse tundmise eksami tulemust on võimalik vaidlustada 30 päeva jooksul pärast selle teatavaks tegemist esitades Haridus- ja Teadusministeeriumile vaide oma eksamitulemuse läbivaatamiseks.
% if taiendavinfo:

${taiendavinfo}
% endif

<hr/>

Э-свидетельство о сдаче экзамена на знание Конституции Эстонской Республики и Закона о гражданстве стало электронным. Бумажные свидетельства больше не выдаются.

При желании Вы сможете посмотреть свое свидетельство, скачать его на свой компьютер и распечатать, воспользовавшись услугой государственного портала <a href="https://www.eesti.ee">www.eesti.ee</a> „Скачивание эсвидетельств о сдаче экзамена на знание Конституции Эстонской Республики и Закона о гражданстве“ или Eksamite Infosüsteem (EIS) <a href="https://eis.ekk.edu.ee">eis.ekk.edu.ee</a>.

На портал можно входить с помощью ID-карты, Mobiil ID или Smart ID. Технические инструкции можно найти рядом с соответствующей услугой или на www.harno.ee; э-почта eis@tugi.edu.ee; тел 7302 135 (Пн-Пт 9-17).

NB! Скачивание и распечатка электронного свидетельства при ходатайстве о гражданстве не являются обязательными.

% if tunnistus:
<b>НОМЕР ВАШЕГО СВИДЕТЕЛЬСТВА О СДАЧЕ ЭКЗАМЕНА НА ЗНАНИЕ КОНСТИТУЦИИ ЭСТОНСКОЙ РЕСПУБЛИКИ И ЗАКОНА О ГРАЖДАНСТВЕ ${tunnistus.tunnistusenr}</b>
% endif

Haridus- ja Noorteamet
Lõõtsa 4, 11415 Tallinn

<%include file="footer.mako"/>
