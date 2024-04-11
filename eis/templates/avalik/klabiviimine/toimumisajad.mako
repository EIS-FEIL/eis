<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Korraldamine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("E-testi läbiviimine"), h.url('klabiviimine_toimumisajad'))} 
</%def>
<h1>${_("E-testi läbiviimine")}</h1>
${h.form_search(url=h.url('klabiviimine_toimumisajad'))}

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
        ${h.flb(_("Testi nimetus"),'nimi')}
        ${h.text('nimi', c.nimi)}
      </div>
    </div>      
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_('Õppeaine'),'aine')}
        ${h.select('aine', c.aine, c.opt.klread_kood('AINE', empty=True))}
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
<%include file="toimumisajad_list.mako"/>
</div>
