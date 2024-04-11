<%include file="/common/message.mako"/>
${h.form(h.url('ylesanded_update_hulga', id=c.ylesanded_id), method='put')}
${h.hidden('sub', 'olek')}
<%
  opt_st = c.opt.klread_kood('Y_STAATUS')
  ignore = []
  #if not c.user.has_permission('ylesanded', const.BT_UPDATE, gtyyp=const.USER_TYPE_AV):
  #   ignore = ignore + list(const.Y_ST_AV)
  #if not c.user.has_permission('ylesanded', const.BT_UPDATE, gtyyp=const.USER_TYPE_EKK):
  #   ignore = ignore + [int(r[0]) for r in opt_st if int(r[0]) not in const.Y_ST_AV]

  if not c.user.has_permission('ylesandemall', const.BT_UPDATE, c.item):
     ignore = ignore + [const.Y_STAATUS_MALL, const.Y_STAATUS_AV_MALL]

  if not c.user.has_permission('sisuavaldamine', const.BT_UPDATE):
     ignore = ignore + [const.Y_STAATUS_AVALIK, const.Y_STAATUS_VALMIS, const.Y_STAATUS_PEDAGOOG]
  opt_st = [r for r in opt_st if int(r[0]) not in ignore]
%>
<p>
Olek
${h.select('staatus', None, opt_st)}
</p>

<p>
${_("Märkused")}<br/>
${h.textarea('markus', '', cols=80, rows=5)}
</p>

${h.submit_dlg()}
${h.end_form()}
