## -*- coding: utf-8 -*- 
${h.pager(c.items,msg_not_found=_("Otsingu tingimustele vastavaid teste ei leitud"),
          msg_found_one=_("Leiti 1 test"), 
          msg_found_many=_("Leiti {n} testi"))}
% if c.items:
<table width="100%" border="0"  class="table table-borderless table-striped" border="0" cellpadding="4" cellspacing="1">
  <thead>
    <tr>
      ${h.th_sort('test.id', _("Testi ID"))}
      ${h.th_sort('test.nimi', _("Nimetus"))}
      ${h.th(_("Õppeaine"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       test, sooritaja = rcd
       sooritaja_id = sooritaja and sooritaja.id or 0
       if sooritaja_id:
          url_edit = h.url('sooritamine_alustamine', test_id=test.id, sooritaja_id=sooritaja_id)
       else:
          url_edit = h.url('sooritamine_test', test_id=test.id)
    %>
    <tr>
      <td>${test.id}</td>
      <td>
        % if url_edit:
        ${h.link_to(test.nimi, url_edit)}
        % else:
        ${test.nimi}
        % endif
      </td>
      <td>${test.aine_nimi}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
