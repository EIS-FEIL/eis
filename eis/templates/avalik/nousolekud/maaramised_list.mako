## -*- coding: utf-8 -*- 
% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('kasutajagrupp.nimi', _('Roll'))}
      ${h.th_sort('test.nimi', _('Test'))}
      ${h.th_sort('toimumisaeg.tahised', _('Toimumisaeg'))}
      ${h.th_sort('testiruum.algus', _('Aeg'))}      
      ${h.th_sort('koht.nimi', _('Soorituskoht'))}
      ${h.th_sort('testikoht.sooritajatearv', _('Testisooritajate arv'))}
      ${h.th_sort('labiviija.tasu', _('Tasu'))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <tr>
      <td>${rcd.kasutajagrupp.nimi}</td>
      <td>
        ${rcd.toimumisaeg.testimiskord.test.nimi}
      </td>
      <td>
        ${rcd.toimumisaeg.tahised}
      </td>
      <td>
        % if rcd.testiruum and rcd.testiruum.algus:
        ${h.str_from_datetime(rcd.testiruum.algus)}
        % else:
        ${rcd.toimumisaeg.millal}
        % endif
      </td>
      <td>
        % if rcd.testikoht:
        ${rcd.testikoht.koht.nimi}
        % endif
      </td>
      <td>
        % if rcd.testiruum:
          <% 
             d = rcd.testiruum.get_sooritajatearvud()
             total = d and d.get('total')
          %>
          ${total}
        % endif
      </td>
      <td>${h.mstr(rcd.tasu)}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
