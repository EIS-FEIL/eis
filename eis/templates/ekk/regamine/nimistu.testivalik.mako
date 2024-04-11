## -*- coding: utf-8 -*- 
<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'testivalik' %>
<%include file="nimistu.tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Eksamile registreerimise taotluse sisestamine")}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Registreerimine"), h.url('regamised'))} 
${h.crumb(_("Registreerimise taotluse sisestamine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'regamised' %>
</%def>

${h.form_search(url=h.url('regamine_nimistu_testivalik'))}
<div class="gray-legend p-3">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testi liik"), 'testiliik')}
        ${h.select('testiliik', c.testiliik, c.opt.testiliik, onchange="this.form.submit()")}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testsessioon"), 'sessioon')}
        ${h.select('sessioon', c.sessioon,
        model.Testsessioon.get_opt(testiliik_kood=c.testiliik), empty=True, onchange='this.form.submit()')}
      </div>
    </div>
    <div class="col d-flex flex-wrap justify-content-end align-items-end">    
      <div>
        ${h.btn_search()}
      </div>
    </div>
  </div>
</div>

${h.end_form()}

<div class="listdiv">
<%include file="nimistu.testivalik_list.mako"/>
</div>
