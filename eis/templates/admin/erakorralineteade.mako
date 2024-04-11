<%inherit file="/common/dlgpage.mako"/>
<div class="body-avaleheteade">
<div style="height:0">
<div id="m_ckeditor_top" class="ckeditor-top-float"></div>
</div>
<%include file="/common/message.mako"/>

${h.form_save(c.item.id, h.url_current('update'))}
<div class="p-3">
  <div class="form-group">
    ${h.flb(_("Sisu"), 'f_sisu')}
    ${h.textarea('f_sisu', c.item.sisu, class_="editable")}
  </div>
</div>
<div class="p-3">
  ${h.checkbox1('kehtiv', checked=c.item.kuni>=model.date.today(), label=_("Aktiivne"))}
</div>
<div class="d-flex mt-2">
  ${h.submit_dlg()}
</div>
${h.hidden('f_pealkiri', 'Erakorraline teade')}
${h.hidden('f_lisasisu', '')}
${h.hidden('f_tyyp', c.item.tyyp)}
${h.hidden('f_kellele', c.item.kellele)}
${h.hidden('f_alates', h.str_from_date(c.item.alates))}
${h.hidden('f_kuni', h.str_from_date(c.item.kuni))}
${h.end_form()}
</div>
<script>
function reinit_ckeditor()
{
    destroy_old_ckeditor();
    var inputs = $('.body-avaleheteade textarea.editable');
    init_ckeditor(inputs, 'm_ckeditor_top', '${request.localizer.locale_name}', '${h.ckeditor_toolbar('basic')}', null, null, 'body16');
}
$(function(){
reinit_ckeditor();
});
</script>
