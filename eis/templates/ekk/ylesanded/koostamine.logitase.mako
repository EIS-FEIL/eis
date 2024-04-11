
${h.form(h.url('ylesanded_update_koostamine', id=c.item.id), method='put')}
${h.hidden('sub', 'logitase')}
<p>
${_("Muudatuste logimine")} ${h.checkbox('logitase_muudatused', checked=(c.item.logitase>=const.LOG_LEVEL_CHANGE))}
</p>
<p>
${_("Märkused")}<br/>
${h.textarea('markus', '', cols=65, rows=4)}
</p>
<div class="text-right">
  ${h.submit()}
</div>
${h.end_form()}
