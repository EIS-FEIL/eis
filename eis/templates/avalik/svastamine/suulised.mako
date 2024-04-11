<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Suuline vastamine")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Intervjuu läbiviimine"), h.url('svastamised'))} 
</%def>

<h1>${_("Intervjuu läbiviimine")}</h1>
${h.form_search(url=h.url('svastamised'))}
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
        ${h.flb(_("Testsessioon"), 'testsessioon_id')}
        ${h.select('testsessioon_id', c.testsessioon_id,
        model.Testsessioon.get_opt(), empty=True, onchange='this.form.submit()')}
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
<%include file="suulised_list.mako"/>
</div>
