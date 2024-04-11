<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%
  c.tab1 = 'sooritus'
%>
<%include file="tabs.mako"/>
</%def>
<%def name="require()">
<%
  c.includes['subtabs'] = True
  c.includes['plotly'] = True
%>
</%def>

<%def name="page_title()">
${c.test.nimi or ''} | ${_("Tulemused")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Minu töölaud'), h.url('tookogumikud'))} 
${h.crumb(c.test.nimi or _('Test'))} 
${h.crumb(_('Tulemused'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'tookogumikud' %>
</%def>

<%def name="draw_subtabs()">
<%namespace name="tab" file='/common/tab.mako'/>
${tab.subdraw('tulemus', h.url('test_tagasiside1', test_id=c.test_id, testiruum_id=c.testiruum_id, id=c.item.id), _("Tagasiside"), current_tab=True)}
% if not c.test.opetajale_peidus:
<% sooritused = list(c.sooritaja.sooritused) %>
% for tos in sooritused:
% if tos.staatus == const.S_STAATUS_TEHTUD:
<% label = (len(sooritused) > 1) and tos.testiosa.nimi or _("Näita vastuseid") %>
${tab.subdraw('sooritus', h.url('test_labiviimine_sooritus', test_id=c.test_id, testiruum_id=tos.testiruum_id, id=tos.id), label)}
% endif
% endfor
% endif
</%def>

<%
  c.opetaja_vaatab_testimiskorrata = True
  c.sooritaja_roll = const.ISIK_KOOL
%>
<%include file="/avalik/tulemused/tulemus_sisu.mako"/>

<div class="mt-2 d-flex flex-wrap">
<div class="flex-grow-1">
  % if c.tagasiside_html:
<%
  pdf_url = h.url_current('download', test_id=c.test_id, testiruum_id=c.testiruum_id, id=c.item.id, format='pdf', lang=c.lang)
%>
${h.btn_to(_("PDF"), pdf_url, level=2)}
% endif
</div>
<div class="text-right">
<% mitu_osa = len(c.sooritaja.sooritused) > 1 %>
% for tos in c.sooritaja.sooritused:
% if tos.staatus == const.S_STAATUS_TEHTUD:
<%
  title = _("Arvuta tulemused uuesti")
  if mitu_osa:
     title += ' (%s)' % tos.testiosa.tahis
%>
${h.btn_to(title, h.url_current('update', sub='arvuta', sooritus_id=tos.id, force=1), method='post', level=2, spinnerin=True)}
% endif
% endfor
</div>
</div>
