${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <col/>
  <col/>
  <col/>
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
    <% prev_osa = None %>
    % for n, rcd in enumerate(c.items):
    <%
      cls = ''
      if prev_osa != rcd[0]:
         if prev_osa:
            cls = "firstrow"
         prev_osa = rcd[0]
    %>
    <tr class="${cls}">
      % for col, value in enumerate(c.prepare_item(rcd)):
      <td>${value}</td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
% endif
