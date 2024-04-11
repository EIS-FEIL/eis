<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Testi korraldamine")} | ${c.test.nimi} ${h.str_from_date(c.toimumisaeg.alates)}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Korraldamine"), h.url('korraldamised'))} 
${h.crumb('%s %s' % (c.test.nimi, h.str_from_date(c.toimumisaeg.alates)))} 
${h.crumb(_("Soorituskohtade planeerimine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'korraldamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<%
  vastvorm = c.testiosa.vastvorm_kood
  c.can_update = c.user.has_permission('korraldamine', const.BT_UPDATE, obj=c.test)
%>

% if not c.test.on_kutse:
${self.lubade_vorm()}
% endif

${h.form_search(url=h.url('korraldamine_soorituskohad', toimumisaeg_id=c.toimumisaeg.id))}

<div class="gray-legend p-3 filter-w">
  % if not c.test.on_kutse:
  ${self.tr_filter(vastvorm)}
  % endif
  <div class="d-flex justify-content-end align-items-end">    
      ${self.tr_nupud(c.maaramata)}
  </div>
</div>
${h.end_form()}

% if c.arvutusprotsessid:
<%
c.url_refresh = h.url('korraldamine_valim', toimumisaeg_id=c.toimumisaeg.id, sub='progress')
%>
<%include file="/common/arvutusprotsessid.mako"/>
% endif

<div>
% if vastvorm == const.VASTVORM_KONS:
${_("Konsultatsiooniga seotud testides on kokku {n} konsultatsioonisooviga sooritajat.").format(n=c.cnt_total)}
  % if c.cnt_total and c.piirkond_id:
 ${_("Valitud piirkonnas on {n} sooritajat.").format(n=c.sooritajad_piirkonniti.get(c.piirkond_id) or 0)}
  % endif
% else:
% if c.maaramata:
${h.link_to(_("Testisoorituskoht on määramata {n} testisooritajal").format(n=c.maaramata),
   h.url('korraldamine_koht_sooritajad', toimumisaeg_id=c.toimumisaeg.id, testikoht_id=0))}
% elif c.maaratud:
${_("Kõigil sooritajatel on soorituskoht määratud.")}
% else:
${_("Sooritajaid ei ole registreeritud")}
% endif
% endif
</div>

${h.form(None)}
<div class="listdiv">
<%include file="soorituskohad_list.mako"/>
</div>
<br/>

<script>
  function toggle_testiruum()
  {
         var invisible = ($('input:checked.tr-id').length == 0);
         $('span#suunaruum').toggleClass('invisible', invisible);
  }
  $(function(){
     toggle_testiruum();
  });
</script>

% if c.test.on_kutse:
% if c.maaratud and not c.maaramata and c.can_update:
% if c.toimumisaeg.on_hindamisprotokollid:
${h.btn_to(_("Kontrolli"), h.url_current('create', sub='kogused'), method='post')}
% else:
${h.btn_to(_("Kinnita"), h.url_current('create', sub='kogused'), method='post')}
% endif
% endif
<span>
  % if not c.toimumisaeg.on_hindamisprotokollid:
  ${_("Toimumisaja andmed on kinnitamata")}
  % endif
</span>
% endif

% if c.can_update:
<span id="suunaruum" class="invisible">
${h.btn_to_dlg(_("Suuna ümber"), 
h.url('korraldamine_otsikohad', toimumisaeg_id=c.toimumisaeg.id, default=True),
title=_("Sooritajate suunamine"), size='lg', params="$(this.form).find('input.tr-id').serialize()")}
</span>

<span style="float:right">
${h.link_to(_("Teated"), h.url('otsing_teated', toimumisaeg_id=c.toimumisaeg.id))}
  % if c.testimiskord.reg_ekk and c.user.has_permission('regamine', const.BT_UPDATE, obj=c.test):
${h.link_to(_("Registreeri sooritaja"), h.url('regamine_new_avaldus', korrad_id=c.testimiskord.id),
class_="button button1")}
${h.link_to(_("Laadi registreerimise nimekiri"),
h.url('regamine_nimistu_testivalik', testiliik=c.test.testiliik_kood, korrad_id=c.testimiskord.id),
class_="button button1")}
% endif
</span>
% endif

${h.end_form()}

## kinnitamise väljund
% if c.kontroll_err or c.kontroll_ok:
<div style="padding:5px 0">
% if c.kontroll_err:
${h.alert_error(c.kontroll_err)}
% elif c.kontroll_ok:
${h.alert_success(c.kontroll_ok)}
% endif
</div>
% endif

<div id="jaotamine" class="invisible">
<%include file="jaotusvalik.mako"/>
</div>


<%def name="lubade_vorm()">
${h.form_save(None)}
${h.hidden('sub', 'luba')}
<div class="d-md-flex">
  <%
    if c.can_update and not c.on_piirkondlik:
       disabled = None
       onchange = "$(this).parents('form').submit()"
    else:
       disabled = True
       onchange = None
  %>
      ${h.checkbox('reg_labiviijaks', 1, 
      checked=c.toimumisaeg.reg_labiviijaks,
      class_="nosave",
      label=_("Läbiviijaks olemise nõusoleku andmine lubatud"),
      onchange=onchange, disabled=disabled)}

      ${h.checkbox('ruumide_jaotus', 1, 
      checked=c.toimumisaeg.ruumide_jaotus,
      label=_("Soorituskohtades ruumide määramine lubatud"),
      class_="nosave",
      onchange=onchange, disabled=disabled)}  

      ${h.checkbox('labiviijate_jaotus', 1, 
      checked=c.toimumisaeg.labiviijate_jaotus,
      label=_("Soorituskohtades läbiviijate määramine lubatud"),
      class_="nosave",
      onchange=onchange, disabled=disabled)}

      ${h.checkbox('kohad_avalikud', 1, 
      checked=c.toimumisaeg.kohad_avalikud,
      label=_("Soorituskohad avalikud"),
      class_="nosave",
      onchange=onchange, disabled=disabled)}

      ${h.checkbox('kohad_kinnitatud', 1, 
      checked=c.toimumisaeg.kohad_kinnitatud,
      label=_("Soorituskohtade andmed kinnitatud"),
      class_="nosave",
      onchange=onchange, disabled=disabled)}
</div>
${h.end_form()}
</%def>

<%def name="tr_filter(vastvorm)">
   <div class="row">
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.piirkond_id)}">
      <div class="form-group">
        ${h.flb(_("Piirkond"),'piirkond_id')}
            <%
               c.piirkond_id = c.piirkond_id
               c.piirkond_field = 'piirkond_id'
            %>
            <%include file="/admin/piirkonnavalik.mako"/>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.maakond_kood)}">
      <div class="form-group">        
        ${h.flb(_("Maakond"),'maakond_kood')}
        ${h.select('maakond_kood', c.maakond_kood, 
            model.Aadresskomponent.get_opt(None),empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.nimi)}">
      <div class="form-group">        
        ${h.flb(_("Nimetus"),'nimi')}
        ${h.text('nimi', c.nimi)}
      </div>
    </div>
    % if vastvorm != const.VASTVORM_KONS:
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.sooritajatearv)}">
      <div class="form-group">        
        ${h.flb(_("Sooritajate arv, kuni"),'sooritajatearv')}
        ${h.posint('sooritajatearv', c.sooritajatearv)}
        ${h.checkbox('keelteloikes',1,checked=c.keelteloikes,
        label=_("Keelte lõikes"))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.vabadearv)}">
      <div class="form-group">        
        ${h.flb(_("Vabade kohtade arv, vähemalt"),'vabadearv')}
        ${h.posint('vabadearv', c.vabadearv)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.kohtipuudu or c.pole_r)}">
      <div class="form-group">
        <div class="${h.hidefilter(c.kohtipuudu)}">
        ${h.checkbox('kohtipuudu',1,checked=c.kohtipuudu,
        label=_("Sooritajaid rohkem kui kohti"))}
        </div>
        <div class="${h.hidefilter(c.pole_r)}">
          ${h.checkbox('pole_r',1,checked=c.pole_r,
          label=_("Ruumid määramata"))}
        </div>
      </div>
    </div>
    % endif
    <div class="col-12 col-md-8 col-lg-6 ${h.hidefilter(c.pole_v or c.pole_h or c.pole_h1 or c.pole_h2 or c.pole_i or c.pole_a or c.pole_a1 or c.pole_k)}">
      <div class="form-group">        
        % if c.toimumisaeg.vaatleja_maaraja:
        <div class="${h.hidefilter(c.pole_v)}">
        ${h.checkbox('pole_v',1,checked=c.pole_v,
        label=_("Välisvaatlejad määramata"))}
        </div>
        % endif
        % if c.toimumisaeg.hindaja1_maaraja:
        <div class="${h.hidefilter(c.pole_h1)}">
          ${h.checkbox('pole_h1',1,checked=c.pole_h1,
          label=_("Hindajad (I) määramata"))}
        </div>
        % endif
        % if c.toimumisaeg.hindaja2_maaraja:
        <div class="${h.hidefilter(c.pole_h2)}">
          ${h.checkbox('pole_h2',1,checked=c.pole_h2,
          label=_("Hindajad (II) määramata"))}
        </div>
        % endif
        % if c.toimumisaeg.intervjueerija_maaraja:
        <div class="${h.hidefilter(c.pole_i)}">
          ${h.checkbox('pole_i',1,checked=c.pole_i,
          label=_("Intervjueerijad määramata"))}
        </div>
        % endif
        % if vastvorm in (const.VASTVORM_KE, const.VASTVORM_SE):
        <div class="${h.hidefilter(c.pole_a)}">
          ${h.checkbox('pole_a',1,checked=c.pole_a,
          label=_("Testi administraatorid määramata"))}
        </div>
        <div class="${h.hidefilter(c.pole_a1)}">
          ${h.checkbox('pole_a1',1,checked=c.pole_a1,
          label=_("Testiruumis pole ühtki administraatorit määratud"))}            
        </div>
        % elif vastvorm == const.VASTVORM_KONS:
        <div class="${h.hidefilter(c.pole_k)}">
          ${h.checkbox('pole_k',1,checked=c.pole_k,
          label=_("Konsultandid määramata"))}
        </div>
        % endif
      </div>
    </div>
  </div>    
