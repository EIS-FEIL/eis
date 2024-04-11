<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Koolipsühholoogia testide tulemused")} | ${c.kasutaja.nimi}
</%def>      

<%def name="active_menu()">
<% c.menu1 = 'psyhtulemused' %>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'psyhtulemus' %>
<%include file="../testid/tabs.mako"/>
</%def>

<%def name="require()">
<%
  c.includes['plotly'] = True
%>
</%def>

<%def name="breadcrumbs()">
${h.crumb(_("Minu töölaud"), h.url('tookogumikud'))}
${h.crumb(c.test.nimi)}
${h.crumb(c.kasutaja.nimi, h.url('test_psyhtulemus', test_id=c.test_id, testiruum_id=c.testiruum_id, id=c.sooritus.id))}
</%def>

<div class="d-flex">
  <div class="flex-grow-1">
    <h2>${c.kasutaja.nimi}</h2>
  </div>
  <div>
    <img src="/static/images/logo_emp_est.jpg" width="360"/>
  </div>
</div>

${c.tagasiside_html}
