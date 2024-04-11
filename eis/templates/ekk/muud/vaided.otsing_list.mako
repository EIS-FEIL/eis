% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      <th>${_("Välja otsitud")}</th>
      % for item in c.prepare_header():
      % if isinstance(item, tuple):
      ${h.th_sort(item[0], item[1])}
      % else:
      ${h.th(item)}
      % endif
      % endfor
      ${h.th_sort('vaie.tunnistada', _("Tunnistus"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       vaie, sooritaja, k, test, tkord, kool_koht = rcd
       url_edit = h.url('muud_edit_vaie', id=vaie.id)
       test = sooritaja.test
       item = c.prepare_item(rcd)
    %>
    <tr>
      <td>${h.checkbox('vaie_id', vaie.id, checked=vaie.valjaotsitud, class_="vaie_id")}
        % if vaie.valjaotsitud:
        ${h.hidden('endine_id', vaie.id)}
        % endif
      </td>
      % for ind, value in enumerate(item):
      <td>
        % if isinstance(value, list):
        ${', '.join(value)}
        % elif ind in (5,6):
        ${h.link_to(value, url_edit)}
        % else:
        ${value}
        % endif
      </td>
      % endfor
      <td>
        % if vaie.tunnistada:
        ${h.link_to(vaie.tunnistada_nimi, h.url('muud_tunnistused_valjastamised', sooritaja_id=vaie.sooritaja_id))}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif


