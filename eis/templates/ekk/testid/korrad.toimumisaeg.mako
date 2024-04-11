<%inherit file="korrad.mako"/>
<%def name="require()">
<%
c.includes['subtabs'] = True
c.includes['subtabs_label'] = True
c.includes['jstree'] = True
%>
</%def>

<%def name="subtabs_label()">
${h.link_to(_("Korraldamine"), h.url('korraldamine_soorituskohad',
toimumisaeg_id=c.item.id))}
</%def>

${h.form_save(c.item.id, style="width:100%")}
<%
  c.testiosa = c.item.testiosa
  c.testimiskord = c.item.testimiskord
%>
<h2>
  ${_("Testi toimumisaja korraldamise parameetrid")}
</h2>
<div class="gray-legend p-3 my-2 border-base-radius">
  <div class="row">
    <div class="form-group mb-0 col-md-3">
      ${h.flb(_("Toimumisaja tähis"))}
      ${c.item.tahised}
    </div>
    <div class="form-group mb-0 col-md-3">
      ${h.flb(_("Vastamise vorm"))}
      ${c.testiosa.vastvorm_nimi}
    </div>
    <div class="form-group mb-0 col">
      ${h.flb(_("Soorituskeeled"))}
      <% keeled = c.testimiskord.get_keeled() %>
      ${', '.join([model.Klrida.get_lang_nimi(lang) for lang in keeled])}
    </div>
  </div>
</div>

${h.rqexp()}
<div class="form-wrapper mb-2">

<div class="border border-base-radius mb-3">
${self.toimumispaevad(c.item.toimumispaevad, 'tpv')}

<div class="m-1">
  ${h.checkbox('f_ruum_voib_korduda', 1, checked=c.item.ruum_voib_korduda,
  label=_("Ruumi saab samal toimumispäeval korduvalt kasutada"))}
</div>
<div class="m-1">
  ${h.checkbox('f_aja_jargi_alustatav', 1, checked=c.item.aja_jargi_alustatav,
  label=_("Etteantud alustamise ajavahemikul saab sooritamist alustada ilma administraatori loata"))}
</div>
<div class="m-1">
  ${h.checkbox('f_algusaja_kontroll', 1, checked=c.item.algusaja_kontroll,
  label=_("Enne alguse kellaaega ei saa sooritamist alustada"))}
</div>
<div class="m-1">
  ${h.checkbox('f_kell_valik', 1, checked=c.item.kell_valik,
  label=_("Soorituskoha kellaaega ei saa vabalt sisestada"))}
</div>
<div class="m-1">
  <%
    if not c.item.id and c.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP):
        c.item.ruum_noutud = True
  %>
  ${h.checkbox('ruum_maaramata', 1, checked=not c.item.ruum_noutud,
  label=_("Võib kasutada määramata ruumi"))}
</div>
% if len(keeled) > 1 and c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE):
<div class="m-1">
  ${h.checkbox1('f_keel_admin', 1, checked=c.item.keel_admin, label=_("Testi administraator võib sooritaja soorituskeelt muuta"))}
</div>
% endif

</div>

<h3>${_("Ülesandekomplektid")}</h3>

