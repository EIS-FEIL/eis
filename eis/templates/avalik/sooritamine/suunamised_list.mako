## -*- coding: utf-8 -*- 
% if c.avaldamistase == const.AVALIK_POLE:
${h.pager(c.items,msg_not_found=_("Sulle sooritamiseks suunatud teste ei leitud"),
          msg_found_one=_("Leiti 1 sulle suunatud test või töö"), 
          msg_found_many=_("Leiti {n} sulle suunatud testi või tööd"))}
% else:
${h.pager(c.items,msg_not_found=_("Otsingu tingimustele vastavaid teste ei leitud"),
          msg_found_one=_("Leiti 1 test"), 
          msg_found_many=_("Leiti {n} testi"))}
% endif

% if c.items:
<table width="100%" border="0"  class="table table-borderless table-striped tablesorter" border="0" cellpadding="4" cellspacing="1">
  <thead>
    <tr>
      ${h.th(_("Testi ID"))}
      % if c.olen_tugiisik:
      ${h.th(_("Sooritaja"))}
      % endif
      ${h.th(_("Nimetus"))}
      ${h.th(_("Õppeaine"))}
      ${h.th(_("Lahendamiseks suunaja"))}
      ${h.th(_("Sooritatav kuni"))}
      ${h.th(_("Olek"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       test, sooritaja = rcd
       sooritaja_id = sooritaja and sooritaja.id or 0
       url_edit = h.url('sooritamine_alustamine', test_id=test.id, sooritaja_id=sooritaja_id)
       nimekiri = sooritaja.nimekiri
       esitaja = nimekiri and nimekiri.esitaja_kasutaja
    %>
    <tr>
      <td>${test.id}</td>
      % if c.olen_tugiisik:
      <td>${sooritaja.eesnimi} ${sooritaja.perenimi}</td>
      % endif
      <td>
        % if url_edit:
        ${h.link_to(test.nimi, url_edit)}
        % else:
        ${test.nimi}
        % endif
      </td>
      <td>${test.aine_nimi}</td>
      <td>
        % if esitaja:
        ${esitaja.nimi}
        % endif
      </td>
      <td>
        % if nimekiri and nimekiri.kuni:
        ${h.str_from_date(nimekiri.kuni)}
        % endif
      </td>
      <td>${sooritaja.staatus_nimi}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
