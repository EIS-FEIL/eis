<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Tulemuste arvutamine")} | ${c.test.nimi} ${c.toimumisaeg.millal}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"), h.url('hindamised'))} 
${h.crumb('%s %s' % (c.test.nimi, c.toimumisaeg.millal))} 
${h.crumb(_("Tulemuste arvutamine"), h.url('hindamine_arvutused', toimumisaeg_id=c.toimumisaeg.id))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'hindamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<% c.can_update = c.user.has_permission('ekk-hindamine', const.BT_UPDATE, obj=c.test) %>

% if c.sisaldab_valimit:
${self.show_cnt(False, c.cnts)}
${self.show_cnt(True, c.cnts_valim)}
% else:
${self.show_cnt(None, c.cnts)}
% endif

<%def name="show_cnt(valimis, cnts)">
<%
  if valimis:
      svalimis = '1'
  elif valimis == False:
      svalimis = '0'
  else:
      svalimis = ''
%>
<div class="data-box mb-2">
  <div class="row">
    <div class="col-md-4 col-lg-4">
      % if valimis:
      ${h.flb(_("Valimi hinnatavaid testisooritusi"))}
      % elif valimis == False:
      ${h.flb(_("Mitte-valimi hinnatavaid testisooritusi"))}
      % else:
      ${h.flb(_("Hinnatavaid testisooritusi"))}
      % endif
      ${cnts.tehtud}
    </div>
    <div class="col-md-4 col-lg-4">    
      ${h.flb(_("Tulemused arvutatud"))}
      ${cnts.arvutatud}
    </div>
    <div class="col-md-4 col-lg-4">        
      ${h.flb(_("Tulemusi ei ole arvutatud"))}
      ${cnts.arvutamata}
      % if cnts.probleemid:
      (${cnts.probleemid})
      % endif
    </div>
    % if c.testiosa.vastvorm_kood == const.VASTVORM_KP:
    <div class="col-md-4 col-lg-4">        
      ${h.link_to(_("Hindamisprotokollide sisestamine"), 
      h.url('sisestamine_kirjalikud',
      sessioon_id=c.toimumisaeg.testimiskord.testsessioon_id,
      toimumisaeg_id=c.toimumisaeg.id))}
      <br/>
      ${h.link_to(_("Testitööde sisestamine"), 
      h.url('sisestamine_testitood', 
      toimumisaeg_id=c.toimumisaeg.id, sessioon_id=c.testimiskord.testsessioon_id))}
    </div>
    % elif c.testiosa.vastvorm_kood == const.VASTVORM_SP:
    <div class="col-md-4 col-lg-4">        
      ${h.link_to(_("Hindamisprotokollide sisestamine"), 
      h.url('sisestamine_suulised',
      sessioon_id=c.toimumisaeg.testimiskord.testsessioon_id,
      toimumisaeg_id=c.toimumisaeg.id))}
    </div>
    % endif

% if cnts.pooleli or cnts.alustamata:
    <div class="col-md-4 col-lg-4">        
      ${h.flb(_("Registreeritud või alustamata"), 'regatud'+svalimis)}

        <span class="nowrap" id="regatud${svalimis}">
          <span class="pr-2">${cnts.alustamata}</span>
          % if cnts.alustamata and c.can_update:
          ${h.btn_to(_("Märgi puudujaks"),
          h.url_current('create', sub='staatus', staatus=const.S_STAATUS_ALUSTAMATA, valimis=svalimis), method='post',
          confirm=_("Kas oled kindel, et soovid nad puudujaks märkida?"), level=2)}
          % endif
        </span>
    </div>
    <div class="col-md-4 col-lg-4">        
      ${h.flb(_("Pooleli"), 'pooleli'+svalimis)}
        <span class="nowrap" id="pooleli${svalimis}">
          <span class="pr-2">${cnts.pooleli}</span>
          % if cnts.pooleli and c.can_update:        
          ${h.btn_to(_("Märgi osalenuks"),
          h.url_current('create', sub='staatus', staatus=const.S_STAATUS_POOLELI, valimis=svalimis), method='post',
          confirm=_("Kas oled kindel, et soovid nad osalenuks märkida?"), level=2)}        
          % endif
        </span>
        % if cnts.max_pooleli_aeg:
        <br/>(${_("viimati vastatud {s}").format(s=h.str_from_datetime(cnts.max_pooleli_aeg))})
        % endif
    </div>
% endif
% if cnts.puudus:
    <div class="col-md-4 col-lg-4">        
      ${h.flb(_("Puudus"), 'puudus'+svalimis)}
        <span class="nowrap" id="puudus${svalimis}">
          <span class="pr-2">${cnts.puudus}</span>
        </span>
    </div>
% endif
% if cnts.prot_kinnitamata:
    <div class="col-md-4 col-lg-4">
      ${h.flb(_("Kinnitamata protokolle"), 'kinnitamata'+svalimis)}
      <span class="nowrap" id="kinnitamata${svalimis}">
        <span class="pr-2">${cnts.prot_kinnitamata}</span>
        ${h.btn_to(_("Kinnita"), h.url_current('create', sub='prot', valimis=svalimis), method='post', level=2)}
      </span>
    </div>
% endif
  </div>
</div>
</%def>

<%
   tkord = c.testimiskord
   testiosa = c.toimumisaeg.testiosa
%>
% if c.can_update:
## peab olema võimalik ka peale tulemuste kinnitamist tulemusi arvutada,
## nt kui vaietest selgub selline vajadus
${h.form_save(None)}
<h2>${_("Toimumisaja tulemuste arvutamine")}</h2>
<div class="gray-legend p-3">
  <div class="d-flex flex-wrap filter">
    <div class="mr-4">
      <div class="form-group">
        ${h.checkbox1('koik_kogumid', value=1, label=_("Kõik hindamiskogumid"),
        checked=c.koik_kogumid)}
      </div>
    </div>

    <% hkogumid = [hk for hk in testiosa.hindamiskogumid if hk.staatus == const.B_STAATUS_KEHTIV] %>
    % if hkogumid:
    <div class="mr-4">
      <div class="form-group d-flex flex-wrap">    
        <a class="btn btn-link mr-3" href id="toggle_hk">${_("Hindamiskogumid")} ${h.mdi_icon('mdi-chevron-right')}</a>
        <div class="hindamiskogumid d-none">
        % for hk in hkogumid:
        ${h.checkbox('hindamiskogum_id', value=hk.id, label=hk.tahis,
        checkedif=c.hindamiskogum_id or hk.id, class_="hindamiskogum_id")}
        % endfor
        </div>
      </div>
    </div>
    % endif

    <div class="mr-4">
      <div class="form-group d-flex flex-wrap">    
        <a class="btn btn-link mr-3" href id="toggle_ty">${_("Ülesanded")} ${h.mdi_icon('mdi-chevron-right')}</a>        
        <div class="ylesanded d-none">
        % for ty in testiosa.testiylesanded:
        % if ty.tahis:
        ${h.checkbox('ty_id', value=ty.id, label=ty.tahis, checkedif=c.ty_id or ty.id, class_="ty-id")}
        % endif
        % endfor
        </div>
      </div>
    </div>

    % if tkord.valim_testimiskord_id and testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I):
    <div class="mr-4">
      <div class="form-group">
      ${h.checkbox('kannayle', 1, label=_("Kanda üle tulemused toimumisajalt:"))}
      <% kanna_ta = tkord.valim_testimiskord.get_toimumisaeg(c.toimumisaeg.testiosa) %>
      ${h.link_to(kanna_ta.tahised, h.url('hindamine_arvutused', toimumisaeg_id=kanna_ta.id))}
      </div>
    </div>
    % endif
    <div class="mr-4 flex-grow-1">
      <div class="form-group float-right">
      % if not tkord.tulemus_kontrollitud or c.user.on_admin:
      ${h.submit(_("Käivita tulemuste kontroll ja arvutamine"))}
      ${h.submit(_("Arvuta statistika"), id='stat', class_="mx-2")}
      <div class="d-inline-block m-1">
      <% nostat = not c.statv and not c.statt %>
      ${h.checkbox('statv', 1, checked=c.statv or nostat, label=_("Vastuste statistika"))}
      ${h.checkbox('statt', 1, checked=c.statt or nostat, label=_("Vastuste väljavõte"))}
      </div>
      % endif
      % if request.params.get('debug'):
      ${h.hidden('debug', request.params.get('debug'))}
      % endif
      </div>
    </div>
  </div>
