% if c.items:
${h.pager(c.items)}
<% can_update = c.user.has_permission('lglitsentsid', const.BT_UPDATE) %>
<table width="100%" class="table table-borderless table-striped" border="0" >
  <tr>
    ${h.th_sort('isikukood', _("Isikukood"))}
    ${h.th_sort('eesnimi', _("Eesnimi"))}
    ${h.th_sort('perenimi', _("Perekonnanimi"))}
    ${h.th_sort('epost', _("E-post"))}    
  </tr>

  % for n, rcd in enumerate(c.items):
  <tr>
    <%
      if can_update:
         rcd_url = h.url('edit_logopeed', id=rcd.id)
      else:
         rcd_url = h.url('logopeed', id=rcd.id)
    %>
    <td>
      ${h.link_to(rcd.isikukood, rcd_url)}
    </td>
    <td>
      ${h.link_to(rcd.eesnimi, rcd_url)}
    </td>
    <td>
      ${h.link_to(rcd.perenimi, rcd_url)}
    </td>
    <td>
      ${rcd.epost}
    </td>
  </tr>
  % endfor  
</table>
% endif

