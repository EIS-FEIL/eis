<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Koolipsühholoogia testide tulemused")}
</%def>      
<%def name="breadcrumbs()">
##${h.crumb(_('Koolipsühholoogia testide tulemused'), h.url('psyhtulemused'))}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'kpsyh' %>
</%def>

<h1>${_("Koolipsühholoogia testide tulemused")}</h1>
% if request.is_ext():
<div class="row">
  <div class="col col-12 col-md-6 col-lg-8">
    <p>
      ${_("Projekt „Põhikooli õpilaste psüühiliste protsesside hindamisvahendite komplekti koostamine ja tugispetsialistide koolitamine“ on rahastatud Euroopa Majanduspiirkonna toetuste programmi „Riskilapsed ja –noored“ avatud taotlusvoorust „Kaasamine ja sekkumised haridussüsteemis“.")}
      ${_("Programmi viivad üheskoos ellu Haridus- ja Teadusministeerium, Justiitsministeerium ja Sotsiaalministeerium. Programmi rakendusüksuseks on Eesti Noorsootöö Keskus ning partneriks Norra Kohalike Omavalitsuste ja Regionaalsete Omavalitsuste Liit.")}
    </p>
    <p>
      ${_("Lisainfo programmi kodulehelt")} <a href="http://www.entk.ee/riskilapsedjanoored/">http://www.entk.ee/riskilapsedjanoored/</a>
    </p>
  </div>
  <div class="col col-12 col-md-6 col-lg-4">
    <img src="/static/images/logo_emp_est.jpg" width="360"/>
  </div>
</div>
% endif

${h.form_search(url=h.url('psyhtulemused'))}

 <div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Isikukood"), 'isikukood')}
        ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Alates"),'alates')}
        ${h.date_field('alates', c.alates)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">      
        ${h.flb(_("Kuni"), 'kuni')}
        ${h.date_field('kuni', c.kuni)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 d-flex justify-content-end align-items-end">  
      <div class="form-group">
        ${h.btn_search()}
      </div>
    </div>
  </div>
 </div>

${h.end_form()}

<br/>

<div class="listdiv">
  % if not c.items and c.items != '':
  ${_("Otsingu tingimustele vastavaid õpilasi ei leitud")}
  % elif c.items:
  <%include file="psyhtulemused_list.mako"/>
  % endif 
</div>
