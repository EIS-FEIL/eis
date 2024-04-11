<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Rahvusvaheliste eksamite tunnistused")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_('Rahvusvaheliste eksamite tunnistused'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<% 
c.can_update = c.user.has_permission('rveksamid', const.BT_UPDATE)
%>    
<h1>${_("Rahvusvaheliste eksamite tunnistused")}</h1>

<table width="100%" class="table table-striped" >
  % for rcd in c.items:
  <tr>
    <td>
      ${h.link_to(rcd.nimi, h.url('admin_edit_rveksam', id=rcd.id))}
    </td>
  </tr>
  % endfor
  % if not len(c.items):
  <tr>
    <td>${_("Ühegi rahvusvahelise eksami andmeid pole kirjeldatud")}</td>
  </tr>
  % endif
</table>

<br/>

    % if c.can_update:
      ${h.btn_to(_('Lisa'), h.url('admin_new_rveksam'))}
    % endif