<div class="p-2 mb-3 border border-base-radius">
  <div class="form-group row">
    <div class="col-12">
      ${h.checkbox('f_komplekt_valitav', 1, checked=c.item.komplekt_valitav,
      label=_("Komplekti valimine sooritaja poolt"), class_="mb-1")}

      <span class="valitav_y1">
        ${h.checkbox('f_komplekt_valitav_y1', 1, checked=c.item.komplekt_valitav_y1,
        label=_("Valikuvõimalus ainult komplekti esimese ülesande juures"))}
      </span>
      <script>
          $(function(){
            $('#f_komplekt_valitav').change(function(){
              $('.valitav_y1').toggle($('#f_komplekt_valitav').prop('checked'));
          });
          $('.valitav_y1').toggle($('#f_komplekt_valitav').prop('checked'));
          });
      </script>
    </div>
  </div>
  % for kvalik in c.testiosa.komplektivalikud:
  <div class="form-group row">
    <div class="col-md-3 fh">
        % if not c.testiosa.on_alatestid and not kvalik.kursus_kood:
        ${_("Komplektid")}
        % endif
        % if kvalik.kursus_kood:
        (${kvalik.kursus_nimi})
        % endif
        % if c.testiosa.on_alatestid:
        ${_("Alatest")} ${kvalik.str_alatestid}:
        % endif
    </div>
    <div class="col-md-9">
        <% found = False %>
        % for rcd in kvalik.komplektid:
        <%
          k_sobib = rcd.staatus == const.K_STAATUS_KINNITATUD and set(keeled).issubset(set(rcd.keeled))
          if k_sobib:
             found = True
          k_checked = rcd in c.item.komplektid
          cb_id = 'komplekt_id_%s' % rcd.id
        %>
        % if k_sobib:
        ${h.checkbox('komplekt_id', rcd.id, checked=k_checked, label=rcd.tahis, id=cb_id)}
        % elif k_checked:
        ${h.checkbox('komplekt_id', rcd.id, checked=k_checked, label=rcd.tahis, id=cb_id)}
        <script>$('#${cb_id}').prop('indeterminate', true)
          % if c.is_edit:
          .click(function(){this.checked=false; this.indeterminate=false; this.disabled=true;})
          % endif
          ;</script>
        % endif
        % endfor

        % if not found:
        ${h.alert_error(_("Valikus pole ühtki komplekti, mis vastaks testimiskorra keeltele ja oleks kinnitatud."), False)}
        % endif
      </div>
  </div>
  % endfor
</div>

<%
  ch = h.colHelper('col-md-6','col-md-6')
  # avaliku vaate testile ei saa hindajaid määrata Eksamikeskuses (vähemalt kirjalikke hindajaid mitte)
  opt_noutav = c.opt.noutav
  opt_noutavmuu = c.opt.noutavmuu
%>

