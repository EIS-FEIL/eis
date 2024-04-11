<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'isikuandmed' %>
<%include file="avaldus.tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Eksamile registreerimise taotluse sisestamine")}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Testi sooritajate määramine"), h.url('nimekirjad_testimiskorrad'))} 
${h.crumb(_("Avaldus"))}
</%def>
<%def name="draw_before_tabs()">
<h1>${c.kasutaja.nimi}</h1>
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

${h.form_save(c.kasutaja.id)}
${h.hidden('testiliik', c.testiliik)}
<div class="form-wrapper m-3">
  <div class="form-group row">
    ${h.flb3(_("Sooritaja"), 'k_nimi')}
    <div class="col">
      <span id="k_nimi">
        % if c.sooritaja:
        ${c.sooritaja.eesnimi}
        ${c.sooritaja.perenimi}
        % else:
        ${c.kasutaja.eesnimi}
        ${c.kasutaja.perenimi}
        % endif
      </span>

      % if c.kasutaja.isikukood:
      ${c.kasutaja.isikukood}
      % else:
      ${h.str_from_date(c.kasutaja.synnikpv)}
      % endif
    </div>
  </div>
% if c.opilane:
  <div class="form-group row">
    ${h.flb3(_("Õppeasutus"))}
    <div class="col">
      ${c.opilane.koht and c.opilane.koht.nimi}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Klass ja paralleel"))}
    <div class="col">
      ${c.opilane.klass} ${c.opilane.paralleel}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Õppevorm"))}
    <div class="col">
      ${c.opilane.oppevorm_nimi}
    </div>
  </div>
% else:
  <div class="form-group row">
    <div class="col">
    ${h.alert_notice(_("Pole andmeid selle kohta, et see isik oleks õpilane"), False)}
    </div>
  </div>
% endif
  
</div>

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
##    ${h.submit(_("Tagasi"), id="tagasi", mdicls2='mdi-arrow-left-circle')}
    ${h.btn_to(_("Tagasi"), h.url('nimekirjad_edit_avaldus', id=c.kasutaja.id, testiliik=c.testiliik), class_='leave-formpage', mdicls='mdi-arrow-left-circle', level=2)}
  </div>
  <div>
##    ${h.submit(_("Jätka"), id="jatka", mdicls2='mdi-arrow-right-circle')}
    ${h.btn_to(_("Jätka"), h.url('nimekirjad_avaldus_testid', id=c.kasutaja.id, testiliik=c.testiliik), mdicls2='mdi-arrow-right-circle')}
  </div>
</div>
${h.end_form()}

<%include file="avaldus.katkestus.mako"/>                             
