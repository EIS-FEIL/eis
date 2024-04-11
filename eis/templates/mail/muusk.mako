Subject: Teise soorituskohta suunamise teade
<p>
  Hea kooli administraator.
</p>
<p>
  Teavitame, et järgmised teie kooli (${kool_nimi}) õpilased on suunatud testi "${test_nimi}" (${tahised}) sooritama teise soorituskohta:
</p>
<ul>
  % for nimi, aeg, koht, aadress in suunamised:
  <li>${nimi} (${aeg} ${koht}${aadress and ', '+aadress or ''})</li>
  % endfor
</ul>
<p>
  Eksamite infosüsteem
</p>
