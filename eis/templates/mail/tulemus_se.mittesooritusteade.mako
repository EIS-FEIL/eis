Subject: Mittesooritusteade
Lp ${isik_nimi}

<b>Teatame, et Te ei sooritanud ${sooritaja.algus.strftime('%d.%m.%Y')} Eesti Vabariigi põhiseaduse ja kodakondsuse seaduse tundmise eksamit.

Teie eksamitulemus on ${int(round(sooritaja.pallid))} punkti vajalikust ${int(round(sooritaja.max_pallid*test.lavi_pr/100.))}-st.</b>

Kui soovite registreeruda korduseksamile, tuleb Teil esitada uus avaldus Haridus- ja Noorteametile.

Edu edaspidiseks!
% if taiendavinfo:

${taiendavinfo}
% endif

Haridus- ja Noorteamet
Lõõtsa 4, 11415 Tallinn

<%include file="footer.mako"/>
