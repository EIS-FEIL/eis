${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('testimiskord.aasta', _("Aasta"))}
      ${h.th_sort('aine_kl.nimi', _("Õppeaine"))}
      ${h.th(_("Eksaminandide arv"))}
      ${h.th(_("Vaiete arv"))}
      ${h.th(_("Vaiete %"))}
      ${h.th(_("Vaietest vastatud %"))}
      ${h.th(_("Tõsteti"))}
      ${h.th(_("Ei muudetud"))}
      ${h.th(_("Langetati"))}
      ${h.th(_("Langetati %"))}
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
      % if len(row) == 5:
      <td colspan="5"></td>
      % endif
    </tr>
    % endfor
  </tbody>
</table>
% endif
