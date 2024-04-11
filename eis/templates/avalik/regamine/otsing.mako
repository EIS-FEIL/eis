<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Testidele registreerimine")}
</%def>      
<%def name="active_menu()">
<% c.menu1 = 'regamised' %>
</%def>
<%def name="breadcrumbs()">
</%def>
<h1>${_("Registreerimine")}</h1>
<div class="mt-4 mb-5">
${h.btn_to(_('Registreeru'), h.url('regamine_avaldus_testid'))}
</div>

<h2>${_("Minu registreeringud")}</h2>
<div class="listdiv">
<%include file="otsing_list.mako"/>
</div>
