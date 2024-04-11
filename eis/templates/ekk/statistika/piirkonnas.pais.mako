<h2>${c.test.nimi}
      % if c.kursus:
        (${model.Klrida.get_str('KURSUS', c.kursus, ylem_kood=c.test.aine_kood).lower()})
      % endif
</h2>
<div class="d-flex pl-1 pb-2">
  <div class="item mr-5">
      ${_("Õppeaine")}: ${c.test.aine_nimi}
  </div>
  <div class="item mr-5">
    ${c.testimiskord.tahised} ${c.testimiskord.millal}
  </div>
  % if not c.test.pallideta:
  <div class="item mr-5">
    ${_("Testi max tulemus")} ${h.fstr(c.test.max_pallid)}p
  </div>
  % endif

  % if len(c.test.testiosad) == 1:
      % for testiosa in c.test.testiosad:
          % if testiosa.piiraeg:
  <div class="item mr-5">
          ${_("Testi kestvus")} ${h.str_from_time(testiosa.piiraeg)}
  </div>
          % endif
      % endfor
    % else:
  <div class="item mr-5">
      <table cellpadding="0" colspacing="0">
      % for testiosa in c.test.testiosad:
      <tr>
        <td>${testiosa.nimi}</td>
        <td width="10"></td>
        <td>
          ${_("Testiosa max tulemus")}
          ${h.fstr(testiosa.max_pallid)}p
        </td>
        <td width="10"></td>
        <td>
          % if testiosa.piiraeg:
          ${_("Testiosa kestvus")} ${h.str_from_time(testiosa.piiraeg)}
          % endif
        </td>
      </tr>
      % endfor
      </table>
  </div>
    % endif

</div>
