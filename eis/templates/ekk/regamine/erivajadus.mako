<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Eritingimused")}: ${c.item.sooritaja.nimi}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Registreerimine"), h.url('regamised'))}
${h.crumb(c.item.sooritaja.nimi,h.url('regamine',id=c.item.sooritaja_id))}
${h.crumb(_("Eritingimused"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'regamised' %>
</%def>
<% 
   c.sooritaja = c.item.sooritaja
   c.kasutaja = c.sooritaja.kasutaja
   c.can_update = c.user.has_permission('erivajadused', const.BT_UPDATE) 
%>
${h.form_save(c.item.id)}
${h.hidden('on_erivajadused_vaadatud', c.item.on_erivajadused_vaadatud and '1' or '')}
<%include file="/ekk/regamine/erivajadus.sisu.mako"/>

<div class="d-flex">
  <div class="flex-grow-1">
    ${h.btn_back(url=h.url('regamine',id=c.sooritaja.id))}
    ${h.btn_to_dlg(_("Määra tugiisik"), h.url('regamine_tugiisikud', sooritus_id=c.item.id), level=2, title=_("Tugiisiku määramine"), size='md')}
  </div>
  <div>
    % if c.is_edit:
    ${h.button(_("Salvesta ja kinnita"), onclick="confirm_save(false)")}
    % if c.sooritaja.test.testiliik_kood!=const.TESTILIIK_RIIGIEKSAM:
    ${h.button(_("Salvesta ja märgi üle vaadatuks"), onclick="confirm_save(true)")}
    % endif
    ${h.button(_("Kanna üle"), onclick='kannayle()')}
    % elif c.can_update:
    ${h.btn_to(_("Muuda"), h.url_current('edit', id=c.item.id), method='get')}
    % endif
  </div>
</div>
${h.end_form()}
