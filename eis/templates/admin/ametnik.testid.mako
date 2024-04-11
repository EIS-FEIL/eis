<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Kasutajad")} | ${c.kasutaja.nimi} 
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Eksamikeskuse kasutajad"), h.url('admin_ametnikud'))} 
${h.crumb(c.kasutaja.nimi)}
${h.crumb(_("Testid"))}
</%def>
<%def name="draw_tabs()">
<%include file="ametnik.tabs.mako"/>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>

<h1 class="h3">${_("Kehtivad individuaalsed õigused testides")}</h1>

<div class="listdiv">
<%include file="ametnik.testid_list.mako"/>
</div>
