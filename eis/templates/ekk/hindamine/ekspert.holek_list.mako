${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('sooritus.tahised', _("Testitöö tähis"))}
      ${h.th(_("Hindamiskogum"))}
      ${h.th(_("Hindamisprobleem"))}
      ${h.th(_("Eksperthindamine"))}
      ${h.th(_("Ekspert"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       tos, holek, hindamine = rcd
       url_edit = h.url('hindamine_ekspert_kogum',  toimumisaeg_id=c.toimumisaeg.id, id=tos.id)
    %>
    <tr>
      <td>${h.link_to(tos.tahised, url_edit)}</td>
      <td>${holek.hindamiskogum.tahis}</td>
      <td>${holek.selgitus}</td>
      <td>${hindamine and hindamine.staatus_nimi}</td>
      <td>${hindamine and hindamine.hindaja_kasutaja and hindamine.hindaja_kasutaja.nimi}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