</div>
<script>
  $(function(){
    $('#koik_kogumid').click(function(){
      $('input.hindamiskogum_id,input.ty-id').prop('checked',$(this).prop('checked'));
    });
    $('input.hindamiskogum_id,input.ty-id').click(function(){
      if(!$(this).prop('checked')) $('input#koik_kogumid,input#loplik').prop('checked',false);
    });
    var toggle_hk = function(show){
      $('#toggle_hk .mdi').toggleClass('mdi-chevron-right', !show).toggleClass('mdi-chevron-left', show);
      $('div.hindamiskogumid').toggleClass('d-none', !show);
      var inp = $('div.hindamiskogumid input[type="checkbox"]');
      if(!show) inp.prop('checked', false);  else if($('#koik_kogumid').prop('checked')) inp.prop('checked', true);
    };
    var toggle_ty = function(show){
      $('#toggle_ty .mdi').toggleClass('mdi-chevron-right', !show).toggleClass('mdi-chevron-left', show);
      $('div.ylesanded').toggleClass('d-none', !show);
      var inp = $('div.ylesanded input[type="checkbox"]');
      if(!show) inp.prop('checked', false);  else if($('#koik_kogumid').prop('checked')) inp.prop('checked', true);  
    };
    ## hindamiskogumite kuvamisel peidame ylesanded
    $('#toggle_hk').click(function(){
      var show = $('#toggle_hk .mdi').hasClass('mdi-chevron-right');
      toggle_hk(show);
      toggle_ty(false);
      return false;
    });
    ## ylesannete kuvamisel peidame hindamiskogumid
    $('#toggle_ty').click(function(){
      var show = $('#toggle_ty .mdi').hasClass('mdi-chevron-right');
      toggle_ty(show);
      toggle_hk(false);
      return false;
    });
    % if not c.koik_ylesanded and c.hindamiskogum_id:
      $('#toggle_hk').click();
    % elif not c.koik_ylesanded and c.ty_id:
      $('#toggle_ty').click();
    % endif
  });
