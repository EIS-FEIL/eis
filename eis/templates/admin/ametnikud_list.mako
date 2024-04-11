% if c.items != '':
${h.pager(c.items, msg_not_found=_("Otsingu tingimustele vastavaid kasutajaid ei leitud"))}
% endif
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
  % for n, rcd in enumerate(c.items):
      <%
        row = c.prepare_item(rcd, n)
        rcd_url = h.url('admin_ametnik', id=rcd.id)
      %>
  <tr>
    % for ind, value in enumerate(row):
    <td>
       % if ind < 3 and rcd_url:
         ${h.link_to(value, rcd_url)}
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

