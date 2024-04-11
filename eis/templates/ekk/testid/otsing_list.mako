% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<% can_hulgi = c.user.has_permission('testhulgi', const.BT_UPDATE) %>
${h.form(url=h.url('testid_new_hulga'), method='get')}
<table width="100%" class="table table-borderless table-striped" border="0" >
  <col width="20px"/>
  <thead>
    <tr>
      <th>
        ${h.checkbox('t_all', 1, title=_("Vali kõik"))}
      </th>
      ${h.th_sort('test.id', _("ID"))}
      ${h.th_sort('test.nimi', _("Nimetus"))}
      ${h.th_sort('test.testiliik_kood', _("Testi liik"))}
      ${h.th_sort('test.periood_kood', _("Periood"))}
      ${h.th_sort('test.staatus', _("Olek"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       url_edit = h.url('edit_test', id=rcd.id)
       url_show = h.url('test', id=rcd.id)
       can_update = c.user.has_permission('ekk-testid', const.BT_UPDATE, rcd)
       can_show = can_update or c.user.has_permission('ekk-testid', const.BT_SHOW,rcd)
    %>
    <tr>
      <td>
        % if can_update or can_hulgi:
        ${h.checkbox('t_id', rcd.id, onclick="toggle_t()", class_='nosave t_id', title=_("Vali rida"))}
        % endif
      </td>
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

      <td>${rcd.testiliik_nimi or ''}</td>
      <td>${rcd.periood_nimi or ''}</td>
      <td>${rcd.staatus_nimi or ''}</td>
    </tr>
    % endfor
  </tbody>
</table>
<br/>
<span id="bulk">
  ${h.submit(_("Muuda hulgi"))}
</span>
<script>
  function toggle_t()
  {
     var visible = ($('input:checked.t_id').length > 0);
     $('span#bulk').toggle(visible);
  }
  $(document).ready(function(){
     toggle_t();
     $('input[name="t_all"]').click(function(){
         $('input[name="t_id"]').prop('checked', $(this).prop('checked'));
         toggle_t();
     });
  });
</script>
${h.end_form()}

% endif
