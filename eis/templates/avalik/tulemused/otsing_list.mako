## -*- coding: utf-8 -*- 
% if c.items != '':
${h.pager(c.items,msg_not_found=_("Sooritatud teste ei leitud"))}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('test.nimi', _("Test"))}
      ${h.th_sort('test.testiliik_kood', _("Testi liik"))}
      ${h.th_sort('sooritaja.algus', _("Aeg"))}
      ${h.th_sort('sooritaja.pallid', _("Tulemus"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <%
      test = rcd.test
      testimiskord = rcd.testimiskord
    %>
    <tr>
      <td>
        ${h.link_to(test.nimi, h.url('tulemus', id=rcd.id))}
      </td>
      <td>${test.testiliik_nimi}</td>
      <td>${rcd.millal}</td>
      <td>
        <% visibility = rcd.tulemus_nahtav(None, False, const.ISIK_SOORITAJA, test, testimiskord) %>
        % if not test.pallideta and visibility.is_k:
        ${rcd.get_tulemus()}
        % else:
        ${rcd.staatus_nimi}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
