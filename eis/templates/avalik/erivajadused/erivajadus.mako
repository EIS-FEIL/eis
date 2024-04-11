<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Eritingimused:")} ${c.item.sooritaja.nimi}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_('Eritingimused'), h.url('erivajadused'))}
${h.crumb(c.item.sooritaja.nimi)}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>
<h1>${_("Eritingimused")}</h1>
<% 
   c.sooritaja = c.item.sooritaja
   c.kasutaja = c.sooritaja.kasutaja
   c.can_update = False
   testimiskord = c.sooritaja.testimiskord

   c.orig_is_edit = c.is_edit
   if c.is_edit_p:
      c.is_edit = False
   can_erivmark = c.user.has_permission('erivmark', const.BT_UPDATE, obj=testimiskord)
   can_update = not c.item.on_erivajadused_kinnitatud and (not testimiskord or can_erivmark)
   can_nimekirjad = c.user.has_permission('nimekirjad', const.BT_UPDATE, obj=testimiskord)
%>
${h.form_save(c.item.id)}

<%include file="/ekk/regamine/erivajadus.sisu.mako"/>

<div class="d-flex">
  <div class="flex-grow-1">
    ${h.btn_back(url=h.url('erivajadused'))}
    % if can_nimekirjad:
      ${h.btn_to_dlg(_("Määra tugiisik"), h.url('nimekiri_kanne_tugiisikud', sooritus_id=c.item.id),
                   level=2, title=_("Tugiisiku määramine"), size='md')}
    % endif
  </div>
  <div>
    % if c.is_edit or c.is_edit_p:
    ${h.btn_remove(id=c.item.id, value=_('Tühista eritingimused'))}
    ${h.submit()}
    % elif can_update:
    ${h.btn_to(_('Muuda'), h.url_current('edit', id=c.item.id), method='get')}
    % elif testimiskord and can_erivmark:
    ## kool võib muuta neid eritingimusi, mis ei vaja Innove kinnitamist
    ${h.btn_to(_('Muuda'), h.url_current('edit', id=c.item.id), method='get')}
    % endif
  </div>
</div>
${h.end_form()}
