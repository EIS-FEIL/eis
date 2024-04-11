<%inherit file="/common/formpage.mako"/>
<%namespace name="tab" file='/common/tab.mako'/>

<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>
<%def name="require()">
<%
  c.includes['subtabs'] = True
  c.includes['plotly'] = True
%>
</%def>
<%def name="page_headers()">
<style>
  <%include file="/avalik/tagasiside/tagasiside.css"/>
</style>
</%def>

<%def name="page_title()">
${c.test.nimi or ''} | ${_("Osalejate tulemused")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_('Tulemused'), h.url('ktulemused'))}
${h.crumb(c.test.nimi, h.url('ktulemused_osalejatetulemused', test_id=c.test.id, testimiskord_id=c.testimiskord.id, kursus=c.kursus or ''))}
</%def>

<%def name="draw_before_tabs()">
<%include file="before.mako"/>
</%def>

<%include file="alamosadega.sisu.mako"/>
