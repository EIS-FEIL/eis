<%inherit file="/common/simplepage.mako"/>
${h.form(c.pank.url, method='post', target='_top', id='pangalink')}
% for key, value in c.vk_data.items():
<input type="hidden" name="${key}" value="${value}"/>
% endfor
<div class="m-5">
${h.alert_notice(_("Kohe suunatakse panka..."), False)}
${h.submit(_('Maksma...'))}
</div>
${h.end_form()}
<script>
  document.forms.pangalink.submit();
</script>
