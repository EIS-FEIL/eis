<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>
<%def name="require()">
<%
  c.includes['math'] = True
%>
</%def>

<%def name="page_title()">
${c.test.nimi or ''} | ${_("Vastuste analüüs")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(c.test.nimi or _('Test'))} 
${h.crumb(_('Vastuste analüüs'))}
</%def>

% if not c.nimekiri_id:
% if c.can_calc:
<%include file="arvutused.mako"/>
% endif

% else:
<span style="float:left">${_("Nimekirja statistika")}</span>
% if c.user.has_permission('ekk-testid', const.BT_UPDATE, c.test):
<span style="float:right">
${h.link_to(_('Vaata üldist statistikat'),
h.url_current('index', test_id=c.test.id, testiruum_id=0))}
</span>
% endif
% endif
<br/>
<% c.fblinks = True %>
<%include file="/ekk/hindamine/analyys.vastused_list.mako"/>