</%def>

<%def name="tr_nupud(maaramata)">    
<div class="flex-grow-1">
   % if c.can_update and not c.on_piirkondlik:
      % if maaramata:
      ${h.btn_to(_("Genereeri õppurite soorituskohad"),
        h.url('korraldamine_soorituskohad', toimumisaeg_id=c.toimumisaeg.id,
        sub='genereeri'),
        method='post', level=2)}

      % if c.test.testiliik_kood != const.TESTILIIK_RIIGIEKSAM:
      ${h.button(_("Jaota sooritajad soorituskohtadesse"),
      onclick="dialog_el($('div#jaotamine'), 'Soorituskohata sooritajate jaotamine soovitud piirkonna järgi', 600);", level=2)}
      % endif
      % endif

      <% testimiskord = c.toimumisaeg.testimiskord %>
      % if len(testimiskord.toimumisajad) > 1:
      ${h.btn_to_dlg(_("Kopeeri soorituskohad"),
        h.url('korraldamine_soorituskohad', toimumisaeg_id=c.toimumisaeg.id,
        sub='kopeeri'),
        title=_("Vali toimumisaeg, mille andmed kopeerida"), width=600, level=2)}
      % endif
      % if not c.test.on_kutse:
      ${h.btn_to_dlg(_("Eralda valim..."), h.url('korraldamine_valim', toimumisaeg_id=c.toimumisaeg.id),
      title=_("Valimi eraldamine"), width=600, level=2)}
      % endif

      % if testimiskord.testsessioon_id:
      ${h.btn_to(_("Uuenda õppimisandmed"),
      h.url('admin_eksaminandid_ehisoppurid', sessioon_id=testimiskord.testsessioon_id, test_id=c.test.id), level=2)}
      % endif
      % if c.cnt_muusk:
      ${h.btn_to(_("Saada muu soorituskoha teated ({n})").format(n=c.cnt_muusk),
      h.url('korraldamine_soorituskohad', toimumisaeg_id=c.toimumisaeg.id, sub='muusk', debug=c.debug), method='post', level=2)}
      % endif
      ${h.btn_to_dlg(_("Lisa soorituskohad"),
        h.url('korraldamine_new_soorituskoht', toimumisaeg_id=c.toimumisaeg.id),
        title='Soorituskohad', size='lg')}

   % endif
</div>
      % if not c.test.on_kutse:
      ${h.toggle_filter(False)}
      ${h.submit(_("CSV"), id='csv', level=2)}
      ${h.btn_search()}
      % endif
</%def>

