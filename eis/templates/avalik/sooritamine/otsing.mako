## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Testide sooritamine")}
</%def>      
<%def name="breadcrumbs()">
##${h.crumb(_("Testide sooritamine"))}
##${h.crumb(_("Sooritamine"), h.url('sooritamised'))} 
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sooritamised' %>
</%def>

<h1>${_("Testide sooritamine")}</h1>
${h.form_search(url=h.url('sooritamised'))}

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
        ${h.flb(_("Õppeaine"),'aine')}
        ${h.select('aine', c.aine, c.opt.klread_kood('AINE', empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Nimetus"),'nimi')}
        ${h.text('nimi', c.nimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Õpetaja"),'omanik')}
        ${h.text('omanik', c.omanik)}
      </div>
    </div>
    <div class="col-12 col-md-8 col-lg-9">
      <div class="form-group">
        ${h.radio('avaldamistase',value=const.AVALIK_SOORITAJAD,
        checkedif=c.avaldamistase, label=_("Kõigile lahendamiseks"))}
        ${h.radio('avaldamistase',value=const.AVALIK_POLE,
        checkedif=c.avaldamistase, label=_("Mulle suunatud testid ja tööd"))}
        ${h.radio('avaldamistase',value='11',
        checkedif=c.avaldamistase, label=_("Olen tugiisik"))}        
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      ${h.btn_search()}
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
% if c.avaldamistase == const.AVALIK_SOORITAJAD:
<%include file="testid_list.mako"/>
% else:
<%include file="suunamised_list.mako"/>
% endif
</div>
