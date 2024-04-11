<%include file="/common/message.mako"/>
${h.form(h.url('ylesanded_update_hulga', id=c.ylesanded_id), method='put')}
${h.hidden('sub', 'tolge')}

<div class="table">
  <div class="row">
    <div class="col-sm-2 col-xs-4 fh">
      ${_("Lisatavad tõlkekeeled")}
    </div>
    <div class="col-sm-10 col-xs-8">
      % for (value, lang_name) in [r[:2] for r in c.opt.SOORKEEL]:
      ${h.checkbox('skeel', value=value, disabled=value in c.keeled, label=lang_name)}
      % endfor
    </div>
  </div>
</div>

${h.submit_dlg()}
${h.end_form()}
