<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Registreerimine")}: ${c.item.test.nimi or ''} | ${_("Sooritajad")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'regamised' %>
</%def>

${h.form_save(c.item.id, multipart=True)}
<table width="100%" class="table" >
  <tr>
    <td class="fh">${_("Test")}</td>
    <td>${c.item.test.nimi}</td>
  </tr>
  <tr>
    <td class="fh">${_("Testimiskord")}</td>
    <td>
      ${h.link_to(c.item.tahis or '-', h.url('test_kord',
      test_id=c.item.test.id, id=c.item.id))}
    </td>
  </tr>
  <tr>
    <td class="fh">${_("Sooritajate fail")}</td>
    <td>${h.file('ik_fail', value=_("Fail"))}</td>
  </tr>
  <tr>
    <td colspan="2" class="fh">
      ${_("Suurest failist sooritajate laadimine võib võtta kaua aega, sest iga sooritaja nime kontrollitakse Rahvastikuregistrist.")}
    </td>
  </tr>
</table>
${h.submit()}

<div class="listdiv">
<%include file="sooritajad_list.mako"/>
</div>
