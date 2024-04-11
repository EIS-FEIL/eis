<%inherit file="/common/dlgpage.mako"/>
<%include file="/common/message.mako"/>

${h.form_search()}
${h.hidden('sub', 'valitest')}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-6">
      <div class="form-group">
        ${h.flb(_("Testi ID"),'test_id')}
        ${h.posint5('test_id', c.test_id)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div>
        ${h.submit_dlg(_("Jätka"))}
      </div>
    </div>
  </div>
</div>
${h.end_form()}
