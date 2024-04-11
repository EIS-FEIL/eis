% if c.items != '':
${h.pager(c.items, msg_not_found=_("Märkustega soorituskohti ei leitud"), msg_found_one=_("Leiti 1 märkustega soorituskoht"), msg_found_many=_("Leiti {n} märkustega soorituskohta"))}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <col width="30%"/>
  <col/>
  <thead>
    <tr>
      ${h.th_sort('koht.nimi', _("Asukoht"))}
      ${h.th_sort('testikoht.markus', _("Märkused"))}
    </tr>
  </thead>
  <tbody>
    % for k_nimi, markus in c.items:
    <tr>
      <td>${k_nimi}</td>
      <td>${markus}
    </tr>
    % endfor
  </tbody>
</table>
% endif
