<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'isikuandmed' %>
<%include file="avaldus.tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Eksamile registreerimise taotluse sisestamine")}
</%def>      
<%def name="active_menu()">
<% c.menu1 = 'regamised' %>
</%def>
<%def name="breadcrumbs()">
${h.crumb(_('Registreerimine'), h.url('regamised'))} 
${h.crumb(_('Registreerimise taotluse sisestamine'))}
</%def>
<%include file="avaldus.teade.mako"/>
${h.form_save(None)}
<h1>${_("Registreerimiseks täida väljad")}</h1>
<%include file="avaldus.valitudtestid.mako"/>

<h2>${_("Minu andmed")}</h2>
<% c.submit_rr = True %>
<%include file="isikuandmed.mako"/>

% if c.testiliik not in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS, const.TESTILIIK_KOOLITUS):
<%include file="/ekk/regamine/haridusandmed.mako"/>
<% c.on_iseregaja = True %>
<%include file="/ekk/regamine/rahvusvaheline_eksam_avaldus.mako"/>
% endif

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.btn_to(_('Tagasi'), h.url('regamine_avaldus_testid_testiliik', testiliik=c.testiliik),
    mdicls='mdi-arrow-left-circle', level=2)}
  </div>
  <div>
    ${h.submit(_('Jätka'), mdicls2='mdi-arrow-right-circle')}
  </div>
</div>
${h.end_form()}

<%include file="avaldus.katkestus.mako"/>
               
