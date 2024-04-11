<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Kasutajad")} | ${c.item.nimi or _("Uus kasutaja")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Eksamikeskuse kasutajad"), h.url('admin_ametnikud'))} 
${h.crumb(c.item.nimi or _("Uus kasutaja"))}
</%def>
<%def name="draw_tabs()">
<%include file="ametnik.tabs.mako"/>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>

<%
  can_edit_adm = c.user.on_admin or not c.item.on_kehtiv_roll(const.GRUPP_ADMIN)
  if not can_edit_adm:
     c.is_edit = False
%>
${h.form_save(c.item.id)}
% if c.item.id:
<div align="right">${h.link_to(_("Testide läbiviimisega seotud isiku andmed"),
  h.url('admin_kasutaja', id=c.item.id))}</div>

  <% kuni = c.item.ametnik_kuni %>
  % if kuni and kuni >= const.MAX_DATE:
  ${h.alert_notice(_("Isik on eksamikeskuse kasutaja"), False)}
  % elif kuni:
  ${h.alert_notice(_("Isik on eksamikeskuse kasutaja kuni {dt}").format(dt=h.str_from_date(kuni)), False)}
  % else:
  ${h.alert_warning(_("Isik ei ole eksamikeskuse kasutaja"), False)}
  % endif
% endif

${h.rqexp()}
<div class="form-wrapper mb-1">
  ## isikukood, nimi, synniaeg, sugu, kasutajatunnus, parool
  <%include file="kasutaja.isikukood.mako"/>

  <div class="form-group row">
    ${h.flb3(_("E-post"),'k_epost')}
    <div class="col-md-3 err-parent">
      ${h.text('k_epost', c.item.epost)}
    </div>
  </div>
  % if c.item.viimati_ekk:
  <div class="form-group row">
    ${h.flb3(_("Viimati sisse loginud"), 'viimati')}
    <div class="col-md-3" id="viimati">
      ${h.str_from_datetime(c.item.viimati_ekk)}
    </div>
  </div>
  % endif
</div>

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.btn_back(url=h.url('admin_ametnikud'))}

    % if c.is_edit and c.item.id:
    ${h.btn_to(_("Vaata"), h.url('admin_ametnik', id=c.item.id), method='get', level=2)}
    % endif
  </div>
  <div>
    % if c.is_edit:
    ${h.submit()}
    % elif c.user.has_permission('ametnikud', const.BT_UPDATE) and can_edit_adm:
    ${h.btn_to(_("Muuda"), h.url('admin_edit_ametnik', id=c.item.id), method='get')}
    % endif
  </div>
</div>
${h.end_form()}

