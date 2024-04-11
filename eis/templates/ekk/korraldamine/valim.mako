<%include file="/common/message.mako"/>
${h.not_top()}
${h.form_save(None, h.url('korraldamine_create_valim', toimumisaeg_id=c.toimumisaeg.id), form_name='va_form_save', multipart=True)}

<div class="rounded border my-1 p-3">
  <div class="form-group row">
    ${h.flb(_("Valimi isikukoodide fail"), 'ik_fail', 'col-md-4')}
    <div class="col-md-8">
      ${h.file('ik_fail', value=_("Fail"))}
    </div>
  </div>
  <div class="form-group row">
    <div class="col">
      ${h.checkbox('uustk', 1, label=_("Loo valim eraldi testimiskorrana"))}
    </div>
  </div>

  <div class="text-right mt-1">
    ${h.submit(_("Laadi fail"), name='laadi')}
  </div>
</div>

% if c.testimiskord.sisaldab_valimit:
<div class="rounded border mt-2 p-3">
  <strong>${_("Testimiskord juba sisaldab valimit")}</strong>
  <div class="d-flex flex-wrap justify-content-between mt-1">
  ${h.submit(_("Tühista valim"), name="tyhista", level=2)}
  ${h.submit(_("Loo valimist eraldi testimiskord"), name="loouus")}
  </div>
</div>
% endif

${h.end_form()}
<script>
  $('#va_form_save').submit(function(){set_spinner($('#laadi'));});
</script>
