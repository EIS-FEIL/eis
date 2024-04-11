% if c.items != '':
${h.pager(c.items, form='', list_url=h.url_current(partial=1))}
% endif
% if c.items:
<table class="table table-borderless table-striped">
  <thead>
    <tr>
      ${h.th_sort('ylesanne.id', _("ID"))}
      ${h.th_sort('ylesanne.nimi', _("Ülesande nimetus"))}
      ${h.th(_("Muutmisõigusega roll"))}
    </tr>
  </thead>
  <tbody>
    % for n, (y_id, y_nimi) in enumerate(c.items):
    <% 
      url_show = h.url('ylesanne', id=y_id)
      is_muutja = c.is_muutja(y_id)
    %>
    <tr>
      <td>
        ${y_id}
      </td>
      <td>
        ${h.link_to2(y_nimi, url_show)}
      </td>
      <td>
        ${h.sbool(is_muutja)}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
