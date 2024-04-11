<%namespace name="markused" file='/common/markused.mako'/>
% if c.eeltest:
<%
  items = model.Testimarkus.query.filter_by(test_id=c.eeltest.id).filter_by(ylem_id=None).order_by(model.Testimarkus.aeg).all()
%>

% if len(items) == 0:
${_("Märkeid ei ole")}
% endif

${markused.show(items, None)}

% else:
${_("Komplekt pole eeltestimiseks antud")}
% endif
