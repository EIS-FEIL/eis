% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <caption>
    ${_("III hindamise nõusolekud")}
  </caption>
  <thead>
    <% header, items = c.prepare_items(c.items) %>
    <tr>
      % for sort_field, title in header:
        % if sort_field:
        ${h.th_sort(sort_field, title)}
        % else:
        ${h.th(title)}
        % endif
      % endfor
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(items):
    <tr>
      % for s in rcd:
      <td>${s}</td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
% endif
