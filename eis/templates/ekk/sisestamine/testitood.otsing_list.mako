% if c.items != '':
${h.pager(c.items, msg_not_found=_('Testitöid ei leitud'), msg_found_one=_('Leiti 1 testitöö'), msg_found_many=_('Leiti {n} testitööd'))}
% endif
% if c.items and not c.sisestuskogum_id:
${h.alert_error(_("Sisestuskogum puudub"))}
% elif c.items:
<%
   c.olen_parandaja = c.user.has_permission('parandamine',const.BT_UPDATE)
   tk = c.toimumisaeg.testimiskord
%>
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('testiprotokoll.tahised', _('Protokollirühm'))}
      % if tk.sisestus_isikukoodiga:
      ${h.th_sort('koht.nimi', _('Soorituskoht'))}
      % endif
      ${h.th_sort('sooritus.tahised', _('Testitöö'))}
      % if tk.sisestus_isikukoodiga:
      ${h.th_sort('kasutaja.isikukood', _('Isikukood'))}
      % endif
      ${h.th_sort('sisestusolek.staatus1', _('I sisestamine'))}
      % if c.toimumisaeg.kahekordne_sisestamine:
      ${h.th_sort('sisestusolek.staatus2', _('II sisestamine'))}
      % endif
      % if c.olen_parandaja:
      ${h.th_sort('sisestusolek.staatus', _('Parandamine'))}      
      % endif
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       tos, solek, tpr_tahised, k_nimi = rcd 
       
       staatus1 = solek and solek.staatus1 or const.H_STAATUS_HINDAMATA
       staatus2 = solek and solek.staatus2 or const.H_STAATUS_HINDAMATA
       staatus = solek and solek.staatus or const.H_STAATUS_HINDAMATA
    %>
    <tr>
      <td>
        % if tpr_tahised:
         ## kuvame tähise viimased kaks kohta ehk KOHT-PROTOKOLL
        ${'-'.join(tpr_tahised.split('-')[-2:])}
        % endif
        <!-- solek ${solek and solek.id} -->
      </td>
      % if tk.sisestus_isikukoodiga:
      <td>${k_nimi}</td>
      % endif
      <td>${tos.tahised}<!-- s ${tos.id}--></td>
      % if tk.sisestus_isikukoodiga:
      <td>${tos.sooritaja.kasutaja.isikukood}</td>
      % endif
      
    % if tpr_tahised:
      <td>
        ## avada saan siis, kui olen ise I sisestaja 
        ## või seda veel pole ja ma pole II sisestaja
        % if not solek or solek.can_sis1(c.user.id):
        ${h.link_to(c.opt.H_STAATUS.get(staatus1), 
        h.url('sisestamine_vastused', sooritus_id=tos.id, sisestus=1, sisestuskogum_id=c.sisestuskogum_id))}
        % else:
        ${c.opt.H_STAATUS.get(staatus1)}
        % endif
      </td>
      % if c.toimumisaeg.kahekordne_sisestamine:
      <td>
        % if not solek or solek.can_sis2(c.user.id):
        ${h.link_to(c.opt.H_STAATUS.get(staatus2), 
        h.url('sisestamine_vastused', sooritus_id=tos.id, sisestus=2, sisestuskogum_id=c.sisestuskogum_id))}
        % else:
        ${c.opt.H_STAATUS.get(staatus2)}
        % endif
      </td>
      % endif
      % if c.olen_parandaja:
      <td>
        % if solek and (solek.staatus1 or solek.staatus2):
        ## avada saan siis, kui mul on sisestuste parandamise õigus
        ${h.link_to(c.opt.H_STAATUS.get(staatus),h.url('sisestamine_vastused',
        sooritus_id=tos.id, sisestus='p', sisestuskogum_id=c.sisestuskogum_id),
        style=staatus==const.H_STAATUS_POOLELI and "color:red" or None)}
        % else:
        ${c.opt.H_STAATUS.get(staatus)}
        % endif
      </td>
      % endif
    % endif
    </tr>
    % endfor
  </tbody>
</table>
% endif
