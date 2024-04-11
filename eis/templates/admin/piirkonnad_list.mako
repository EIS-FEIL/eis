${h.btn_new(h.url('admin_new_piirkond'))}
% if c.items:
${h.pager(c.items)}
<table width="100%" class="table table-borderless table-striped" border="0" >
  <tr>
    ${h.th_sort('nimi', _("Nimetus"))}
    ${h.th_sort('kehtib', _("Kehtiv"))}
  </tr>

  % for n, rcd in enumerate(c.items):
  <tr>
    <td>
      ${h.link_to(rcd.nimi, h.url('admin_piirkond', id=rcd.id))}
    </td>
    <td>
      ${h.link_to(rcd.staatus_nimi, h.url('admin_piirkond', id=rcd.id))}
    </td>
  </tr>
  % endfor
  
</table>
% endif

