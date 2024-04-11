<%include file="/common/message.mako"/>
${h.form(h.url('testid_update_hulga', id=c.testid_id), method='put')}
${h.hidden('sub', 'aste')}

<div class="table">
  <div class="row">
    <div class="col-sm-2 col-xs-4 fh">
      ${_("Kooliastmed")}
    </div>
    <div class="col-sm-10 col-xs-8">
        ${h.select_checkbox('v_aste_kood', None, c.opt.astmed())}
    </div>
  </div>
</div>

${h.submit_dlg()}
${h.end_form()}
