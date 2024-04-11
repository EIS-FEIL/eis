% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('kasutaja.isikukood', _("Isikukood"))}
      ${h.th_sort('kasutaja.perenimi kasutaja.eesnimi', _("Nimi"))}
      ${h.th_sort('kasutaja.epost', _("E-posti aadress"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <tr>
      <% k_id, k_ik, k_synnikpv, k_nimi, k_epost = rcd %>
      <td>${k_ik}</td>
      <td>${k_nimi}</td>
      <td>${k_epost}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
