<%include file="/common/message.mako"/>
${h.form(h.url('ylesanded_update_hulga', id=c.ylesanded_id), method='put')}
${h.hidden('sub', 'autor')}
<p>
${_("Autor")}
${h.text('autor', '', maxlength=128)}
</p>

${h.submit_dlg()}
${h.end_form()}
