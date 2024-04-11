<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Suulise vastamise hindamisprotokolli sisestamine")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sisestamine' %>
</%def>

<h1>${_("Suulise vastamisega p-testi hindamisprotokolli sisestamine")}</h1>
${h.form_search(url=h.url('sisestamine_suulised'))}

<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-3 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Sisesta toimumisaja tähis"),'ta_tahised')}
        ${h.text('ta_tahised', c.ta_tahised)}
      </div>
    </div>
    <div class="col-12 col-md-3 col-lg-3">
      <div class="form-group">
        ${h.flb(_("ja hindamisprotokolli tähis"),'ta_tahised')}
        ${h.text('tahis', c.tahis)}
      </div>
    </div>
    <div class="col-12 col-md-3 col-lg-3">
      <div class="form-group">
        ${h.flb(_("hindamise liik"), 'liik')}
        ${h.select('liik', c.liik, c.opt_liik, empty=True)}
      </div>
    </div>
    <div class="col d-flex flex-wrap justify-content-end align-items-end">
      <div class="flex-grow-1">    
        ${h.submit(_("Sisesta"), id='sisesta')}
      </div>
    </div>

  </div>
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("või vali testsessioon"),'sessioon_id')}
        ${h.select('sessioon_id', c.sessioon_id,
        c.opt.testsessioon, empty=True, onchange='this.form.submit()')}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("ja toimumisaeg"),'toimumisaeg_id')}
        ${h.select('toimumisaeg_id', c.toimumisaeg_id,
          c.opt_toimumisaeg, empty=True, onchange='this.form.submit()')}
      </div>
    </div>
  % if c.opt_testikoht:
    <div class="col-12 col-md-3 col-lg-3">
      <div class="form-group">
        ${h.flb(_("soorituskoht"),'testikoht_id')}
        ${h.select('testikoht_id', c.testikoht_id, c.opt_testikoht, empty=True)}
      </div>
    </div>
  % endif
    <div class="col d-flex flex-wrap justify-content-end align-items-end">
      <div class="flex-grow-1">
        ${h.btn_search()}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="suulised.otsing_list.mako"/>
</div>
