% if c.items != '':
${h.pager(c.items, msg_not_found=_("Otsingu tingimustele vastavaid läbiviijaid ei leitud"))}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <tr>
    % for h_sort, h_title in c.header:
    % if h_sort:
    ${h.th_sort(h_sort, h_title)}
    % else:
    ${h.th(h_title)}
    % endif
    % endfor
  </tr>
  % for n, rcd in enumerate(c.items):
      <%
        row, rcd_url = c.prepare_row(rcd)
      %>
  <tr>
    % for ind, value in enumerate(row):
    <td>
       % if ind < 3:
         ${h.link_to(value, rcd_url)}
       % else:
         ${value}
       % endif
    </td>
    % endfor
  </tr>
  % endfor  
</table>
% endif

