<%namespace name="markused" file='/common/markused.mako'/>
<%
  items = model.Testifailimarkus.query.filter_by(testifail_id=c.item.id).filter_by(ylem_id=None).order_by(model.Testifailimarkus.aeg).all()
  url_to_new = lambda rcd: h.url('test_edit_fail', test_id=c.test.id, id=c.item.id, sub='markus', ylem_id=rcd and rcd.id, partial=True)
%>

% if len(items) == 0:
${_("Märkeid ei ole")}
% endif

${h.btn_to_dlg(_("Alusta uut teemat"), url_to_new(None), title=_("Märkus"), width=600)}    
${markused.show(items, url_to_new)}
