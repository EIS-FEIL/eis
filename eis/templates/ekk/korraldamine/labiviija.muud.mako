<table width="100%" class="table table-borderless table-striped tablesorter"  id="table_isikud">
  <caption>${_("Läbiviija {s} osalemine testsessioonil").format(s=c.kasutaja.nimi)}</caption>
  <thead>
    <tr>
      ${h.th(_("Test"))}
      ${h.th(_("Toimumisaeg"))}
      ${h.th(_("Soorituskoht"))}
      ${h.th(_("Roll"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% labiviija, toimumisaeg, test = rcd %>
    <tr>
      <td>
        ${test.nimi}
      </td>
      <td>
        ${h.str_from_date(toimumisaeg.alates)} -
        ${h.str_from_date(toimumisaeg.kuni)}
      </td>
      <td>
        % if labiviija.testikoht:
          ${labiviija.testikoht.koht.nimi}
          % if labiviija.testiruum and labiviija.testiruum.ruum:
          ${labiviija.testiruum.ruum.tahis}
          % endif
        % endif
      </td>
      <td>
        ${labiviija.kasutajagrupp.nimi}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
<script>
  $(document).ready(function(){
     $('table#table_isikud').tablesorter();
  });
</script>
