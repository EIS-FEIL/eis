Subject: Soorituskoha teade
Lp ${isik_nimi}
<% delf = notdelf = False %>
Teatame rahvusvahelise eksami toimumise aja ja koha.
% for (test_nimi, testiosa_nimi, koht_nimi, ruum_tahis, aadress, algus, kavaaeg, kursus_nimi, lang_nimi) in kohad:
<%
  buf = ''
  if kursus_nimi:
     buf += ', %s' % kursus_nimi
  if lang_nimi:
     buf += ', %ses' % lang_nimi
  if koht_nimi:
     buf += '; %s' % koht_nimi
     if ruum_tahis:
        buf += ', ruum %s' % ruum_tahis
  if aadress:
     buf += '; %s' % aadress
  buf += '. '
%>
<b>${kavaaeg or algus}</b> - ${test_nimi} (${testiosa_nimi})${buf}
% if 'DELFscolaire' in test_nimi:
    <% delf = True %>
% else:
    <% notdelf = True %>
% endif
% endfor

% if taiendavinfo:
${taiendavinfo}

% endif
% if delf and not notdelf:

Eksamikoolis tuleb kohal olla hiljemalt 30 minutit enne eksami algust ning kaasa võtta kehtiv pildiga isikut tõendav dokument (pass, ID-kaart või autojuhiluba) ja sinine või must pastakas. Hariliku pliiatsiga eksamitööle märkmete tegemine või mis tahes kustutusvahendite kasutamine on keelatud. Oma vastuste sõnastamiseks saate kasutada mustandipaberit. Samuti ei ole eksamil lubatud kasutada elektroonikaseadmeid (mobiiltelefon, (tahvel)arvuti, nutikell, kalkulaator) ükskõik mis eesmärgil.

Infot eksami sisu ja korralduse kohta leiate Haridus- ja Noorteameti koduleheküljelt www.harno.ee.

% elif not delf and notdelf:
Infot eksami sisu ja korralduse kohta leiate Haridus- ja Noorteameti koduleheküljelt www.harno.ee.

Eksamile palume kohale tulla 15 minutit enne eksami algust ning kaasa võtta kehtiv pildiga isikut tõendav dokument (pass, ID-kaart või autojuhiluba). Eksamil ei ole lubatud kasutada mobiiltelefoni ükskõik mis eesmärgil (kaasa arvatud kella või kalkulaatorina).
% if teade7pv:
Kui Te ei soovi eksamil osaleda, siis palume saata teade hiljemalt seitse (7) päeva enne eksami toimumise kuupäeva aadressile info@harno.ee.
% endif

% elif delf and notdelf:

Infot eksami sisu ja korralduse kohta leiate Haridus- ja Noorteameti koduleheküljelt www.harno.ee.

***
Eksamile palume kohale tulla 15 minutit enne eksami algust ning kaasa võtta kehtiv pildiga isikut tõendav dokument (pass, ID-kaart või autojuhiluba). Eksamil ei ole lubatud kasutada mobiiltelefoni ükskõik mis eesmärgil (kaasa arvatud kella või kalkulaatorina).
% if teade7pv:
Kui Te ei soovi eksamil osaleda, siis palume saata teade hiljemalt seitse (7) päeva enne eksami toimumise kuupäeva aadressile info@harno.ee.
% endif

Eksamikoolis tuleb kohal olla hiljemalt 30 minutit enne eksami algust ning kaasa võtta kehtiv pildiga isikut tõendav dokument (pass, ID-kaart või autojuhiluba) ja sinine või must pastakas. Hariliku pliiatsiga eksamitööle märkmete tegemine või mis tahes kustutusvahendite kasutamine on keelatud. Oma vastuste sõnastamiseks saate kasutada mustandipaberit. Samuti ei ole eksamil lubatud kasutada elektroonikaseadmeid (mobiiltelefon, (tahvel)arvuti, nutikell, kalkulaator) ükskõik mis eesmärgil.

% endif

Haridus- ja Noorteamet
Lõõtsa 4, 11415 Tallinn
Tel: 7350 500
http://www.harno.ee 

<%include file="footer.mako"/>
    
