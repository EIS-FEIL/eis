## Testiosa soorituse kuvamine
<%inherit file="/common/formpage.mako"/>
<%namespace name="tab" file='/common/tab.mako'/>
<%def name="require()">
<%
  c.includes['subtabs'] = True
  c.includes['plotly'] = True
%>
</%def>
<%def name="draw_tabs()">
<% c.tab1 = 'opetajatulemus' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<% c.tab2 = 'opilasetulemus' %>
<%include file="sooritus.tabs.mako"/>
</%def>
<%def name="page_headers()">
<style>
  <%include file="/avalik/tagasiside/tagasiside.css"/>
</style>
</%def>

<%def name="page_title()">
${_("Tsentraalsete testid")}
| ${c.test.nimi} 
| ${c.sooritaja.nimi}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_('Tulemused'), h.url('ktulemused'))}
${h.crumb(c.test.nimi, h.url('ktulemused_osalejad', test_id=c.test.id, testimiskord_id=c.testimiskord.id, kursus=c.kursus or ''))}
${h.crumb(c.sooritaja.nimi)}
</%def>


<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

<%
  c.on_ktulemus = True
  c.sooritaja_roll = const.ISIK_KOOL
  c.item = c.sooritaja
%>
<%include file="/avalik/tulemused/tulemus_sisu.mako"/>

% if c.tagasiside_html:
<%
  pdf_url = h.url_current('download', format='pdf', id=c.sooritaja.id)
%>
${h.btn_to(_("Tagasiside (PDF)"), pdf_url)}
% endif
