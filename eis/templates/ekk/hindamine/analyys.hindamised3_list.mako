${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      % for h_sort, h_title in c.header:
      % if h_sort:
      ${h.th_sort(h_sort, h_title)}
      % else:
      ${h.th(h_title)}
      % endif
      % endfor
    </tr>
  </thead>
  <tbody>
    % for rcd in c.items:
    <tr>
      <%
         item, url_edit = c.prepare_item(rcd)
      %>
      % for n, value in enumerate(item):
      <td>
      % if n == 0:
      ${h.link_to(value, url_edit)}
      % elif n == 7:
      <b>${value}</b>
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
