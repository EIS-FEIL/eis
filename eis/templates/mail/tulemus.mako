Subject: Tulemuse teavitus

Lp ${isik_nimi}!

Eksamite infosüsteem teatab, et ${isik_nimi} on saanud järgmised tulemused:
  % for s in sooritajad:
  <% testi_nimi = s.testimiskord.test.nimi %>    
  ${testi_nimi} - ${s.get_tulemus()}
  % if 'DELFscolaire' in testi_nimi:
  NB! Eksaminand on DELFscolaire eksami edukalt sooritanud vaid juhul, kui täidetud on kõik alljärgnevad tingimused:
  - saavutas igas osaoskuses (kuulamine, lugemine, kirjutamine, rääkimine) vähemalt 5p 25-st;
  - eksami koondtulemus on vähemalt 50p 100-st;
  - osales nii kirjalikul kui suulisel eksamil.
  Osaoskuste eest saadud tulemuste kontrollimiseks palume Teil sisse logida <a href="https://eis.ekk.edu.ee/eis">eksamite infosüsteemi</a>.
  % endif
% endfor
% if taiendavinfo:

${taiendavinfo}
% endif

Lugupidamisega

Eksamite infosüsteem

<%include file="footer.mako"/>
  
