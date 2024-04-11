## Töövaataja rolli muutmine või kustutamine

${h.form_save(c.item.id)}

<div class="m-3">
  <div class="form-group row">
    ${h.flb3(_("Nimi"), 'f_id')}
    <div class="col-md-9" id="f_id">
      ${c.kasutaja.nimi}
      ${h.hidden('kasutaja_id', c.item.kasutaja_id)}
    </div>
  </div>
  
  <div class="form-group row">
    ${h.flb3(_("Kehtib kuni"), 'kehtib_kuni')}
    <div class="col-md-9">
      ${h.date_field('kehtib_kuni', c.item.kehtib_kuni)}
    </div>
  </div>
</div>

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.button(_("Katkesta"), onclick="close_dialog()", level=2)}
  </div>
  <div>
    % if c.item.id:
    ${h.btn_remove(h.url_current('delete', id=c.item.id))}
    % endif
        ${h.submit_dlg(_("Salvesta"))}
  </div>
</div>

${h.end_form()}
