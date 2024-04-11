<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Kasutajate volitused")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Kasutajate volitused"), h.url('admin_volitused'))}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<h1>${_("Kasutajate volitused")}</h1>
${h.form_search(url=h.url('admin_volitused'))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Isikukood"),'isikukood')}
        ${h.text('isikukood', c.isikukood)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div>
        ${h.submit(_("Jätka"))}
      </div>
    </div>
  </div>
</div>
${h.end_form()}
