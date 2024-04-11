% if c.items != '' and not c.items:
${_("Ettepanekuid ei ole")}

% elif c.items:
${h.pager(c.items)}

<table width="100%" class="table table-borderless table-striped" border="0" >
  <tr>
    % for sort, title in c.header:
    ${h.th_sort(sort, title)}
    % endfor
  </tr>
  % for rcd, koht_nimi in c.items:
  <tr>
    <td>
      ${h.str_from_datetime(rcd.created)}
    </td>
    <td nowrap="nowrap">
      ${rcd.saatja}
    </td>
    <td>${rcd.epost}</td>
    <td>
      ${koht_nimi}
    </td>
    <td>${rcd.url and h.link_to(rcd.url, rcd.url) or ''}</td>
    <td>
      ${h.link_to_dlg(rcd.teema, h.url_current('edit', id=rcd.id), width=700, title=rcd.teema)}
    </td>
    <td>
      ${h.sbool(rcd.ootan_vastust)}
    </td>
    <td>
      ${h.sbool(rcd.on_vastatud)}
    </td>
  </tr>
  % endfor
</table>
% endif
