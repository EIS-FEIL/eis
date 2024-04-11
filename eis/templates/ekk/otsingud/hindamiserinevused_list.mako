% if c.toimumisaeg and c.hindamiskogum_id:
<h2>
${c.toimumisaeg.testiosa.test.nimi}
${c.toimumisaeg.tahised}
</h2>

${h.pager(c.items, msg_not_found=_("Hindamiserinevusi ei leitud"), msg_found_one=_("Leiti 1 hindamiserinevus"), msg_found_many=_("Leiti {n} hindamiserinevust"))}
% endif

% if c.items:
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
      % if ind in c.header_bold:
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
