% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<table class="table table-borderless table-striped">
  <thead>
    <tr>
      ${h.th_sort('abivahend.kood', _("Kood"))}
      ${h.th_sort('abivahend.nimi', _("Nimetus"))}
      <th class="nosort"></th>
      <th class="nosort"></th>
    </tr>
  </thead>
  <tbody>
    % for n, item in enumerate(c.items):
    <%
      url = h.url('admin_edit_abivahend', id=item.id)
    %>
    <tr>
      <td>
        ${item.kood}
      </td>
      <td>
        ${h.link_to_dlg(item.nimi, url, title=_("Abivahend"))}
      </td>
      <td>
        % if item.kirjeldus:
              <% 
                 onclick = "open_dlg({dialog_id:'vahend_%s', iframe_url:'%s', width:'%s', height:'%s'})" % (item.id, h.url('admin_abivahend', id=item.id, sub='vahend'), item.laius or 600, item.korgus or 400) 
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

