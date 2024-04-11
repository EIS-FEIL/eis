
<%
  rcd = c.ska_sooritaja
  sooritused = list(rcd.sooritused)
  # kas mõnel toimumisajal on sooritajale juba aeg määratud?
  on_aeg = [r for r in sooritused if r.kavaaeg]
  testimiskord = c.ska_sooritaja.testimiskord
%>
% if testimiskord and testimiskord.reg_kohavalik:
## registreerimisel kohavaliku korral näitame ainult esimese testiosa kohta ja aega
<div>${rcd.kohavalik_nimi}</div>
% elif not on_aeg:
## kui sooritusaega pole veel määratud, siis näitame kogu testimiskorra aega
<div>
  ${rcd.piirkond_nimi}
  ${testimiskord and testimiskord.millal}
</div>
% else:
## sooritaja individuaalne algusaeg testiosade kaupa
% for tos in sooritused:
<div>
          <%
              testikoht = tos.testikoht
              koht_id = testikoht and testikoht.koht_id
              testiruum = tos.testiruum
              ruum_id = testiruum and testiruum.ruum_id
              aeg = h.str_from_datetime(tos.kavaaeg, hour0=False) or tos.toimumisaeg.millal
              #if testiruum and tos.testiosa.vastvorm_kood == const.VASTVORM_KE and testiruum.algus and testiruum.lopp:
              #    # kuvame ruumi algust ja lõppu
              #    if testiruum.algus.date() != testiruum.lopp.date():
              #        aeg = h.str_from_datetime(testiruum.algus, hour0=False) + ' - ' + h.str_from_datetime(testiruum.lopp, hour23=False)
          %>
          % if len(sooritused) > 1:
          ${tos.testiosa.nimi}
          % endif
          % if tos.staatus == const.S_STAATUS_VABASTATUD:
          ${_("vabastatud")}
          % else:
            % if aeg:
            ${aeg}
            % endif
            % if koht_id:
            ${model.Koht.get(koht_id).nimi}
              % if ruum_id:
              ${_("ruum")} ${model.Ruum.get(ruum_id).tahis}
              % endif
             % elif rcd.piirkond_id:
             ${rcd.piirkond.nimi}
             % endif
          % endif
</div>
% endfor
% endif
