% if c.items != '' and not c.items:
${_("Kirjeid ei leitud")}

% elif c.items:
${h.pager(c.items)}

<table width="100%" class="table table-borderless table-striped table-align-top">
  <thead>
  <tr>
    ${h.th_sort('id', _("ID"))}
    ${h.th_sort('aeg', _("Aeg"))}
    ${h.th(_("Kestus"))}
    ${h.th_sort('client', _("Klient"))}
    ${h.th_sort('userid', _("Isikukood"))}
    ${h.th_sort('service', _("Teenuse nimi"))}
    ${h.th(_("Sisend"))}
    ${h.th(_("Väljund"))}
    ${h.th_sort('server_addr', _("Server"))}
  </tr>
  </thead>
  <tbody>
  % for n, rcd in enumerate(c.items):
  <tr>
    <td>
      ${rcd.id}
    </td>
    <td nowrap="nowrap" >
      ${h.str_from_datetime(rcd.aeg, microseconds=True)}
    </td>
    <td nowrap="nowrap">
      % if rcd.algus:
      ${(rcd.aeg-rcd.algus).total_seconds()}
      % endif
    </td>
    <td>
      ${rcd.client}
    </td>
    <td>${rcd.userid}</td>
    <td>
      ${rcd.service}
    </td>
    <td>
      % if rcd.tyyp == rcd.TYYP_JSON:
      ${h.link_to(_("Sisend"), h.url_current('download', id=rcd.id, format='in.json'))}
      % else:
      ${h.link_to(_("Sisend"), h.url_current('download', id=rcd.id, format='in.xml'))}
      % endif
    </td>
    <td>
      % if rcd.tyyp == rcd.TYYP_JSON:
      ${h.link_to(_("Väljund"), h.url_current('download', id=rcd.id, format='out.json'))}
      % else:
      ${h.link_to(_("Väljund"), h.url_current('download', id=rcd.id, format='out.xml'))}
      % endif
    </td>
    <td>${rcd.server_addr}</td>
  </tr>
  % endfor
  </tbody>
</table>
% endif
