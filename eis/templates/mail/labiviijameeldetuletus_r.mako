Subject: Läbiviija meeldetuletus
<p>
Lugupeetud ${isik_nimi}
</p>
<p>
Soovime Teile meelde tuletada, et olete registreeritud
% if len(labiviijad)==1:
järgmise eksami läbiviijaks:
% else:
järgmiste eksamite läbiviijaks:
% endif
</p>
<table width="100%">
  <thead>
    <tr>
      <td><b>Kuupäev</b></td>
      <td><b>Algusaeg</b></td>
      <td><b>Eksam</b></td>
      <td><b>Eksamikoht</b></td>
      <td><b>Aadress</b></td>
      <td><b>Roll</b></td>
    </tr>
  </thead>
  <tbody>
    % for lv in labiviijad:
    <tr>
      <td>${lv.testiruum and lv.testiruum.algus.strftime('%d.%m.%Y')}</td>
      <td>${lv.testiruum and lv.testiruum.algus.strftime('%H.%M')}</td>
      <td>${lv.toimumisaeg.testimiskord.test.nimi}</td>
      <td>${lv.testikoht and lv.testikoht.koht.nimi}</td>
      <td>${lv.testikoht and lv.testikoht.koht.tais_aadress}</td>
      <td>${lv.kasutajagrupp.nimi}</td>
    </tr>
    % endfor
  </tbody>
</table>

<p>
Palun andke teada, kui olete kirja kätte saanud!
</p>
<p>
Maie Jürgens
<br/>
Tel 7350562, 56482403

<%include file="footer_p.mako"/>
