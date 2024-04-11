<%include file="/common/message.mako"/>
${h.form(h.url('testid_update_hulga', id=c.testid_id), method='put')}
${h.hidden('sub', 'olek')}
<p>
  ${_("Olek")}
  ${h.select('staatus', None, c.opt.klread_kood('T_STAATUS', empty=True))}
</p>
<p>
  ${_("Kasutatavus")}
<%
  opt_avalik = c.opt.opt_avalik
  ignore = []
  if not c.user.has_permission('sisuavaldamine', const.BT_UPDATE):
      ignore = ignore + [const.AVALIK_SOORITAJAD, const.AVALIK_OPETAJAD]

  opt_avalik = [r for r in opt_avalik if int(r[0]) not in ignore]
%>
  ${h.select('avaldamistase', None, opt_avalik, empty=True)}
</p>
<p>
  ${_("Märkused")}<br/>
  ${h.textarea('markus', '', cols=80, rows=5)}
</p>

${h.submit_dlg()}
${h.end_form()}
