<%inherit file="/common/page.mako"/>
## antud: c.test (alati), 
##        c.sooritaja (kui on suunatud), 
##        c.toimumisaeg (kui on testimiskorraga test)
<%def name="page_title()">
${_("Testi sooritamine")}: ${c.test.nimi} 
</%def>      
<%def name="breadcrumbs()">
% if not c.user.testpw_id:
${h.crumb(_("Testisooritus"), h.url('sooritamised'))} 
${h.crumb(c.test.nimi, h.url('sooritamine_alustamine', test_id=c.test.id, sooritaja_id=c.sooritaja and c.sooritaja.id or '0'))}
% endif
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sooritamised' %>
</%def>

<h1>${c.test.nimi}</h1>
% if c.sooritaja:
<div class="h4">${c.sooritaja.nimi}</div>
% endif
<%
  c.on_diag2 = c.test.diagnoosiv
  c.test_pallideta = c.test.test_pallideta
  testimiskord = c.sooritaja and c.sooritaja.testimiskord
  if c.sooritaja:
     sooritaja_roll = c.sooritaja.kasutaja_id == c.user.id and const.ISIK_SOORITAJA or const.ISIK_TUGI
     visibility = c.sooritaja.tulemus_nahtav(None, c.app_ekk, sooritaja_roll, c.test, testimiskord)
  else:
     visibility = None
%>
% if c.sooritaja and c.sooritaja.staatus==const.S_STAATUS_TEHTUD and c.tagasiside_html and visibility.is_ts:
  ## kui test on tehtud ja on tagasiside, siis kuvame tagasiside
  ${c.tagasiside_html}
% else:
  ## kui test ei ole tehtud või ei ole midagi muud kuvada, siis kuvame sooritamise andmed
  ${self.test_data(visibility)}
  % for testiosa in c.test.testiosad:
    ${self.testiosa_data(testiosa, testimiskord)}
  % endfor
% endif

% if c.user.get_seb_id():
${h.btn_to(_("Välju"), h.url('login', action='signout'))}
<script>window.location.replace("${h.url('login', action='signout')}");</script>
% endif

<%def name="test_data(visibility)">
<div class="gray-legend d-flex flex-wrap mb-2 p-3">
  <div class="item mr-5">
    ${h.flb(_("Testi ID"),'testi_id')}
    <div id="testi_id">
      ${c.test.id}
      % if c.test.salastatud > const.SALASTATUD_SOORITATAV:
      (${_("salastatud")})
      % endif
    </div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Testi nimetus"),'test_nimi')}
    <div id="test_nimi">
      ${c.test.nimi}
    </div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Õppeaine"),'aine_nimi')}
    <div id="aine_nimi">
      ${c.test.aine_nimi}
      % if c.sooritaja and c.sooritaja.kursus_kood:
      (${c.sooritaja.kursus_nimi})
      % endif
    </div>
  </div>
  % if c.sooritaja:
  <div class="item mr-5">
    ${h.flb(_("Soorituskeel"), 'd_lang')}
    <div id="d_lang">
      ${c.sooritaja.lang_nimi}
    </div>
  </div>
  % endif
  % if c.sooritaja and c.sooritaja.staatus == const.S_STAATUS_TEHTUD:
  % if c.sooritaja.pallid is not None and visibility.is_k and not c.test_pallideta:
  <div class="item mr-5">
    ${h.flb(_("Tulemus"),'tulemusp')}
    <div id="tulemusp">
      ${_("{p} palli").format(p=h.fstr(c.sooritaja.pallid))}
    </div>
  </div>
  % endif
  % endif
</div>
</%def>

<%def name="testiosa_data(testiosa, testimiskord)">
<%
  if c.sooritaja:
     tos = c.sooritaja.get_sooritus(testiosa.id)
     tugik = tos.tugiisik_kasutaja
     olen_tugi = tos.tugiisik_kasutaja_id == c.user.id
     sooritaja_roll = olen_tugi and const.ISIK_TUGI or const.ISIK_SOORITAJA
     visibility = c.sooritaja.tulemus_nahtav(tos, c.app_ekk, sooritaja_roll, c.test, testimiskord)
  else:
     tos = tugik = visibility = None
  testikoht = tos and tos.testikoht
  koht = testikoht and testikoht.koht
  toimumisaeg = tos and tos.toimumisaeg
  testiruum = tos and tos.testiruum 
