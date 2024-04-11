<table class="table table-borderless table-striped tablesorter" width="100%">
  <thead>
    <tr>
      ${h.th(_('Muutja'))}
      ${h.th(_('Aeg'))}
      ${h.th(_('Mida muudeti'))}
      ${h.th(_('Vana väärtus'))}
      ${h.th(_('Uus väärtus'))}
    </tr>
  </thead>
  <tbody>
    % for rcd in c.hindamine.sisestuslogid:
    <tr>
      <td>${rcd.kasutaja.nimi}</td>
      <td>${h.str_from_datetime(rcd.aeg)}</td>
      <td>
        % if rcd.liik == rcd.LIIK_PALLID and rcd.ylesandehinne:
        ${_("Ülesanne")} ${rcd.ylesandehinne.ylesandevastus.testiylesanne.seq}
          % if rcd.aspektihinne:
          aspekt "${rcd.aspektihinne.hindamisaspekt.aspekt_nimi}"
          % endif
        % else:
        ${rcd.liik_nimi}
        % endif
      </td>
      <td>${rcd.vana}</td>
      <td>${rcd.uus}</td>
    </tr>
    % endfor
  </tbody>
</table>
