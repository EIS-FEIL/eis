Subject: Läbiviija teade
<p>
Lugupeetud ${isik_nimi}
</p>
<p>
Olete määratud 
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
      <td> 
      <% 
      testiruum = lv.testiruum 
      ruum = testiruum and testiruum.ruum 
      ruum_tahis = ruum and ruum.tahis or None 
      %>
      <% 
      testikoht = lv.testikoht 
      koht = testikoht and testikoht.koht 
      koht_nimi = koht and koht.nimi or None 
      %> 
        % if ruum_tahis:
        ${koht_nimi}, ruum ${ruum_tahis}
        % else:
        ${koht_nimi}        
        % endif
      </td>
      <td>${lv.testikoht and lv.testikoht.koht.tais_aadress}</td>
      <td>${lv.kasutajagrupp.nimi}</td>
    </tr>
    % endfor
  </tbody>
</table>

<p>
${user_nimi}
<br/>
Tel 7350562, 56482403

<%include file="footer_p.mako"/>
