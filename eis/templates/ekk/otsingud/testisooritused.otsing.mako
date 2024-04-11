<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Testisooritused")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Päringud"))}
${h.crumb(_("Testisooritused"), h.url('otsing_testisooritused'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>
<h1>${_("Testisooritused")}</h1>
${h.form_search(url=h.url('otsing_testisooritused'))}
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
        ${h.flb(_("Testimiskord"),'kord_tahis')}
        ${h.text('kord_tahis', c.kord_tahis, pattern='[^-]*')}
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
        ${h.flb(_("Eesnimi"),'eesnimi')}
        ${h.text('eesnimi', c.eesnimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Perekonnanimi"),'perenimi')}
        ${h.text('perenimi', c.perenimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Isikukood"),'isikukood')}
        ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Verifitseerimise otsus"),'vercode')}
        ${h.select('vercode', c.vercode, model.Verifflog.opt_dec(), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("E-posti aadress"),'epost')}
        ${h.text('epost', c.epost)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Sooritamise olek"),'staatus')}
        ${h.select('staatus', c.staatus, c.opt.opt_s_staatus_test, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Sooritamise oleku testiosa"),'testiosa_id')}
        <%
          opt_testiosa = []
          if c.test_id:
              test = model.Test.get(c.test_id)
              if test:
                 opt_testiosa = test.opt_testiosad
        %>
        ${h.select('testiosa_id', c.testiosa_id, opt_testiosa, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Sooritaja ID"),'sooritaja_id')}
        ${h.posint('sooritaja_id', c.sooritaja_id)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testiosa soorituse ID"),'sooritus_id')}
        ${h.posint('sooritus_id', c.sooritus_id)}
      </div>
    </div>
    % if c.is_debug or c.is_devel:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Soorituse tähis"),'tahised')}
        ${h.text('tahised', c.tahised)}
      </div>
    </div>
    % endif
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.checkbox('soorituskoht', 1, checked=c.soorituskoht, label=_("Soorituskoht"))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.checkbox('valim', 1, checkedif=c.valim, label=_("Valim"))}
        ${h.checkbox('valim', 0, checkedif=c.valim, label=_("Mitte-valim"))}
      </div>
    </div>

  <div class="col d-flex justify-content-end align-items-end">
    <div class="form-group">
    ${h.btn_search()}
    ${h.submit(_("Väljasta CSV"), id="csv", level=2, class_="filter")}
    </div>
  </div>
  </div>
</div>
${h.end_form()}

<script>
  $(function(){
  ## testi ID muutmisel muuta testiosade valik
  $('input#test_id').change(
  callback_select("${h.url_current('index', sub='osa')}", 'test_id', $('#testiosa_id')));
  });
</script>

<div class="listdiv">
  % if not c.items and c.items != '':
  ${_("Otsingu tingimustele vastavaid sooritusi ei leitud")}
  % elif c.items:
  <%include file="testisooritused_list.mako"/>
  % endif 
</div>
