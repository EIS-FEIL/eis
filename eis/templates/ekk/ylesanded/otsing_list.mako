% if c.items != '':
${h.pager(c.items,msg_not_found=_("Otsingu tingimustele vastavaid ülesandeid ei leitud"),
          msg_found_one=_("Leiti üks tingimustele vastav ülesanne"),
          msg_found_many=_("Leiti {n} tingimustele vastavat ülesannet"))}
% endif
% if c.items:
<% can_hulgi = c.user.has_permission('ylhulgi', const.BT_UPDATE) %>
${h.form(url=h.url('ylesanded_new_hulga'), method='get')}
<table class="table table-borderless table-striped">
  <col width="20px"/>
  <thead>
    <tr>
      <th scope="col">
        ${h.checkbox('y_all', 1, title=_("Vali kõik"))}
      </th>
      ${h.th_sort('ylesanne.id', _("ID"))}
      ${h.th_sort('ylesanne.nimi', _("Nimetus"))}
      ${h.th(_("Õppeaine"))}
      ${h.th(_("Alateema"))}
      ${h.th_sort('ylesanne.max_pallid', _("Toorpunktid"))}
      <th scope="col">Koostaja</th>
##      <th scope="col"></th>
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       url_edit = h.url('edit_ylesanne', id=rcd.id)
       url_show = h.url('ylesanne', id=rcd.id)
       can_update = c.user.has_permission('ylesanded', const.BT_UPDATE,rcd)
       can_show = can_update or c.user.has_permission('ylesanded',const.BT_SHOW, rcd)
    %>
    <tr>
      <td>
        % if can_update or can_hulgi:
        ${h.checkbox('yl_id', rcd.id, onclick="toggle_yl()", class_='nosave yl_id', title=_("Vali rida {s}").format(s=rcd.id))}
        % endif
      </td>
      % if can_show:
      <td>
        ${rcd.id}
      </td>
      <td>
        % if rcd.is_encrypted:
        ${h.link_to2(_("Krüptitud ülesanne"), url_show)}        
        % else:
        ${h.link_to2(rcd.nimi, url_show)}
        % endif
      </td>
      % else:
      <td>${rcd.id}</td>
      <td>${rcd.nimi}</td>
      % endif
      <% yained = list(rcd.ylesandeained) %>
      <td>
        % for yaine in yained:
        ${yaine.aine_nimi}<br/>
        % endfor
      </td>
      <td>
        % for yaine in yained:
        % for r in yaine.ylesandeteemad:
        % if r.alateema_kood:
        ${r.alateema_nimi}<br/>
        % endif
        % endfor
        % endfor
      </td>
      <td>${h.fstr(rcd.max_pallid)}</td>
      <td>
        % for yi in rcd.ylesandeisikud:
          % if yi.kasutajagrupp_id==const.GRUPP_Y_KOOSTAJA:
          ${yi.kasutaja.nimi}
          % endif
        % endfor
      </td>
##      <td nowrap>
##      % if can_update:
##      ${h.show(url_show)}
##      ${h.edit(url_edit)}
##      % elif can_show:
##      ${h.show(url_show)}
##      % endif
##      </td>
    </tr>
    % endfor
  </tbody>
</table>
<br/>
<span id="bulk">
  ${h.submit(_("Muuda hulgi"))}
  ${h.submit(_("Ekspordi"), id="export")}
</span>

<script>
  function toggle_yl()
  {
     var visible = ($('input:checked.yl_id').length > 0);
     $('span#bulk').toggle(visible);
  }
  $(function(){
     toggle_yl();
     $('input[name="y_all"]').click(function(){
         $('input.yl_id').prop('checked', $(this).prop('checked'));
         toggle_yl();
     });
  });
</script>
${h.end_form()}

% endif
