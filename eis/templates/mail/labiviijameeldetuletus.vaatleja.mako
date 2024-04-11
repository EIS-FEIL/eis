Subject: Vaatleja meeldetuletus
<p>
Lugupeetud ${isik_nimi}
</p>
<p>
Soovime Teile meelde tuletada, et olete registreeritud välisvaatlejaks 
% if len(labiviijad)==1:
järgmisele eksamile:
% else:
järgmistele eksamitele:
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
    </tr>
  </thead>
  <tbody>
    % for lv in labiviijad:
    <tr>
      <td>${lv.testiruum.algus.strftime('%d.%m.%Y')}</td>
      <td>${lv.testiruum.algus.strftime('%H.%M')}</td>
      <td>${lv.toimumisaeg.testimiskord.test.nimi}</td>
      <td>
        <% ruum_tahis = lv.testiruum and lv.testiruum.ruum and lv.testiruum.ruum.tahis or None %>
        % if ruum_tahis:
        ${lv.testikoht.koht.nimi}, ruum ${ruum_tahis}
        % else:
        ${lv.testikoht.koht.nimi}        
        % endif
      </td>
      <td>${lv.testikoht.koht.tais_aadress}</td>
    </tr>
    % endfor
  </tbody>
</table>

<p>
  % if taiendavinfo:
  ${taiendavinfo}
  % endif
  Kui Te ei saa mingil põhjusel eksamil osaleda, 
palume sellest viivitamatult teatada allpool toodud telefonidel või e-posti aadressil.
</p>
<p>
Maie Jürgens
<br/>
Tel 7350562, 56482403
<br/>
maie.jyrgens@harno.ee
<p>

<%include file="footer_p.mako"/>
