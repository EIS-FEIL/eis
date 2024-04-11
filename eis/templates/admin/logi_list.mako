% if c.items != '' and not c.items:
${_("Kirjeid ei leitud")}

% elif c.items:
${h.pager(c.items)}

<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
  <tr>
    ${h.th_sort('id', _("ID"))}
    ${h.th_sort('aeg', _("Aeg"))}
    ${h.th_sort('kestus', _("Kestus"))}    
    ${h.th_sort('isikukood', _("Kasutaja"))}
    ${h.th_sort('tyyp', _("Logi tüüp"))}
    ${h.th_sort('kontroller', _("Lehekülg"))}
    ${h.th_sort('tegevus', _("Tegevus"))}
    ${h.th(_("Parameetrid"))}
    ${h.th_sort('sisu,meetod,url', _("Logi"))}
    ${h.th_sort('server_addr', _("Server"))}
    ${h.th_sort('remote_addr', _("Klient"))}
    ${h.th_sort('user_agent', _("Brauser"))}
  </tr>
  </thead>
  <tbody>
  % for n, rcd in enumerate(c.items):
    % if rcd.tyyp == const.LOG_ERROR:
  <tr class="red">
    % else:
  <tr>
    % endif
    <td class="align-top">
      <div>${rcd.request_id}</div>
      <div>${rcd.id}</div>
      <div>${rcd.uuid}</div>
    </td>
    <td nowrap="nowrap" class="align-top">
      ${h.str_from_datetime(rcd.aeg, microseconds=True)}
    </td>
    <td class="align-top">
      ${h.fstr(rcd.kestus)}
    </td>
    <td class="align-top">
      ${rcd.isikukood}
    </td>
    <td class="align-top">${rcd.tyyp_nimi}</td>
    <td class="align-top">
      ${rcd.kontroller}
    </td>
    <td class="align-top">
      ${rcd.tegevus}
    </td>
    <td class="align-top" style="min-width:360px">
      ${rcd.param}
    </td>
    <td class="align-top">
      % if rcd.tyyp in (const.LOG_LOGIN, const.LOG_KOHT):
      ${rcd.sisu.replace('\n','<br/>')}
      % elif rcd.tyyp == const.LOG_XTEE:
      ${h.link_to(_("X-tee sõnum"), h.url_current('download', id=rcd.id, format='xml'))}<br/>
      % elif rcd.tyyp == const.LOG_JSON and rcd.sisu:
      ${h.link_to(_("JSON sõnum"), h.url_current('download', id=rcd.id, format='json'))}<br/>      
      % elif rcd.sisu:
      % if len(rcd.sisu) > 8000:
      ${h.link_to(_("Logi"), h.url_current('download', id=rcd.id, format='txt'))}<br/>
      % else:
      <pre><xmp>${rcd.sisu}</xmp></pre>     
      % endif
      % endif
      <div>${rcd.meetod} ${rcd.url}</div>
    </td>
    <td class="align-top">${rcd.server_addr}</td>
    <td class="align-top">${rcd.remote_addr}</td>
    <td class="align-top">${rcd.user_agent}</td>
  </tr>
  % endfor
  </tbody>
</table>
% endif
