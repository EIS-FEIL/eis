<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tunnistused.tabs.mako"/>
</%def>
<%def name="page_title()">
${_("Allkirjastatud eksamitunnistuste salvestamine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Eksamitunnistused"), h.url('muud_tunnistused_valjastamised'))}
${h.crumb(_("Salvestamine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'muud' %>
</%def>

${h.form_save(None)}
<br/>
% if c.user.has_permission('tunnistused', const.BT_UPDATE):
${h.submit(_("Salvesta allkirjastatud tunnistused"), clicked=True)}
% endif
${h.end_form()}

% if c.arvutusprotsessid:
<br/>
<%
  c.protsessid_no_caption = True
  c.url_refresh = h.url('muud_tunnistused_salvestamised', sub='progress')
%>
<%include file="/common/arvutusprotsessid.mako"/>
% endif
