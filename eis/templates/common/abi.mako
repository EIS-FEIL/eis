## Abiinfo sisestamise vorm
% if c.item:
${h.form(h.url_current('update'), method='post', id='form_abi')}
% if c.item.kood != 'pagehelp':
<div class="form-group">
  ${h.flb(_("Abiinfo sisestamine"))}
  ${h.textarea('f_sisu', c.item.sisu, rows=6)}
</div>
% endif
<div class="form-group">
  ${h.flb(_("Juhendi URL"))}
  ${h.text('f_url', c.item.url)}
</div>
<div class="mt-2 text-right">
  ${h.submit_dlg(_("Salvesta ja sule"))}
  ##  ${h.button(_("Salvesta ja sule"), onclick="$.ajax({type:'post',url:'"+h.url_current('update')+"',success:hide_help,data:$('#form_abi').serialize(),error:callback_error($('#message_abi'))})")}
</div>
<span id="message_abi"></span>
${h.end_form()}
% endif


