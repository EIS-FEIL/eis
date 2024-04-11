<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['subtabs'] = True %>
</%def>
<%def name="page_title()">
${c.toimumisaeg.testimiskord.test.nimi} ${c.toimumisaeg.millal} | ${_("Mõõtmisvea piiridesse jäävad tulemused")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"), h.url('hindamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.millal))} 
${h.crumb(_("Hindamise analüüs"), h.url('hindamine_analyys_protokollid', toimumisaeg_id=c.toimumisaeg.id))}
${h.crumb(_("Mõõtmisvea kontroll"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'hindamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'analyys' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<%include file="analyys.tabs.mako"/>
</%def>

<h3>${_("Mõõtmisvea piiridesse jäävad tulemused")}</h3>

${h.form_search(url=h.url_current('index'))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    ${h.flb3(_("Standardne mõõtmisviga"),'mootmisviga','text-md-right')}
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.posint5('mootmisviga', c.mootmisviga, maxvalue=100, maxlength=2)} 
        ${_("protsendipunkti")}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.btn_search()}
        ${h.submit(_("Väljasta PDF"), id='pdf')}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="analyys.mootmisvead_list.mako"/>
</div>
<br/>
