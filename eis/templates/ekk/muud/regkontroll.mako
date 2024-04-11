<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Registreerimise kontroll")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'muud' %>
</%def>

<h1>${_("Registreerimise kontroll")}</h1>
${h.form_search()}
<div class="gray-legend p-3 filter-w">
##  ##${h.toggle_filter()}

  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Klass"), 'klass')}
        ${h.select('klass', c.klass, ['9','12'], empty=True)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
      ${h.btn_search()}
      ${h.submit(_("Excel"), id='xls', level=2)}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

% if c.items != '':
<h5>
  % if c.klass == '9':
  ${_("9. klassi õpilased, kes ei ole registreeritud kõigile kohustuslikele eksamitele või on registreeritud mitmele valikeksamile")}
  % elif c.klass == '12':
  ${_("12. klassi õpilased, kes ei ole registreeritud kõigile kohustuslikele eksamitele ega ole neid ka varem sooritanud")}
  % endif
</h5>
<div class="listdiv">
<%include file="regkontroll_list.mako"/>
</div>
% endif

