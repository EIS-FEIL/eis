<%namespace name="markused" file='/common/markused.mako'/>
<%
  items = model.Ylesandefailimarkus.query.filter_by(ylesandefail_id=c.fail.id).filter_by(ylem_id=None).order_by(model.Ylesandefailimarkus.aeg).all()
  url_to_new = lambda rcd: h.url('ylesanded_edit_juhised', id=c.item.id, fail_id=c.fail.id, sub='markus', partial=True, ylem_id=rcd and rcd.id)
%>

% if len(items) == 0:
${_("Märkeid ei ole")}
% endif

${h.btn_to_dlg(_("Alusta uut teemat"), url_to_new(None), title=_("Märkus"), width=600)}    
${markused.show(items, url_to_new)}
