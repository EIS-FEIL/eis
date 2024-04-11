Subject: Eksamikutse
Lp ${isik_nimi}
<p>
% if len(algused) == 1:
% for osa, algus, koht in algused:
<strong>Teatame, et eesti keele ${keeletase_nimi}-taseme eksam toimub ${algus} asukohaga ${koht}.</strong>
% endfor
% else:
<strong>Teatame, et eesti keele ${keeletase_nimi}-taseme eksam toimub:
  <ul>
% for osa, algus, koht in algused:
<li>${osa} - ${algus} asukohaga ${koht}</li>
% endfor
  </ul>
</strong>
% endif
</p>

% if konsultatsioonikohad:
<p>
  <i>Eksamieelne konsultatsioon toimub ${'; '.join(konsultatsioonikohad)}.</i>
  <br/>
  <i>Konsultatsioon kestab kuni 4,5 tundi (kuni 6 akadeemilist tundi).</i>
</p>
% endif
% if taiendavinfo:
<p>${taiendavinfo}</p>
% endif
<p>
Isik, kes puudub eksamilt mõjuva põhjuseta või kelle eksamitulemus jääb alla 45 protsendipunkti võimalikust punktisummast, ei saa eksamit uuesti sooritada varem kui kuue kuu möödumisel eksami toimumisest.
</p>
<p>
  Piirangut ei kohaldata, kui isik tühistab eksamile registreerumise hiljemalt <b>neli (4) tööpäeva</b> enne eksami toimumise kuupäeva! Registreeringut saab tühistada ööpäevaringselt, kirjutades aadressile info@harno.ee (kindlasti lisada isikukood!) või helistades E–R 9.00–17.00 telefonil +372 735 0500.
</p>
<p>
Isikul, kes puudus eksamilt mõjuval põhjusel ning kes soovib eksamit sooritada enne 6 kuu möödumist, tuleb 30 päeva jooksul esitada vabas vormis selgitus puudumise põhjuse kohta koos tõendiga Haridus- ja Noorteametile. Dokumentidele tuleb lisada eksamile registreerumise avaldus.
</p>
<p>
Palume eesti keele tasemeeksamile tulles meeles pidada järgmist:
</p>
<p>
  1. Eesti keele tasemeeksam algab täpselt kell 10.00. Hilinejaid eksamile ei lubata. Soovitame olla eksamipunktis kohal 15-20 minutit enne eksami algust. Eksamiruumi numbri saab teada seinal olevatest nimekirjadest.
  <br/>
  2. Eksamile lubatakse järgmiste dokumentide alusel: ID-kaart, pass või elamisluba. NB! Autojuhiluba ei ole isikut tõendav dokument.
  <br/>
  3. Enne eksami algust tuvastab eksami läbiviija eksaminandi isiku ja kontrollib esitatud dokumente. Kui eksami läbiviijal ei õnnestu eksaminandi isikut tuvastada või tekib dokumente kontrollides kahtlus, et eksamil on vale isik või dokument pole ehtne, tuvastab isiku politsei.
  <br/>
  4. Käekell (mehhaaniline; elektrooniline; nuti vmt)  tuleb eksami ajaks käelt ära võtta!
  <br/>
  5. Eksamitöö täitmisel:
  <ul>
    <li>tuleb kirjutada loetava käekirjaga, käekirja tõttu ebaselged kohad loetakse veaks;</li>
    <li>tuleb kirjutada musta või sinise tindi või pastakaga, hariliku pliiatsiga kirjutatud ja tindi või pastakaga ülekirjutatud eksamitööd loetakse kehtetuks;</li>
    <li>laual tohib olla ainult kirjutusvahend;</li>
    <li>parandused eksamitöös tuleb teha selgelt, tõmmates maha terve sõna, sümboli või numbri;</li>
    <li>ei ole lubatud kasutada korrektorpliiatsit;</li>
    <li>ei ole lubatud kasutada abimaterjale (sõnastikud, õpikud vms);</li>
    <li>ei ole lubatud kasutada eksamitöö tegemisel kellegi teise abi;</li>
    <li>ei ole lubatud kasutada mobiiltelefoni; </li>
    <li>ei ole lubatud häirida eksamit;</li>
    <li>ei ole lubatud eksamitööde üleandmise ajal eksamitööd lehitseda või sinna midagi kirjutada.</li>
  </ul>
  6. Kui eksamitöö hindamise käigus tuvastatakse kõrvalise abi kasutamine, hinnatakse eksamitöö 0 punktiga.
  <br/>
  7. Valikvastuste kirjutamisel tuleb kasutada suuri trükitähti (A, B, C jne). I ja J, C ja G peavad selgelt eristuma. Kui eksaminand on valikülesannetes ära märkinud mitu vastust, loetakse vastus valeks.
  <br/>
  8. Eksamikorra rikkumisel kõrvaldatakse eksaminand eksamilt ette hoiatamata.
  <br/>
  9. Reeglina ei ole eksami ajal lubatud ruumist lahkuda; erandkorras võib eksami ajal ruumist lahkuda üksnes eksami läbiviija loal.
  <br/>
  10. Eksam koosneb kirjalikust ja suulisest osast. Eksam algab kirjutamisosaga. Järgnevad kuulamis- ning lugemisosa.
  <br/>
  11. Eesti keele ${keeletase_nimi}-taseme eksami kirjalik osa kestab ${kestus}.
  <br/>
  12. Eksami suuline osa algab umbes 15-20 minutit peale kirjaliku osa lõppu juhul, kui suuline osa toimub samal päeval. Eksami suulise osa läbivad eksaminandid paarikaupa nimekirja järgi. Kõikide eksaminandide suuline vastus salvestatakse ja seda hinnatakse hiljem salvestise järgi.
  <br/>
  13. Eksam on sooritatud, kui eksaminand on kogunud vähemalt 60% võimalikust punktisummast, ühegi osaoskuse tulemus ei tohi olla 0 punkti.
  <br/>
  14. Eksamitulemused teatatakse hiljemalt 40 päeva pärast eksamit kirja või e-posti teel registreerimisavaldusel märgitud aadressil. Telefoni teel eksamitulemuste kohta informatsiooni ei anta.
  <br/>
  15. Eksami sooritanud isikule vormistatakse eesti keele tasemeeksami elektrooniline tunnistus. Tunnistust saab soovi korral vaadata, alla laadida ning välja trükkida riigiportaalis https://www.eesti.ee ja testide andmekogus (EIS) https://eis.ekk.edu.ee/eis/ 
  <br/>
  16. Kui eksaminand ei ole rahul tasemeeksami tulemusega, on tal õigus 30 päeva jooksul pärast selle teatavaks tegemist <b>esitada põhjendatud vaie</b>. Vaide saab esitada <b>ainult elektroonselt</b> testide andmekogus EIS: https://eis.ekk.edu.ee/eis. Pärast sisse logimist valige "Minu tulemused" ja leidke õige eksam. Seejärel vajutage nupule "Esita vaie" ja täitke kõik vajalikud väljad. <b>Selleks, et vaie saaks esitatud, tuleb see kindlasti digitaalselt allkirjastada.</b> 
  <br/>
</p>
<p>
Soovime Teile edu eksamiks!    
</p>
<p>
Haridus- ja Noorteamet<br/>
Lõõtsa 4, 11415 Tallinn, tel 7350 500
</p>
<%include file="footer_p.mako"/>
