<%inherit file="/common/dlgpage.mako"/>
<div class="body-avaleheteade">
<div style="height:0">
<div id="m_ckeditor_top" class="ckeditor-top-float"></div>
</div>
<%include file="/common/message.mako"/>

${h.form_save(c.item.id)}
${h.rqexp()}
<div class="form-wrapper-lineborder mb-2">
  <div class="form-group">
    ${h.flb(_("Pealkiri"), 'f_pealkiri', rq=True)}
    ${h.text('f_pealkiri', c.item.pealkiri, maxlength=100)}
  </div>
  <div class="form-group">
    ${h.flb(_("Sisu"), 'f_sisu', rq=True)}
    ${h.textarea('f_sisu', c.item.sisu, class_="editable")}
  </div>
  <div class="form-group ml-5">
    ${h.flb(_("Rohkem infot"), 'f_lisasisu')}
    ${h.textarea('f_lisasisu', c.item.lisasisu, class_="editable")}
  </div>

  <div class="bg-gray-50">
  ${h.flb(_("Teate omadused"))}
  <div class="row">
    <div class="col-sm-6">
      ${h.flb(_("Teate tüüp"), 'f_tyyp', rq=True)}
      % for value, label in model.Avaleheinfo.opt_tyyp():
      <div>
        ${h.radio('f_tyyp', value, checkedif=c.item.tyyp, label=label)}
      </div>
      % endfor
    </div>
    <div class="col-sm-6">
      ${h.flb(_("Kellele kuvatakse"), 'kellele')}
      <% kellele = list((c.item.kellele or '').split(',')) %>
      % for value, label in model.Avaleheinfo.opt_kellele():
      <div>
        ${h.checkbox('kellele', value, checkedif=kellele, label=label)}
      </div>
      % endfor
    </div>
  </div>
  </div>
  <div class="p-3">
  ${h.flb(_("Kuvamise ajavahemik"))}
  <div class="row">
    <div class="col-sm-6">
      ${h.flb(_("Algus"), 'f_alates', rq=True)}
      ${h.date_field('f_alates', c.item.alates)}
    </div>
    <div class="col-sm-6">
      ${h.flb(_("Lõpp"), 'f_kuni')}
      ${h.date_field('f_kuni', c.item.kuni_ui)}
    </div>
  </div>
  </div>
</div>

<div class="d-flex mt-2">
  <div class="flex-grow-1">
    ${h.submit_dlg(_("Salvesta koopiana"), op='copy', level=2)}
  </div>
  ${h.submit_dlg()}
</div>
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
