Subject: Eksamikutse
Lp ${isik_nimi}

<b>Teatame Teile, et olete registreeritud Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse tundmise eksamile, mis toimub ${aeg} asukohaga ${koht_aadress}.</b>

% if not ruum_tahis:
<b>Eksamiruumi numbri saate teada kohapeal olevast nimekirjast.</b>

% endif

<b>Palume eksamile tulles kaasa võtta isikut tõendav dokument (pass, ID-kaart või elamisluba). NB! Autojuhiluba ei ole isikut tõendav dokument! Isikut tõendava dokumendita eksamile ei lubata.</b>
% if konsultatsioonikohad:
<i>
   % if len(konsultatsioonikohad) == 1:
Eksamieelne konsultatsioon toimub:
   % else:
Eksamieelsed konsultatsioonid toimuvad järgmistel kuupäevadel:
   % endif
</i>
   % for s in konsultatsioonikohad:
${s}
   % endfor
   
   % if len(konsultatsioonikohad) > 1:
Konsultatsioonil osalemiseks palun valige antud aegade seast endale sobivaim!
   % endif
Konsultatsioon kestab kuni 1,5 tundi.
% endif

% if taiendavinfo:
${taiendavinfo}
% endif

Teadmiseks Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse tundmise eksami sooritajale!
1. Eksamile lubatakse ainult isikut tõendava dokumendi esitamisel (pass, ID-kaart või elamisluba). 
2. Hilinejaid eksamiruumi ei lubata.
3. Eksami sooritamiseks on aega 45 minutit.
4. Eksam sooritatakse eksamipunktis, kus eksamitöö täidetakse elektrooniliselt ehk arvutil eesti keeles.
5. Eksami ajal ei ole lubatud eksamiruumist lahkuda.
6. Eksamitöö koosneb 24 valikvastusega küsimusest. 
7. Eksamil on võimalik kasutada Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse eestikeelset teksti ning sõnaraamatut, mis on eksamiruumis olemas.
8. Eksamineeritaval palutakse eksamilt lahkuda, kui eksaminand kirjutab maha, üritab seda teha või aitab sellele kaasa; eksaminandi käitumine häirib teisi eksaminande või takistab eksami läbiviimist ja/või eksaminand ei allu eksamikomisjoni korraldusele.
9. Eksam loetakse sooritatuks, kui eksamineeritav on vastanud õigesti vähemalt 18 küsimusele. 
10. Eksamil osalejatele saadetakse 14 päeva jooksul teade eksami tulemuse kohta.
11. Kui eksamikutse saanud isik loobub eksamist või ei soorita eksamit, tuleb tal vajadusel ise  uuesti eksamile registreeruda.
12. Eksamitulemust saab vaidlustada 30 päeva jooksul pärast tulemuse teadasaamist. Selleks tuleb esitada avaldus Haridus-ja Teadusministeeriumile.

Soovime Teile edu eksamiks!    

Haridus- ja Noorteamet
Lõõtsa 4, 11415 Tallinn, tel 7350 500

<%include file="footer.mako"/>
