<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'ylesanded' %>
</%def>

<%def name="page_title()">
${c.item.nimi} | ${_("Kasutamise ajalugu")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Ülesandepank"), h.url('ylesanded'))} 
${h.crumb(c.item.nimi or c.item.id, h.url('ylesanne', id=c.item.id))} 
${h.crumb(_("Kasutamise ajalugu"), None, True)}
</%def>

${h.form_save(None)}

% if c.items1:
<table class="table table-borderless table-striped">
  <caption>${_("Ülesande esinemine eksamikeskuse poolt koostatud testides")}</caption>
  <thead>
    ${h.th(_("Test"))}
    ${h.th(_("Toimumisaeg"))}
    ${h.th(_("Komplekt"))}
    ${h.th(_("Sooritajate arv"))}
    ${h.th(_("Keskmine lahendusprotsent"))}
##    <th></th>
  </thead>
  <tbody>
  % for rcd in c.items1:
      <%
        test_id, test_nimi, ta_id, ta_tahised, k_tahis, r_cnt, prot = rcd
      %>
  <tr>
    <td>
      ${h.link_to(test_nimi, h.url('test', id=test_id))}
    </td>
    <td>
      % if ta_tahised:
      ${h.link_to(ta_tahised, h.url('hindamine_arvutused', toimumisaeg_id=ta_id))}
      % else:
      <i>${_("Korraldamata")}</i>
      % endif
    </td>
    <td>${k_tahis}</td>
    <td>${r_cnt}</td>
    <td>${h.fstr(prot,3)}</td>
  </tr>
  % endfor  
  </tbody>
  % if c.total:
  <tfoot>
    <tr>
      <td colspan="3" align="right">
        <b>${_("KOKKU")}</b>
        <%
          t_cnt = c.total['sooritajate_arv']
          t_prot = c.total['lahendatavus']
        %>
      </td>
      <td><b>${t_cnt}</b></td>
      <td><b>${h.fstr(t_prot,3)}</b></td>
    </tr>
  </tfoot>
  % endif
</table>
% else:
${h.alert_notice(_("Ülesanne ei kuulu ühtegi eksamikeskuse testi"), False)}
% endif
${h.end_form()}

% if c.items2:
<table class="table table-borderless table-striped">
  <caption>${_("Ülesande esinemine avalikus vaates koostatud testides")}</caption>
  <thead>
    ${h.th(_("Test"))}
    ${h.th(_("Sooritajate arv"))}
    ${h.th(_("Keskmine lahendusprotsent"))}
  </thead>
  <tbody>
  % for rcd in c.items2:
      <%
        test_id, test_nimi, ta_id, ta_tahised, k_tahis, r_cnt, prot = rcd
      %>
  <tr>
    <td>
      ${test_nimi}
    </td>
    <td>${r_cnt}</td>
    <td>${h.fstr(prot,3)}</td>
  </tr>
  % endfor  
  </tbody>
</table>
% else:
${h.alert_notice(_("Ülesanne ei kuulu ühtegi avaliku vaate testi"), False)}
% endif

