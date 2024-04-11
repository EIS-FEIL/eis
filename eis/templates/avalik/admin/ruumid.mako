## -*- coding: utf-8 -*- 
<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Soorituskoha andmed")} 
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Soorituskoha andmed"))}
${h.crumb(_("Ruumid"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>


<%def name="draw_tabs()">
<%include file="/admin/koht.tabs.mako"/>
</%def>
<%include file="/admin/ruumid.sisu.mako"/>