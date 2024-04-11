<%include file="/common/message.mako"/>
${h.form(h.url('testid_update_hulga', id=c.testid_id), method='put')}
${h.hidden('sub', 'kvaliteet')}
<p>
${_("Kvaliteedimärk")}
${h.select2('kvaliteet_kood', '', c.opt.klread_kood('KVALITEET'), max_sel_length=1)}
</p>

${h.submit_dlg()}
${h.end_form()}
