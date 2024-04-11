<%include file="/common/message.mako"/>
${h.form_save(c.item.id)}

<div>
  <div>
    ${c.item.saatja}
    ${c.item.epost}
    ${h.str_from_datetime(c.item.created)}
  </div>
  <% koht = c.item.koht %>
  % if koht:
  <div>
    ${koht.nimi}
  </div>
  % endif
</div>
    
<div class="my-2">
  <div class="form-group row">
    ${h.flb3(_("Saadetud lehelt"))}
    <div class="col">
      <a href="${c.item.url}">${c.item.url}</a>
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Teema"))}
    <div class="col">
      ${c.item.teema}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Teate sisu"))}
    <div class="col">
      ${c.item.sisu}
    </div>
  </div>
  <div class="form-group row">
    <div class="col-12">
    % if c.item.ootan_vastust:
    ${_("Pöörduja ootab vastuskirja")}
    % else:
    ${_("Pöörduja ei oota vastuskirja")}
    % endif
    </div>
    <div class="col-12">
      ${h.checkbox('f_on_vastatud', 1, checked=c.item.on_vastatud, label=_("Pöördujale on vastatud"))}
    </div>
  </div>
  <div class="form-group">
    ${h.flb(_("Vastuse sisu"))}
    <div>
      ${h.textarea('f_vastus', c.item.vastus, rows=8)}
    </div>
  </div>
</div>
<div class="text-right">
% if c.is_edit:
${h.submit_dlg()}
% endif
</div>
${h.end_form()}
