## -*- coding: utf-8 -*- 
% if c.items != '':
${h.pager(c.items,
msg_not_found=_('Töökogumikke ei leitud'),
msg_found_one=_('Leiti üks töökogumik'),
msg_found_many=_('Leiti {n} töökogumikku'))}
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
        row = c.prepare_item(rcd, n)
        if c.is_jagatud:
           rcd_url = h.url('tookogumik', id=rcd.id)
        else:
           rcd_url = h.url('edit_tookogumik', id=rcd.id)
      %>
  <tr>
    % for ind, value in enumerate(row):
    <td>
       % if ind < 2 and rcd_url:
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
