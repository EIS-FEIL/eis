<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Statistikaraportite avaldamine")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="require()">
<% c.includes['progressbar'] = True %>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'muud' %>
</%def>

<h1>${_("Statistikaraportite avaldamine")}</h1>
${h.form_search()}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    ${h.flb3(_("Testsessioon"),'sessioon_id', 'text-right')}
    <div class="col-md-9">
      ${h.select('sessioon_id', c.sessioon_id, c.opt_sessioon,
      onchange="this.form.submit()")}
    </div>
  </div>
</div>

${h.end_form()}

<div class="alert alert-secondary fade show" role="alert">
  <i class="mdi mdi-information-outline"></i>
      <ul>
        <li>
          ${_("Avaliku vaates statistikas saab avaldada ainult neid testimiskordi, mis on kasutusel Harno statistikas.")}
        <li>
          ${_("Harno statistikasse saab avaldamiseelse ülevaatamise eesmärgil kaasata testimiskordi, mis ei ole veel avalikus vaates avaldatud.")}
        <li>
          ${_("Raportid genereeritakse Harno statistikasse kaasatud testimiskordade põhjal.")}
        <li>
          ${_("Raporti avaldamise nupp ilmub siis, kui testi kõik Harno statistikasse kaasatud testimiskorrad on ka avalikus vaates avaldatud, sest vastasel juhul ei vasta raport avaldatud testimiskordade valikule.")}
        <li>
          ${_("Testi avaldatud testimiskordade valiku muutmisel kustutatakse avaldatud raportid, kuna nende sisu ei vasta enam avaldatud testimiskordade valikule.")}
        <li>
          ${_("Testi Harno statistikasse kaasatud testimiskordade valiku muutmisel kustutatakse testi kohta seni genereeritud raportid.")}
      </ul>
</div>

${h.form_save(None)}
${h.hidden('sessioon_id', c.sessioon_id)}
% if request.params.get('debug'):
${h.hidden('debug', request.params.get('debug'))}
% endif

<div class="listdiv">
<%include file="statistikaraportid_list.mako"/>
</div>

<div class="mb-2">
<span id="add" class="d-none">
  ${h.btn_to_dlg(_("Muuda statistika avaldamist"), h.url('muud_new_statistikaraport'), 
title=_("Muuda avaldamist"), width=450, form='$(this.form)', id='avaldamine')}
</span>

<span id="add2" class="d-none">
  ${h.submit(_("Genereeri raportid"), id="raport")}
</span>
</div>
${h.end_form()}

% if c.arvutusprotsessid:
<%
  c.protsessid_no_caption = True
  c.url_refresh = h.url('muud_statistikaraportid', sessioon_id=c.sessioon_id, sub='progress')
%>
<%include file="/common/arvutusprotsessid.mako"/>
% endif
