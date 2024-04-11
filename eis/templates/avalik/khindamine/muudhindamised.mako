## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Muude testide hindamine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"))}
${h.crumb(_("Muud testid"), h.url('muudhindamised'))} 
</%def>

<%def name="active_menu()">
<% c.menu1 = 'hindamine' %>
</%def>

<h1>${_("Muude testide hindamine")}</h1>
${h.form_search(url=h.url('muudhindamised'))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testi ID"), 'test_id')}
        ${h.posint('test_id', c.test_id)}
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
        ${h.flb(_("Testi nimetus"),'t_nimi')}
        ${h.text('t_nimi', c.t_nimi)}
      </div>
    </div>      
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Nimekirja nimetus"),'n_nimi')}
        ${h.text('n_nimi', c.n_nimi)}
      </div>
    </div>
    ##% if c.opt_esitaja:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Nimekirja looja"),'esitaja_id')}
        ${h.select('esitaja_id', c.esitaja_id, c.opt_esitaja, empty=True)}
      </div>
    </div>
    ##% endif
    <div class="col-12 col-md-7 col-lg-5 d-flex align-items-end">
      <div class="form-group">
        ${h.checkbox1('peidus', 1, checked=c.peidus, label=_("ka peidus nimekirjad"))}
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

<div class="listdiv">
<%include file="rhindamised_list.mako"/>
</div>
