Subject: Läbiviija meeldetuletus
<p>
Lugupeetud ${isik_nimi}
</p>
<p>
Soovime Teile meelde tuletada, et osalete peatselt toimuval Eesti Vabariigi
põhiseaduse ja kodakondsuse seaduse tundmise eksamil
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
${test.nimi} 
% if lv.testikoht:
${lv.testiruum.algus.strftime('%d.%m.%Y %H.%M')} 
asukohaga ${lv.testikoht.koht.nimi} 
${lv.testikoht.koht.tais_aadress or ''}
% endif
 - ${lv.kasutajagrupp.nimi}
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
