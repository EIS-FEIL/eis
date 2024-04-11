<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'isikuvalik' %>
<%include file="avaldus.tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Eksamile registreerimise taotluse sisestamine")}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Registreerimine"), h.url('regamised'))} 
${h.crumb(_("Registreerimise taotluse sisestamine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'regamised' %>
</%def>

${h.form_save(c.kasutaja and c.kasutaja.id)}
${h.hidden('korrad_id', c.korrad_id)}

${h.rqexp(None, _("Sisesta isikukood või kui isikukood pole teada, siis sünniaeg ja nimi"))}
<div class="gray-legend p-3">
  <div class="row filter">
      <div class="col-lg-3 col-md-6" >
        ${h.flb(_("Isikukood"),'isikukood')}
        <%
          if c.kasutaja:
             value = c.kasutaja.isikukood
          else:
             value = c.isikukood
        %>
        ${h.text('isikukood', value)}
      </div>
      <% if c.kasutaja: c.is_edit = False %>
      <div class="col-lg-3 col-md-6">
        ${h.flb(_("Sünniaeg"), 'synnikpv')}
        ${h.date_field('synnikpv', c.kasutaja and c.kasutaja.synnikpv or c.synnikpv)}
      </div>
      <div class="col-lg-3 col-md-6">
        ${h.flb(_("Eesnimi"), 'eesnimi')}
        ${h.text('eesnimi', c.kasutaja and c.kasutaja.eesnimi or c.eesnimi)}
      </div>
      <div class="col-lg-3 col-md-6">
        ${h.flb(_("Perekonnanimi"), 'perenimi')}
        ${h.text('perenimi', c.kasutaja and c.kasutaja.perenimi or c.perenimi)}
      </div>
  </div>
</div>

<script>
$(function(){
## kui isikukood on sisestatud, siis synnikpv ja nime väljad olgu disabled
  $('#isikukood').keyup(function(){
    var f=$('#synnikpv,#eesnimi,#perenimi');
    f.prop('disabled', ($('#isikukood').val()!=''));
  });
});
</script>


% if c.items:
<% cnt = len(c.items) %>
% if cnt==1:
${_("Andmebaasist leiti 1 sama sünniaja ja nimega isik")}
% else:
${_("Andmebaasist leiti {n} sama sünniaja ja nimega isikut").format(n='<span class="brown">%s</span>' % cnt)}
% endif

<table  class="table table-borderless table-striped" width="100%">
  <thead>
    <th></th>
    <th>${_("Isikukood")}</th>
    <th>${_("Sünniaeg")}</th>
    <th>${_("Nimi")}</th>
    <th>${_("Aadress")}</th>
    <th>${_("E-posti aadress")}</th>
    <th>${_("Telefon")}</th>
  </thead>
  <tbody>
    % for item in c.items:
    <tr>
      <td>
        % if item.isikukood:
        ${h.btn_to(_("See on sama isik"), h.url('regamine_create_avaldus', isikukood=item.isikukood, korrad_id=c.korrad_id), 
        method='post')}
        % else:
        ${h.btn_to(_("See on sama isik"), h.url('regamine_avaldus_edit_isikuandmed', id=item.id, korrad_id=c.korrad_id))}
        % endif
      </td>
      <td>${item.isikukood}</td>
      <td>${h.str_from_date(item.synnikpv)}</td>
      <td>${h.link_to(item.nimi, h.url('admin_eksaminand', id=item.id), target='_blank')}</td>
      <td>
        ${item.tais_aadress}
      </td>
      <td>${item.epost}</td>
      <td>${item.telefon}</td>
    </tr>
    % endfor
  </tbody>
</table>

% endif

% if c.kontroll:
% if not c.sooritajad:
${_("Isik ei ole testidele registreeritud")}
% else:
<table  class="table table-borderless table-striped" width="100%">
  <caption>${_("Olemasolevad registreeringud")}</caption>
  <thead>
    <tr>
      <th>${_("Test")}</th>
      <th>${_("Testimiskord")}</th>
      <th>${_("Testi liik")}</th>
      <th>${_("Registreerimise olek")}</th>
    </tr>
  </thead>
  <tbody>
    % for sooritaja in c.sooritajad:
    <%
      tkord = sooritaja.testimiskord
      test = sooritaja.test
    %>
    <tr>
      <td>${test.nimi}</td>
      <td>
        % if tkord:
        ${tkord.tahised}
        % endif
      </td>
      <td>${test.testiliik_nimi}</td>
      <td>${sooritaja.staatus_nimi}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
% endif

<div class="d-flex flex-wrap">
<div class="flex-grow-1">
  ${h.btn_to(_("Tagasi"), h.url('regamised'), mdicls='mdi-arrow-left-circle', level=2)}
  % if not c.kontroll:
  ${h.submit(_("Kontrolli registreeringuid"), id='kontroll', level=2)}
  % endif
</div>
<div>
% if c.items:
${h.submit(_("Jätka, on uus isik"), id='uus', mdicls2='mdi-arrow-right-circle')}
% else:
${h.submit(_("Jätka"), id='jatka', mdicls2='mdi-arrow-right-circle')}
% endif
</div>
</div>
${h.end_form()}

