% if c.items != '':
${h.pager(c.items)}
% endif
<% is_tr = c.lang and c.lang != const.LANG_XX and c.lang != const.LANG_ET %>
% if c.items:
<table class="table table-borderless table-striped">
  <thead>
    <tr>
      ${h.th_sort('abivahend.kood', _("Kood"))}
      ${h.th_sort('abivahend.nimi', _("Nimetus"))}
      % if is_tr:
      ${h.th(_("Tõlge"))}
      % endif
      <th class="nosort"></th>
      <th class="nosort"></th>
    </tr>
  </thead>
  <tbody>
    % for n, item in enumerate(c.items):
    <%
      if c.user.has_permission('klassifikaatorid', const.BT_UPDATE):
         url = h.url('admin_edit_abivahend', id=item.id, lang=c.lang)
      else:
         url = h.url('admin_abivahend', id=item.id, lang=c.lang)
    %>
    <tr>
      <td>
        ${item.kood}
      </td>
      <td>
        ${h.link_to_dlg(item.nimi, url, title=_("Abivahend"), size='lg')}
      </td>
      % if is_tr:
      <td>
        <% tran = item.tran(c.lang, False) %>
        ${tran and tran.nimi or ''}
      </td>        
      % endif
      <td>
        % if item.kirjeldus:
              <% 
                 onclick = "open_dlg({dialog_id:'vahend_%s', iframe_url:'%s', width:'%s', height:'%s'})" % (item.id, h.url('admin_abivahend', id=item.id, sub='vahend', lang=c.lang), item.laius or 600, item.korgus or 400) 
                 ikoon = item.ikoon_url or '/static/abivahendid/muu_ikoon.png'
              %>
              ${h.image(src=ikoon, onclick=onclick, alt=item.nimi, title=item.nimi, height=32)}
       % endif
      </td>
      <td>
        % if item.kehtib:
        ${h.badge_success(_("Kasutusel"))}
        % else:
        ${h.badge_secondary(_("Pole kasutusel"))}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

