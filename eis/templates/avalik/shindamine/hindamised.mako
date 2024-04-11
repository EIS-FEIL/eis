## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Suuliste vastuste hindamine")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"))}
${h.crumb(_("Tsentraalsed testid"), h.url('khindamised'))} 
% if c.testiruum and c.testikoht:
${h.crumb(c.test.nimi + ', ' + c.testikoht.koht.nimi + ' ' + (c.testiruum.tahis or ''),
h.url('shindamine_vastajad', testiruum_id=c.testiruum.id))}
% else:
${h.crumb(c.test.nimi, h.url('khindamine_vastajad', toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.labiviija.id))}
% endif
${h.crumb(_("Hindamine"))}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

<%def name="require()">
<%
  c.includes['subtabs'] = True
  c.includes['test'] = c.includes['spectrum'] = True 
  c.includes['math'] = True
%>
</%def>

<h1>${_("Hindamine")}</h1>
<%
   c.counter = -1
%>
<%include file="suulinesisu.mako"/>
