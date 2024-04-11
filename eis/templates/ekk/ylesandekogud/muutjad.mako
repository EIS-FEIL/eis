<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${c.ylesandekogu.nimi or _("Koostamise ajalugu")} 
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("E-kogud"), h.url('ylesandekogud'))}
${h.crumb(c.ylesandekogu.nimi or _("E-kogu"), h.url('ylesandekogu', id=c.ylesandekogu.id))}
${h.crumb(_("Koostamise ajalugu"), h.url('ylesandekogu_muutjad', id=c.ylesandekogu.id))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>

<div width="100%" class="listdiv">
<%include file="muutjad_list.mako"/>
</div>

