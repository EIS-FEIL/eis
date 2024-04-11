<%include file="/common/message.mako"/>
% if c.is_saved:
<script>close_dialog()</script>

% elif not c.item and not c.opt_sooritus:
${h.form_search(h.url('muud_skannid_new_tellimine'))}
${h.hidden('sub', 'item')}

<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-6">
      <div class="form-group">
        ${h.flb(_("Isikukood"))}
        ${h.text('isikukood', c.isikukood)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.submit_dlg(_("Otsi"), id='otsi')}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

% if c.kasutaja:
<div class="form-group row">
  ${h.flb3(_("Sooritaja nimi"))}
  <div class="col">
    ${c.kasutaja.nimi}
  </div>
</div>
% endif

% else:
<% if not c.item: c.item = c.new_item() %>
${h.form_save(c.item.id or None)}
${h.hidden('kasutaja_id', c.kasutaja.id)}
<div class="mb-2">
  <div class="form-group row">
    ${h.flb3(_("Sooritaja nimi"))}
    <div class="col">
      ${c.kasutaja.nimi}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Testisooritus"))}
    <div class="col">
      % if c.item.id:
      <% sooritus = c.item or model.Sooritus.get(c.sooritus_id) %>
      ${sooritus.toimumisaeg.tahised} ${sooritus.sooritaja.test.nimi}
      ${h.hidden('sooritus_id', sooritus.id)}
      % else:
      ${h.select('sooritus_id', c.sooritus_id, c.opt_sooritus)}
      % endif
      <div class="py-2">
        ${h.checkbox1('soovib_skanni', 0, checked=c.item.soovib_skanni, label=_("soovib oma eksamitöö skannitud koopiat"))}
      </div>
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("E-post"))}
    <div class="col err-parent">
      ${h.text('k_epost', c.kasutaja.epost, size=50)}
    </div>
  </div>
</div>
% if len(c.opt_sooritus) or c.item.id:
<div class="soovib text-right" style="display:none">
  ${h.submit_dlg()}
</div>
% endif
${h.end_form()}
% endif

<script>
  $(function(){
  $('#soovib_skanni').click(function(){
    $('div.soovib').toggle($('#soovib_skanni').filter(':checked').length > 0);
  });
  $('div.soovib').toggle($('#soovib_skanni').filter(':checked').length > 0);
  });
</script>
