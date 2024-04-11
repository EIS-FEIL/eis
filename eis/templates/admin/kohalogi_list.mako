% if c.items != '' and not c.items:
${_("Kirjeid ei leitud")}

% elif c.items:
${h.pager(c.items)}

<table width="100%" class="table table-borderless table-striped" border="0" >
  <tr>
    ${h.th_sort('koht.id', _("ID"))}
    ${h.th_sort('koht.nimi', _("Nimi"))}
    ${h.th_sort('kohalogi.allikas', _("Allikas"))}
    ${h.th_sort('kasutaja.nimi', _("Kasutaja"))}
    ${h.th_sort('kohalogi.modified', _("Muudatuse aeg"))}
    ${h.th_sort('kohalogi.vali', _("Muudetud väli"))}
    ${h.th_sort('kohalogi.vana', _("Vana väärtus"))}
    ${h.th_sort('kohalogi.uus', _("Uus väärtus"))}
  </tr>

  % for n, rcd in enumerate(c.items):
  <% l, koht_nimi, muutja_nimi = rcd %>
  <tr>
    <td>
      ${l.koht_id}
    </td>
    <td>
      ${h.link_to(koht_nimi, h.url('admin_koht', id=l.koht_id))}
    </td>
    <td>${l.allikas_nimi}</td>
    <td>
      ${muutja_nimi}
    </td>
    <td>
      ${h.str_from_datetime(l.modified)}
    </td>
    <td>${l.vali}</td>
    <td>
      ${l.vana}
    </td>
    <td>
      ${l.uus}
    </td>
  </tr>
  % endfor
</table>
% endif
