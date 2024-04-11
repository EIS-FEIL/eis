<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Testide tulemuste statistika")}
</%def>      
<%def name="breadcrumbs()">
% if c.user.is_authenticated:
${h.crumb(_("Muud"))}
${h.crumb(_("Testide tulemuste statistika"), h.url('eksamistatistika'))}
${h.crumb(f"{c.test.nimi} {c.aasta} {c.kursus or ''}", h.url_current())}
% endif
</%def>
<%def name="require()">
<%
  c.includes['plotly'] = True
%>
</%def>
<%def name="page_headers()">
<style>
  <%include file="/avalik/tagasiside/tagasiside.css"/>
</style>
</%def>

<%def name="active_menu()">
<% c.menu1 = c.user.is_authenticated and 'muud' or 'eksamistatistika' %>
</%def>

<div class="fbwrapper" url="${h.url_current(None, getargs=True)}">
  ${c.tagasiside_html}
</div>

% if c.tagasiside_html:
${h.btn_to(_("PDF"), h.url_current(pdf=1))}
% endif

