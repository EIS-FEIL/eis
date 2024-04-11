<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Sooritajad")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Sooritajad"), h.url('admin_eksaminandid'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<h1>${_("Sooritajad")}</h1>
${h.form_search(url=h.url('admin_eksaminandid'))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Isikukood"),'isikukood')}
        ${h.text('isikukood', c.isikukood, maxlength=50)}
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
        ${h.flb(_("Testi liik"),'testiliik')}
        ${h.select('testiliik', c.testiliik, c.opt.testiliik, empty=True)}
      </div>
    </div>
    % if c.is_devel:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Kool"),'kool')}
        ${h.text('kool', c.kool)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Klass"), 'klass')}
        ${h.select('klass', c.klass, const.EHIS_KLASS, empty=True)}
      </div>
    </div>
    % endif
    <div class="col-12 col-md-8 col-lg-6">
      <div class="form-group">    
        ${h.checkbox('mitukooli', 1, checked=c.mitukooli,
        label=_("Korraga mitmes üldhariduskoolis õppijad"))}
      </div>
    </div>
  </div>
  <div class="d-flex justify-content-end align-items-end">
    <div class="form-group">
      ${h.btn_search()}
      ${h.btn_new(h.url('admin_new_eksaminand'))}
      ${h.btn_to(_("Uuenda EHISest"), h.url('admin_eksaminandid_ehisoppurid'), level=2)}
% if c.user.has_permission('caeeeltest', const.BT_CREATE):
      ${h.btn_to(_("CAE eeltesti sooritanud"), h.url('admin_caeeeltestid'), level=2)}      
% endif
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
  <%include file="eksaminandid_list.mako"/>
</div>
