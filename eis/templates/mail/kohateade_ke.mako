Subject: Kutseeksami toimumise teade
Lp ${isik_nimi}

Teatame kutseeksami toimumise aja ja koha.
% for (test_nimi, testiosa_nimi, koht_nimi, ruum_tahis, aadress, algus, kavaaeg) in kohad:
<%
  buf = ''
  if koht_nimi:
     buf += '; %s' % koht_nimi
     if ruum_tahis:
        buf += ', ruum %s' % ruum_tahis
  if aadress:
     buf += '; %s' % aadress
  buf += '. '
%><b>${kavaaeg or algus}</b> - ${test_nimi} (${testiosa_nimi})${buf}
% endfor

% if taiendavinfo:
${taiendavinfo}

% endif

<%include file="footer.mako"/>
