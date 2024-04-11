% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <tr>
    ${h.th_sort('kasutajagrupp.id', _("ID"))}
    ${h.th_sort('kasutajagrupp.nimi', _("Nimi"))}
    % if c.oigus_id:
    ${h.th(_("Õigus"))}
    % endif
  </tr>

  % for n, rcd in enumerate(c.items):
  <%
    if c.oigus_id:
       rcd, bitimask = rcd
  %>
  <tr>
    <td width="100px">
      ${rcd.id}
    </td>
    <td>
       ${h.link_to(rcd.nimi, h.url('admin_kasutajagrupp', id=rcd.id))}
    </td>
    % if c.oigus_id:
    <td>
      % if bitimask & const.BT_ALL == const.BT_ALL:
      ${_("Muutmine")}
      % elif bitimask & const.BT_VIEW == const.BT_VIEW:
      ${_("Vaatamine")}
      % endif
    </td>
    % endif
  </tr>
  % endfor
</table>
% endif

