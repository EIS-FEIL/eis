% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('test.id', u'ID')}
      ${h.th_sort('test.nimi', _('Nimetus'))}
      ${h.th_sort('test.aine_KL', _('Õppeaine'))}
      ${h.th_sort('test.keeletase_kood', _('Keeleoskuse tase'))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       url_edit = h.url('edit_konsultatsioon', id=rcd.id)
       url_show = h.url('konsultatsioon', id=rcd.id)
       can_update = c.user.has_permission('konsultatsioonid', const.BT_UPDATE, rcd)
       can_show = can_update or c.user.has_permission('konsultatsioonid', const.BT_SHOW,rcd)
    %>
    <tr>
      % if can_show:
      <td>
        ${h.link_to(rcd.id, url_show)}
      </td>
      <td>
        ${h.link_to(rcd.nimi, url_show)}
      </td>
      % else:
      <td>${rcd.id}</td>
      <td>${rcd.nimi}</td>
      % endif

      <td>${rcd.aine_nimi or ''}</td>
      <td>${rcd.keeletase_nimi or ''}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
