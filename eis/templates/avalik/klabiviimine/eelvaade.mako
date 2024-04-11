## Testiosa sooritamise eelvaade testi administraatorile
<%inherit file="/ekk/testid/eelvaade.mako"/>

<%def name="active_menu()">
<% c.menu1 = 'tookogumikud' %>
</%def>

<%def name="page_title()">
${_("Test")}: ${c.test.nimi or ''} | ${_("Eelvaade")}
</%def>

<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Kirjaliku e-testi läbiviimine"), h.url('klabiviimine_toimumisajad'))} 
${h.crumb(c.test.nimi + ' ' + h.str_from_date(c.toimumisaeg.alates))}
</%def>