<h3>${_("Kontroll ja hindamine")}</h3>
<div class="p-2 mb-3 border border-base-radius">
  <div class="form-group row">
    <div class="col-12">
      ${h.checkbox('f_vaatleja_maaraja', 1,
      checked=c.item.vaatleja_maaraja, label=_("Välisvaatleja nõutavus"))}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Vaatleja koolituse varaseim lubatud kuupäev"),'f_vaatleja_koolituskp')}
    <div class="${ch.col2}">
      ${h.date_field('f_vaatleja_koolituskp', c.item.vaatleja_koolituskp)}
    </div>
  </div>

  % if c.testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP):
  ## suuline test
  <div class="form-group row">
    ${ch.flb(_("Hindaja I nõutavus"),'f_hindaja1_maaraja')}
    <div class="${ch.col2}">
      ${h.select('f_hindaja1_maaraja', c.item.hindaja1_maaraja, opt_noutav)}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Hindaja II nõutavus"),'f_hindaja2_maaraja')}
    <div class="${ch.col2}">
      ${h.select('f_hindaja2_maaraja', c.item.hindaja2_maaraja, opt_noutav)}
    </div>
  </div>
  % if c.testimiskord.sisaldab_valimit:
  <div class="form-group row">
    ${ch.flb(_("Hindaja I nõutavus (valim)"),'f_hindaja1_maaraja_valim')}
    <div class="${ch.col2}">
      ${h.select('f_hindaja1_maaraja_valim', c.item.hindaja1_maaraja_valim, opt_noutav)}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Hindaja II nõutavus (valim)"),'f_hindaja2_maaraja_valim')}
    <div class="${ch.col2}">
      ${h.select('f_hindaja2_maaraja_valim', c.item.hindaja2_maaraja_valim, opt_noutav)}
    </div>
  </div>
  % endif
  <div class="form-group row">
    ${ch.flb(_("Hindaja koolituse varaseim lubatud kuupäev"),'f_hindaja_koolituskp')}
    <div class="${ch.col2}">
      ${h.date_field('f_hindaja_koolituskp', c.item.hindaja_koolituskp)}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Hindaja käskkirja lisamise varaseim kuupäev"),'f_hindaja_kaskkirikpv')}
    <div class="${ch.col2}">
      ${h.date_field('f_hindaja_kaskkirikpv', c.item.hindaja_kaskkirikpv)}
    </div>
  </div>
  % endif
  
  % if c.testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP, const.VASTVORM_I):
  <div class="form-group row">
    ${ch.flb(_("Intervjueerija nõutavus"),'f_intervjueerija_maaraja')}
    <div class="${ch.col2}">
      ${h.select('f_intervjueerija_maaraja', c.item.intervjueerija_maaraja, opt_noutav)}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Intervjueerija koolituse varaseim lubatud kuupäev"),'f_intervjueerija_koolituskp')}
    <div class="${ch.col2}">
      ${h.date_field('f_intervjueerija_koolituskp', c.item.intervjueerija_koolituskp)}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Intervjueerija käskkirja lisamise varaseim kuupäev"),'f_intervjueerija_kaskkirikpv')}
    <div class="${ch.col2}">
      ${h.date_field('f_intervjueerija_kaskkirikpv', c.item.intervjueerija_kaskkirikpv)}
    </div>
  </div>
  % endif

  % if c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_KP, const.VASTVORM_I):
  ## kirjalik test
  <div class="form-group row">
    ${ch.flb(_("Hindajate määramine"),'f_hindaja1_maaraja')}
    <div class="${ch.col2}">
      ${h.select('f_hindaja1_maaraja', c.item.hindaja1_maaraja, opt_noutavmuu)}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("II hindaja määramine"),'f_hindaja2_maaraja')}
    <div class="${ch.col2}">
      ${h.select('f_hindaja2_maaraja', c.item.hindaja2_maaraja or const.MAARAJA_POLE, opt_noutavmuu)}
    </div>
  </div>
  % if c.testimiskord.sisaldab_valimit:
  <div class="form-group row">
    ${ch.flb(_("Hindajate määramine (valim)"),'f_hindaja1_maaraja_valim')}
    <div class="${ch.col2}">
      ${h.select('f_hindaja1_maaraja_valim', c.item.hindaja1_maaraja_valim, opt_noutavmuu)}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("II hindaja määramine (valim)"),'f_hindaja2_maaraja_valim')}
    <div class="${ch.col2}">
      ${h.select('f_hindaja2_maaraja_valim', c.item.hindaja2_maaraja_valim or const.MAARAJA_POLE, opt_noutavmuu)}
    </div>
  </div>
  % endif
  % endif
  <div class="form-group row">
    <div class="col-md-12">
      ${h.checkbox('f_oma_kooli_hindamine', 1,
      checked=c.item.oma_kooli_hindamine,
      label=_("Oma kooli tööde hindamine lubatud"))}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Ühest koolist hinnatavate õpilaste arv"),'f_sama_kooli_hinnatavaid')}
    <div class="${ch.col2}">
      ${h.int5('f_sama_kooli_hinnatavaid', c.item.sama_kooli_hinnatavaid)}
    </div>
  </div>
  <div class="form-group row">
    <div class="col-md-12">
      ${h.checkbox('f_oma_prk_hindamine', 1,
      checked=c.item.oma_prk_hindamine,
      label=_("Hindaja hindab ainult oma piirkonna töid"))}
    </div>
  </div>
  <div class="form-group row">
    <div class="col-md-12">
      ${h.checkbox('f_hindamise_luba', 1,
      checked=c.item.hindamise_luba,
      label=_("Hindamine lubatud"))}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Hindamise algus"), 'f_hindamise_algus_kp')}
    <div class="${ch.col2}">
      <div class="d-flex">
        <div class="flex-grow-1">
          ${h.date_field('hindamise_algus_kp', c.item.hindamise_algus)}
        </div>
        ${h.time('hindamise_algus_kell', c.item.hindamise_algus, wide=False)}
      </div>
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Hindamise tähtaeg"), 'f_hindamise_tahtaeg')}
    <div class="${ch.col2}">
      ${h.date_field('f_hindamise_tahtaeg', c.item.hindamise_tahtaeg)}
    </div>
  </div>

  % if c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_KP, const.VASTVORM_I):  
  <div class="form-group row">
    ${ch.flb(_("Hindaja käskkirja lisamise varaseim kuupäev"),'f_hindaja_kaskkirikpv')}
    <div class="${ch.col2}">
      ${h.date_field('f_hindaja_kaskkirikpv', c.item.hindaja_kaskkirikpv)}
    </div>
  </div>
  <div class="form-group row">
    <div class="col-md-12">
      ${h.checkbox('f_admin_teade', 1,
      checked=c.item.admin_teade,
      label=_("Testi administraatori ja komisjoniliikme määramise teate saatmine"))}
    </div>
  </div>
  % endif

  <div class="form-group row">
    <div class="col-md-12">
      ${h.checkbox('f_esimees_maaraja', 1, checked=c.item.esimees_maaraja,
      label=_("Eksamikomisjoni esimehe nõutavus"))}
    </div>
  </div>
  <div class="form-group row">
    <div class="col-md-6">
      ${h.checkbox('f_komisjoniliige_maaraja', 1, checked=c.item.komisjoniliige_maaraja,
      label=_("Eksamikomisjoni liikme nõutavus"))}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Eksamikomisjoni liikmete määramise tähtaeg"), 'f_komisjon_maaramise_tahtaeg')}
    <div class="col-md-6">
      ${h.date_field('f_komisjon_maaramise_tahtaeg', c.item.komisjon_maaramise_tahtaeg)}
    </div>
  </div>
