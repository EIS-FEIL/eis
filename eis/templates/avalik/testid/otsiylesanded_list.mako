<span id="progress"></span>
% if c.items != '' and len(c.items) == 0:
 ${_("Otsingu tingimustele vastavaid ülesandeid ei ole")}
% else:
${h.pager(c.items,
          msg_not_found=_("Otsingu tingimustele vastavaid ülesandeid ei leitud"),
          msg_found_one=_("Leiti üks tingimustele vastav ülesanne"),
          msg_found_many=_("Leiti {n} tingimustele vastavat ülesannet"),
          listdiv='#listdiv_yl',
          form='#yl_search')}
<table width="100%" class="table table-borderless table-striped" border="0" >
  <tr>
    <th>${h.checkbox('all_id', 1, title=_("Vali kõik"))}</th>
    ${h.th_sort('id', 'ID')}
    ${h.th_sort('nimi', _('Nimetus'))}
    ${h.th_sort('max_pallid', _('Pallid'))}
    ${h.th_sort('arvutihinnatav', _('Arvutiga hinnatav'))}
    ${h.th_sort('staatus', _('Olek'))}
  </tr>
  % for item in c.items:
  <tr>
    <td>
      ${h.checkbox('ylesanne_id', item.id, title=_("Vali rida {s}").format(s=item.id))} 
    </td>
    <td>${item.id}</td>
    <td>${h.link_to(item.nimi, h.url('lahendamine1', id=item.id), target='_blank')}</td>
    <td>${h.fstr(item.get_max_pallid())}</td>
    <td>${h.sbool(item.arvutihinnatav)}</td>
    <td>${item.staatus_nimi}</td>
  </tr>
  % endfor
</table>
% endif
<br/>
% if c.items:
<span id="add" class="invisible">
${h.submit(_('Salvesta'))}
</span>
% endif
