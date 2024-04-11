% if c.items != '':
${h.pager(c.items, msg_not_found=_('Sooritatuks märgitud testitöid ei leitud'), msg_found_one=_('Leiti 1 testitöö'), msg_found_many=_('Leiti {n} testitööd'))}
% endif
% if c.items and not c.sisestuskogum_id:
${h.alert_error(_("Skannitav sisestuskogum puudub"))}
% elif c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('testiprotokoll.tahised', _('Protokollirühm'))}
      ${h.th_sort('sooritus.tahised', _('Testitöö'))}
      ${h.th_sort('sisestusolek.staatus', _('Olek'))}      
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       tos, solek, tpr_tahised = rcd 
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
      <td>${tos.tahised}<!-- s ${tos.id}--></td>
      <td>
        ${c.opt.H_STAATUS.get(staatus)}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
