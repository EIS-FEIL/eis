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
    <% prev_time = None %>
    % for n, rcd in enumerate(c.items):
    <%
      curr_time = rcd[0]
      cls = ''
      if prev_time:
          diff = curr_time - prev_time
          if diff.days * 86400 + diff.seconds > c.step * 60:
              # eristame vahe, mil ei ole yhtki sooritajat
              cls = "firstrow"
      prev_time = curr_time 
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
