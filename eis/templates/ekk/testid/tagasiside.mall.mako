<%include file="/common/message.mako"/>
${h.form_save(None)}
${h.hidden('sub', 'mall')}
<%
  opt_tsmall = [('', _("Ilma tagasisideta"))] + [(str(k), v) for k, v in c.opt.tsmall]
  current = c.test.tagasiside_mall
  if current is None:
     current = ''
%>
${h.select_radio('mall', current, opt_tsmall, linebreak=True)}
${h.submit_dlg()}
${h.end_form()}
