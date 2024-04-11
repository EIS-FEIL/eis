% if c.items != '':
${h.pager(c.items, msg_not_found=_("Sooritajaid ei leitud"), msg_found_one=_("Leiti 1 sooritaja"), msg_found_many=_("Leiti {n} sooritajat"))}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <col width="180"/>
  <thead>
    <tr>
      % for h_sort, h_title in c.header:
      ${h.th_sort(h_sort, h_title)}
      % endfor
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <%
      row = c.prepare_item(rcd, n)
      sooritaja_id = rcd[0]
    %>
    <tr>
      % for ind, value in enumerate(row):
      <td>
        % if ind in (1,2):
        ## nimi
        ${h.link_to(value, h.url('regamine', id=sooritaja_id))}
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