%>

<div class="form-wrapper p-3 mb-2">
  <% ch = h.colHelper('col-sm-4 col-md-3 col-lg-2', 'col-sm-8 col-md-9 col-lg-10') %>
  % if len(c.test.testiosad) > 1:
  <div class="form-group row">
    ${ch.flb(_("Testiosa"), 'd_testiosa')}
    <div id="d_testiosa" class="${ch.col2}">
      ${testiosa.nimi}
    </div>
  </div>
  % endif
  % if tugik:
  <div class="form-group row">
    ${ch.flb(_("Tugiisik"), 'd_tugik')}
    <div id="d_tugik" class="${ch.col2}">
      ${tugik.nimi}
    </div>
  </div>
  % endif
  % if testiosa.naita_max_p:
  <div class="form-group row">  
    ${ch.flb(_("Max pallid"), 'd_max_p')}
    <div id="d_max_p" class="${ch.col2}">    
      ${h.fstr(testiosa.max_pallid)}
    </div>
  </div>    
  % endif
  % if testiosa.piiraeg:
  <div class="form-group row">  
    ${ch.flb(_("Testiosa piiraeg"), 'd_piiraeg')}
    <div id="d_piiraeg" class="${ch.col2}">    
      ${h.str2_from_timedelta(testiosa.piiraeg)}
    </div>
  </div>    
  % endif
  % if koht:
  <div class="form-group row">  
    ${ch.flb(_("Soorituskoht"), 'd_knimi')}
    <div id="d_knimi" class="${ch.col2}">    
      ${koht.nimi}
    </div>
  </div>    
  % endif
  % if toimumisaeg:
  <div class="form-group row">  
    ${ch.flb(_("Toimumisaja tähis"), 'd_ta_tahis')}
    <div id="d_ta_tahis" class="${ch.col2}">    
      ${toimumisaeg.tahised}
    </div>
  </div>    
  <div class="form-group row">  
    ${ch.flb(_("Toimumise aeg"), "d_ta")}
    <div id="d_ta" class="${ch.col2}">    
      % if testiruum and testiruum.algus and testiruum.lopp and testiruum.algus.date() == testiruum.lopp.date():
      ${h.str_from_datetime(testiruum.algus)} - ${h.str_time_from_datetime(testiruum.lopp)}
      % elif testiruum and testiruum.algus and testiruum.lopp and testiruum.algus.date() != testiruum.lopp.date():
      ${h.str_from_datetime(testiruum.algus, hour0=False)} - ${h.str_from_datetime(testiruum.lopp, hour23=False)}      
      % elif toimumisaeg.aja_jargi_alustatav and testiruum and testiruum.algus:
      ${h.str_from_datetime(testiruum.algus)}
      % elif testiruum and testiruum.algus:
      ${h.str_from_date(testiruum.algus)}
      % else:
      ${toimumisaeg.millal}
      % endif
    </div>
  </div>    
  % endif
  <div class="form-group row">
    <div class="col">
      ${self.toimumisaja_sooritamine(c.test, testiosa, c.sooritaja, tos, testiruum, visibility)}
    </div>
  </div>
</div>
</%def>

<%def name="toimumisaja_sooritamine(test, testiosa, sooritaja, tos, testiruum, visibility)">
% if tos:
<%
  lang = sooritaja.lang
  juhend = testiosa.tran(lang).alustajajuhend
%>
% if juhend:
<div class="alert alert-primary fade show" role="alert">
  <i class="mdi mdi-information-outline"></i> 
  ${juhend}
</div>
% endif
% endif

