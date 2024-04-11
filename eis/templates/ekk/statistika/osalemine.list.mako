${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('testimiskord.aasta', _("Aasta"))}
      ${h.th_sort('aine_kl.nimi', _("Õppeaine"))}
      % if c.tkord:
      ${h.th_sort('test.id', _("Test"))}
      ${h.th_sort('testimiskord.tahis', _("Testimiskord"))}
      % endif
      ${h.th(_("Registreerunute arv"))}
      ${h.th(_("Puudus"))}
      ${h.th(_("Puudumise %"))}
      ${h.th(_("Eemaldatud"))}
      ${h.th(_("Eemaldatute %"))}
      ${h.th(_("Sooritajad"))}
      ${h.th(_("Sooritanute %"))}
      <th>${_("Keskmine tulemus")}</th>
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <%
       row = c.prepare_row(rcd)
    %>
    <tr>
      % for value in row:
      <td>${value}</td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
% endif
