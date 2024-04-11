${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('kasutaja_1.perenimi kasutaja_1.eesnimi', _('Läbiviija I'))}
      ${h.th_sort('kasutaja_2.perenimi kasutaja_2.eesnimi', _('Läbiviija II'))}
      ${h.th_sort('hindamiskogum.tahis', _('Hindamiskogum'))}
      ${h.th_sort('labiviija_1.lang', _('Keel'))}
      ${h.th_sort('labiviija_1.staatus', _('Olek'))}
      ${h.th_sort('labiviija_1.planeeritud_toode_arv', _('Planeeritud hinnata'))}
      ${h.th_sort('labiviija_1.toode_arv', _('Antud hinnata'))}
    </tr>
  </thead>
  <tbody>
    % for rcd in c.items:
    <%
       kogum, hindaja1, hindaja2 = rcd
       url_edit = h.url('sisestamine_valjastamine_hindajaymbrikud',
            toimumisaeg_id=c.toimumisaeg.id, hindaja_id=hindaja1.id)
    %>
    <tr>
      <td>${h.link_to('%s %s' % (hindaja1.kasutaja.isikukood,
      hindaja1.kasutaja.nimi), url_edit)}</td>
      <td>
      % if hindaja2:
      ${hindaja2.kasutaja.isikukood} ${hindaja2.kasutaja.nimi}
      % endif
      </td>
      <td>${kogum.tahis}</td>
      <td>${model.Klrida.get_lang_nimi(hindaja1.lang)}</td>
      <td>
        ${hindaja1.staatus_nimi}
      </td>
      <td>
        ${hindaja1.planeeritud_toode_arv}
      </td>
      <td>
        ${hindaja1.toode_arv}
        % if hindaja2:
        / ${hindaja2.toode_arv}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
