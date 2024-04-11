## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Protokollitava testi toimumisaja valik")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Testi toimumise protokolli koostamine"), h.url('protokollid'))} 
</%def>

${h.form_search(url=h.url('protokollid'))}
<h1>${_("Testi toimumise protokolli koostamine")}</h1>
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testsessioon"), 'testsessioon_id')}
        ${h.select('testsessioon_id', c.testsessioon_id,
        model.Testsessioon.get_opt(), empty=True)}
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
<%include file="otsing_list.mako"/>
</div>
