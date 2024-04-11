<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Kasutajad")} | ${c.kasutaja.nimi} 
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Eksamikeskuse kasutajad"), h.url('admin_ametnikud'))} 
${h.crumb(c.kasutaja.nimi)}
${h.crumb(_("Ülesanded"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<%def name="draw_tabs()">
<%include file="ametnik.tabs.mako"/>
</%def>

<h1 class="h3">${_("Kehtivad individuaalsed õigused ülesannetes")}</h1>

<div class="listdiv">
<%include file="ametnik.ylesanded_list.mako"/>
</div>

