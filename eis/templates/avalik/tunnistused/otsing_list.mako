${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('kasutaja.nimi',  _('Saaja'))}
      ${h.th_sort('tunnistus.id',  _('Nimetus'))}
      ${h.th_sort('tunnistus.valjastamisaeg',  _('Aeg'))}
      ${h.th_sort('tunnistus.staatus',  _('Olek'))}
      ${h.th( _('Tunnistus'))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       tunnistus, kasutaja, rveksam_nimi = rcd
       url_edit = h.url('tunnistus', id='%s.%s' % (tunnistus.id, tunnistus.fileext))
    %>
    <tr>
      <td>
        ${kasutaja.isikukood}
        ${kasutaja.nimi}
      </td>
      <td>
        ${rveksam_nimi or _('Tunnistus')}
      </td>
      <td>${h.str_from_date(tunnistus.valjastamisaeg)}</td>
      <td>${tunnistus.staatus_nimi}</td>
      <td>
        % if tunnistus.has_file and tunnistus.staatus == const.N_STAATUS_AVALDATUD:
        ${h.link_to(tunnistus.tunnistusenr, url_edit)}
        % elif tunnistus.rvsooritaja and kasutaja.id==c.user.id:
        ${h.link_to(tunnistus.tunnistusenr or ' - ', h.url('tunnistused_rvtunnistus', id=tunnistus.rvsooritaja.id))}
        % else:
        ${tunnistus.tunnistusenr}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
