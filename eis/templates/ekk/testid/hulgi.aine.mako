<%include file="/common/message.mako"/>
${h.form(h.url('testid_update_hulga', id=c.testid_id), method='put')}
${h.hidden('sub', c.sub)}

<p>
  ${_("Õppeaine")}
  ${h.select('aine_kood', None, c.opt.klread_kood('AINE'))}
</p>

${h.submit_dlg()}
${h.end_form()}

