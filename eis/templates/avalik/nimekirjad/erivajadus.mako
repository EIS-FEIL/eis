<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Eritingimused")}: ${c.item.sooritaja.nimi}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Testi sooritajate määramine"), h.url('nimekirjad_testimiskorrad'))} 
<%
   sooritaja = c.item.sooritaja
   c.testimiskord = sooritaja.testimiskord
   c.test = sooritaja.test
   c.nimekiri = sooritaja.nimekiri
   c.testiruum_id = c.item.testiruum_id
%>
% if c.testimiskord:
${h.crumb('%s %s' % (c.test.nimi, c.testimiskord.tahised),
h.url('nimekirjad_testimiskord_korrasooritajad',testimiskord_id=c.testimiskord.id))} 
${h.crumb(c.item.sooritaja.kasutaja.nimi, 
h.url('nimekiri_kanne', testimiskord_id=c.testimiskord_id, id=c.item.sooritaja_id))}
% elif c.nimekiri:
${h.crumb(c.nimekiri.nimi, h.url('test_nimekiri', test_id=c.test_id, testiruum_id=c.testiruum_id, id=c.nimekiri.id))}
${h.crumb('%s %s' % (sooritaja.eesnimi, sooritaja.perenimi))}
% else:
${h.crumb('%s %s' % (sooritaja.eesnimi, sooritaja.perenimi))}
% endif

${h.crumb(_("Eritingimused"))}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>
<h1>${_("Eritingimused")}</h1>
<% 
   c.sooritaja = c.item.sooritaja
   c.kasutaja = c.sooritaja.kasutaja
   # lisakontroll sooritaja kooli kohta
   can_regtk = c.user.has_permission('regikuitk', const.BT_UPDATE, obj=c.sooritaja)
   c.can_update = c.user.has_permission('erivmark', const.BT_UPDATE, c.testimiskord) and \
                  not c.item.on_erivajadused_kinnitatud or \
                  c.user.has_permission('erivmark_p', const.BT_UPDATE, c.testimiskord)
   c.can_update = c.can_update and can_regtk
   c.orig_is_edit = c.is_edit
   if c.is_edit_p:
      c.is_edit = False
   can_nimekirjad = can_regtk and c.user.has_permission('nimekirjad', const.BT_UPDATE, obj=c.testimiskord)
%>
${h.form_save(c.item.id)}
<%include file="/ekk/regamine/erivajadus.sisu.mako"/>

<div class="d-flex">
  <div class="flex-grow-1">
    % if c.testimiskord:
    ${h.btn_back(url=h.url('nimekiri_kanne', testimiskord_id=c.testimiskord.id, id=c.sooritaja.id))}
    % else:
    ${h.btn_back(url=h.url('test_nimekiri_kanne', nimekiri_id=c.nimekiri.id, id=c.sooritaja.id, test_id=c.test.id, testiruum_id=c.testiruum_id))}
    % endif
    % if can_nimekirjad:
      ${h.btn_to_dlg(_("Määra tugiisik"), h.url('nimekiri_kanne_tugiisikud', sooritus_id=c.item.id),
                   level=2, title=_("Tugiisiku määramine"), size='md')}
    % endif
  </div>
  <div>
    % if c.is_edit or c.is_edit_p:
    ${h.btn_remove(id=c.item.id, value=_("Tühista eritingimused"))}
    ${h.submit()}
    % elif c.can_update:
    ${h.btn_to(_("Muuda"), h.url_current('edit', id=c.item.id), method='get')}
    % endif
  </div>
</div>

${h.end_form()}
