% if c.items != '':
${h.pager(c.items, msg_not_found=_('Toimumisaegu ei leitud'), msg_found_one=_('Leiti 1 toimumisaeg'), msg_found_many=_('Leiti {n} toimumisaega'))}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped tablesorter" border="0" >
  <thead>
    <tr>
      ${h.th(_('Test'))}
      ${h.th(_('Tähis'))}
      ${h.th(_('Toimumise aeg'))}
      ${h.th(_('Vastamise vorm'))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <tr>
      <td>${rcd.testiosa.test.nimi}</td>
      <td>${rcd.tahised}</td>
      <td>
        ${h.link_to(rcd.millal, h.url('sisestamine_turvakotinumbrid', toimumisaeg_id=rcd.id))}
      </td>
      <td>
        ${rcd.testiosa.vastvorm_nimi}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
