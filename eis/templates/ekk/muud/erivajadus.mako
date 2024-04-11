<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Eritingimused:")} ${c.item.sooritaja.nimi}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Eritingimused"), h.url('muud_erivajadused'))}
${h.crumb(c.item.sooritaja.nimi)}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'muud' %>
</%def>

<% 
   c.sooritaja = c.item.sooritaja
   c.kasutaja = c.sooritaja.kasutaja
   c.can_update = c.user.has_permission('ekk-testid', const.BT_UPDATE) 
%>
${h.form_save(c.item.id)}
${h.hidden('on_erivajadused_vaadatud', c.item.on_erivajadused_vaadatud and '1' or '')}
<%include file="/ekk/regamine/erivajadus.sisu.mako"/>

<div class="d-flex">
  <div class="flex-grow-1">
    ${h.btn_back(url=h.url('muud_erivajadused'))}
    ${h.btn_to_dlg(_("Määra tugiisik"), h.url('muud_erivajadused_tugiisikud', sooritus_id=c.item.id), level=2, title=_("Tugiisiku määramine"), size='md')}
  </div>
  <div>
    % if c.is_edit:
    ${h.button(_("Salvesta ja kinnita"), onclick="confirm_save()")}
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
