<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Lepingud")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Lepingud"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<%def name="require()">
<%
  c.pagexl = True
%>
</%def>

<h1>${_("Lepingud")}</h1>
${h.form_search(url=h.url('admin_lepingud'))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Aasta"),'aasta')}
        <% c.opt_aasta = list(range(model.date.today().year, 2014, -1)) %>
        ${h.select('aasta', c.aasta, c.opt_aasta, empty=True, onchange="this.form.submit()")}
      </div>
    </div>
    <div class="col d-flex flex-wrap justify-content-end align-items-end">
      <div class="flex-grow-1 text-right">
        % if c.user.has_permission('lepingud', const.BT_CREATE):
        ${h.btn_new(h.url_current('new'))}
        % endif
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
  <%include file="lepingud_list.mako"/>
</div>

