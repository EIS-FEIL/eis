
<%include file="/common/message.mako" />
% if c.item.id:
${h.form_save(c.item.id)}
${c.item.kasutaja.nimi}
<% ch = h.colHelper('col-md-6','col-md-6') %>
<div class="form-wrapper-lineborder mb-1">
  <div class="form-group row">
    ${ch.flb(_("Kasutajaroll"))}
    <div class="col">
      ${h.select('kasutajagrupp_id', c.item.kasutajagrupp_id, c.opt.ylesandegrupp)}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Kehtib kuni"))}
    <div class="col">
      ${h.date_field('kehtib_kuni', c.item.kehtib_kuni_ui)}
    </div>
  </div>
</div>
<div class="d-flex">
${h.btn_to(_("Kustuta"), h.url('ylesanne_koostamine_delete_isik', id=c.item.id, ylesanne_id=c.ylesanne.id),
method='post', confirm=_("Kas oled kindel, et soovid kustutada?"), level=2)}
<div class="flex-grow-1 text-right">
${h.submit_dlg()}
</div>
</div>

${h.end_form()}
% endif
