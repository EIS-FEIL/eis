<%include file="/common/message.mako"/>
${h.form(h.url('testid_update_hulga', id=c.testid_id), method='put')}
${h.hidden('sub', 'testiliik')}

<div class="table">
  <div class="row">
    <div class="col-sm-2 col-xs-4 fh">  
      ${_("Testi liik")}
    </div>
    <div class="col-sm-10 col-xs-8">
      ${h.select('testiliik_kood', const.TESTILIIK_EELTEST, c.opt.testiliik)}
    </div>
  </div>
</div>

${h.submit_dlg()}
${h.end_form()}
