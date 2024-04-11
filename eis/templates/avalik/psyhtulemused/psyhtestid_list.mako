${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('test.id', u'ID')}
      ${h.th_sort('test.nimi', _('Nimetus'))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       url_edit = h.url('test', id=rcd.id)
    %>
    <tr>
      <td width="70px">
        ${rcd.id}
      </td>
      <td>
        ${h.link_to(rcd.nimi, url_edit)}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
