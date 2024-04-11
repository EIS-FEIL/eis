Subject: Soorituskoha teade
Lp ${isik_nimi}
<% tapsustus = u'Vastamise kellaaja saate teada  kirjalikul eksamil.' %>
Teatame riigieksami toimumise aja ja koha.
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
  if not kavaaeg and tapsustus:
     buf += tapsustus
%>
<b>${kavaaeg or algus}</b> - ${test_nimi} (${testiosa_nimi})${buf}
% endfor

% if taiendavinfo:
${taiendavinfo}

% endif
Infot eksami sisu ja korralduse kohta leiate Haridus- ja Noorteameti koduleheküljelt www.harno.ee.

Eksamile palume kohale tulla 15 minutit enne eksami algust ning kaasa võtta kehtiv pildiga isikut tõendav dokument (pass, ID-kaart või autojuhiluba). Eksamil ei ole lubatud kasutada mobiiltelefoni ükskõik mis eesmärgil (kaasa arvatud kella või kalkulaatorina).

Elektroonilised riigieksamitunnistused avaldatakse riigiportaalis <a href="https://www.eesti.ee">www.eesti.ee</a>.


Haridus- ja Noorteamet
Lõõtsa 4, 11415 Tallinn
Tel: 7350 500
http://www.harno.ee 

<%include file="footer.mako"/>
