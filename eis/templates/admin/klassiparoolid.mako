<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Paroolide omistamine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Klassi paroolid"),h.url('admin_klassiparoolid'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<h1>${_("Paroolide omistamine")}</h1>
${h.form_search(url=h.url('admin_klassiparoolid'), disablesubmit=True)}

<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-md-2 text-md-right">
      ${h.flb(_("Klass"),'klass')}
    </div>
    <div class="col-md-3">
      ${h.select('klass', c.klass, c.opt_klassid_ryhmad)}
    </div>
    <div class="col-md-2 text-md-right">
      ${h.flb(_("Paralleel"),'paralleel')}
    </div>
    <div class="col-md-3">
      ${h.text('paralleel', c.paralleel)}
    </div>
    <div class="col">
      <div>
      ${h.btn_search()}

      % if not request.is_ext():
      ${h.btn_to_dlg(_("Laadi fail"), h.url('admin_klassiopilased', klass=c.klass, paralleel=c.paralleel),
      title=_("Õpilaste andmete faili laadimine"), width=700, level=2)}
      % endif
      </div>
    </div>
  </div>
</div>

${h.end_form()}

% if c.items == []:
${h.alert_error(_("Õpilasi ei leitud"), False)}

% elif c.items:
${h.form_save(None)}
${h.hidden('klass', c.klass)}
${h.hidden('paralleel', c.paralleel)}
<div class="listdiv">
<%include file="klassiparoolid_list.mako"/>
</div>
${h.end_form()}
% endif

