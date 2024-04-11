${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('sooritus.tahised', _("Testisooritus"))}
      ${h.th_sort('hindamine.tyhistatud hindamine.staatus', _("Hindamise olek"))}
      ${h.th_sort('hindamine.pallid', _("Hindaja pallid"))}
      ${h.th_sort('hindamisolek.staatus', _("Hindamiskogumi olek"))}
      ${h.th_sort('hindamisolek.pallid', _("Lõplikud pallid"))}
      ${h.th_sort('hindamisolek.hindamistase', _("Hindamistase"))}
      ${h.th_sort('hindamisolek.hindamisprobleem', _("Probleem"))}
      ${h.th_sort('koht.nimi', _("Soorituskoht"))}
      <th sorter="false"></th>
    </tr>
  </thead>
  <tbody>
    % for rcd in c.items:
    <% tos, holek, hindamine, koht_nimi = rcd %>
    <tr>
      <td>
        % if hindamine and hindamine.staatus == const.H_STAATUS_SUUNATUD:
        ${tos.tahised}
        % elif c.testiosa.vastvorm_kood == const.VASTVORM_SH:
        ${h.link_to(tos.tahised, h.url('hindamine_hindajavaade_shindamised', toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.hindaja.id, sooritus_id=tos.id))}
        % else:
        ${h.link_to(tos.tahised, h.url('hindamine_hindajavaade_hkhindamised', toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.hindaja.id, sooritus_id=tos.id))}
        % endif
      </td>
      <td>
        % if hindamine.tyhistatud:
        ${_("Tühistatud")}
        % elif hindamine:
        ${hindamine.staatus_nimi}
        % else:
        ${_("Alustamata")}
        % endif
      </td>
      <td>
        % if hindamine:
        ${h.fstr(hindamine.pallid)}
        % endif
      </td>
      <td>${holek.staatus_nimi}</td>
      <td>${h.fstr(holek.pallid)}</td>
      <td>${holek.hindamistase}</td>
      <td>
        ${holek.selgitus or holek.hindamisprobleem_nimi}
      </td>
      <td>${koht_nimi}</td>
      <td>
        % if hindamine and hindamine.staatus == const.H_STAATUS_HINDAMATA:
        ${h.remove(h.url_current('delete', id=hindamine.id))}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

