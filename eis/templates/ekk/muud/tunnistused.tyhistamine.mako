<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tunnistused.tabs.mako"/>
</%def>
<%def name="page_title()">
${_("Eksamitunnistuste tühistamine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Eksamitunnistused"), h.url('muud_tunnistused_valjastamised'))}
${h.crumb(_("Tühistamine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'muud' %>
</%def>

${h.form_search(url=h.url('muud_tunnistused_tyhistamised'))}
${h.hidden('staatus', c.staatus)}
<div class="form-wrapper-lineborder mb-1">
  <div class="form-group row">
    ${h.flb3(_("Isikukood"))}
    <div class="col-md-3">
      ${h.text('isikukood', c.isikukood, maxlength=50)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Tunnistuse nr"))}
    <div class="col-md-3">
      ${h.text('tunnistusenr', c.tunnistusenr)}
    </div>
  </div>
  <div class="form-group row">
    <div class="col text-right">
      ${h.btn_search()}
    </div>
  </div>
</div>
${h.end_form()}


<div class="listdiv">
<%include file="tunnistused.tyhistamine_list.mako"/>
</div>

