
${h.form(h.url('ylesanded_update_hulga', id=c.ylesanded_id), method='put')}
${h.hidden('sub', 'logitase')}
<p>
${_("Muudatuste logimine")} ${h.checkbox('logitase_muudatused')}
</p>
<p>
${_("Märkused")}<br/>
${h.textarea('markus', '', cols=65, rows=4)}
</p>
${h.submit()}
${h.end_form()}
