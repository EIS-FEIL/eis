## Kui SEB kasutaja on automaatselt välja logitud (kuna logis mujalt sisse)
<%inherit file="/common/page.mako"/>
<%def name="page_headers()">
<% c.had_errors = request.handler.has_errors() %>
</%def>
% if not c.had_errors:
% if c.user.is_authenticated:
${h.alert_notice(_("Ligipääsuõigus puudub!"), False)}
% else:
${h.alert_notice(_("Kasutaja on välja logitud!"), False)}
% endif
% endif
${h.btn_to(_("Välju"), h.url('login', action='signout'))}
