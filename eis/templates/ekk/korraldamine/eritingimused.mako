<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Testi korraldamine")} | ${c.test.nimi} ${h.str_from_date(c.toimumisaeg.alates)}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Korraldamine"), h.url('korraldamised'))} 
${h.crumb('%s %s' % (c.test.nimi, h.str_from_date(c.toimumisaeg.alates)))} 
${h.crumb(_("Eritingimused"),h.url_current())}
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'korraldamised' %>
</%def>


<%def name="draw_tabs()">
<% c.tab1 = 'muu' %>
<%include file="tabs.mako"/>
</%def>

<%def name="require()">
<% c.includes['subtabs'] = True %>
</%def>

<%def name="draw_subtabs()">
<%include file="muu.subtabs.mako"/>
</%def>

<h2>${_("Sooritajad, kellel on lisatingimused või kellel on kunagi olnud eritingimustega registreeringuid")}</h2>

<div class="listdiv">
<%include file="eritingimused_list.mako"/>
</div>
