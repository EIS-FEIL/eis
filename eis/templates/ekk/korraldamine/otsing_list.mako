${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('testimiskord.test_id', _("Testi ID"))}
      ${h.th_sort('test.nimi', _("Testi nimetus"))}
      ${h.th_sort('toimumisaeg.tahised', _("Toimumisaeg"))}
      ${h.th_sort('toimumisaeg.alates', _("Aeg"))}
      ${h.th_sort('testiosa.vastvorm_kood', _("Vastamise vorm"))}
      ${h.th(_("Soorituskohata"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
      url_edit = h.url('korraldamine_soorituskohad', toimumisaeg_id=rcd.id)
      testimiskord = rcd.testimiskord
      test = testimiskord.test
      can_show = c.user.has_permission('korraldamine', const.BT_SHOW, test)
      row = c.prepare_item(rcd, n)
    %>
    <tr>
      <td>${testimiskord.test_id}</td>
      <td>
        % if can_show:
        ${h.link_to(test.nimi, url_edit)}
        % else:
        ${test.nimi}
        % endif
      </td>
      % for ind, value in enumerate(row[2:]):
      <td>${value}</td>
      % endfor
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
