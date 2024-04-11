<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Tugiisikud")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Päringud"))}
${h.crumb(_("Tugiisikud"), h.url('otsing_tugiisikud'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>
<h1>${_("Tugiisikud")}</h1>
${h.form_search(url=h.url_current('index'))}
<div class="gray-legend p-3 filter-w">
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
        ${h.flb(_("Tugiisiku isikukood"),'isikukood')}
        ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.radio('kokku', '', checked=not c.kokku, label=_("Kuva tugiisikuga sooritused"))}
        ${h.radio('kokku', 1, checked=c.kokku, label=_("Kuva tugiisikuga soorituste arv"))}        
      </div>
    </div>

    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.submit(_("Väljasta CSV"), id="csv", level=2, class_="filter")}
        ${h.btn_search()}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
  % if not c.items and c.items != '':
  ${_("Otsingu tingimustele vastavaid andmeid ei leitud")}
  % elif c.items:
  <%include file="tugiisikud_list.mako"/>
  % endif 
</div>