% if c.testiosa.test.on_tseis:
  <div class="form-group row">
    ${ch.flb(_("Eksamikomisjoni esimehe koolituse varaseim lubatud kuupäev"),'f_esimees_koolituskp')}
    <div class="${ch.col2}">
      ${h.date_field('f_esimees_koolituskp', c.item.esimees_koolituskp)}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Eksamikomisjoni liikme koolituse varaseim lubatud kuupäev"),'f_komisjoniliige_koolituskp')}
    <div class="${ch.col2}">
      ${h.date_field('f_komisjoniliige_koolituskp', c.item.komisjoniliige_koolituskp)}
    </div>
  </div>
% endif
  <div class="form-group row">
    <div class="col-md-12">
      ${h.checkbox('f_reg_labiviijaks', 1,
      checked=c.item.reg_labiviijaks,
      label=_("Läbiviijaks registreerimine avatud"))}
    </div>
  </div>
  <div class="form-group row">
    <div class="col-md-12">
    ${h.checkbox('f_ruumide_jaotus', 1,
      checked=c.item.ruumide_jaotus,
      label=_("Soorituskohtades ruumide määramine lubatud"))}
    </div>
  </div>
  <div class="form-group row">
    <div class="col-md-12">
      ${h.checkbox('f_labiviijate_jaotus', 1,
      checked=c.item.labiviijate_jaotus,
      label=_("Soorituskohtades läbiviijate määramine lubatud"))}
    </div>
  </div>
  <div class="form-group row">
    <div class="col-md-12">
    ${h.checkbox('f_hinnete_sisestus', 1,
      checked=c.item.hinnete_sisestus,
      label=_("Testi tulemuste sisestamine hindajatele lubatud"))}
    </div>
  </div>
  <div class="form-group row">
    <div class="col-md-12">
      ${h.checkbox('f_kahekordne_sisestamine', 1,
      checked=c.item.kahekordne_sisestamine!=False,
      label=_("Kahekordne sisestamine"))}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Sooritajaid protokollil"),'f_protok_ryhma_suurus')}
    <div class="${ch.col2}">
      ${h.int5('f_protok_ryhma_suurus', c.item.protok_ryhma_suurus)}
    </div>
  </div>

  % if c.testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP):
  <div class="form-group row">
    ${ch.flb(_("Samaaegseid vastajaid"),'f_samaaegseid_vastajaid')}
    <div class="${ch.col2}">
      ${h.int5('f_samaaegseid_vastajaid', c.item.samaaegseid_vastajaid)}
    </div>
  </div>
  % endif
  % if c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I):
  <div class="form-group row">
    <div class="col-md-12">
      ${h.checkbox1('f_on_arvuti_reg', 1, checked=c.item.on_arvuti_reg,
      label=_("Arvutite registreerimine nõutav"))}
    </div>
    % if len(c.test.testiosad) > 1:
    <div class="col-md-12">
      ${h.checkbox1('f_on_reg_test', 1, checked=c.item.on_arvuti_reg and c.item.on_reg_test,
      label=_("Kehtivad kõigi toimumisaegade arvutite registreeringud samas ruumis"))}
    </div>
    <script>
      ## kui arvutite reg ei toimu, siis arvutite reg toimumisaegade piires peab olema disabled
      $('#f_on_arvuti_reg').click(function(){
         $('#f_on_reg_test').prop('disabled', !$(this).prop('checked'));
         if(!$(this).prop('checked')) $('#f_on_reg_test').prop('checked', false);
      });
      $('#f_on_reg_test').prop('disabled', !$('#f_on_arvuti_reg').prop('checked'));
    </script>
    % endif
  </div>
  % endif
  % if c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE):  
  <div class="form-group row">
    <div class="col-md-6">
      ${h.checkbox1('f_verif_seb', 1, checked=c.item.verif_seb,
      label=_("Safe Exam Browser nõutav"))}
    % if c.item.id:
    <span class="mx-3" id="seb_param" style="display:none">
      ${h.btn_to_dlg(_("Seaded"), h.url_current(c.is_edit and 'edit' or 'show', sub='seb'), title=_("SEB seaded"), size='lg', level=2)}
      <script>
      function toggle_seb(){
         $('#seb_param').toggle($('#f_verif_seb').prop('checked'));
      }
      $('input#f_verif_seb').change(toggle_seb);
      toggle_seb();
      </script>
    </span>
    % endif
    </div>
  </div>

  <div class="form-group row">
    ${ch.flb(_("Sooritaja verifitseerimine"))}
    <div class="${ch.col2}">
      <div>
        ${h.checkbox('f_verif', const.VERIF_VERIFF, checkedif=c.item.verif, class_="verif", label=_("Veriff"))}
        <span id="veriff_param">
          ${h.select('veriff_int_id', c.item.verif_param, c.opt_veriff, wide=False)}
        </span>
      </div>
      <div>
        ${h.checkbox('f_verif', const.VERIF_PROCTORIO, checkedif=c.item.verif, class_="verif verif-proctorio", label=_("Proctorio"))}
        % if c.item.id:
        <span id="proctorio_param">
          ${h.btn_to_dlg(_("Seaded"), h.url_current(c.is_edit and 'edit' or 'show', sub='proctorio'), title=_("Proctorio seaded"), size='lg', level=2)}
        </span>
        % endif
      </div>
      <script>
      function toggle_verif(){
      $('#proctorio_param').toggle($('#f_verif_p').prop('checked'));
      $('#veriff_param').toggle($('#f_verif_v').prop('checked'));
      }
      $('input.verif').change(function(){
      if(this.checked) $('input.verif:not([id="'+this.id+'"])').prop('checked',false);
      toggle_verif();
      });
      toggle_verif();

      ## korraga ei saa valida Proctorio ja SEBi
      $('input#f_verif_seb').click(function(){
         if(this.checked){
            $('input.verif-proctorio').prop('checked', false);
            $('#proctorio_param').hide();
         }
      });
      $('input.verif-proctorio').click(function(){
        if(this.checked) {
          $('input#f_verif_seb').prop('checked', false);
          $('#seb_param').hide();
        }
      });
      
      </script>
    </div>
  </div>
  % endif
  % if c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I):  
  <div class="form-group row">
    <div class="col-md-12">
      ${h.checkbox('f_jatk_voimalik', 1, checked=c.item.jatk_voimalik,
      label=_("Testi administraator võib avada sooritamiseks lõpetatud testi"))}
    </div>
  </div>
  % elif c.testiosa.vastvorm_kood == const.VASTVORM_SH:  
  <div class="form-group row">
    <div class="col-md-12">
      ${h.checkbox('f_jatk_voimalik', 1, checked=c.item.jatk_voimalik,
      label=_("Intervjueerija võib avada sooritamiseks lõpetatud testi"))}
    </div>
  </div>
  % endif
  % if c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I):  
  <div class="form-group row">
    <div class="col-md-12">
      ${h.checkbox('f_eelvaade_admin', 1, checked=c.item.eelvaade_admin,
      label=_("Testi administraator näeb testi eelvaadet"))}
    </div>
  </div>
  % endif
