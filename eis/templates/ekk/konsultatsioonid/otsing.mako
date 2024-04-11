## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Konsultatsioonid")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'konsultatsioonid' %>
</%def>

<h1>${_("Konsultatsioonid")}</h1>
${h.form_search(url=h.url('konsultatsioonid'))}

<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("ID"), 'id')}
        ${h.posint('id', c.id)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Nimetus"), 'nimi')}
        ${h.text('nimi', c.nimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">        
        ${h.flb(_("Testi liik"), 'testiliik')}
        <% opt_testiliik = [r for r in c.opt.testiliik if r[0] in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS)] %>
        ${h.select('testiliik', c.testiliik, opt_testiliik, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">        
        ${h.flb(_("Õppeaine"), 'aine')}
        ${h.select('aine', c.aine, c.opt.klread_kood('AINE'), empty=True)}
      </div>
    </div>
  </div>
  <div class="d-flex justify-content-end align-items-end">    
    <div class="form-group">
    ${h.btn_search()}
    % if c.user.has_permission('konsultatsioonid', const.BT_CREATE):
    ${h.btn_new(h.url('new_konsultatsioon'))}
    % endif
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="otsing_list.mako"/>
</div>