<div>${_("Testisooritus")}</div>
% if tos and tos.staatus == const.S_STAATUS_VABASTATUD:
${h.alert_notice(_("Testiosa sooritamisest vabastatud"), False)}
% elif testiosa.vastvorm_kood == const.VASTVORM_SH:
${h.alert_notice(_("Test sooritatakse suulise hindajaga"), False)}
% elif testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
${h.alert_notice(_("Ei sooritata e-testina"), False)}
% else:
<table class="table table-borderless table-striped" border="0" >
% if tos:
    <%
           ta = tos.toimumisaeg
           testikoht = tos.testikoht
           algus = testiruum and testiruum.algus
           if algus and algus <= c.now and algus.date == c.now.date:
              toimub = True
           elif ta:
              toimub = True
           elif not ta and (not c.test.avalik_kuni or c.test.avalik_kuni >= model.date.today()):
              ## mulle suunatud avalik test
              toimub = True
           else:
              toimub = False
           if test.salastatud > const.SALASTATUD_SOORITATAV:
              toimub = False
           if tos.tugiisik_kasutaja_id:
              minu_tehtav = tos.tugiisik_kasutaja_id == c.user.id
           else:
              minu_tehtav = c.sooritaja.kasutaja_id == c.user.id
    %>
          <tr>
            % if ta:
            <th>${_("Tähis")}</th>
            % endif
            <th>${_("Olek")}</th>
            <th>${_("Soorituskoht")}</th>
            % if tos.toimumisaeg:
            <th>${_("Ruum")}</th>
            % else:
            <th>${_("Nimekiri")}</th>
            % endif
            <th>${_("Lahendaja piiraeg")}</th>
            <th>${_("Alustatud")}</th>
            <th>${_("Lõpetatud")}</th>
            <th>${_("Ajakulu")}</th>
            % if not c.test_pallideta:
            <th>${_("Tulemus")}</th>
            % endif
            % if c.test.testiliik_kood != const.TESTILIIK_KOOLIPSYH:
            <th></th>
            % endif
          </tr>
          <tr>
            % if ta:
            <td>
              ${tos.tahised}
            </td>
            % endif
            <td>
              <b class="mr-2">${tos.staatus_nimi}</b>
              % if testiosa.vastvorm_kood == const.VASTVORM_I:
              ${_("Intervjuu")}

              % elif toimub:
              <%
                error = None
                if not minu_tehtav:
                   if tos.tugiisik_kasutaja_id:
                       error = _("Test sooritatakse tugiisikuga")
                   else:
                       error = _("Sooritaja sooritab testi tugiisikuta")
                elif testiruum and testiruum.lopp and testiruum.lopp < model.datetime.now():
                    error = _("Testi sooritamise ajavahemik on läbi")
                saab_alustada = not error and tos.saab_alustada(ta, testiruum)
                if saab_alustada or tos.staatus in (const.S_STAATUS_POOLELI, const.S_STAATUS_KATKESTATUD, const.S_STAATUS_ALUSTAMATA):
                   if (testiruum and testiruum.arvuti_reg) or (ta and ta.on_arvuti_reg):
                      arvuti, error = model.Testiarvuti.get_by_request(c.test.id, testiruum, ta, request)
               %>
                                                                     
                % if error:
                ${h.alert_warning(error, False)}
                % elif saab_alustada or tos.staatus == const.S_STAATUS_POOLELI or tos.staatus == const.S_STAATUS_KATKESTATUD:
                   ${self.alusta_toimumisaeg(tos, ta, testiosa)}
                % elif tos.staatus == const.S_STAATUS_ALUSTAMATA and ta and ta.algusaja_kontroll:
                  <% now = model.datetime.now() %>
                  % if testiruum.algus.date() != now.date():
                   ${_("Test toimub {dt}").format(dt=h.str_from_date(testiruum.algus))}
                  % else:
                    <div id="bta${tos.id}" class="d-inline-block invisible">
                      ${self.alusta_toimumisaeg(tos, ta, testiosa)}
                    </div>
                    <div id="mta${tos.id}">
                      ${_("Test algab kell {s}").format(s=h.str_time_from_datetime(testiruum.algus))}
                      <% msec = (testiruum.algus - now).seconds * 1000; %>
                      <script>setTimeout(function(){$('#mta${tos.id}').hide();$('#bta${tos.id}').removeClass('invisible');}, ${msec});</script>
                    </div>
                  % endif
                % elif tos.staatus == const.S_STAATUS_REGATUD:
			       <br/>
                   <span class="pr-4">${_("Testi alustamiseks pole veel luba antud")}</span>
				   ${h.btn_to(_("Kontrolli loa andmist"), h.url('sooritamine_alustamine', test_id=c.test.id, sooritaja_id=c.sooritaja.id))}
				% endif
              % endif
              <!--${tos.id}-->
            </td>
            <td>
              % if testikoht:
              <% koht = testikoht.koht %>
              % if koht:
              ${koht.nimi}
              % endif
              % endif
            </td>
            <td>
              <% nimekiri = testiruum and testiruum.nimekiri %>
              % if nimekiri:
              ${nimekiri.nimi}
              % elif testiruum:
              ${testiruum.tahis or ''}
              % endif
            </td>
            <td>
              % if tos.piiraeg:
                ${h.str2_from_timedelta(tos.piiraeg)}
              % else:
              ${_("Piiramata")}
              % endif
            </td>
            <td>
              % if tos.algus:
               ${h.str_from_datetime(tos.algus)}
              % endif
            </td>
            <td>
              % if tos.lopp:
                 ${h.str_from_datetime(tos.lopp)}
              % endif
            </td>
            <td>
              ${h.str2_from_timedelta(tos.ajakulu)}
            </td>

            % if not c.test_pallideta:
            <td>
              % if tos.staatus == const.S_STAATUS_TEHTUD and tos.pallid is not None:
                 % if visibility.is_k:
                 ${tos.get_tulemus()}
                 % endif
                 % if visibility.is_a:
                   % for alatest in tos.alatestid:
                   <div>
                   <% atos = tos.get_alatestisooritus(alatest.id) %>
                   ${alatest.nimi}
                   % if atos and atos.staatus==const.S_STAATUS_TEHTUD and not c.test.pallideta:
                   ${atos.get_tulemus(alatest.max_pallid) or atos.staatus_nimi}
                   % elif atos:
                   ${atos.staatus_nimi}
                   % endif
                   </div>
                  % endfor
                % endif
              % endif
            </td>
            % endif
            % if c.test.testiliik_kood != const.TESTILIIK_KOOLIPSYH:
            <td>
              % if visibility.is_resp:
              ${h.btn_to(_("Näita vastuseid"), h.url('tulemus_osa', test_id=c.test.id, testiosa_id=testiosa.id, alatest_id='', id=tos.id), level=2)}
              % endif
            </td>
            % endif
          </tr>
          % if tos.markus:
          <tr>
            <td colspan="10">
              <i>${_("Märkus")}.</i> ${tos.markus}
            </td>
          </tr>
          % endif
