## Testiosa sooritamise eelvaade
<%inherit file="/ekk/testid/eelvaade.mako"/>

<%def name="active_menu()">
<% c.menu1 = 'tookogumikud' %>
</%def>

<%def name="page_title()">
Test: ${c.test.nimi or ''} | ${_("Testi sooritamise eelvaade")}
</%def>      

<%def name="breadcrumbs()">
${h.crumb( _('Minu töölaud'), h.url('tookogumikud'))} 
${h.crumb(c.test.nimi or  _('Test'), request.handler._url_out())} 
${h.crumb( _('Eelvaade'))}
</%def>
