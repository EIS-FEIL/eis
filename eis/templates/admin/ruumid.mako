<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Soorituskohad")} | ${c.koht.nimi} | ${_("Ruumid")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Soorituskohad"), h.url('admin_kohad'))} 
${h.crumb(c.koht.nimi, h.url('admin_koht', id=c.koht.id))}
${h.crumb(_("Ruumid"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>

<%def name="draw_tabs()">
<%include file="koht.tabs.mako"/>
</%def>
<%include file="ruumid.sisu.mako"/>
