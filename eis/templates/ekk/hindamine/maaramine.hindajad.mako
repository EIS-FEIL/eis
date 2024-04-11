<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['subtabs'] = True %>
</%def>
<%def name="page_title()">
${_("Hindamine")} | ${c.toimumisaeg.testimiskord.test.nimi} ${c.toimumisaeg.millal}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"), h.url('hindamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.millal))} 
${h.crumb(_("Läbiviijate määramine"), h.url('hindamine_hindajad', toimumisaeg_id=c.toimumisaeg.id))}
${h.crumb(_("Esmane (I ja II) hindamine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'hindamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'maaramine' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<%include file="maaramine.tabs.mako"/>
</%def>

<%include file="maaramine.sooritustearvud.mako"/>

${h.form_search(url=h.url('hindamine_hindajad', toimumisaeg_id=c.toimumisaeg.id))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Hindaja"),'hindaja_id')}
        ${h.select('hindaja_id', c.hindaja_id, c.hindajad_opt, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Hindamiskogum"),'hindamiskogum_id')}
        ${h.select('hindamiskogum_id', c.hindamiskogum_id, c.hindamiskogumid_opt, empty=True)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.submit(_("CSV"), id='csv', level=2)}            
        ${h.btn_search()}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="maaramine.hindajad_list.mako"/>
</div>

% if c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I, const.VASTVORM_KP, const.VASTVORM_SH):
${h.btn_to_dlg(_("Lisa hindaja"), h.url('hindamine_new_hindaja', toimumisaeg_id=c.toimumisaeg.id, partial=True),
title=_("Hindaja lisamine"), width=650, level=2, mdicls='mdi-plus')}

% if c.testimiskord.sisaldab_valimit:
${h.btn_to_dlg(_("Lisa valimi hindaja"), h.url('hindamine_new_hindaja', toimumisaeg_id=c.toimumisaeg.id, partial=True, valimis=1),
title=_("Valimi hindaja lisamine"), width=650, level=2, mdicls='mdi-plus')}
% endif
% endif
