## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Testi läbiviimise korraldamine"), h.url('korraldamised'))} 
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

<%def name="page_title()">
${_("Korraldamine")}
</%def>      
<h1>${_("Testi läbiviimise korraldamine")}</h1>
${h.form_search(url=h.url('korraldamised'))}
<div class="gray-legend p-3 filter-w">
##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Toimumise algusaeg"),'alates')}
        ${h.date_field('alates', h.str_from_date(c.alates), allow_clear=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("kuni"),'kuni')}
        ${h.date_field('kuni', h.str_from_date(c.kuni), allow_clear=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Testsessioon"),'testsessioon_id')}
        ${h.select('testsessioon_id', c.testsessioon_id, model.Testsessioon.get_opt(), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.radio('aktiiv', 't', checked=c.aktiiv != 'f', label=_("Näita aktiivsed testid"))}
        ${h.radio('aktiiv', 'f', checked=c.aktiiv == 'f', label=_("Näita kõik testid"))}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div>
        ${h.btn_search()}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="otsing_list.mako"/>
</div>
