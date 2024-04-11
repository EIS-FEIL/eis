<%inherit file="/common/page.mako"/>
## jagatud töö ülesannete loetelu
## antud: c.test, c.sooritaja, c.nimekiri
<%def name="page_title()">
${_("Jagatud töö")}: ${c.test.nimi} 
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Sooritus"), h.url('sooritamised'))} 
${h.crumb(c.test.nimi)}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sooritamised' %>
</%def>
<%include file="tooylesanded.sisu.mako"/>
${h.btn_back(url=h.url('sooritamised'))}
