## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Sooritajate nimistu")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"))}
${h.crumb(_("Tsentraalsed testid"), h.url('khindamised'))} 
${h.crumb(c.testiruum.testikoht.toimumisaeg.testimiskord.test.nimi + ', ' +
c.testiruum.testikoht.koht.nimi + ' ' + (c.testiruum.tahis or ''), h.url('shindamine_vastajad', testiruum_id=c.testiruum.id))} 
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>
<h1>${_("Suulise vastamise hindamine")}</h1>
<%include file="vastajad_sisu.mako"/>
