## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Tsentraalsete testide tulemused")}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Tulemused"), h.url('ktulemused'))} 
</%def>
<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

<h1>${_("Testide tulemused")}</h1>
${h.form_search()}
<div class="gray-legend p-3 filter-w">
##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testi ID"), 'test_id')}
        ${h.posint('test_id', c.test_id)}
      </div>
    </div>
    <div class="col-12 col-md-8 col-lg-6">
      <div class="form-group">
        ${h.flb(_("Toimumise algusaeg"), 'alates')}
        <div class="row">
          <div class="col-md-5">
            ${h.date_field('alates', h.str_from_date(c.alates))}
          </div>
          <div class="col-md-1">
            ${_("kuni")}
          </div>
          <div class="col-md-5">
            ${h.date_field('kuni', h.str_from_date(c.kuni))}
          </div>
        </div>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testsessioon"),'testsessioon_id')}
        ${h.select('testsessioon_id', c.testsessioon_id, model.Testsessioon.get_opt(), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Klass"), 'klass')}
        ${h.select('klass', c.klass, const.EHIS_KLASS, empty=True)}
      </div>
    </div>
  </div>
  <div class="d-flex justify-content-end align-items-end">
    <div class="form-group">
    ${h.btn_search()}
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="otsing_list.mako"/>
</div>