% elif c.test.avaldamistase == const.AVALIK_SOORITAJAD and not c.test.salastatud and not c.user.testpw_id:
          ## soorituse kirje võib siin ise luua ainult 
          ## nende testide puhul, mida võivad kõik ilma suunamiseta kasutada
          <%
             test = testiosa.test
             opt_kursused = test.opt_kursused or [(None, None)]
             opt_keeled = test.opt_keeled or [(None, None)]
          %>
          % for opt_k in opt_kursused:
          <% kursus_kood, kursus_nimi = opt_k[:2] %>
          <tr>
            <td>
              % if kursus_kood:
              ${_("Kursus")}: ${kursus_nimi}
              % endif
              % for opt_l in opt_keeled:
              <%
                 lang, lang_nimi = opt_l[:2]
                 title = _("Alustan")
                 if lang_nimi:
                    title += ' (%s)' % lang_nimi.lower()
                 juhend = testiosa.tran(lang).alustajajuhend
              %>
              <div style="padding:4px">
              % if juhend:
              <div style="padding:5px">${juhend}</div>
              % endif
              ${h.btn_to(title,
              h.url('sooritamine_alusta_osa', test_id=test.id, testiosa_id=testiosa.id, id=0, lang=lang, kursus=kursus_kood),
              method='post')}
              </div>
              % endfor
            </td>
          </tr>
          % endfor

% endif
</table>
% endif
</%def>

% if not c.user.testpw_id:
<div class="mt-3">
${h.btn_back(url=h.url('sooritamised'))}
</div>
% endif

