% if c.items != '':
${h.pager(c.items, msg_not_found=_("Otsingu tingimustele vastavaid sooritajaid ei leitud"))}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <tr>
    ${h.th_sort('isikukood synnikpv', _("Isikukood või sünniaeg"))}
    ${h.th_sort('eesnimi', _("Eesnimi"))}
    ${h.th_sort('perenimi', _("Perekonnanimi"))}
  </tr>

  % for n, rcd in enumerate(c.items):
  <tr>
      <%
         rcd_url = h.url('admin_eksaminand', id=rcd.id)
      %>
    <td>
      ${h.link_to(rcd.isikukood or h.str_from_date(rcd.synnikpv), rcd_url)}
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

