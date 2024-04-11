## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Tulemus")}: ${c.item.test.nimi}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Registreerimisnimekirjad"), h.url('nimekirjad_testimiskorrad'))}
${h.crumb(_("Testidele registreerimise kontroll"), h.url('nimekirjad_kontrollid'))}
${h.crumb(c.item.nimi, h.url('nimekirjad_kontroll_tulemus',id=c.item.id))}
</%def>

<%
  c.on_kontroll = True
  c.sooritaja_roll = const.ISIK_KOOL
%>
<%include file="/avalik/tulemused/tulemus_sisu.mako"/>
