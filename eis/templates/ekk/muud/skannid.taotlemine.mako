${h.form_save(None)}
${h.hidden('list_url', c.list_url)}
% for kord in c.korrad:
${h.hidden('kord_id', kord.id)}
% endfor
<%include file="/common/message.mako"/>

<div class="my-2">
  ${_("Tööga tutvumise taotluse esitamise ajavahemik")}
  <div class="form-group row">
    ${h.flb3(_("Taotlemise algus"))}
    <div class="col">
      ${h.date_field('tutv_taotlus_alates', c.tutv_taotlus_alates, wide=False)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Taotlemise lõpp"))}
    <div class="col">
      <span class="pr-3">
        ${h.date_field('tutv_taotlus_kuni', c.tutv_taotlus_kuni, wide=False)}
      </span>
      ${h.checkbox('alatine', 1, checked=c.tutv_taotlus_alates and not c.tutv_taotlus_kuni, label=_("alatine"))}
    </div>
  </div>
</div>

<div class="my-2">
  ${_("Sooritajale saadetav hindamisjuhendi URL")}
  <div class="form-group row">
    <div class="col">
      ${h.text('tutv_hindamisjuhend_url', c.tutv_hindamisjuhend_url)}
    </div>
  </div>
</div>

${h.submit_dlg()}
${h.end_form()}
<script>
  $(function(){
  $('#tutv_taotlus_kuni').change(function(){ $('#alatine').prop('checked', false);});
  $('#alatine').click(function(){ $('#tutv_taotlus_kuni').val('');});  
  });
</script>
