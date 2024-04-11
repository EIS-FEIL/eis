Subject: Läbiviija teade
<p>
Lugupeetud ${isik_nimi}
</p>
<p>
Olete määratud osalema peatselt toimuval eesti keele tasemeeksamil
% if len(labiviijad)==1:
järgmises rollis:
% else:
järgmistes rollides:
% endif
</p>
% for lv in labiviijad:
<% test=lv.toimumisaeg.testimiskord.test %>
<p>
<b>
${test.keeletase_nimi} ${test.nimi} 

<% testikoht, testiruum = lv.testikoht, lv.testiruum %>
% if testikoht:
<% koht = testikoht and testikoht.koht or None %>
${testiruum and testiruum.algus and testiruum.algus.strftime('%d.%m.%Y %H.%M')} asukohaga ${koht.nimi} 
${koht.tais_aadress or ''} 
% endif

<% 
ruum = testiruum and testiruum.ruum 
ruum_tahis = ruum and ruum.tahis or None 
%>
% if ruum_tahis:
- ${lv.kasutajagrupp.nimi}, ruum ${ruum_tahis}
% else:
- ${lv.kasutajagrupp.nimi}       
% endif
</b>
</p>
% endfor

<p>
Palun andke teada, kui olete kirja kätte saanud!
</p>
<p>
Maie Jürgens
<br/>
Tel 7350562, 56482403
<%include file="footer_p.mako"/>
