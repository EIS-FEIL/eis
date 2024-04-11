<%inherit file="/common/formpage.mako" />
<%def name="page_title()">
${_("Sooritajate arv")}
</%def>
<%def name="breadcrumbs()">
</%def>
<%def name="draw_tabs()">
<%include file="sooritajatearv.tabs.mako"/>
</%def>
<%def name="requirenw()">
<% c.pagenw = True %>
</%def>
<h1>${_("Sooritajate arv")}</h1>
${h.form_search()}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testi ID"),'test_id')}
        ${h.posint('test_id', c.test_id)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testimiskord"),'kord_tahis')}
        ${h.text('kord_tahis', c.kord_tahis, pattern='[^-]*')}
      </div>
    </div>
  </div>
  <div class="col d-flex justify-content-end align-items-end">
    <div class="form-group">
    ${h.btn_search()}
    ${h.submit(_("CSV"), id="csv", class_="filter", level=2)}      

    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="sooritajateolekud_list.mako" />
</div>
