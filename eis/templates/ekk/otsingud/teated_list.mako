% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      % for h_sort, h_title in c.header:
      ${h.th_sort(h_sort, h_title)}
      % endfor
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <tr>
      <%
        row, url_dlg, url_pdf, k_teema = c.prepare_item(rcd, n, True)
      %>
      % for ind, value in enumerate(row):
      <td>
        % if ind == 5:
        ${h.link_to_dlg(value, url_dlg, title=k_teema or "Teade", width=800)}
        % elif ind == 6 and url_pdf:
        ${h.pdflink_to(url_pdf)}
        % else:
        ${value}
        % endif
      </td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
% endif
