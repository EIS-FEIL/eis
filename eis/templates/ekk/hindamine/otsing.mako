<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Korraldatava testi toimumisaja valik")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'hindamised' %>
</%def>

<h1>${_("Hindamine")}</h1>
${h.form_search(url=h.url('hindamised'))}

<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testi ID"),'test_id')}
        ${h.posint('test_id', c.test_id)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Toimumisaja tähis"),'ta_tahised')}
        ${h.text('ta_tahised', c.ta_tahised)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testsessioon"),'testsessioon_id')}
        ${h.select('testsessioon_id', c.testsessioon_id,
        c.opt.testsessioon, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testi liik"),'testiliik')}
        ${h.select('testiliik', c.testiliik, c.opt.testiliik, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Periood"),'periood')}
        ${h.select('periood', c.periood, c.opt.klread_kood('PERIOOD'),
        empty=True)}
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
        ${h.flb(_("Toimumise algusaeg"),'alates')}
        ${h.date_field('alates', h.str_from_date(c.alates))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("kuni"),'kuni')}
        ${h.date_field('kuni', h.str_from_date(c.kuni))}
      </div>
    </div>
    % if c.is_devel:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Vastamise vorm"),'vastvorm')}
        ${h.select('vastvorm', c.vastvorm, c.opt.klread_kood('VASTVORM'), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 d-flex align-items-end">
      <div class="form-group">
        ${h.checkbox1('hinnatud', 1, checked=c.hinnatud, label="Hinnatud")}
        ${h.checkbox1('hindamata', 1, checked=c.hindamata, label="Hindamata")}
      </div>
    </div>
    % endif
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
