Subject: Mittesooritusteade
Lp ${isik_nimi}

<b>Teatame, et Te ei sooritanud  ${sooritaja.algus.strftime('%d.%m.%Y')} ${taseme} eksamit. Teie eksamitulemus on ${int(round(sooritaja.tulemus_protsent))}% võimalikust punktisummast.</b>

Teie keeleoskusele anti järgmine hinnang (protsentides võimalikust punktisummast): ${', '.join(s_vahemikud)+'.'}

Eesti keele tasemeeksami tööga tutvumiseks tuleb esitada avaldus meie infolauda (avatud esmaspäevast reedeni kell 9.00–17.00), saata Haridus- ja Noorteameti postiaadressile Lõõtsa 4, 11415 Tallinn või digitaalselt e-posti teel aadressile <a href="mailto:info@harno.ee">info@harno.ee</a>.

Eksaminandil on õigus 30 päeva jooksul pärast tasemeeksami tulemuse teatavaks tegemist esitada oma eksamitulemuse läbivaatamiseks vaie Haridus- ja Noorteameti vaidekomisjonile.  Vaide saab esitada testide andmekogus EIS: <a href="https://eis.ekk.edu.ee">eis.ekk.edu.ee</a>. NB! Vaide esitamiseks on vaja avaldus digitaalselt allkirjastada! Palun veenduge, et teil on olemas digiallkirjastamise võimalus, enne kui alustate avalduse täitmist. Täpsemalt eksamitulemuste vaidlustamise kohta on võimalik lugeda Haridus- ja Noorteameti <a href="https://harno.ee/eesti-keele-tasemeeksamid#tutvumine">kodulehelt</a>.
% if taiendavinfo:

${taiendavinfo}
% endif

<hr/>

Для ознакомления с экзаменационной работой уровневого экзамена по эстонскому языку, необходимо подать заявление через информационный стол Haridus- ja Noorteamet (открыт с понедельника по пятницу с 9:00 до 17:00), либо отправив его по адресу Haridus- ja Noorteamet, Lõõtsa tn 4, 11415 Tallinn, либо отправив дигитально на электронную почту <a href="mailto:info@harno.ee">info@harno.ee</a>.

Экзаменуемый имеет право в течение 30 дней после получения сведений о результатах экзамена представить возражение для пересмотра результатов экзамена в комиссию по рассмотрению возражений Департамента по делам образования и молодежи. Возражение можно подать через Собрание данных по тестам EIS: <a href="https://eis.ekk.edu.ee">eis.ekk.edu.ee</a>. NB! Для подачи возражения необходимо поставить цифровую подпись на заявлении! Пожалуйста, прежде чем начать заполнять заявление, убедитесь, что у вас есть возможность цифровой подписи. Подробнее об оспаривании результатов экзамена можно прочитать на сайте Департамента по делам образования и молодежи.

<hr/>

To review your Estonian language proficiency exam papers, you can submit an application either to our information desk (open from Monday to Friday from 9:00 a.m. to 5:00 p.m.), send it by post to the Education and Youth Board at Lõõtsa 4, 11415 Tallinn, or send it by e-mail to <a href="mailto:info@harno.ee">info@harno.ee</a>.

The examinee has the right, within 30 days after the announcement of the results of the proficiency exam, to file a challenge with the Education and Youth Board challenge committee for the review of their examination result. Challenges can be submitted in the Test Database EIS: <a href="https://eis.ekk.edu.ee">eis.ekk.edu.ee</a>. NB! To submit the challenge, you need to digitally sign the form! Please make sure you have the digital signature option before you start filling out the application. You can read more about challenging exam results on the Education and Youth Board website.

Haridus- ja Noorteamet
Lõõtsa 4, 11415 Tallinn

<%include file="footer.mako"/>
