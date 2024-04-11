% if not c.items and c.items != '':
${_("Otsingu tingimustele vastavaid soorituskohti ei leitud")}
% elif c.items:
${h.pager(c.items)}

<% can_send = c.user.has_permission('kohad', const.BT_UPDATE) %>

<table width="100%" class="table table-borderless table-striped" border="0" >
  <tr>
    % if can_send:
    <th></th>
    % endif
    ${h.th_sort('koht.kool_id', _("EHIS ID"))}
    ${h.th_sort('koht.nimi', _("Nimetus"))}
    ${h.th_sort('koht.staatus', _("Kehtiv"))}
  </tr>

  % for n, rcd in enumerate(c.items):
  <tr>
    % if can_send:
    <td>${h.checkbox('koht_id', rcd.id, class_="koht", onclick="toggle_send()")}</td>
    % endif
    <td>${rcd.kool_id}</td>
    <td>
      % if c.user.has_permission('kohad', const.BT_SHOW, piirkond_id=rcd.piirkond_id):
      ${h.link_to(rcd.nimi, h.url('admin_koht', id=rcd.id))}
      % else:
      ${rcd.nimi}
      % endif
    </td>
    <td>
      ${rcd.staatus_nimi}
    </td>
  </tr>
  % endfor
  
</table>
% endif

