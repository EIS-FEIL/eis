<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Testi korraldamine")} | ${c.toimumisaeg.testimiskord.test.nimi} ${h.str_from_date(c.toimumisaeg.alates)}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Testi läbiviimise korraldamine"), h.url('korraldamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.tahised))}
${h.crumb(_("Läbiviijad"), h.url('korraldamine_labiviijad', testikoht_id=c.testikoht.id))}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

<%def name="draw_before_tabs()">
<h1>${_("Testi läbiviimise korraldamine")}</h1>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'labiviijad' %>
<%include file="tabs.mako"/>
</%def>

<% testiosa = c.toimumisaeg.testiosa %>

<div class="question-status d-flex flex-wrap justify-content-between mb-2">
  <div class="item mr-5">
    ${h.flb(_("Välisvaatleja nõutavus"),'vaatleja_maaraja')}
    <div id="vaatleja_maaraja">
      ${h.sbool(c.toimumisaeg.vaatleja_maaraja)}
    </div>
  </div>
  % if c.toimumisaeg.vaatleja_koolituskp:
  <div class="item mr-5">
    ${h.flb(_("Vaatleja koolitus"),'vaatleja_koolituskp')}
    <div id="vaatleja_koolituskp">
      ${h.str_from_date(c.toimumisaeg.vaatleja_koolituskp)}
    </div>
  </div>
  % endif
  % if testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP):
  <div class="item mr-5">
    ${h.flb(_("I hindaja nõutavus"), 'hindaja1_maaraja')}
    <div id="hindaja1_maaraja">
      ${c.opt.MAARAJA.get(c.toimumisaeg.hindaja1_maaraja)}
    </div>
  </div>
  % if c.toimumisaeg.hindaja_koolituskp:
  <div class="item mr-5">
    ${h.flb(_("Hindaja koolitus"),'hindaja_koolituskp')}
    <div id="hindaja_koolituskp">
      ${h.str_from_date(c.toimumisaeg.hindaja_koolituskp)}
    </div>
  </div>
  % endif
  <div class="item mr-5">
    ${h.flb(_("II hindaja nõutavus"), 'hindaja2_maaraja')}
    <div id="hindaja2_maaraja">
      ${c.opt.MAARAJA.get(c.toimumisaeg.hindaja2_maaraja)}
    </div>
  </div>
  % endif
  % if testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP, const.VASTVORM_I):  
  <div class="item mr-5">
    ${h.flb(_("Intervjueerija nõutavus"), 'intervjueerija_maaraja')}
    <div id="intervjueerija_maaraja">
      ${c.opt.MAARAJA.get(c.toimumisaeg.intervjueerija_maaraja)}
    </div>
  </div>
  % if c.toimumisaeg.intervjueerija_koolituskp:
  <div class="item mr-5">
    ${h.flb(_("Intervjueerija koolitus"), 'intervjueerija_koolituskp')}
    <div id="intervjueerija_koolituskp">
      ${h.str_from_date(c.toimumisaeg.intervjueerija_koolituskp)}
    </div>
  </div>
  % endif
  % endif
</div>

<div class="listdiv">
<%include file="labiviijad_list.mako"/>
</div>

${h.btn_to_dlg(_("Lisa komisjoniliige"), h.url('korraldamine_otsilabiviijad',
testikoht_id=c.testikoht.id,
grupp_id=const.GRUPP_KOMISJON,default=True), 
title=_("Komisjoniliikme lisamine"),level=2, mdicls='mdi-plus')}

${h.btn_to_dlg(_("Lisa komisjoni esimees"), h.url('korraldamine_otsilabiviijad',
testikoht_id=c.testikoht.id,
grupp_id=const.GRUPP_KOMISJON_ESIMEES,default=True), 
title=_("Komisjoni esimehe lisamine"),width=700, level=2, mdicls='mdi-plus')}

% if c.toimumisaeg.admin_maaraja and c.on_lisa_admin:
${h.btn_to_dlg(_("Lisa testi administraator"), h.url('korraldamine_otsilabiviijad',
testikoht_id=c.testikoht.id,
grupp_id=const.GRUPP_T_ADMIN,default=True), 
title=_("Testi administraatori lisamine"),width=700, level=2, mdicls='mdi-plus')}
% endif

${h.btn_to(_("Väljasta CSV"), h.url_current('index', csv=1), id='csv',
style="float:right;", level=2)}

