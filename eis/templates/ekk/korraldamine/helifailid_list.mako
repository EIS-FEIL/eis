% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <col width="180"/>
  <thead>
    <tr>
      % for key, label in c.prepare_header():
      ${h.th_sort(key, label)}
      % endfor
    </tr>
  </thead>
  <tbody>
    % for rcd in c.items:
    <tr>
    % for value in c.prepare_item(rcd):
    <td>${value}</td>
    % endfor
    </tr>
    % endfor
  </tbody>
</table>
% endif
