## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Testidele registreerimise kontroll")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Testi sooritajate määramine"), h.url('nimekirjad_testimiskorrad'))}
${h.crumb(_("Testidele registreerimise kontroll"), h.url('nimekirjad_kontrollid'))}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

<h1>${_("Testidele registreerimise kontroll")}</h1>

${h.form_search(url=h.url('nimekirjad_kontrollid'), disablesubmit=True)}

<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}

  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Õppeasutus"),'koht_nimi')}
        <div id="koht_nimi">
          ${h.roxt(c.user.koht.nimi)}
        </div>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Klass"),'klass')}
        ${h.select('klass', c.klass, const.EHIS_KLASS)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Paralleel"),'paralleel')}
        ${h.text('paralleel', c.paralleel)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testi liik"),'testiliik')}
        ${h.select('testiliik',c.testiliik, c.opt.klread_kood('TESTILIIK', empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testsessioon"),'sessioon_id')}
        ${h.select('sessioon_id', c.sessioon_id,
        model.Testsessioon.get_opt(), empty=True)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.submit(_("Excel"), id='csv', level=2)}
        ${h.btn_search()}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

% if c.items == []:
${_("Õpilasi ei leitud")}

% elif c.items:

<div class="listdiv">
<%include file="kontroll_list.mako"/>
</div>
% endif
<p/>
