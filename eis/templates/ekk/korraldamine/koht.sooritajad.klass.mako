${h.form_save(None, form_name="form_save_klass")}
${h.hidden('sub', 'klass')}
% for s_id in c.sooritused_id:
${h.hidden('s_id', s_id)}
% endfor
<div class="mb-2">
<div class="form-group row">
  ${h.flb3(_("Kool"))}
  <div class="col">
    ${c.koht.nimi}
  </div>
</div>
<div class="form-group row">
  ${h.flb3(_("Klass"))}
  <div class="col">
    ${h.select('klass', c.klass, const.EHIS_KLASS, wide=False)}    
  </div>
</div>
<div class="form-group row">
  ${h.flb3(_("Paralleel"))}
  <div class="col">
    ${h.text5('paralleel', c.paralleel)}
  </div>
</div>
<div class="form-group row">
  ${h.flb3(_("Õppekeel"))}
  <div class="col">
    ${h.select('oppekeel', c.oppekeel, const.EHIS_LANG_OPT, wide=False)}
  </div>
</div>
</div>

<div class="d-flex">
  <div class="flex-grow-1">
    ${h.submit_dlg(_("Eemalda õppimisandmed"), op="eemalda", level=2)}
  </div>
  <div>
    ${h.submit_dlg(_("Salvesta"))}
  </div>
</div>
${h.end_form()}
