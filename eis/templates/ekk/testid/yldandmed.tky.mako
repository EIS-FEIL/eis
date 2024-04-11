<%inherit file="/common/dlgpage.mako"/>
## taustakysitluse õpetaja ja õpilase testi sidumine
<%include file="/common/message.mako"/>
${h.form_save(c.item.id)}
${h.hidden('sub', 'tky')}
<div class="my-2">
<div class="form-group row">
  ${h.flb3(_("Testi ID"), 'opetaja_test_id')}
  <div class="col">
    ${h.posint5('opetaja_test_id', c.test2 and c.test2.id)}
  </div>
</div>
</div>
${h.submit_dlg()}
${h.end_form()}
