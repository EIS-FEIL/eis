<%include file="/common/message.mako"/>
${h.form_save(c.item.id)}
<table width="100%" class="table" >
  <tr>
    <td class="fh">
      ${_("Grupi nimetus")}
    </td>
  </tr>
  <tr style="height:150px">
    <td>
      ##${h.ckeditor('yg_nimi', '', 'basic', rows=2)}
      ${h.textarea('yg_nimi', '', ronly=False,class_='editable')}
    </td>
  </tr>
</table>
${h.submit_dlg()}
${h.hidden('vyy_id', '', class_="new-grp-vyy")}
${h.end_form()}
<script>
$(function(){
    destroy_old_ckeditor();
    var inputs = $('#yg_nimi.editable');
    init_ckeditor(inputs, 'aa', '${request.localizer.locale_name}', 'basic');


  var vyy_id = $('input[name="vy_id"]:checked')
    .map(function(){return this.value}).get().join();
  $('input.new-grp-vyy').val(vyy_id);
});
</script>
