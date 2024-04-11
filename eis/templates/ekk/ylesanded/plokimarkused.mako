<%namespace name="markused" file='/common/markused.mako'/>
<%
  items = model.Plokimarkus.query.filter_by(sisuplokk_id=c.sisuplokk.id).filter_by(ylem_id=None).order_by(model.Plokimarkus.aeg).all()
  url_to_new = lambda rcd: h.url('ylesanded_edit_sisu', id=c.sisuplokk.ylesanne_id, sub='markus',ylem_id=rcd and rcd.id or None, sisuplokk_id=c.sisuplokk.id, partial=True, lang=c.lang)
  url_to_delete = lambda rcd: h.url('ylesanded_delete_sisu', id=c.sisuplokk.ylesanne_id, sub='markus',markus_id=rcd.id, sisuplokk_id=c.sisuplokk.id, partial=True, lang=c.lang)  
%>

% if len(items) == 0:
${_("Märkeid ei ole")}
% endif

${h.btn_to_dlg(_("Alusta uut teemat"), url_to_new(None), title=_("Märkus"), width=600)}    

${markused.show(items, url_to_new, url_to_delete)}
