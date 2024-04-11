<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['subtabs'] = True %>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'sisu' %>
<%include file="tabs.mako"/>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'ylesanded' %>
</%def>

<%def name="draw_subtabs()">
<% 
c.tab2 = c.item.id 
c.ylesanne = c.item.ylesanne
%>
<%include file="sisuplokk.tabs.mako"/>
</%def>
<%def name="page_title()">
${c.item.ylesanne.nimi} | ${_("Sisuplokk")} ${c.item.seq}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Ülesandepank"), h.url('ylesanded'))} 
${h.crumb(c.item.ylesanne.nimi, h.url('ylesanne', id=c.item.ylesanne_id))} 
${h.crumb(_("Sisu"), h.url('ylesanded_sisu', id=c.item.ylesanne_id))} 
${h.crumb('%s %s' % (_("Sisuplokk"), c.item.seq or ''))}
</%def>
<%include file="sisuplokk.sisu.mako"/>
