<%include file="/common/message.mako"/>
${h.form_save(c.roll.id)}
<% sub = c.params.get('sub') %>
${h.hidden('sub', sub)}
<div class="form-wrapper-lineborder mb-2">
  <div class="form-group row">
    ${h.flb3(_("Soorituskoht"))}
    <div class="col">
      ${c.roll.koht.nimi}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Kehtib kuni"))}
    <div class="col">
      ${h.date_field('kehtib_kuni', c.roll.kehtib_kuni_ui, wide=False)}
    </div>
  </div>
</div>

<script>
  $(document).ready(function(){
    $('input#kehtib_kuni').datepicker();
  });
</script>
<div class="text-right">
  ${h.submit_dlg()}
</div>
${h.end_form()}
