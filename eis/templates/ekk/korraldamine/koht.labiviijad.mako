<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['subtabs'] = True %>
</%def>
<%def name="page_title()">
${_("Testi korraldamine")} | ${c.toimumisaeg.testimiskord.test.nimi} ${h.str_from_date(c.toimumisaeg.alates)}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Korraldamine"), h.url('korraldamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, h.str_from_date(c.toimumisaeg.alates)))} 
${h.crumb(_("Soorituskohtade planeerimine"), h.url('korraldamine_soorituskohad', toimumisaeg_id=c.toimumisaeg.id))}
${h.crumb(c.testikoht.koht.nimi)}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'korraldamised' %>
</%def>
<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'soorituskohad' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<%include file="koht.tabs.mako"/>
</%def>

% if not c.test.on_kutse:
<% testiosa = c.toimumisaeg.testiosa %>
<div class="question-status d-flex flex-wrap justify-content-between mb-2">
  % if testiosa.vastvorm_kood==const.VASTVORM_KONS:
  <div class="item mr-5">
    ${h.flb(_("Konsultandi koolitus"))}
    <br/>
    ${h.str_from_date(c.toimumisaeg.konsultant_koolituskp)}
  </div>

  % elif testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP):
  <div class="item mr-5">
    ${h.flb(_("Välisvaatleja nõutavus"))}
    <br/>
    ${h.sbool(c.toimumisaeg.vaatleja_maaraja)}
  </div>
  % if c.toimumisaeg.vaatleja_koolituskp:
  <div class="item mr-5">
    ${h.flb(_("Vaatleja koolitus"))}
    <br/>
    ${h.str_from_date(c.toimumisaeg.vaatleja_koolituskp)}
  </div>
  % endif
  <div class="item mr-5">
    ${h.flb(_("I hindaja nõutavus"))}
    <br/>
    ${c.opt.MAARAJA.get(c.toimumisaeg.hindaja1_maaraja)}
  </div>
  % if c.testimiskord.sisaldab_valimit:
  <div class="item mr-5">
    ${h.flb(_("I hindaja nõutavus (valim)"))}
    <br/>
    ${c.opt.MAARAJA.get(c.toimumisaeg.hindaja1_maaraja_valim)}
  </div>
  % endif
  % if c.toimumisaeg.hindaja_koolituskp:
  <div class="item mr-5">
    ${h.flb(_("Hindaja koolitus"))}
    <br/>
    ${h.str_from_date(c.toimumisaeg.hindaja_koolituskp)}
  </div>
  % endif
  <div class="item mr-5">
    ${h.flb(_("II hindaja nõutavus"))}
    <br/>
    ${c.opt.MAARAJA.get(c.toimumisaeg.hindaja2_maaraja)}
  </div>
  % if c.testimiskord.sisaldab_valimit:
  <div class="item mr-5">
    ${h.flb(_("II hindaja nõutavus (valim)"))}
    <br/>
    ${c.opt.MAARAJA.get(c.toimumisaeg.hindaja2_maaraja_valim)}
  </div>
  % endif
  <div class="item mr-5">
    ${h.flb(_("Intervjueerija nõutavus"))}
    <br/>
    ${c.opt.MAARAJA.get(c.toimumisaeg.intervjueerija_maaraja)}
  </div>
  % if c.toimumisaeg.intervjueerija_koolituskp:
  <div class="item mr-5">
    ${h.flb(_("Intervjueerija koolitus"))}
    <br/>
    ${h.str_from_date(c.toimumisaeg.intervjueerija_koolituskp)}
  </div>
  % endif
  % elif testiosa.vastvorm_kood == const.VASTVORM_I:
  <div class="item mr-5">
    ${h.flb(_("Intervjueerija nõutavus"))}
    <br/>
    ${c.opt.MAARAJA.get(c.toimumisaeg.intervjueerija_maaraja)}
  </div>
  % if c.toimumisaeg.intervjueerija_koolituskp:
  <div class="item mr-5">
    ${h.flb(_("Intervjueerija koolitus"))}
    <br/>
    ${h.str_from_date(c.toimumisaeg.intervjueerija_koolituskp)}
  </div>
  % endif
  
  % else:
  <div class="item mr-5">
    ${h.flb(_("Hindajate määramine"))}
    <br/>
    ${c.opt.MAARAJA.get(c.toimumisaeg.hindaja1_maaraja)}
  </div>
  % if c.testimiskord.sisaldab_valimit:
  <div class="item mr-5">
    ${h.flb(_("Hindajate määramine (valim)"))}
    <br/>
    ${c.opt.MAARAJA.get(c.toimumisaeg.hindaja1_maaraja_valim)}
  </div>
  % endif
  % endif
</div>
% endif
<% c.can_update = c.user.has_permission('korraldamine', const.BT_UPDATE, obj=c.testikoht) %>

${h.form_save(None, h.url('korraldamine_koht_labiviijad',
toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht.id))}
<div class="listdiv">
<%include file="koht.labiviijad_list.mako"/>
</div>

% if c.can_update:

<script>
  function toggle_viija()
  {
     var visible = ($('input:checked.labiviija_id').length > 0);
     $('div#viija').toggleClass('invisible', !visible);
  }
  $(function(){
    toggle_viija();
    $('.listdiv').on('click', '#all', function(){
      $('input.labiviija_id').prop('checked', this.checked);
      toggle_viija();
    });
  });
  
</script>

<div class="d-flex flex-wrap">
<div id="viija" class="flex-grow-1 invisible">
${h.btn_to_dlg(_("Suuna ümber"), h.url('korraldamine_koht_otsilabikohad',
toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht.id, default=True),
title=_("Läbiviijate suunamine"),width=700, level=2)}

${h.btn_to_dlg(_("Saada teade"), h.url('korraldamine_koht_new_labiviija', sub='mail',
toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht.id, partial=True),
title=_("Teate saatmine"), width=600, height=450, level=2, mdicls='mdi-email')}
</div>


% if c.toimumisaeg.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I, const.VASTVORM_KP):
${h.btn_to_dlg(_("Lisa komisjoniliige"), h.url('korraldamine_koht_otsilabiviijad',
toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht.id,
grupp_id=const.GRUPP_KOMISJON,default=True),title=_("Komisjoniliige"),width=800, level=2, size='lg', mdicls='mdi-plus')}

${h.btn_to_dlg(_("Lisa komisjoni esimees"), h.url('korraldamine_koht_otsilabiviijad',
toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht.id,
grupp_id=const.GRUPP_KOMISJON_ESIMEES,default=True),title=_("Komisjoni esimees"),width=800, level=2, size='lg', mdicls='mdi-plus')}
% endif
</div>
% endif

${h.end_form()}

