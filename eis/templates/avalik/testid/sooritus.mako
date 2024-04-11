## Testiosa sooritamise vaatamine
<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<%
  c.includes['test'] = True
  if c.test.diagnoosiv:
     c.includes['subtabs'] = True
%>
</%def>
<%def name="draw_tabs()">
<% c.tab1 = 'sooritus' %>
<%include file="tabs.mako"/>
</%def>
<%def name="page_title()">
${c.test.nimi} | ${c.sooritus.sooritaja.nimi}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Minu töölaud'), h.url('tookogumikud'))} 
${h.crumb(c.test.nimi or _('Test'))} 
${h.crumb(c.sooritus.sooritaja.nimi)}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'tookogumikud' %>
</%def>


<%def name="draw_subtabs()">
<%namespace name="tab" file='/common/tab.mako'/>
${tab.subdraw('tulemus', h.url('test_tagasiside1', test_id=c.test_id, testiruum_id=c.testiruum_id, id=c.sooritus.sooritaja_id), _("Tagasiside"))}
${tab.subdraw('sooritus', h.url('test_labiviimine_sooritus', test_id=c.test_id, testiruum_id=c.sooritus.testiruum_id, id=c.sooritus.id), _("Näita vastuseid"), current_tab=True)}
</%def>

<% 
   c.url_to_alatest = lambda alatest :  h.url('test_labiviimine_alatestisooritus', id=c.sooritus_id, alatest_id=alatest.id, testiruum_id=c.testiruum_id, test_id=c.test.id)
   heading = None
%>
% if heading:
${heading}
% endif

<%include file="/avalik/sooritamine/testiosasisu.mako"/>
