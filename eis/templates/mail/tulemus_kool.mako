Subject:${test_nimi} (tulemused avaldatud)
Lp ${koht_nimi}!
<p>
  Teatame, et <a href="${tulemused_url}">testi "${test_nimi}" tulemused</a> on avalikustatud ja EISis kättesaadavad
% if tulemus_koolile and tulemus_admin:
kooli administraatorile ning testi administraatorile.
% elif tulemus_koolile:
kooli administraatorile.
% elif tulemus_admin:
testi administraatorile.
% endif
</p>
% if hindamata:
<p>
Tulemus on puudu ${hindamata} õpilasel, kellel pole kõik vastused hinnatud. Tulemuste tekkimiseks tuleb kõik vastused hinnata.
</p>
% endif

Eksamite infosüsteem