</div>


<h3>${_("Logistika")}</h3>
<div class="p-2 mb-3 border border-base-radius">
  ${h.flb(_("Väljastusümbrike liigid"))}
  % if c.is_edit:
  ${h.button(_("Lisa"), onclick="grid_addrow('tbl_vb')", mdicls='mdi-plus', level=2)}
  % endif
  ${self.ymbrikuliigid(c.item.valjastusymbrikuliigid, 'vb')}
  <div class="form-group row">
    ${ch.flb(_("Väljastuse turvakoti maht (tööde arv)"),'f_valjastuskoti_maht')}
    <div class="${ch.col2}">
      ${h.int5('f_valjastuskoti_maht', c.item.valjastuskoti_maht)}
    </div>
  </div>
</div>

<div class="p-2 mb-3 border border-base-radius">
  ${h.flb(_("Tagastusümbrike liigid"))}
  % if c.is_edit:
  ${h.button(_("Lisa"), onclick="grid_addrow('tbl_tb')", mdicls='mdi-plus', level=2)}
  % endif
  ${self.ymbrikuliigid(c.item.tagastusymbrikuliigid, 'tb')}
  <div class="form-group row">
    ${ch.flb(_("Tagastuse turvakoti maht (tööde arv)"),'f_tagastuskoti_maht')}
    <div class="${ch.col2}">
      ${h.int5('f_tagastuskoti_maht', c.item.tagastuskoti_maht)}
    </div>
  </div>
