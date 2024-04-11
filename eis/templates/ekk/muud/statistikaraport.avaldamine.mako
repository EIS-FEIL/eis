## Testimiskordade avaldamise seadete muutmise vorm

${h.form_save(None)}
${h.hidden('sub', 'avaldamine')}
${h.hidden('list_url', c.list_url)}
% for kord in c.korrad:
${h.hidden('kord_id', kord.id)}
% endfor

<table width="100%" class="table"  cellpadding="4">
  <tr>
    <td>
      ${h.checkbox('statistika_ekk', 1,
      checked=c.statistika_ekk, 
      label=_("Eksamistatistika siseveebis"))}
    </td>
  </tr>
  <tr>
    <td>
      ${h.checkbox('statistika_avaldet', 1,
      checked=c.statistika_avaldet, 
      label=_("Eksamistatistika avalikus vaates"))}
    </td>
  </tr>
</table>
${h.submit_dlg()}
${h.end_form()}

<script>
$(document).ready(function(){
  $('input#statistika_avaldet').change(function(){
     if($(this).prop('checked'))
        $('input#statistika_ekk').prop('checked', true);
  });
  $('input#statistika_ekk').change(function(){
     if(!$(this).prop('checked'))
        $('input#statistika_avaldet').prop('checked', false);
  });
});
</script>
