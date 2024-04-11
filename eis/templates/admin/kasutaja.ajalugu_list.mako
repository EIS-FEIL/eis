% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('kasutajagrupp_id',_("Roll"))}
      ${h.th(_("Test"))}
      ${h.th_sort('toimumisaeg.tahised', 'Toimumisaeg')}
      ${h.th_sort('testiruum.algus', _("Aeg"))}
      ${h.th(_("Soorituskoht"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       toimumisaeg = rcd.toimumisaeg
       test = toimumisaeg.testimiskord.test
       can_show = can_update or c.user.has_permission('ekk-testid',const.BT_SHOW,obj=test)
       url_show = h.url('test', id=test.id)
    %>
    <tr>
      <td>${rcd.kasutajagrupp.nimi}</td>
      <td>
        % if can_show:
        ${h.link_to(test.nimi, url_show)}
        % else:
        ${test.nimi}
        % endif
      </td>
      <td>
        ${toimumisaeg.tahised}
      </td>
      <td>
        % if rcd.testiruum and rcd.testiruum.algus:
        ${h.str_from_datetime(rcd.testiruum.algus)}
        % else:
        ${rcd.toimumisaeg.millal}
        % endif
      </td>
      <td>${rcd.testiruum.testikoht.koht.nimi or ''}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
