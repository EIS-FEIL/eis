<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Klassifikaatorid")}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>

% if c.search_template:
<div id="boxback">
  <%include file="${c.search_template}"/>
</div>
% endif

<table width="100%">
  <tr>
    <td valign="top">
      <div id="listdiv">
        <%include file="${c.list_template}"/>
      </div>
    </td>
    <td valign="top">
      <div id="itemdiv">
        % if c.item and c.item_template:
         <%include file="${c.item_template}"/>
        % endif
      </div>
    </td>
  </tr>
</table>
