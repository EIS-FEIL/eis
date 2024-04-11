${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('rveksam.nimi', _("Tunnistus"))}
      ${h.th_sort('tunnistus.tunnistusenr', _("Tunnistuse nr"))}
      ${h.th_sort('tunnistus.valjastamisaeg', _("Väljastamisaeg"))}
      ${h.th_sort('rvsooritaja.kehtib_kuni', _("Kehtib kuni"))}
      ${h.th_sort('kasutaja.isikukood', _("Isikukood"))}
      ${h.th_sort('tunnistus.eesnimi', _("Eesnimi"))}
      ${h.th_sort('tunnistus.perenimi', _("Perekonnanimi"))}
      ${h.th_sort('rvsooritaja.keeletase_kood', _("Tase"))}
      ${h.th_sort('sooritaja.test_id', _("Testi ID"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <%
       rvsooritaja, rveksam, tunnistus, kasutaja_ik, test_id = rcd
       url_show = h.url('otsing_rvtunnistus', id=rvsooritaja.id)
    %>
    <tr>
      <td>${rveksam.nimi}</td>
      <td>${tunnistus.tunnistusenr}</td>
      <td>${h.str_from_date(tunnistus.valjastamisaeg)}</td>
      <td>${h.str_from_date(rvsooritaja.kehtib_kuni)}</td>
      <td>${h.link_to(kasutaja_ik, url_show)}</td>
      <td>${h.link_to(tunnistus.eesnimi, url_show)}</td>
      <td>${h.link_to(tunnistus.perenimi, url_show)}</td>
      <td>${rvsooritaja.keeletase_kood}</td>
      <td>${test_id}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
