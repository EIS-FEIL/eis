## -*- coding: utf-8 -*- 
${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      % for r in c.header:
      <% sort_field, title = r[:2] %>
      % if sort_field:
      ${h.th_sort(sort_field, title)}
      % else:
      <th scope="col" sorter="false">
        ${title}
        <% helpable_id = len(r) > 2 and r[2] or None %>
        % if helpable_id:
        <span class="helpable" id="${helpable_id}"></span>
        % endif
      </th>
      % endif
      % endfor
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):    
    <tr>
      <%
        item, testiruum_id, badge = c.prepare_item(rcd, True)
        test_id = item[0]
        url_pooleli = h.url('test_ylesandehindamised', test_id=test_id, testiruum_id=testiruum_id)
      %>
      % for ind, v in enumerate(item):
      <td>
        % if ind == 0:
          <div class="dot-badge"><span class="badge badge-${badge}"> </span>
            ${v}
          </div>
        % elif ind in (1,2):
        ${h.link_to(v, url_pooleli)}
        % else:
        ${v}
        % endif
      </td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
% endif
