${h.form_save(c.item.id, form_name='form_dlg')}
${h.hidden('lang', c.lang)}
<%include file="/common/message.mako" />
<%include file="mathsetting.sisu.mako"/>


<br/>
% if c.updated:
<script>
  close_dialog();
</script>
% endif
<div class="d-flex">
  <div class="flex-grow-1">
    ${h.button(_("Tagasi"), onclick="close_dialog();", level=2)}
  </div>
  % if c.is_edit:
  ${h.submit_dlg()}
  % endif
</div>
${h.end_form()}