<%def name="alusta_toimumisaeg(tos, ta, testiosa)">
## sooritaja võib alustada testi või kontrolli, kuvame alustamise nupu
% if c.user.get_seb_id():
    ## SEBi brauseri sees olles ei saa uut testi alustada

% elif ta and ta.on_proctorio and not tos.luba_veriff:
   <%
     if tos.staatus == const.S_STAATUS_POOLELI or tos.staatus == const.S_STAATUS_KATKESTATUD:
        bname = _("Jätkan")
     else:
        bname = _("Alustan")
   %>
   ${h.btn_to(bname, h.url('proctorio_start', test_id=testiosa.test_id, testiosa_id=testiosa.id, sooritus_id=tos.id), id='bproc%s' % ta.id, clicked=2000)}

   % if c.is_test and request.params.get('debug'):
   <% url = h.url('sooritamine_jatka_osa', test_id=c.test.id, testiosa_id=testiosa.id, id=tos.id) %>
   ${h.btn_to("Testi ilma Proctoriota", url, method='post')}
   % endif
   
% elif ta and ta.on_veriff and not c.user.verified_id and not tos.luba_veriff:
   ${h.btn_to(_("Isiku tõendamine"), h.url('veriff_start', sooritus_id=tos.id))}
   <div style="display:inline-block;padding:4px;">
     % if tos.staatus == const.S_STAATUS_POOLELI or tos.staatus == const.S_STAATUS_KATKESTATUD:
     ${_("Palume enne testi jätkamist oma isik tõendada Veriffi teenuse abil")}
     % else:
     ${_("Palume enne testi alustamist oma isik tõendada Veriffi teenuse abil")}
     % endif
   </div>

% elif ta and ta.verif_seb and not tos.luba_veriff:
   <%
     if tos.staatus == const.S_STAATUS_POOLELI or tos.staatus == const.S_STAATUS_KATKESTATUD:
        bname = _("Jätkan")
     else:
        bname = _("Alustan")
   %>
   ${h.btn_to(bname, h.url('seb_start', test_id=testiosa.test_id, testiosa_id=testiosa.id, sooritus_id=tos.id), id=f'bproc{ta.id}')}
   ${h.btn_to(_("Uuenda"), h.url('sooritamine_alustamine', test_id=c.test.id, sooritaja_id=c.sooritaja.id), id=f'brefr{ta.id}', style="display:none")}   
   <script>
     var timeout${ta.id} = null;
     var timeout_keepsess${ta.id} = null;
     ## seansi alleshoidmiseks tehakse SEBi kasutamise ajal pöördumisi     
     function keepsess${ta.id}(){
        if(timeout_keepsess${ta.id}) clearTimeout(timeout_keepsess${ta.id});
        timeout_keepsess${ta.id} = setTimeout(function(){
           $.getJSON("${h.url('keepsess')}", function(data){ if(data.rc) keepsess${ta.id}(); });
        }, 840000);  
     }
     $('button#bproc${ta.id}').click(function(){
        ## mõni aeg peale konfi allalaadimist kaotame nupu ära
        ## et peale testi lõpetamist ei tuleks jälle ette "Alustan"
        if(timeout${ta.id}) clearTimeout(timeout${ta.id});
        timeout${ta.id} = setTimeout(function(){
          $('button#bproc${ta.id}').hide();
          $('button#brefr${ta.id}').show();     
        }, 60000); 

        ## seansi alleshoidmiseks tehakse SEBi kasutamise ajal pöördumisi
        keepsess${ta.id}();
     });
     
   </script>
   ${h.alert_notice(_("Testi sooritamiseks peab arvutis olema Safe Exam Browser"), False)}
   
% else:
   <%
     if tos.staatus == const.S_STAATUS_POOLELI or tos.staatus == const.S_STAATUS_KATKESTATUD:
        bname = _("Jätkan")
        url = h.url('sooritamine_jatka_osa', test_id=c.test.id, testiosa_id=testiosa.id, id=tos.id)
     else:
        bname = _("Alustan")
        url = h.url('sooritamine_alusta_osa', test_id=c.test.id, testiosa_id=testiosa.id, id=tos.id)
   %>
   ${h.btn_to(bname, url, method='post')}   

% endif
</%def>              
