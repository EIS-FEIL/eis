<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'isikuvalik' %>
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

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

<%def name="draw_before_tabs()">
<h1>
  % if c.kasutaja:
  ${c.kasutaja.nimi}
  % else:
  ${_("Testidele registreerimise avaldus")}
  % endif
</h1>
</%def>

${h.form_save(c.kasutaja and c.kasutaja.id, disablesubmit=True)}
${h.hidden('testiliik', c.testiliik)}
<div class="gray-legend p-3">
  <div class="row filter">
    <div class="col-md-4">
      ${h.flb(_("Isikukood"),'isikukood')}
      % if c.kasutaja:
      ${h.text('isikukood', c.kasutaja.isikukood)}
      % else:
      ${h.text('isikukood', c.isikukood)}
      % endif
    </div>
  </div>
</div>

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.btn_to(_("Tagasi"), h.url('nimekirjad_testimiskorrad'), mdicls='mdi-arrow-left-circle', level=2)}
  </div>
  <div>
    ${h.submit(_("Jätka"), id='jatka', mdicls2='mdi-arrow-right-circle')}
  </div>
</div>
${h.end_form()}
