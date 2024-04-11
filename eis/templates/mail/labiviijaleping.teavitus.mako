Subject: Lepingu sõlmimise teavitus
<p>
Lugupeetud ${isik_nimi}
</p>
% for kaskkirikpv, testiliik, aine, roll in rollid:
<p>
Teile on määratud ${kaskija} ${kaskkirikpv} käskkirjaga järgmine roll:<br/>
${testiliik} ${aine} ${roll}.
</p>
% endfor
<p>
  Palun sõlmige leping Eksamite Infosüsteemis.
  <br/>
  Selleks logige sisse aadressil <a href="https://eis.ekk.edu.ee/eis">https://eis.ekk.edu.ee/eis</a>, klõpsake paremal ülal oma nimel ning valige avanevast menüüst „Testi läbiviimise nõusolekud“.
</p>
<p>
  Sakis „Isikuandmed“ saab tutvuda Teile suunatud teenuslepinguga, sellega nõustudes täitke esimene märkeruut.
  Seejärel ilmub teise märkeruudu taha lisaküsimus kolmanda hindamise valmisoleku kohta.
</p>
<p>
  Leping on sõlmitud, kui vajutate „Kinnita leping“.
</p>
% if taiendavinfo:
<p>
  ${taiendavinfo}
</p>
% endif
<p>
Küsimuste puhul pöörduge EISi kasutajatoe poole tel 7350777 või e-postiga eis@tugi.edu.ee
</p>
<p>
Haridus- ja Noorteamet
</p>

<%include file="footer_p.mako"/>
