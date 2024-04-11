${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('filename', _("Failinimi"))}
      <th>${_("Kirjeldus")}</th>
      <th>${_("Testi ID")}</th>
      <th>${_("Õppetase")}</th>
      <th>${_("Haridustase")}</th>
      <th>${_("Lisatud")}</th>
      <th>${_("Avalik alates")}</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <tr>
      <td>
        ${h.link_to(rcd.filename, url=h.url('muud_edit_toofail', id=rcd.id))}
      </td>
      <td>
        ${rcd.kirjeldus}
      </td>
      <td>${rcd.test_id}</td>
      <td>${rcd.oppetase_nimi}</td>
      <td>
        % for r in rcd.toofailitasemed:
        ${r.kavatase_nimi}<br/>
        % endfor
      </td>
      <td>
        ${h.str_from_datetime(rcd.modified)}
      </td>
      <td>
        ${h.str_from_datetime(rcd.avalik_alates)}
      </td>      
      <td>
        ${h.link_to(_("Laadi alla"), h.url('muud_toofail_format', id=rcd.id, format=rcd.fileext))}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif