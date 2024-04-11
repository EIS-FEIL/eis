${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      % for srt, title in c.prepare_header():
      % if srt:
      ${h.th_sort(srt, title)}
      % else:
      ${h.th(title)}
      % endif
      % endfor
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <%
      sooritaja = rcd[0]
      url_edit = h.url_current('show', id=sooritaja.id)
    %>
    <tr>
      % for col, value in enumerate(c.prepare_item(rcd)):
      % if col == 3:
      <td>${h.link_to(value, url_edit)}</td>
      % else:
      <td>${value}</td>
      % endif
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
% endif