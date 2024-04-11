<%inherit file="/common/dlgpage.mako"/>

${h.form_save(c.item.id)}
<h3>${_("Eksamiserverite klaster")}</h3>
${h.rqexp()}
<div class="form-wrapper pb-1 mb-3">
  <div class="form-group row">
    ${h.flb3(_("Unikaalne kordaja"), rq=True)}
    <div class="col-md-9">
      ${c.item.seqmult}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Sisevõrgu host"), rq=True)}
    <div class="col-md-9">
      ${h.text('f_int_host', c.item.int_host)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Olek"), rq=True)}
    <div class="col-md-9">
      ${h.radio('f_staatus', const.B_STAATUS_KEHTIV,
      checked=c.item.staatus, label=_("Kasutusel"))}
      ${h.radio('f_staatus', const.B_STAATUS_KEHTETU,
      checked=not c.item.staatus, label=_("Pole kasutusel"))}      
    </div>
  </div>
</div>

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
  % if c.item.id:
  ${h.btn_remove(id=c.item.id, confirm=_("Kas oled kindel, et soovid kustutada?"))}
  % endif
  </div>
  <div>
    ${h.submit_dlg(clicked=True)}
  </div>
</div>
${h.end_form()}
