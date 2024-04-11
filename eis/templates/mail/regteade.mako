Subject: Testile registreerimise teade
<p>
  Lp ${isik_nimi}
</p>
<p>
% if on_eksam and len(testimiskorrad_id) == 1:
Teid on registreeritud järgmisele eksamile:
% elif on_eksam:
Teid on registreeritud järgmistele eksamitele:
% elif len(testimiskorrad_id) == 1:
Teid on registreeritud järgmisele testile:
% else:
Teid on registreeritud järgmistele testidele:
% endif
</p>
<% cadvanced = notcadvanced = False %>
% for j, extra in sooritajad:
<%
  test = j.test
  koht_aeg = extra.get('koht_aeg')
  koht_nimi = extra.get('koht_nimi')
  alates = extra.get('alates')
  vahemik = extra.get('vahemik')
  kons = extra.get('kons')
  sooritused = list(j.sooritused)
  if test.testiliik_kood == const.TESTILIIK_SISSE:
      sooritused = [sooritused[0]]
  on_osa = len(sooritused) > 1
%>
% for tos in sooritused:
<div style="margin-bottom:6px">
  - ${test.nimi}${on_osa and ' (%s)' % tos.testiosa.nimi or ''}${j.kursus_kood and ', %s' % j.kursus_nimi or ''} – ${tos.toimumisaeg.millal}
<% 
if 'C1 Advanced' in j.test.nimi: 
    cadvanced = True # testide seas leidub C1 Advanced test
else: 
    notcadvanced = True # testide seas leidub mingi muu test kui C1 Advanced
%>
% endfor
% if test.aine_kood == const.AINE_M and test.testiliik_kood == const.TESTILIIK_RIIGIEKSAM:
<div>Soorituskeel: ${(j.lang_nimi or '').lower()}</div>
% endif
% if test.testiliik_kood == const.TESTILIIK_TASE:
<div>Tase: ${j.test.keeletase_nimi}</div>
% endif
% if koht_aeg and not alates:
<div>Toimumiskoht: ${koht_aeg}</div>
% elif koht_nimi:
<div>Toimumiskoht: ${koht_nimi}</div>
% elif j.piirkond_id:
<div>Piirkonnaks olete valinud ${j.piirkond_nimi}</div>
% endif
% if kons:
<div>Konsultatsioon: ${kons}</div>
% endif
% if test.testiliik_kood == const.TESTILIIK_KOOLITUS:
<div>
  Koolitus avatakse ${alates}.
  % if vahemik:
  Testi saate sooritada ajavahemikul ${vahemik}.
  % endif
</div>
% endif
</div>
% endfor

% if reg_auto:
<p>
  Teie alustatud pooleli jäänud registreering eksamile kinnitati automaatselt.
</p>
% endif

% if notcadvanced and testiliik_kood != const.TESTILIIK_KOOLITUS:
 % if on_lisaeksam:
<p>Eksamikoha teate saadame hiljemalt üks (1) päev enne eksami toimumist.</p>
 % elif testiliik_kood==const.TESTILIIK_RIIGIEKSAM or testiliik_kood==const.TESTILIIK_RV:
<p>Eksamikoha teate saadame hiljemalt kaks (2) nädalat enne eksamit.</p>
 % elif testiliik_kood==const.TESTILIIK_SEADUS:
<p>Eksamikoha teate saadame hiljemalt 7 päeva enne eksamit.</p>
 % elif testiliik_kood==const.TESTILIIK_TASE:
<p>Eksamikoha teate saadame hiljemalt 14 päeva enne eksamit.</p>
 % endif

 % if testiliik_kood==const.TESTILIIK_TASE:
<p>Kui Te ei soovi eksamil osaleda, palume tühistada eksamile registreerumise hiljemalt neli (4) tööpäeva enne eksami toimumise kuupäeva! Registreeringut saab tühistada ööpäevaringselt, kirjutades aadressile info@harno.ee (kindlasti lisada isikukood!) või helistades E–R 9.00–17.00 telefonil +372 735 0500.</p>
 % elif not on_lisaeksam and teade6pv and on_eksam:
<p>Kui Te ei soovi eksamil osaleda, palume saata teade hiljemalt seitse (7) päeva enne eksami toimumise kuupäeva aadressile info@harno.ee.</p>
 % elif not on_lisaeksam and teade6pv and not on_eksam:
<p>Kui Te ei soovi testil osaleda, palume saata teade hiljemalt seitse (7) päeva enne testi toimumise kuupäeva aadressile info@harno.ee.</p>
 % endif
% endif

% if cadvanced:
<p>NB! C1 Advanced eksamile on õpilasel õigus registreeruda vaid ühe korra.</p>
<p>Kui õpilase tulemus ei ole keeletaseme tunnistuse saamiseks piisav ning jääb alla 142 punkti ehk "not reported", siis EISi kantakse tulemuseks 0 punkti, mis tähendab, et võõrkeele riigieksam on sooritamata ja gümnaasiumi lõpetamise tingimus täitmata.</p>
<p>Kui õpilane on registreerunud C1 Advanced eksamile, aga ei ilmu kohale ja (arsti)tõendit pole esitada, siis Harno poolt korraldatavale Cambridge C1 Advanced eksamile uuesti registreerida ei saa, inglise keele (lisa)eksamile registreerida ei saa ning seega gümnaasiumi lõpetamiseks tuleb eksam järgmisel aastal uuesti sooritada.</p>
<p>Teavituse täpse soorituskoha ja ajagraafikuga saadame osalejatele hiljemalt kaks (2) nädalat enne eksamit. Palume arvesse võtta, et kirjalik ja suuline eksam ei pruugi toimuda samas eksamikoolis ja/või samal päeval. </p>
<p>Rohkem infot C1 Advanced eksami kohta leiate <a href="https://www.harno.ee/eksamid-testid-ja-uuringud/eksamid-testid-ja-lopudokumendid/rahvusvahelised-keeleeksamid#cambridge" target="_blank" rel="noopener">Haridus- ja Noorteameti kodulehelt</a>.</p>
% endif

<p>
Haridus- ja Noorteamet<br/>
Lõõtsa 4, Tallinn 11415<br/>
Tel 7350 500<br/>
info@harno.ee<br/>
</p>
<%include file="footer_p.mako"/>
