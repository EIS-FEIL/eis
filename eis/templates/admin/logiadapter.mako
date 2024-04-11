<%inherit file="/common/page.mako" />
<%def name="page_title()">
${_("X-tee adapteri logi")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("X-tee adapteri logi"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<%def name="require()">
<%
  c.pagexl = True
%>
</%def>
<h1>${_("X-tee teenuste pakkumise logi")}</h1>
${h.form_search(url=h.url('admin_logiadapter'))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Logi ID"), 'id')}
        ${h.posint('id', c.id)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Isikukood"), 'isikukood')}
        ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Klient"), 'client')}
        ${h.text('client', c.client)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Teenus"),'service')}
        ${h.text('service', c.service)}
      </div>
    </div>
  </div>
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Aeg"),'alates')}
        ${h.date_field('alates', c.alates)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("kell"), 'alates_kell')}
        ${h.time('alates_kell', c.alates_kell, show0=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("kuni"),'kuni')}
        ${h.date_field('kuni', c.kuni)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("kell"),'kuni_kell')}
        ${h.time('kuni_kell', c.kuni_kell, show0=True)}            
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Sisend"),'input')}
        ${h.text('input', c.input)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Väljund"),'output')}
        ${h.text('output', c.output)}
      </div>
    </div>

    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.btn_search()}
        ${h.submit(_("Excel"), id='xls', class_="filter", level=2)}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="logiadapter_list.mako" />
</div>
