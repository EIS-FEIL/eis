<div id="pcontents">
${c.test.nimi}<br/>
% if c.toimumisaeg:
${c.toimumisaeg.tahised}
% endif

% if c.testikoht:
${c.testikoht.koht.nimi},
% endif
% if c.testiruum and c.testiruum.nimekiri:
${c.testiruum.nimekiri.nimi}
% elif c.testiruum.ruum:
${_("ruum")} ${c.testiruum.ruum.tahis}
% endif

<table border="1" cellpadding="8"  style="border-collapse:collapse">
  <tr>
    <th>${_("Isikukood")}</th>
    <th>${_("Eesnimi")}</th>
    <th>${_("Perekonnanimi")}</th>
    <th>${_("Testiparool")}</th>
  </tr>
  % for (isikukood, eesnimi, perenimi, pwd) in c.items:
  <tr>
    <td>${isikukood}</td>
    <td>${eesnimi}</td>
    <td>${perenimi}</td>
    <td>${pwd}</td>
  </tr>
  % endfor
</table>
<p>
  ${_("Genereeritud {n} parooli").format(n=len(c.items))}
</p>
</div>
<div class="text-right">
  ${h.button(_("Trüki"), onclick="doprint()")}
</div>
<iframe id="piframe" name="piframe" style="display:none"></iframe>
<script>
function doprint()
{
  $('#piframe').contents().find('body').css('margin', '80px').html($('#pcontents').html());
  window.frames.piframe.print();  
}
</script>
