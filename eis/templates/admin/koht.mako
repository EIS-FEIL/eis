<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<%
c.includes['jstree'] = True
c.includes[ 'optiontree'] = True
%>
</%def>
<%def name="page_title()">
${_("Soorituskohad")} | ${c.item.nimi or _("Uus soorituskoht")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Soorituskohad"), h.url('admin_kohad'))} 
${h.crumb(c.item.nimi or _("Uus soorituskoht"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<%def name="draw_tabs()">
<%include file="koht.tabs.mako"/>
</%def>

<%include file="koht.sisu.mako"/>