</div>


<h3>${_("Töötasud")}</h3>
<div class="p-2 mb-3 border border-base-radius">
  <div class="form-group row">
    ${ch.flb(_("Välisvaatleja põhitasu"),'f_vaatleja_tasu')}
    <div class="${ch.col2}">
      ${h.money('f_vaatleja_tasu', c.item.vaatleja_tasu)} €
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Eksamikomisjoni liikme tasu"),'f_komisjoniliige_tasu')}
    <div class="${ch.col2}">
      ${h.money('f_komisjoniliige_tasu', c.item.komisjoniliige_tasu)} €
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Eksamikomisjoni esimehe tasu"),'f_esimees_tasu')}
    <div class="${ch.col2}">
      ${h.money('f_esimees_tasu', c.item.esimees_tasu)} €
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Testi administraatori tasu"),'f_admin_tasu')}
    <div class="${ch.col2}">
      ${h.money('f_admin_tasu', c.item.admin_tasu)} €
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Läbiviija lisatasu"),'f_vaatleja_lisatasu')}
    <div class="${ch.col2}">
      ${h.money('f_vaatleja_lisatasu', c.item.vaatleja_lisatasu)} €
    </div>
  </div>
</div>

<h3>${_("Protokoll")}</h3>
<div class="p-2 mb-3 border border-base-radius">
  <div class="form-group row">
    <div class="col-12">
      ${h.checkbox1('f_prot_eikinnitata', 1, checked=c.item.prot_eikinnitata,
      label=_("Soorituskohtades toimumise protokolle ei kinnitata"))}
    </div>
  </div>
  <div class="form-group row">
    <div class="col-12">
      ${h.checkbox1('prot_admin1', const.PROT_SISEST, checked=c.item.prot_admin,
      label=_("Testi administraator saab täita testi toimumise protokolli"))}
      ${h.checkbox1('prot_admin2', const.PROT_KINNIT, checkedif=c.item.prot_admin,
      label=_("Soorituskohtades, kus on üksainus testi administraator, saab ta testi toimumise protokolli ka kinnitada"))}            
      % if c.is_edit:
      <script>
       ## kui kinnitamist ei kasutata, siis deaktiveerime võimaluse lubada adminil kinnitada
       function protkinnit(){
         if($('#f_prot_eikinnitata').prop('checked') && $('#prot_admin2').prop('checked'))
         {
            $('#prot_admin2').prop('checked', false);
         }       
         $('#prot_admin2').prop('disabled', $('#f_prot_eikinnitata').prop('checked'));
       }
       $('#f_prot_eikinnitata').change(protkinnit);
       protkinnit();

       ## kinnitabise luba eeldab täitmise luba
       $('#prot_admin2').change(function(){
         if($('#prot_admin2').prop('checked')) $('#prot_admin1').prop('checked', true);
       });
       ## täitmise loa eemaldamisel eemaldada ka kinnitamise luba
       $('#prot_admin1').change(function(){
         if(!$('#prot_admin1').prop('checked')) $('#prot_admin2').prop('checked', false);
       });       
      </script>
      % endif
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Sooritajate järjestamine PDF-väljatrükkides"))}
    <div class="${ch.col2}">
      ${h.radio('f_nimi_jrk', 1, checked=c.item.nimi_jrk, label=_("nime järgi"))}
      ${h.radio('f_nimi_jrk', '', checked=not c.item.nimi_jrk, label=_("töökoodi järgi"))}
    </div>
  </div>
