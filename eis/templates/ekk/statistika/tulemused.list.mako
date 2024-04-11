${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      % for h_sort, h_title in c.header:
      % if h_sort:
      ${h.th_sort(h_sort, h_title)}
      % elif h_title == _("Keskmine") and c.aasta_alates != c.aasta_kuni:      
      <th>Keskmine
        <%
           link_title = '<img src="/static/images/chart.png" alt="Diagramm" width="20px"/>'
        %>
        ${h.link_to_dlg(h.literal(link_title), h.url_current(sub='keskmised', getargs=True),
        title=_("Keskmine tulemus"), width=650, size='md')}
      </th>
      % else:
      ${h.th(h_title)}
      % endif
      % endfor
      <th></th>
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <%
       row, d_url = c.prepare_row(rcd)
    %>
    <tr>
      % for value in row:
      <td>${value}</td>
      % endfor
      <td>
        % if d_url:
        <%
           link_title = '<img src="/static/images/chart.png" alt="Diagramm" width="20px"/>'
        %>
        ${h.link_to_dlg(h.literal(link_title), d_url, title=_("Tulemuste jaotus"), width=900, size='lg')}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
