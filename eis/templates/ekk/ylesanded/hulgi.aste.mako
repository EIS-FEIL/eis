<%include file="/common/message.mako"/>
${h.form(h.url('ylesanded_update_hulga', id=c.ylesanded_id), method='put')}
${h.hidden('sub', 'aste')}

<div class="table">
  <div class="row">
    <div class="col-sm-2 col-xs-4 fh">
      ${_("Peamine kooliaste")}
    </div>
    <div class="col-sm-10 col-xs-8">
      <% aste_opt = c.opt.astmed() %>
      ${h.select_radio('f_aste_kood', None, aste_opt)}
    </div>
  </div>
  <div class="row">
    <div class="col-sm-2 col-xs-4 fh">
      ${_("Kooliastmed")}
    </div>
    <div class="col-sm-10 col-xs-8">
        ${h.select_checkbox('v_aste_kood', None, aste_opt)}
    </div>
  </div>
</div>

${h.submit_dlg()}
${h.end_form()}
