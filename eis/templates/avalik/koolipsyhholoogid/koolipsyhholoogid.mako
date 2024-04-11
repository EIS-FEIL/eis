<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Koolipsühholoogid")}
</%def>
<%def name="breadcrumbs()">
##${h.crumb(_("Koolipsühholoogid"), h.url('koolipsyhholoogid'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'kpsyh' %>
</%def>

<h1>${_("Koolipsühholoogid")}</h1>
${h.form_search(url=h.url('koolipsyhholoogid'))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
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
    ${h.btn_to(_("Laadi CSV"), h.url('koolipsyhholoogid_litsentsid'), level=2)}
    ${h.btn_new(h.url('new_koolipsyhholoog'))}
    </div>

    ${h.submit(_("CSV"), id="csv", level=2)}
    ${h.btn_search()}
  </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
  <%include file="koolipsyhholoogid_list.mako"/>
</div>
