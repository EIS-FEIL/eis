${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('kasutaja.isikukood',  _('Isikukood'))}
      ${h.th_sort('tunnistus.eesnimi',  _('Eesnimi'))}
      ${h.th_sort('tunnistus.perenimi',  _('Perekonnanimi'))}
      ${h.th_sort('test.nimi',  _('Testi ID'))}
      ${h.th_sort('test.nimi',  _('Test'))}
      ${h.th( _('Aeg'))}
    </tr>
  </thead>
  <tbody>
    % for n, sooritus in enumerate(c.items):
    <%
       sooritaja = sooritus.sooritaja
       url_show = h.url('test_psyhtulemus', test_id=sooritaja.test_id, testiruum_id=sooritus.testiruum_id or 0, id=sooritus.id)
       kasutaja = sooritaja.kasutaja
       test = sooritaja.test
    %>
    <tr>
      <td>${h.link_to(kasutaja.isikukood, url_show)}</td>
      <td>${h.link_to(sooritaja.eesnimi, url_show)}</td>
      <td>${h.link_to(sooritaja.perenimi, url_show)}</td>
      <td>${test.id}</td>
      <td>${test.nimi}</td>
      <td>${sooritaja.millal}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
