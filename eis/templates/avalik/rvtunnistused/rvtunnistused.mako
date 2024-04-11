## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Rahvusvaheliste eksamite tunnistused")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_('Rahvusvaheliste eksamite tunnistused'), h.url('otsing_rvtunnistused'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>
<h1>${_("Rahvusvaheliste eksamite tunnistused")}</h1>
${h.form_search(url=h.url('otsing_rvtunnistused'))}

<div class="gray-legend p-3 filter-w">
##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Õppeasutus"), 'koht_nimi')}
        <div id="koht_nimi">${h.roxt(c.user.koht.nimi)}</div>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Klass"), 'klass')}
        ${h.select('klass', c.klass, const.EHIS_KLASS, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">        
        ${h.flb(_("Paralleel"), 'paralleel')}
        ${h.text('paralleel', c.paralleel)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">            
        ${h.flb(_("Eksam"), 'rveksam_id')}
        ${h.select('rveksam_id', c.rveksam_id, c.opt.rveksamid(), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">        
        ${h.flb(_("Õppeaine"),'aine')}
        ${h.select('aine', c.aine, c.opt.klread_kood('AINE'), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">            
        ${h.flb(_("Isikukood"),'isikukood')}
        ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col-12 col-md-8 col-lg-6">
      <div class="form-group">
        ${h.flb(_("Väljastamisaeg alates"),'alates')}
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
  </div>
  <div class="d-flex justify-content-end align-items-end">
    <div class="form-group">
    ${h.btn_search()}
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
  % if not c.items and c.items != '':
  ${_("Otsingu tingimustele vastavaid tunnistusi ei leitud")}
  % elif c.items:
  <%include file="rvtunnistused_list.mako"/>
  % endif 
</div>