</script>
${h.end_form()}

% endif



<%
  tkorral_arvutamata = 0
  trcls = 'bg-gray-50'
%>
% for ta in tkord.toimumisajad:
<% trcls = not trcls and 'bg-gray-50' or '' %>
  
    <div class="d-flex flex-wrap p-3 ${trcls}">
      <div class="item mr-5" style="width:200px">
        <b>${_("Toimumisaeg")}</b>
        % if ta == c.toimumisaeg:
        ${ta.tahised}
        % else:
        ${h.link_to(ta.tahised, h.url('hindamine_arvutused',
        toimumisaeg_id=ta.id))}
        % endif
      </div>
      <div class="item mr-5" style="width:200px">
        % if ta.tulemus_kinnitatud:
        ${_("Tulemused kinnitatud")}
        % else:
        ${_("Tulemused kinnitamata")}
        % endif

        % if ta == c.toimumisaeg:
        <div class="d-flex flex-wrap mt-2">
          <div>
            ${h.checkbox1('hindamise_luba', 1,checked=c.toimumisaeg.hindamise_luba,
            label=_("Hindamine lubatud"))}
          </div>
          <div id="h_luba_res">
            % if c.err_hindamise_luba:
            ${h.alert_warning(c.err_hindamise_luba, False)}
            % endif
          </div>
        </div>
        <script>
          $('#hindamise_luba').click(function(){
            var url = "${h.url_current('create')}",
                data = 'sub=hluba&luba=' + ($(this).prop('checked') ? '1' : '0');
            dialog_load(url, data, 'post', $('#h_luba_res'), null, false);
          });
        </script>
        % endif
      </div>
      <div class="item">
% if c.can_update:
      % if ta.tulemus_kinnitatud and (c.user.on_admin or c.test.testityyp == const.TESTITYYP_AVALIK):
    ${h.form_save(None)}
    ${h.submit(_("Eemalda tulemuste kinnitus"), id='syrra', level=2)}
    ${h.end_form()}
      % endif
      % if ta == c.toimumisaeg and not ta.tulemus_kinnitatud:
        ${h.form_save(None)}
        % if request.params.get('debug'):
        ${h.hidden('debug', request.params.get('debug'))}
        % endif
        % if c.cnt_arvutamata > 0:
         <% tkorral_arvutamata += c.cnt_arvutamata %>
         ${_("Tulemusi ei saa kinnitada, kuni on arvutamata sooritusi")}
        % else:
        ${h.submit(_("Kinnita"), id='kinnita')}
        % endif
        % if not tkord.tulemus_kontrollitud or c.user.on_admin:
         ${h.submit(_("Arvuta läbiviijate tööde arv"), id='lvtood')}
        % endif
         ${h.end_form()}
      % endif
% endif
      </div>
    </div>
