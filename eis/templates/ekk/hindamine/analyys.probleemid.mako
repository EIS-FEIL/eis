<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['subtabs'] = True %>
</%def>
<%def name="page_title()">
${c.toimumisaeg.testimiskord.test.nimi} ${c.toimumisaeg.millal} | ${_("Hindamisprobleemid")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"), h.url('hindamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.millal))} 
${h.crumb(_("Hindamise analüüs"), h.url('hindamine_analyys_protokollid', toimumisaeg_id=c.toimumisaeg.id))}
${h.crumb(_("Hindamisprobleemid"))}
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
<h3>${_("Tähelepanu vajavad hindamised")}</h3>

${h.form_search(url=h.url('hindamine_analyys_probleemid', toimumisaeg_id=c.toimumisaeg.id))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Probleemi liik"),'probleem')}
            <%
               opt_probleem = [(const.H_PROBLEEM_SISESTAMATA, _("Sisestamata")),
                               (const.H_PROBLEEM_SISESTUSERINEVUS, _("Sisestusvead")),
                               (const.H_PROBLEEM_HINDAMISERINEVUS, _("Hindamiserinevused")),
                               (const.H_PROBLEEM_TOOPUUDU, _("Töö puudu"))]
            %>
            ${h.select('probleem', c.probleem, opt_probleem, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Hindamistase"),'hindamistase')}
            <%
              opt_hindamistase = [(const.HINDAJA1, 'I'), (const.HINDAJA3, 'III'), (const.HINDAJA4, 'IV')]
            %>
            ${h.select('hindamistase', c.hindamistase, opt_hindamistase, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Hindamiskogum"),'hindamiskogum_id')}
            <% 
               opt_hindamiskogum = [(hk.id, hk.tahis) for hk in c.toimumisaeg.testiosa.hindamiskogumid if hk.staatus] 
            %>            
            ${h.select('hindamiskogum_id', c.hindamiskogum_id, opt_hindamiskogum, empty=True)}
      </div>
    </div>
    % if c.testimiskord.sisaldab_valimit:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.checkbox('valim', 1, checkedif=c.valim, label=_("Valim"))}
        ${h.checkbox('valim', 0, checkedif=c.valim, label=_("Mitte-valim"))}
      </div>
    </div>
    % endif
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.btn_search()}
        ${h.submit(_("Excel"), id='xls', level=2)}            
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="analyys.probleemid_list.mako"/>
</div>
<br/>
