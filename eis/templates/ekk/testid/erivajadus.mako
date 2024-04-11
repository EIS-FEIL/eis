<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Eritingimused")}: ${c.item.sooritaja.nimi}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('testid'))} 
${h.crumb(c.test.nimi or _("Test"))} 
${h.crumb(_("Ülesanded"))}
${h.crumb(_("Eritingimused"))}
${h.crumb(c.item.sooritaja.nimi)}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'testid' %>
</%def>
<% 
   c.sooritaja = c.item.sooritaja
   c.kasutaja = c.sooritaja.kasutaja
   c.can_update = c.user.has_permission('erivajadused', const.BT_UPDATE, c.test) 
%>
${h.form_save(c.item.id)}
<%include file="/ekk/regamine/erivajadus.sisu.mako"/>

% if c.is_edit:
${h.submit()}
% elif c.can_update:
${h.btn_to(_("Muuda"), h.url_current('edit', id=c.item.id), method='get')}
% endif

${h.btn_back(url=h.url('test_erialatest',test_id=c.test.id, id=c.komplekt.id))}
${h.end_form()}
