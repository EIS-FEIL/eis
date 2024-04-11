## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Keskserver")}
</%def>
<%def name="breadcrumbs()">
${_("Autentimine keskserveris")}
</%def>

${h.form(c.referer, method='POST')}
${h.hidden('referer',c.referer)}
% for key, value in c.data.items():
  ${h.hidden(key, value)}
% endfor

<table width="100%" class="table" >
  <col width="150px"/>
  <col width="80%"/>
  <tr>
    <td class="fh">${_("Nimi")}</td>
    <td>${c.user.fullname}</td>
  </tr>
  <tr>
    <td class="fh">${_("Õppeasutus")}</td>
    <td>${c.data['koht_nimi']}</td>
  </tr>
  <tr>
    <td class="fh" nowrap>${_("Kohalik server")}</td>
    <td>${c.referer}</td>
  </tr>
  <tr>
    <td colspan="2" class="fh">
      ${h.submit(_("Tagasi kohalikku serverisse..."))}
    </td>
  </tr>
</table>
${h.end_form()}
