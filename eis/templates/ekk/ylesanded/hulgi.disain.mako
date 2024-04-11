<%include file="/common/message.mako"/>
${h.form(h.url('ylesanded_update_hulga', id=c.ylesanded_id), method='put')}
${h.hidden('sub', 'disain')}

<div class="form-group">
  ${h.radio('disain_ver', const.DISAIN_EIS1, label=_("Vana disain"))}
  ${h.radio('disain_ver', const.DISAIN_HDS, label=_("Uus disain"))}
</div>

${h.submit_dlg()}
${h.end_form()}
