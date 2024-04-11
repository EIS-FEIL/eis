<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Testi läbiviimise nõusolekud")}
</%def>
<%def name="breadcrumbs()">
</%def>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

${h.form_save(None)}

<%include file="/admin/kasutaja.profiilisisu.mako"/>

<table width="100%" class="table" >
  <tbody>
    <tr>
      <td class="fh" width="150px">${_("Märkus")}</td>
      <td>${h.textarea('f_markus',c.profiil.markus)}</td>
    </tr>
  </tbody>
</table>
<br/>
% if c.is_edit:
${h.submit()}
% endif

${h.end_form()}

