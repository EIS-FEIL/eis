${h.form(h.url('ylesanded_update_koostamine', id=c.item.id), method='put')}
${h.hidden('sub', 'olek')}
<div class="d-flex flex-wrap my-3">
${h.flb(_("Olek"), 'staatus', 'mr-3')}
<div>
<%
  opt_st = c.opt.klread_kood('Y_STAATUS')
  ignore = []
  if not c.user.has_permission('ylesanded', const.BT_UPDATE, gtyyp=const.USER_TYPE_AV):
     ignore = ignore + list(const.Y_ST_AV)
  if not c.user.has_permission('ylesanded', const.BT_UPDATE, gtyyp=const.USER_TYPE_EKK):
     ignore = ignore + [int(r[0]) for r in opt_st if int(r[0]) not in const.Y_ST_AV]
  if not c.user.has_permission('ylesandemall', const.BT_UPDATE, c.item):
     ignore = ignore + [const.Y_STAATUS_MALL, const.Y_STAATUS_AV_MALL]
  if not c.user.has_permission('sisuavaldamine', const.BT_UPDATE):
     ignore = ignore + [const.Y_STAATUS_AVALIK, const.Y_STAATUS_VALMIS, const.Y_STAATUS_PEDAGOOG]
  
  opt_st = [r for r in opt_st if (c.item.staatus == int(r[0])) or (int(r[0]) not in ignore)]
%>
${h.select('staatus', c.item.staatus, opt_st)}
</div>
</div>

<div class="my-3">
${_("Märkused")}<br/>
${h.textarea('markus', '', cols=80, rows=5)}
</div>
<div class="text-right">
  ${h.submit_dlg()}
</div>
${h.end_form()}
