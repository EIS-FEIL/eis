<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Kasutajad")} | ${c.kasutaja.nimi or _("Uus kasutaja")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Kasutajad"), h.url('admin_kasutajad'))} 
${h.crumb(c.kasutaja.nimi, h.url('admin_kasutaja', id=c.kasutaja.id))}
${h.crumb(_("Läbiviija profiil"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<%def name="draw_tabs()">
<%include file="kasutaja.tabs.mako"/>
</%def>
${h.form_save(c.kasutaja.id)}

<%include file="kasutaja.profiilisisu.mako"/>

<div class="form-wrapper-lineborder mb-2">
  <div class="form-group row">
    ${h.flb3(_("Märkus"), 'f_markus')}
    <div class="col">
      ${h.textarea('f_markus',c.profiil.markus, disabled=not c.can_update_profiil)}</div>
  </div>
</div>

<div class="d-flex flex-wrap">
${h.btn_back(url=h.url('admin_kasutajad'))}

% if c.is_edit:
%   if c.kasutaja.id:
${h.btn_to(_("Vaata"), h.url('admin_kasutaja_profiil', id=c.kasutaja.id), method='get', level=2)}
%   endif
% elif c.can_update_profiil or c.can_update_vaatleja:
${h.btn_to(_("Muuda"), h.url('admin_kasutaja_edit_profiil', id=c.kasutaja.id), method='get', level=2)}
% endif
<div class="flex-grow-1 text-right">
% if c.is_edit:
${h.submit()}
% endif
</div>
</div>

${h.end_form()}

