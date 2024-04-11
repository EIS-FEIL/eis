% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  % if c.step == 1:
  <col width="160"/>
  <col width="160"/>
  % else:
  <col width="70"/>
  <col width="200"/>
  % endif
  <col/>
  <thead>
    <tr>
      % for title in c.prepare_header():
      ${h.th(title)}
      % endfor
    </tr>
  </thead>
  <tbody>
    <% prev_time = None %>
    % for n, rcd in enumerate(c.items):
    <%
      dt = rcd[0]
      rcd = c.prepare_item(rcd)
      if c.step == 30:
         cls = dt.month == 1 and 'firstrow' or ''
      elif c.step == 7:
         cls = ''
      else:
         cls = dt.weekday() == 0 and 'firstrow' or ''
    %>
    <tr class="${cls}">
      % for col, value in enumerate(rcd):
      <td>${value}</td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
% endif
