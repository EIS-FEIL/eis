## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Sooritatud testid")}
</%def>      
<%def name="breadcrumbs()">
##${h.crumb(_("Sooritatud testid"), h.url('tulemused'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'tulemused' %>
</%def>

<h1>${_("Minu tulemused")}</h1>
${h.form_search(url=h.url('tulemused'))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testi nimetus"),'nimi')}
        ${h.text('nimi', c.nimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testi liik"),'testiliik')}
        ${h.select('testiliik', c.testiliik,
        c.opt.klread_kood('TESTILIIK', empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testisooritaja"),'kasutaja_id')}
        ${h.select('kasutaja_id', c.kasutaja_id,
        model.Volitus.get_opilased_opt(c.user.id))}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.btn_search()}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="row">
  <div class="col-12 col-md-12 col-lg-8 listdiv">
    <%include file="otsing_list.mako"/>
  </div>
  <div class="col-12 col-md-12 col-lg-4">
    <%include file="volitused.mako"/>
  </div>
</div>
