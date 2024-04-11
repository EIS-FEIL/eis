## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Testile registreerimise nimekirjad")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Testi sooritajate määramine"))}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

<h1>${_("Testi sooritajate määramine")}</h1>
${h.form_search(url=h.url('nimekirjad_testimiskorrad'))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testi ID"), 'test_id')}
        ${h.posint('test_id', c.test_id)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testi nimetus"), 'nimi')}
        ${h.text('nimi', c.nimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Õppeaine"),'aine')}
        ${h.select('aine', c.aine, c.opt.klread_kood('AINE', empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testi liik"), 'testiliik')}
        ${h.select('testiliik',c.testiliik, c.opt.klread_kood('TESTILIIK', empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Registreerimise aeg"), 'reg_aeg_alates')}
        ${h.date_field('reg_aeg_alates', h.str_from_date(c.reg_aeg_alates), allow_clear=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("kuni"), 'reg_aeg_kuni')}
        ${h.date_field('reg_aeg_kuni', h.str_from_date(c.reg_aeg_kuni), allow_clear=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Reg viis"),'regviis')}
        ${h.select('regviis', c.regviis or const.REGVIIS_KOOL_EIS, c.opt.klread_kood('REGVIIS'))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.radio('aktiiv', 't', checked=c.aktiiv != 'f', label=_("Näita aktiivsed testid"))}
        ${h.radio('aktiiv', 'f', checked=c.aktiiv == 'f', label=_("Näita kõik testid"))}
      </div>
    </div>
  </div>
  <div class="d-flex flex-wrap justify-content-end align-items-end">    
    <div class="flex-grow-1">
    ${h.btn_to(_("Registreerimise kontroll"), h.url('nimekirjad_kontrollid'), level=2)}
    ${h.btn_to(_("Sisesta registreerimise avaldus"), h.url('nimekirjad_new_avaldus'))}
    </div>
    <div>
    ${h.btn_search()}
    </div>
  </div>
</div>
${h.end_form()}
<div class="listdiv">
<%include file="testimiskorrad_list.mako"/>
</div>
