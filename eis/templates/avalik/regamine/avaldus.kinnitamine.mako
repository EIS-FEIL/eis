<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'kinnitamine' %>
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

<% regamata = [r for r in c.sooritajad if r.staatus == const.S_STAATUS_REGAMATA] %>
% if regamata:
<h1>${_("Registreerimise kinnitamine")}</h1>
<div class="mb-4">
  ${_('Kontrolli sisestatud andmed ja kliki nupul "Kinnita avaldus".')}
</div>
% endif

<%include file="avaldus.valitudtestid.mako"/>

<% c.is_edit = False %>
<div class="d-flex flex-wrap">
  <h2 class="flex-grow-1">${_("Minu andmed")}</h2>
  ${h.link_to(_("Muuda andmeid"), h.url('regamine_avaldus_isikuandmed', testiliik=c.testiliik))}
</div>
<%include file="isikuandmed.mako"/>

## Õppimine
% if c.testiliik not in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS, const.TESTILIIK_KOOLITUS):
<%include file="/ekk/regamine/haridusandmed.mako"/>
<% c.on_iseregaja = True %>
<%include file="/ekk/regamine/rahvusvaheline_eksam_avaldus.mako"/>
% endif

<%
  tyhistatav = False
  for sooritaja in c.sooritajad:
     if sooritaja.voib_reg():
         tyhistatav = True
         break
%>
<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.btn_to(_('Tagasi'), h.url('regamine_avaldus_isikuandmed', testiliik=c.testiliik), mdicls='mdi-arrow-left-circle', level=2)}
    % if not regamata and tyhistatav:
    ${h.btn_to(_("Tühista registreering"), h.url('regamine_avaldus_tyhista', testiliik=c.testiliik), level=2)}
    % endif

  </div>
  <div>
    % if regamata:
    ${h.btn_to(_('Katkesta'), h.url('regamine_avaldus_delete_kinnitamine', testiliik=c.testiliik), method='delete', confirm=_('Kas oled kindel, et soovid registreerimise katkestada?'), class_='confirm-yesno', level=2)}
    ${h.submit(_('Kinnita avaldus'))}
    % elif c.tasumata:
    ${h.submit(_("Riigilõivu tasumine"))}
    % else:
    ${h.submit(_('Kinnitamise kontroll'))}    
    % endif
  </div>
</div>
               
${h.end_form()}

<% c.continue_url = h.url('regamine_avaldus_kinnitamine', testiliik=c.testiliik) %>
<%include file="avaldus.katkestus.mako"/>
               
