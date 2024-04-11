## -*- coding: utf-8 -*- 
## $Id: kasutajad_list.mako 544 2016-04-01 09:07:15Z ahti $         
% if c.items:
${h.pager(c.items)}
<table width="100%" class="table table-borderless table-striped" border="0" >
  <tr>
    ${h.th_sort('isikukood', _("Isikukood"))}
    ${h.th_sort('eesnimi', _("Eesnimi"))}
    ${h.th_sort('perenimi', _("Perekonnanimi"))}
  </tr>

  % for n, rcd in enumerate(c.items):
  <tr>
      <%
         rcd_url = h.url('admin_kasutaja', id=rcd.id)
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
  </tr>
  % endfor  
</table>
% endif

