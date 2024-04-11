<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Eksamiserverid")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Eksamiserverid"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<div class="p-3 d-flex">
  <div class="flex-grow-1">
    <h1>${_("Eksamiserverite klastrid")}</h1>
    
  </div>
  <div class="text-right">
    ${h.btn_to_dlg(_("Lisa"), h.url('admin_new_klaster'), level=1, title=_("Uus klaster"), mdicls='mdi-plus')}
  </div>
</div>
  
<div class="listdiv">
  <%include file="klastrid_list.mako"/>
</div>
