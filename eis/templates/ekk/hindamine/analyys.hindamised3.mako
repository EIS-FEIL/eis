<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['subtabs'] = True %>
</%def>
<%def name="page_title()">
${c.toimumisaeg.testimiskord.test.nimi} ${c.toimumisaeg.millal} | ${_("Kolmas hindamine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"), h.url('hindamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.millal))} 
${h.crumb(_("Hindamise analüüs"), h.url('hindamine_analyys_protokollid', toimumisaeg_id=c.toimumisaeg.id))}
${h.crumb(_("Kolmas hindamine"))}
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
<h3>${_("Kolmas hindamine")}</h3>

${h.form_search(url=h.url('hindamine_analyys_hindamised3', toimumisaeg_id=c.toimumisaeg.id))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Hindamiskogum"),'hindamiskogum_id')}
            <% 
               opt_hindamiskogum = [(hk.id, hk.tahis) for hk in c.toimumisaeg.testiosa.hindamiskogumid if hk.staatus] 
            %>            
            ${h.select('hindamiskogum_id', c.hindamiskogum_id,
            opt_hindamiskogum, empty=True, onchange='this.form.submit()')}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
            ${h.radio('punktides', 0, checked=not c.punktides, label=_("Näita palle"))}
            ${h.radio('punktides', 1, checked=c.punktides, label=_("Näita toorpunkte"))}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.btn_search()}
        ${h.submit(_("CSV"), id='csv', level=2)}                        
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="analyys.hindamised3_list.mako"/>
</div>