% endfor
<% trcls = not trcls and 'bg-gray-50' or '' %>    
    <div class="d-flex flex-wrap p-3 mb-2 ${trcls}">
      <div class="item mr-5" style="width:200px">
        <b>${_("Testimiskord")}</b> ${tkord.tahis}
      </div>
      <div class="item mr-5" style="width:200px">
        % if tkord.tulemus_kinnitatud:
          % if tkord.tulemus_kontrollitud:
        ${_("Tulemused kinnitatud ja kontrollitud")}
          % else:
          ${_("Tulemused kinnitatud")}
          % endif
        
        % if tkord.test.on_tseis:
        <p>
        ${h.btn_to(_("Kinnitamise käskkirja lisa 1"), h.url_current('download', id='lisa1', format='pdf'), level=2)}
        </p>
        <p>
        ${h.btn_to(_("Kinnitamise käskkirja lisa 2"), h.url_current('download', id='lisa2', format='pdf'), level=2)}
        </p>
        % endif

        % elif tkord.tulemus_kontrollitud:
        ${_("Tulemused kinnitamata, kuid kontrollitud")}
        % else:
        ${_("Tulemused kinnitamata")}
        % endif
      </div>
      <div class="item mr-5">
        ${h.form_save(None)}
        ${h.form_save(None, h.url('hindamine_arvutused', toimumisaeg_id=c.toimumisaeg.id))}
        % if tkord.statistika_arvutatud:
        ${_("Statistika arvutatud")}
          % else:
          ${_("Statistika arvutamata")}
        % endif
% if c.can_update:
        % if not tkorral_arvutamata and c.user.on_admin and not tkord.tulemus_kontrollitud:
        ${h.submit(_("Tulemused kontrollitud"), id='kontrollitud')}
        % endif
          % if request.params.get('debug'):
          ${h.hidden('debug', request.params.get('debug'))}
          % endif
% endif        
        ${h.end_form()}
      </div>

      % if c.test.testityyp == const.TESTITYYP_AVALIK:
        % if not tkord.koondtulemus_avaldet and not tkord.alatestitulemused_avaldet and not tkord.ylesandetulemused_avaldet and not tkord.aspektitulemused_avaldet and not tkord.ylesanded_avaldet:
      <div class="item mr-5 d-flex">
        <div class="mr-3">
        ${_("Tulemused avaldamata")}
        </div>
        % if c.can_update:
        <div>
        ${h.btn_to_dlg(_("Muuda avaldamist"), h.url('hindamine_arvutused', toimumisaeg_id=c.toimumisaeg.id, sub='avaldamine'), 
        title=_("Muuda avaldamist"), form="$('form#form_save')", id='avaldamine')}
        </div>
        % endif
      </div>
        % else:
      <div class="item d-flex flex-wrap mt-3">
          <div class="item mr-5">
            ${h.flb(_("Koondtulemused avaldatud"))}
            <div>${h.str_from_date(tkord.koondtulemus_aval_kpv) or '-'}</div>
          </div>
          <div class="item mr-5">
            ${h.flb(_("Alatestide lõikes tulemused avaldatud"))}
            <div>${h.str_from_date(tkord.alatestitulemused_aval_kpv) or '-'}</div>
          </div>
          <div class="item mr-5">
            ${h.flb(_("Ülesannete lõikes tulemused avaldatud"))}
            <div>${h.str_from_date(tkord.ylesandetulemused_aval_kpv) or '-'}</div>
          </div>
          <div class="item mr-5">
            ${h.flb(_("Aspektide lõikes tulemused avaldatud"))}
            <div>${h.str_from_date(tkord.aspektitulemused_aval_kpv) or '-'}</div>
          </div>
          <div class="item mr-5">
            ${h.flb(_("Ülesanded ja vastused avaldatud"))}
            <div>${h.str_from_date(tkord.ylesanded_aval_kpv) or '-'}</div>
          </div>
          % if c.can_update:
          <div class="item mr-5">
          ${h.btn_to_dlg(_("Muuda avaldamist"), h.url('hindamine_arvutused', toimumisaeg_id=c.toimumisaeg.id, sub='avaldamine'), 
          title=_("Muuda avaldamist"), form="$('form#form_save')", id='avaldamine')}
          </div>
          % endif
      </div>
        % endif
      % endif
      
    </div>

<%
c.url_refresh = h.url('hindamine_arvutused', toimumisaeg_id=c.toimumisaeg.id, sub='progress')
c.protsessid_caption = _("Arvutusprotsesside logi")
%>
<%include file="/common/arvutusprotsessid.mako"/>
