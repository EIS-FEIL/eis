<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Eksamitunnistused")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Päringud"))}
${h.crumb(_("Eksamitunnistused"), h.url('otsing_tunnistused'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>
<h1>${_("Eksamitunnistused")}</h1>
${h.form_search(url=h.url('otsing_tunnistused'))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Isikukood"),'isikukood')}
        ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Tunnistuse nr"),'tunnistusenr')}
        ${h.text('tunnistusenr', c.tunnistusenr)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div>
        ${h.btn_search()}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
  % if not c.items and c.items != '':
  ${_("Otsingu tingimustele vastavaid tunnistusi ei leitud")}
  % elif c.items:
  <%include file="tunnistused.otsing_list.mako"/>
  % endif 
</div>
