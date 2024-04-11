% if c.items:
${h.pager(c.items)}

<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      % for r in c.prepare_header():
      ${h.th(r)}
      % endfor
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <tr>
    <% row = c.prepare_item(rcd, n) %>
    % for ind, value in enumerate(row):
    <td>
      ${value}
    </td>
    % endfor
    </tr>
    % endfor
  </tbody>
</table>
% endif
