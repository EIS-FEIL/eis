% if c.items:
${model.Klrida.get_lang_nimi(c.lang)}
<table class="table tablesorter iline" >
  <thead>
    <tr>
      ${h.th(_("Suunaja"))}
      ${h.th(_("Õppeasutus"))}
      ${h.th(_("Nimekirjad"))}
      ${h.th(_("Lahendajad"))}
    </tr>
  </thead>
  <tbody>
    % for item in c.items:
    <tr>
      % for value in item:
      <td>${value}</td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
% endif
