<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Klassifikaatorid")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Klassifikaatorid"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<h1>${_("Klassifikaatorid")}</h1>
${h.form_search()}
<div class="p-3" style="text-align:right">
${_("Tõlkekeel")}: ${h.select('lang', c.lang, c.opt.SOORKEEL, empty=True, style="width:190px", onchange="this.form.submit()")}
</div>
${h.end_form()}

<div class="listdiv">
  % if c.lang:
  <%include file="tklassifikaatorid_list.mako"/>
  % else:
  <%include file="klassifikaatorid_list.mako"/>
  % endif
</div>