</div>

## end form-wrapper
</div>
${h.end_form()}


<%def name="buttons()">
% if c.can_update:
  % if c.is_edit:
  ${h.submit(out_form=True)}
  % elif c.item.id:
  ${h.btn_to(_("Muuda"), h.url('test_kord_edit_toimumisaeg', test_id=c.test.id,
  kord_id=c.item.testimiskord_id, id=c.item.id))}
  % endif
% endif
</%def>

<%def name="row_ymbrikuliik(item, prefix)">
    <tr>
      <td>
        ${item.tahis}
      </td>
      <td>
        % if prefix.startswith('vb'):
          ${h.textarea('%s.nimi' % (prefix), item.nimi, rows=3, style="min-width:140px")}
        % else:
          ${h.text('%s.nimi' % (prefix), item.nimi)}
        % endif
      </td>
      <td>${h.int5('%s.maht' % (prefix), item.maht)}</td>
      % if prefix.startswith('vb'):
      ## väljastusymbrikud
      <td>
        <div class="d-flex flex-wrap">
          <div style="min-width:160px">${_("Lisatööde koefitsient")}</div>
          ${h.float5('%s.lisatoode_koef' % (prefix), item.lisatoode_koef)}
        </div>
        <div class="d-flex flex-wrap">
          <div style="min-width:160px">${_("Lisatööde arv")}</div>
          ${h.posint5('%s.lisatoode_arv' % (prefix), item.lisatoode_arv)}
        </div>
        <div class="d-flex flex-wrap">
          <div style="min-width:160px">${_("Ümarduskordaja")}</div>
          ${h.posint5('%s.ymarduskordaja' % (prefix), item.ymarduskordaja)}
        </div>
      </td>
      <td>
        <div>
          ${h.select('%s.sisukohta' % prefix, item.sisukohta, model.Valjastusymbrikuliik.opt_sisukohta())}          
        </div>
        <div>
          <% label = c.test.on_kursused and _("Keele- ja kursuseülene") or _("Keeleülene") %>
          ${h.checkbox('%s.keeleylene' % (prefix), 1, checked=item.keeleylene, label=label)}
        </div>
      </td>
      % else:
      ## tagastusymbrikud
      <td>
        <%
          hkid_id = [hk.id for hk in item.hindamiskogumid]
          size = min(9, len(c.opt_hindamiskogum)) + 1
        %>
        ${h.select('%s.hindamiskogum_id' % (prefix), hkid_id, c.opt_hindamiskogum, multiple=True, size=size, empty=True)}
      </td>      
      <td>
        ${h.select('%s.sisukohta' % prefix, item.sisukohta, model.Tagastusymbrikuliik.opt_sisukohta())}
      </td>
      % endif
      <td>
        % if c.can_update and c.is_edit:
        ${h.grid_remove()}
        % endif
        ${h.hidden('%s.id' % prefix, item.id)}
      </td>
    </tr>
