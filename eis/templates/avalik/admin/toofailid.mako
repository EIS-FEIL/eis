## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Failid")}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Failide laadimine"), h.url('toofailid'))} 
</%def>
<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

<h1>${_("Tööfailid")}</h1>
${h.form_search(url=h.url_current('index'))}
<div class="gray-legend p-3 filter-w">
##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Failinimi"),'filename')}
        ${h.text('filename', c.filename)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Kirjeldus"), 'kirjeldus')}
        ${h.text('kirjeldus', c.kirjeldus)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-6 d-flex justify-content-end align-items-end">    
      <div class="form-group">
        ${h.btn_search()}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="toofailid_list.mako"/>
</div>
