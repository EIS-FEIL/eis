## Testiosa soorituse vaatamine
<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<%
  c.includes['form'] = True
  c.includes['test'] = True
  c.includes['subtabs'] = True
%>
</%def>
<%def name="draw_tabs()">
<% c.tab1 = 'opetajatulemus' %>
<%include file="tabs.mako"/>
</%def>
<%def name="draw_subtabs()">
<% c.tab2 = c.sooritus.id %>
<%include file="sooritus.tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Tsentraalsed testid")}
| ${c.test.nimi} 
| ${c.sooritaja.nimi}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_('Tulemused'), h.url('ktulemused'))}
${h.crumb(c.test.nimi, h.url('ktulemused_osalejad', test_id=c.test.id, kursus=c.kursus, testimiskord_id=c.testimiskord.id))}
${h.crumb(c.sooritaja.nimi)}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

<% 
  c.sooritus = c.item
  c.url_to_alatest = lambda alatest :  h.url('ktulemused_osa', test_id=c.test.id, testimiskord_id=c.testimiskord.id, testiosa_id=c.item.testiosa_id, id=c.item.id, kursus=c.kursus, alatest_id=alatest.id)
  c.prepare_correct = 'Y'
%>
<%include file="/avalik/sooritamine/testiosasisu.mako"/>


