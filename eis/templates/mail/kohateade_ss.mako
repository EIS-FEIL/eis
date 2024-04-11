Subject: Sisseastumiseksami toimumise teade
Lp ${isik_nimi}

Teatame sisseastumiseksami toimumise aja ja koha.
% for (test_nimi, testiosa_nimi, koht_nimi, ruum_tahis, aadress, algus, kavaaeg) in kohad:
  % if ruum_tahis and aadress:
<b>${kavaaeg or algus}</b> - ${test_nimi} (${testiosa_nimi}); ${koht_nimi}, ruum ${ruum_tahis}; ${aadress}. 
  % elif ruum_tahis:
<b>${kavaaeg or algus}</b> - ${test_nimi} (${testiosa_nimi}); ${koht_nimi}, ruum ${ruum_tahis}. 
  % elif aadress:
<b>${kavaaeg or algus}</b> - ${test_nimi} (${testiosa_nimi}); ${koht_nimi}; ${aadress}. 
  % elif koht_nimi:
<b>${kavaaeg or algus}</b> - ${test_nimi} (${testiosa_nimi}); ${koht_nimi}. 
  % else:
${test_nimi} (${testiosa_nimi}).
  % endif
% endfor

% if taiendavinfo:
${taiendavinfo}
% endif

Sisseastumiseksamit viiakse läbi e-testide keskkonnas, kuhu saab sisse logida kasutades ID-kaarti, mobiil-ID'd või Smart-ID'd ning vastava autentimisvahendi PIN1.

Eksamile palume kohale tulla 15 minutit enne eksami algust ning kaasa võtta pass või ID-kaart.

Mobiiltelefoni on lubatud kasutada üksnes ja ainult eksamisüsteemi mobiil-ID või Smart ID-ga sisselogimiseks. Ühelgi muul eesmärgil (kaasa arvatud kella või kalkulaatorina) mobiiltelefoni eksamil kasutada ei ole lubatud.
