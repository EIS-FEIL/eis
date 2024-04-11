% if c.items:
<table width="100%" border="0"  class="table table-borderless table-striped">
  <col width="50%"/> 
  <col width="50%"/> 
  <tr>
    ${h.th_sort('nimi', _("Klassifikaator"))}
    ${h.th(_("Tõlge"))}
  </tr>
  % for n, rcd in enumerate(c.items):
  <tr>
    <td>
      ${h.link_to(rcd.nimi, h.url('admin_edit_tklassifikaator', id=rcd.kood, lang=c.lang))}
    </td>
    <td>
      <% tran = rcd.tran(c.lang, False) %>
      ${tran and tran.nimi or ''}
    </td>
  </tr>
  % endfor  
</table>
% endif
