Subject: Eritingimuste teade

Haridus- ja Noorteameti eritingimuste spetsialist on läbi vaadanud testi ${test.nimi}
% for tos in sooritused:

sooritaja ${tos.sooritaja.nimi} eritingimused testiosas "${tos.testiosa.nimi}" ning kinnitanud:
${tos.get_str_erivajadused('\n')}
% endfor

Eksamite infosüsteem

<%include file="footer.mako"/>
