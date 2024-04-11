<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Oluline info")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Oluline info"), h.url('admin_avaleheteated'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<%def name="require()">
<%
  c.includes['ckeditor'] = True
  c.includes['dropzone'] = True
%>
</%def>

<div class="row">
  <div class="col-lg-7 p-3" id="div_avaleheteated">

  </div>
  <div class="col-lg-5 p-3 bg-gray-50" id="div_avalehepildid">

  </div>
</div>

<script>
  % if c.controller == 'avaleheteatelogid':
  dialog_load("${h.url('admin_avaleheteatelogid')}", null, 'GET', $('#div_avaleheteated'));
  % else:
  dialog_load("${h.url('admin_avaleheteated')}", null, 'GET', $('#div_avaleheteated'));
  % endif
  dialog_load("${h.url('admin_avalehepildid')}", null, 'GET', $('#div_avalehepildid'));  
</script>
