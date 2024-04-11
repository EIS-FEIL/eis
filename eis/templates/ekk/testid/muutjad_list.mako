${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('aeg', _("Aeg"))}
      ${h.th_sort('kasutaja_id', _("Tegija"))}
      ${h.th_sort('liik', _("Liik"))}
      ${h.th_sort('vanad_andmed', _("Vanad andmed"))}
      ${h.th_sort('uued_andmed', _("Uued andmed"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <tr>
      <td>${h.str_from_datetime(rcd.aeg, True)}</td>
      <td>${rcd.kasutaja and rcd.kasutaja.nimi or ''}</td>
      <td>${rcd.liik}</td>
      <td>${rcd.vanad_andmed}</td>
      <td>${rcd.uued_andmed}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