</%def>

<%def name="ymbrikuliigid(choices, prefix)">
<table id="tbl_${prefix}" class="table" width="100%" border="0" > 
  <thead>
    <tr>
      <th width="40px">${_("Tähis")}</th>
      <th>${_("Tekst ümbrikul / nimetus")}</th>
      <th>${_("Ümbriku maht")}</th>
      % if prefix.startswith('vb'):
      <th>${_("Lisatööd")}</th>
      <th>${_("Sisu")}</th>
      % else:
      <th>${_("Hindamiskogumid")}</th>
      <th>${_("Sisu")}</th>
      % endif
      <th width="10px"></th>
    </tr>
  </thead>
  <tbody>
  % if c._arrayindexes != '':
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get(prefix) or []:
        ${self.row_ymbrikuliik(c.new_item(),'%s-%s' % (prefix, cnt))}
  %   endfor
  % else:
## tavaline kuva
  %   for cnt,item in enumerate(choices):
        ${self.row_ymbrikuliik(item, '%s-%s' % (prefix, cnt))}
  %   endfor
  % endif
  </tbody>
</table>
% if c.is_edit:
<div id="sample_tbl_${prefix}" class="invisible">
<!--
   ${self.row_ymbrikuliik(c.new_item(),'%s__cnt__' % prefix)}
-->
</div>
% endif
</%def>

<%def name="row_toimumispaev(item, prefix)">
    <tr>
      <td>
        ${h.checkbox('%s.valim' % prefix, 1, checked=item.valim)}
      </td>
      <td>
        ${h.date_field('%s.kuupaev' % prefix, item.aeg, wide=False)}
      </td>
      <td>
        <% dflt = c.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP) and '10.00' or None %>
        ${h.time('%s.kell' % prefix, item.aeg, default=dflt, wide=False)}
      </td>
      <td>
        ${h.date_field('%s.d_lopp' % prefix, item.lopp, wide=False)}
      </td>
      <td>
        ${h.time('%s.t_lopp' % prefix, item.lopp, wide=False)}
      </td>
      <td>
        % if c.can_update and c.is_edit:
        ${h.grid_remove()}
        % endif
        ${h.hidden('%s.id' % prefix, item.id)}
      </td>
    </tr>
</%def>

<%def name="toimumispaevad(choices, prefix)">
<table id="tbl_${prefix}" width="100%" border="0" class="table table-striped"> 
  <thead>
    <tr>
      ${h.th(_("Valim"))}
      ${h.th(_("Toimumise kuupäev"), rq=True)}
      ${h.th(_("Algus kell"))}
      ${h.th(_("Kuni"))}
      ${h.th(_("Lõpp kell"))}
      <th>
      % if c.is_edit:
      ${h.button(_("Lisa"), onclick="grid_addrow('tbl_tpv')", mdicls='mdi-plus', class_="btn-normal", level=2)}
      % endif
      </th>
    </tr>
  </thead>
  <tbody>
  % if c._arrayindexes != '':
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get(prefix) or [0]:
        ${self.row_toimumispaev(c.new_item(),'%s-%s' % (prefix, cnt))}
  %   endfor
  % else:
## tavaline kuva
    <%
    if len(choices) == 0:
       ## alati peab vähemalt yks kuupäev olemas olema
       choices = [c.new_item()]
    %>
  %   for cnt,item in enumerate(choices):
        ${self.row_toimumispaev(item, '%s-%s' % (prefix, cnt))}
  %   endfor
  % endif
  </tbody>
</table>
% if c.is_edit:
<div id="sample_tbl_${prefix}" class="invisible">
<!--
   ${self.row_toimumispaev(c.new_item(),'%s__cnt__' % prefix)}
-->
</div>
% endif
</%def>


