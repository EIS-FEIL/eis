<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Rahvusvaheline eksamitunnistus")} | ${c.item.tunnistus.kasutaja.nimi}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Rahvusvaheliste eksamite tunnistused"), h.url('otsing_rvtunnistused'))}
${h.crumb(c.item.tunnistus.kasutaja.nimi, h.url('otsing_rvtunnistus', id=c.item.id))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>

<%include file="rvtunnistus.sisu.mako"/>
