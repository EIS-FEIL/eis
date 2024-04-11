<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Logopeedid")}
</%def>
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'logopeedid' %>
</%def>

<h1>${_("Logopeedid")}</h1>
${h.form_search(url=h.url('logopeedid'))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Isikukood"), 'isikukood')}
        ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("E-posti aadress"), 'epost')}
        ${h.text('epost', c.epost)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Eesnimi"),'eesnimi')}
        ${h.text('eesnimi', c.eesnimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Perekonnanimi"), 'perenimi')}
        ${h.text('perenimi', c.perenimi)}
      </div>
    </div>
  <div class="col d-flex flex-wrap justify-content-end align-items-end">
    <div class="flex-grow-1">
    ${h.btn_to(_("Laadi CSV"), h.url('logopeedid_litsentsid'), level=2)}
    ${h.btn_new(h.url('new_logopeed'))}
    </div>

    ${h.submit(_("CSV"), id="csv", level=2)}
    ${h.btn_search()}
  </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
  <%include file="logopeedid_list.mako"/>
</div>
