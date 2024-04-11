<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<%
  c.includes['subtabs'] = True
  c.includes['test'] = True
%>
</%def>
<%def name="page_title()">
${_("Hinnatavad sooritused")} | ${c.hindaja.kasutaja.nimi}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"), h.url('hindamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.millal))} 
${h.crumb(_("Läbiviijate määramine"), h.url('hindamine_hindajad', toimumisaeg_id=c.toimumisaeg.id))}
% if c.hindaja.liik == const.HINDAJA3:
${h.crumb(_("III hindamine"), h.url('hindamine_hindajad3', toimumisaeg_id=c.toimumisaeg.id))}
% else:
${h.crumb(_("Esmane (I ja II) hindamine"), h.url('hindamine_hindajad', toimumisaeg_id=c.toimumisaeg.id))}
% endif
${h.crumb(c.hindaja.kasutaja.nimi)}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'hindamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'maaramine' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<%
  c.tab2 = 'vastajad'
%>
<%include file="maaramine.tabs.mako"/>
</%def>

${_("Hindaja eelvaade")} -
${h.link_to(c.hindaja.kasutaja.nimi,
h.url('hindamine_sooritused', toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.hindaja.id))}

% if c.testiosa.vastvorm_kood == const.VASTVORM_SH and c.hindaja.testiruum_id:

${h.alert_notice(_("Soorituskohas määratud hindaja eelvaade kuvatakse ainult siis, kui hinnatav töö on valitud!"), False)}

% else:
<%include file="/avalik/khindamine/vastajad_sisu.mako"/>
% endif
