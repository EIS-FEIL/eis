% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped tablesorter" border="0" >
  <thead>
    <tr>
      ${h.th(_('Test'))}
      ${h.th(_('Toimumisaja tähis'))}
      ${h.th(_('Toimumise aeg'))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <tr>
      <td>${rcd.testiosa.test.nimi}</td>
      <td>${rcd.tahised}</td>
      <td>
        ${h.link_to(rcd.millal, h.url('sisestamine_valjastamine_hindamispaketid', toimumisaeg_id=rcd.id))}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
