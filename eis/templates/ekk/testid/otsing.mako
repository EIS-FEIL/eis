<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Testid")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'testid' %>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'testid' %>
</%def>
<h1>${_("Testid")}</h1>
${h.form_search(url=h.url('testid'))}

<div class="gray-legend p-3 filter-w">

  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("ID"),'idr')}
        ${h.text('idr', c.idr)}
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
        ${h.flb(_("Olek"),'staatus')}
        ${h.select('staatus', c.staatus, c.opt.klread_kood('T_STAATUS', empty=True))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testsessioon"),'sessioon')}
        ${h.select('sessioon', c.sessioon, c.opt.testsessioon, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testi liik"),'testiliik')}
        <%
          opt_testiliik = c.opt.testiliik
          if not c.user.has_permission('ekk-testid', const.BT_INDEX, gtyyp=const.USER_TYPE_EKK):
              opt_testiliik = [r for r in opt_testiliik if r[0] == const.TESTILIIK_AVALIK]
          if not c.user.has_permission('ekk-testid', const.BT_INDEX, gtyyp=const.USER_TYPE_AV):
              opt_testiliik = [r for r in opt_testiliik if r[0] != const.TESTILIIK_AVALIK]
        %>
        ${h.select('testiliik', c.testiliik, opt_testiliik, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Periood"),'periood')}
        ${h.select('periood', c.periood, c.opt.klread_kood('PERIOOD', empty=True))}
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
        ${h.flb(_("Koostaja"),'koostaja')}
        ${h.text('koostaja', c.koostaja)}    
      </div>
    </div>
    % if c.is_debug:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Vastamise vorm"),'vastvorm')}
        ${h.select('vastvorm', c.vastvorm, c.opt.klread_kood('VASTVORM', empty=True))}
      </div>
    </div>
    % endif
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
      ${h.btn_search()}
      % if c.user.has_permission('ekk-testid', const.BT_CREATE):
      ${h.btn_new(h.url('new_test'))}
      % endif
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="otsing_list.mako"/>
</div>
