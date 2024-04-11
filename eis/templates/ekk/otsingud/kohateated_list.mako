% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:

<% 
on_testikaupa = c.testiliik in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS, const.TESTILIIK_SISSE) 
on_eksaminandivaataja = c.user.has_permission('eksaminandid', const.BT_SHOW)
%>

<table width="100%" class="table table-borderless table-striped" border="0" >
  <caption>
    % if c.naita == 'epost':
    ${_("Sooritajad, kellele saadetakse teade e-postiga")}
    % elif c.naita == 'tpost':
    ${_("Sooritajad, kellele saadetakse teade postiga")}
    % else:
    ${_("Sooritajad, kelle aadress pole teada")}
    % endif
  </caption>
  <thead>
    <tr>
      ${h.th_sort('kasutaja.isikukood', _("Isikukood"))}
      ${h.th_sort('kasutaja.nimi', _("Nimi"))}
      % if c.naita == 'epost':
      ${h.th_sort('kasutaja.epost', _("E-post"))}
      % endif
      % if on_testikaupa:
      ${h.th_sort('test.nimi', _("Test"))}
      % endif
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <tr>
      <% k = on_testikaupa and rcd.kasutaja or rcd %>
      <td>${k.isikukood}</td>
      <td>
        % if on_eksaminandivaataja:
        ${h.link_to(k.nimi, h.url('admin_eksaminand', id=k.id))}
        % else:
        ${k.nimi}
        % endif
      </td>
      % if c.naita == 'epost':
      <td>${k.epost}</td>
      % endif
      % if on_testikaupa:
      <td>${rcd.test.nimi}</td>
      % endif
    </tr>
    % endfor
  </tbody>
</table>
% endif
