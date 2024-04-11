${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('filename', _("Failinimi"))}
      <th>Pilt</th>
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <tr>
      <td>
        ${h.link_to(rcd.filename, url=h.url('ylesanne_yhisfail', id=rcd.id))}
      </td>
      <td>
        % if rcd.is_image:
        ${h.image(h.literal('shared/%s' % rcd.filename), 'Pilt', height=50)}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
