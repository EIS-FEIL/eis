<%inherit file="/common/page.mako"/>
<%def name="page_title()">
Piirkonnad | ${c.item.nimi or _("Uus piirkond")}
</%def>
<%def name="breadcrumbs()">
${h.link_to(_("Piirkonnad"), h.url('admin_piirkonnad'))} 
${h.crumb_sep()}
${c.item.nimi or _("Uus piirkond")}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>

<div width="100%" class="lightback">
${h.form_save(c.item.id)}

<table width="100%">
  <tr>
    <td class="fh">${_("Nimi")}</td>
    <td>${h.text('f_nimi', c.item.nimi, size=80)}</td>
  </tr>
  <tr>
    <td class="fh">${_("Kehtiv")}</td>
    <td>${h.checkbox('f_kehtib', checked=c.item.staatus, label=_("Kehtiv"))}</td>
  </tr>
</table>
% if c.is_edit:
${h.submit()}
%   if c.item.id:
${h.btn_to(_("Vaata"), h.url('admin_piirkond', id=c.item.id), method='get')}
%   endif
% elif c.user.has_permission('admin', const.BT_UPDATE):
${h.btn_to(_("Muuda"), h.url('admin_edit_piirkond', id=c.item.id), method='get')}
% endif
${h.btn_back(url=h.url('admin_piirkonnad'))}

${h.end_form()}


</div>
