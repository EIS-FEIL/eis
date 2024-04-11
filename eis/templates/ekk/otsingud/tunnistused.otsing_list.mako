${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('kasutaja.nimi', _("Saaja"))}
      ${h.th(_("Tunnistuse liik"))}
      ${h.th_sort('tunnistus.valjastamisaeg', _("Aeg"))}
      ${h.th_sort('tunnistus.staatus', _("Olek"))}
      ${h.th(_("Tunnistus"))}
      ${h.th_sort('tunnistus.alus', _("Alus"))}
      ${h.th_sort('tunnistus.pohjendus tunnistus.tyh_pohjendus', _("Põhjendus"))}
      ${h.th_sort('tunnistusekontroll.korras tunnistusekontroll.viga', _("Kooskõla kontroll"))}
      ${h.th_sort('tunnistusekontroll.seisuga', _("Kontrollitud"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       tunnistus, kasutaja, rveksam_nimi, ktr = rcd
       url_edit = h.url('otsing_tunnistus', id='%s.%s' % (tunnistus.id, tunnistus.fileext))
    %>
    <tr>
      <td>
        ${kasutaja.isikukood}
        ${kasutaja.nimi}
      </td>
      <td>${rveksam_nimi or tunnistus.testiliik_nimi}</td>
      <td>${h.str_from_date(tunnistus.valjastamisaeg)}</td>
      <td>${tunnistus.staatus_nimi}</td>
      <td>
        % if tunnistus.has_file:
        ${h.link_to(tunnistus.tunnistusenr, url_edit)}
        % else:
        ${tunnistus.tunnistusenr}
        % endif
      </td>
      <td>${tunnistus.alus}</td>
      <td>
        % if tunnistus.pohjendus:
        ${tunnistus.pohjendus}<br/>
        % endif
        ${tunnistus.tyh_pohjendus}
      </td>
      % if ktr:
      <td>${ktr.korras and _("Korras") or ktr.viga or _("Viga")}</td>
      <td>${h.str_from_datetime(ktr.seisuga)}</td>
      % else:
      <td></td>
      <td></td>
      % endif
    </tr>
    % endfor
  </tbody>
</table>
% endif
