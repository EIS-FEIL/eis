<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Koolipsühholoogia testide tulemused")} | ${c.kasutaja.nimi}
</%def>      
<%def name="active_menu()">
<% c.menu1 = 'muud' %>
</%def>

<table width="100%">
  <tr>
    <td>
      <h2>${c.kasutaja.nimi}</h2>
    </td>
    <td width="370" valign="top">
      <img src="/static/images/logo_emp_est.jpg" width="360"/>
    </td>
  </tr>
</table>

${c.tagasiside_html}
