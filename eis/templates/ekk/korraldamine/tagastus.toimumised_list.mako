${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('koht.nimi', _("Soorituskoht"))}
      ${h.th_sort('testikoht.tahised', _("Tähis"))}
      ${h.th_sort('toimumisprotokoll.lang', _("Keel"))}
      ${h.th_sort('toimumisprotokoll.staatus', _("Olek"))}
      <th></th>
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <%
       toimumisprotokoll, koht_nimi = rcd
    %>
    <tr>
      <td>${koht_nimi}</td>
      <td>${toimumisprotokoll.tahistus}</td>
      <td>${toimumisprotokoll.lang_nimi}</td>
      <td>${toimumisprotokoll.staatus_nimi}</td>
      <td>${h.link_to(_("Sisesta"), h.url('sisestamine_protokoll_osalejad',
        toimumisprotokoll_id=toimumisprotokoll.id), target='_blank')}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
