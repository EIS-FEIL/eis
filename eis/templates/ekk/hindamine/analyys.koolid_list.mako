% if len(c.sooritused) > 0:
<table class="table table-borderless table-striped tablesorter" width="100%" >
  <caption>${_("Testitööd")}</caption>
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
    % for ind, rcd in enumerate(c.sooritused):
    <%
      row = c.prepare_item(rcd, ind)
      tos = rcd[0]
      rcd_url = h.url('hindamine_analyys_testitoo', toimumisaeg_id=c.toimumisaeg_id, id=tos.id)
    %>
    <tr>
      % for ind2, value in enumerate(row):
      <td>
        % if ind2 == 0:
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
