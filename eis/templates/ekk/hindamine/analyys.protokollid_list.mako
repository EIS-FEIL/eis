${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('koht.nimi', _("Soorituskoht"))}
      ${h.th_sort('testiprotokoll.tahised', _("Protokollirühm"))}
      ${h.th_sort('sisestuskogum.tahis', _("Sisestuskogum"))}
      ${h.th_sort('hindamisprotokoll.liik', _("Hindamise liik"))}
      ${h.th_sort('hindamisprotokoll.staatus', _("Olek"))}
      ${h.th_sort('hindamisprotokoll.staatus1', _("I sisestus"))}
      ${h.th_sort('hindamisprotokoll.staatus2', _("II sisestus"))}
    </tr>
  </thead>
  <tbody>
    % for rcd in c.items:
    <% 
       hpr, tpr_tahised, skogum, koht_nimi = rcd
       testiosa = c.toimumisaeg.testiosa
       if testiosa.vastvorm_kood == const.VASTVORM_KP:
          url_edit = h.url('sisestamine_kirjalikud_hindamised',
                        hindamisprotokoll_id=hpr.id, sisestus='p')
       elif testiosa.vastvorm_kood == const.VASTVORM_SP:
          url_edit = h.url('sisestamine_suulised_hindamised',
                        hindamisprotokoll_id=hpr.id, sisestus='p')
       else:
          url_edit = None
    %>
    <tr>
      <td>${koht_nimi}</td>
      <td>
        % if url_edit:
        ${h.link_to(tpr_tahised, url_edit)}
        % else:
        ${tpr_tahised}
        % endif
      </td>
      <td>${skogum.tahis} ${skogum.nimi}</td>
      <td>${hpr.liik_nimi}</td>
      <td>${hpr.staatus_nimi}</td>
      <td>${hpr.staatus1_nimi}</td>
      <td>${hpr.staatus2_nimi}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
