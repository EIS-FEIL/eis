${h.form_save(c.item.id, multipart=True)}
<div>
  <div class="form-group row">
    ${h.flb3(_("Fail"))}
    <div class="col">
      ${h.file('filedata', value='Fail')}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Ruum"))}
    <div class="col">
      ${h.select('testiruum_id', c.item.testiruum_id, c.opt_testiruumid)}
    </div>
  </div>
</div>  
${h.submit(_('Salvesta'), onclick='set_spinner()')}
${h.end_form()}
