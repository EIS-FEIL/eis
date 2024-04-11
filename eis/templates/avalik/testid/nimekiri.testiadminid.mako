<%
  grupp_id = const.GRUPP_T_ADMIN
  labiviijad = [r for r in c.testiruum.labiviijad if r.kasutajagrupp_id == grupp_id]
%>
% if labiviijad:
<table class="table table-striped tablesorter">
  <caption>
    ${_("Testi administraatorid")}
  </caption>
  <thead>
    <tr>
      ${h.th(_('Isikukood'))}
      ${h.th(_('Nimi'))}
      % if c.can_update:
      ${h.th('', sorter='false', width="20px")}
      % endif
    </tr>
  </thead>
  <tbody>
    % for roll in labiviijad:
    <tr>
      <td>${roll.kasutaja.isikukood_hide}</td>
      <td>${roll.kasutaja.nimi}</td>
      % if c.can_update:
      <td>
        ${h.remove(h.url('test_nimekiri_delete_otsiadmin', test_id=c.test.id, nimekiri_id=c.nimekiri.id, testiruum_id=c.testiruum.id, id=roll.id))}
      </td>
      % endif
    </tr>
    % endfor    
  </tbody>
</table>
% endif
% if c.can_update:
${h.btn_to_dlg(_("Lisa testi administraator"),
h.url('test_nimekiri_otsiadminid', test_id=c.test.id, nimekiri_id=c.nimekiri.id, testiruum_id=c.testiruum.id),
title=_("Testi administraatorite lisamine"), level=2)}
% endif
