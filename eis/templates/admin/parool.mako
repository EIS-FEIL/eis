<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Parooli omistamine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Parooli omistamine"), h.url('admin_paroolid'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>

<h1>${_("Parooli omistamine")}</h1>
% if c.kasutaja:   
${h.form_save(None)}
% else:
${h.form_search(url=h.url('admin_paroolid'))}
% endif

<div class="gray-legend p-3 filter-w">
  % if c.kasutaja:
  <div class="row">
    <div class="col">
      ${c.kasutaja.isikukood}
      ${c.kasutaja.eesnimi}
      ${c.kasutaja.perenimi}
      ${h.hidden('id', c.kasutaja.id)}
    </div>
  </div>
  % else:
  <div class="row filter">
    <div class="col-md-3">
      <div class="form-group">
      ${h.flb(_("Isikukood"))}
      ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
  </div>
  % endif
</div>

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    % if c.kasutaja:
    ${h.btn_back(url=h.url('admin_paroolid'))}
    % endif
  </div>
  <div>
  % if c.kasutaja:
  ${h.submit(_("Genereeri parool"))}
  % else:
  ${h.submit(_("Jätka"), name="jatka")}
  % endif
  </div>
</div>

${h.end_form()}

% if c.kasutaja:
  <div class="listdiv my-3">
   <%include file="parool.ajalugu.mako"/>
  </div>
% endif
