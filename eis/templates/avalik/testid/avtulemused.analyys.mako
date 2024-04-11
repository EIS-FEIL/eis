<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'avtulemused' %>
<%include file="tabs.mako"/>
</%def>
<%def name="require()">
<%
c.includes['subtabs'] = True
c.includes['subtabs_label'] = True
%>
</%def>
<%def name="page_title()">
${c.test.nimi or ''} | ${_("Vastuste analüüs")}
</%def>      
<%def name="breadcrumbs()">
% if c.test.on_jagatudtoo:
${h.crumb(_('Töölaud'), h.url('tookogumikud'))}
% endif
${h.crumb(c.test.nimi or _('Test'), h.url('testid_yldandmed', id=c.test_id, testiruum_id=c.testiruum_id))} 
${h.crumb(_('Tulemused'), h.url('test_avtulemused', test_id=c.test_id, testiruum_id=c.testiruum_id))}
${h.crumb(_('Vastuste analüüs'), h.url('test_avanalyys', test_id=c.test_id, testiruum_id=c.testiruum_id))}
</%def>

<%def name="draw_subtabs()">
<%include file="avtulemused.tabs.mako"/>
</%def>

<%def name="subtabs_label()">
% if c.nimekiri_id and c.data:
% if not c.hide_header_footer:
${_("Nimekirja statistika")}
% endif
% if c.test.testityyp == const.TESTITYYP_EKK and c.user.has_permission('ekk-testid', const.BT_UPDATE, c.test):
${h.link_to(_('Vaata üldist statistikat'),
h.url_current('index', test_id=c.test.id, testiruum_id=0))}
% endif
% endif

<% c.testiosavalik_action = h.url_current('index') %>
<%include file="testiosavalik.mako"/>
</%def>

% if c.can_calc:
<%include file="arvutused.mako"/>
% endif

% if not (c.nimekiri_id and c.data):
${h.alert_notice(_("Nimekirjas ei ole keegi veel testi sooritanud"), False)}
% else:

<% c.fblinks = True %>
<%include file="/ekk/hindamine/analyys.vastused_list.mako"/>
% endif
