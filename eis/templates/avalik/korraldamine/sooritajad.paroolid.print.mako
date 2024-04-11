<div id="pcontents">
${c.testimiskord.test.nimi}<br/>
${c.toimumisaeg.tahised}
${c.testikoht.koht.nimi}

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
</div>
<br/>
${h.button(_("Trüki"), onclick="doprint()")}
<iframe id="piframe" name="piframe" style="display:none"></iframe>
<script>
function doprint()
{
  $('#piframe').contents().find('body').html($('#pcontents').html());
  window.frames.piframe.print();  
}
</script>
