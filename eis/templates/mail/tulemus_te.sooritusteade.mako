Subject: Sooritusteade
Lp ${isik_nimi}

Sooritusteade

<b>Teatame, et Te sooritasite ${sooritaja.algus.strftime('%d.%m.%Y')} ${taseme} eksami. Teie eksamitulemus on ${int(round(sooritaja.tulemus_protsent))}% võimalikust punktisummast.</b>

Teie keeleoskusele anti järgmine hinnang (protsentides võimalikust punktisummast): ${', '.join(s_vahemikud)}.

% if tunnistus:
<b>TEIE EESTI KEELE OSKUSE TUNNISTUSE NUMBER ON ${tunnistus.tunnistusenr}.</b>
% endif

Eesti keele oskuse tunnistus on elektrooniline. Paberil tunnistusi ei väljastata.

<b>Te saate oma tunnistust vaadata, alla laadida ning välja trükkida riigiportaalis www.eesti.ee, kasutades teenust "Eesti keele tasemeeksami e-tunnistuse allalaadimine." E-tunnistus on kättesaadav ka testide andmekogus (EIS) <a href="https://eis.ekk.edu.ee/eis">eis.ekk.edu.ee</a>.</b>

Portaali saate siseneda ID-kaardi, Mobiil-ID või Smart-ID abil. Juhised leiab riigiportaalist vastava teenuse juurest või <a href="https://www.harno.ee">www.harno.ee</a>. Lisainfot saate tel 7350 500 ja EISi kasutajatoest: e-post <a href="mailto:eis@tugi.edu.ee">eis@tugi.edu.ee</a>, tel 7302 135 (E-R 9-17).

<b>NB! Elektroonilise tunnistuse allalaadimine ja väljatrükkimine ei ole kohustuslik. Keeleoskuse tõendamiseks tööandjale või ametiisikule piisab, kui edastate talle oma isikukoodi ja tunnistuse numbri.</b>

Eksaminandil on õigus 30 päeva jooksul pärast tasemeeksami tulemuse teatavaks tegemist esitada oma eksamitulemuse läbivaatamiseks vaie Haridus- ja Noorteameti vaidekomisjonile.  Vaide saab esitada testide andmekogus EIS: <a href="https://eis.ekk.edu.ee">eis.ekk.edu.ee</a>. NB! Vaide esitamiseks on vaja avaldus digitaalselt allkirjastada! Palun veenduge, et teil on olemas digiallkirjastamise võimalus, enne kui alustate avalduse täitmist. Täpsemalt eksamitulemuste vaidlustamise kohta on võimalik lugeda Haridus- ja Noorteameti <a href="https://harno.ee/eesti-keele-tasemeeksamid#tutvumine">kodulehelt</a>.
% if taiendavinfo:

${taiendavinfo}
% endif

% if sooritaja.test.keeletase_kood in (const.KEELETASE_A2, const.KEELETASE_B1):
<hr/>
% if tunnistus:
НОМЕР ВАШЕГО СВИДЕТЕЛЬСТВА О ВЛАДЕНИИ ЭСТОНСКИМ ЯЗЫКОМ ${tunnistus.tunnistusenr}.
% endif

Свидетельство о владении эстонским языком является электронным. Свидетельства на бумажном носителе не выдаются.

При желании Вы сможете посмотреть свое свидетельство, скачать его на компьютер и распечатать, воспользовавшись услугой государственного портала www.eesti.ee „Скачивание э-свидетельств об уровне владения эстонским языком.“ Э-свидетельство также доступно в Собрании данных по тестам EIS <a href="https://eis.ekk.edu.ee">eis.ekk.edu.ee</a>.

На портал можно входить с помощью ID-карты, Mobiil-ID или Smart-ID. Технические инструкции можно найти на государственном портале рядом с соответствующей услугой или на <a href="https://www.harno.ee">www.harno.ee</a>. Дополнительную информацию можно получить по телефону 7350 500 и через поддержку пользователя EIS по э-почте <a href="mailto:eis@tugi.edu.ee">eis@tugi.edu.ee</a> и телефону 7302 135 (Пн-Пт 9-17).

NB! Скачивание и распечатка электронного свидетельства не являются обязательными. Чтобы доказать свое знание языка работодателю или должностному лицу, достаточно предоставить им свой личный код и номер свидетельства.

Экзаменуемый имеет право в течение 30 дней после получения сведений о результатах экзамена представить возражение для пересмотра результатов экзамена в комиссию по рассмотрению возражений Департамента по делам образования и молодежи. Возражение можно подать через Собрание данных по тестам EIS: <a href="https://eis.ekk.edu.ee">eis.ekk.edu.ee</a>. NB! Для подачи возражения необходимо поставить цифровую подпись на заявлении! Пожалуйста, прежде чем начать заполнять заявление, убедитесь, что у вас есть возможность цифровой подписи. Подробнее об оспаривании результатов экзамена можно прочитать на сайте Департамента по делам образования и молодежи.

<hr/>
% if tunnistus:
YOUR ESTONIAN LANGUAGE CERTIFICATE NUMBER IS ${tunnistus.tunnistusenr}.
% endif

The Estonian language proficiency certificate is electronic. Certificates are not issued on paper.
You can view, download, and print your certificate on the state portal www.eesti.ee using the service "Estonian proficiency exam e-certificate download." The e-certificate is also available in the Test Database (EIS) <a href="https://eis.ekk.edu.ee">eis.ekk.edu.ee</a>.

You can enter the website using an ID card, Mobile ID or Smart ID. Instructions can be found on the state portal at the corresponding service or <a href="https://www.harno.ee">www.harno.ee</a>. You can get additional information by tel. 7350 500 and from the EIS user support: e-mail <a href="mailto:eis@tugi.edu.ee">eis@tugi.edu.ee</a>, tel. 7302 135 (Mon-Fri 9-17).

NB! Downloading and printing the electronic certificate is not mandatory. To prove your language skills to an employer or an official, it is enough to provide them with your personal identification number and certificate number.

The examinee has the right, within 30 days after the announcement of the results of the proficiency exam, to file a challenge with the Education and Youth Board challenge committee for the review of their examination result. Challenges can be submitted in the Test Database EIS: <a href="https://eis.ekk.edu.ee">eis.ekk.edu.ee</a>. NB! To submit the challenge, you need to digitally sign the form! Please make sure you have the digital signature option before you start filling out the application. You can read more about challenging exam results on the Education and Youth Board website.

% endif

NB! Positiivselt sooritatud eksami korral on Teil võimalus taotleda eesti keele õppe kulude hüvitamist. Info ja tingimused: <a href="https://www.harno.ee">www.harno.ee</a>.
% if sooritaja.test.keeletase_kood in (const.KEELETASE_A2, const.KEELETASE_B1):

В случае положительной сдачи экзамена, у Вас есть возможность ходатайствовать о возмещении затрат на изучение эстонского языка. Информация и условия: <a href="https://www.harno.ee">www.harno.ee</a>.

NB! In the case of a positive result, you have the opportunity to apply for compensation for the costs of learning the Estonian language. Information and conditions: <a href="https://www.harno.ee">www.harno.ee</a>.
% endif

Haridus- ja Noorteamet
Lõõtsa 4, 11415 Tallinn

<%include file="footer.mako"/>
