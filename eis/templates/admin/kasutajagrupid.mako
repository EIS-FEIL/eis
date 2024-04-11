<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Kasutajagrupid")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Kasutajagrupid"),h.url('admin_kasutajagrupid'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<h1>${_("Kasutajagrupid")}</h1>
${h.form_search(url=h.url('admin_kasutajagrupid'))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-8 col-lg-6">
      <div class="d-flex">
        ${h.flb(_("Õigus"), 'oigus_id', 'pr-2')}
        <% opt_oigused = [('0', _("Kõik")),] + c.opt.oigused() %>
        ${h.select2('oigus_id', c.oigus_id, opt_oigused, empty=True)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.submit(_("Otsi"))}
        ${h.btn_new(h.url('admin_new_kasutajagrupp'))}      
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
  <%include file="kasutajagrupid_list.mako"/>
</div>
