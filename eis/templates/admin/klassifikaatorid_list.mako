% if c.items:
<table width="100%" border="0"  class="table table-striped">
  <tr>
    ${h.th_sort('nimi', _("Klassifikaator"))}
  </tr>
  % for n, rcd in enumerate(c.items):
  <tr>
    <td>
      ${h.link_to(rcd.nimi, h.url('admin_edit_klassifikaator', id=rcd.kood))}
    </td>
  </tr>
  % endfor  
</table>
% endif
