${h.form_save(None)}
${h.hidden('sub', 'mail')}
<table width="100%" class="table" >
  <tr>
    <td>
      ${_("Teate pealkiri")}
      <br/>
      ${h.text('subject', c.subject)}
    </td>
  </tr>
  <tr>
    <td>
      ${_("Teate sisu")}<br/>
      ${h.textarea('body', c.body, rows=20)}
    </td>
  </tr>
</table>


${h.hidden('labiviijad_id', '')}
<script>
  $(function(){
    var f = $('input.labiviija_id:checked');
    var buf = "";
    for(var i=0; i<f.length; i++) buf += ','+f.eq(i).val();
    $('#labiviijad_id').val(buf);
  });
</script>

${h.submit(_("Saada"))}
${h.end_form()}
