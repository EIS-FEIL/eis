<%inherit file="/avalik/eksamistatistika/riikliktagasiside.mako"/>
<%def name="page_title()">
${_("Testide tulemuste statistika")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Testide tulemuste statistika"), h.url('eksamistatistika'))}
${h.crumb(f"{c.test.nimi} {c.aasta} {c.kursus or ''}", h.url_current())}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>
