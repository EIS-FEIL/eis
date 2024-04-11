% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('kasutaja.perenimi kasutaja.eesnimi', _("Nimi"))}
      ${h.th_sort('kasutaja.isikukood', _("Isikukood"))}
      ${h.th_sort('koht.nimi', _("Kool"))}
    </tr>
  </thead>
  <tbody>
    % for (k_nimi, isikukood, kool_nimi) in c.items:
    <tr>
      <td>${k_nimi}</td>
      <td>${isikukood}</td>
      <td>${kool_nimi}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
