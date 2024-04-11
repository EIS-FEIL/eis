<%include file="/common/message.mako"/>
${h.form_save(None, multipart=True)}
${h.hidden('sub', 'fail')}

<% ch = h.colHelper('col-md-2', 'col-md-4') %>

  <div class="form-group row">
    ${ch.flb(_("Andmefail"), 'fail')}
    <div class="col" id="id">
      ${h.file('fail', value=_("Fail"))}
      <small>
        ${_("Faili igal real peab olema üks isikukood")}
      </small>
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Kehtib kuni"), 'kehtib_kuni')}
    <div class="col" id="id">
      ${h.date_field('kehtib_kuni','', wide=False)}
    </div>
  </div>

  <div class="text-right">
    ${h.submit(_("Laadi"))}
  </div>
${h.end_form()}
