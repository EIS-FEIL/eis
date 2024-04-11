<%inherit file="korrad.mako"/>
<%def name="require()">
<%
c.includes['subtabs'] = True
c.includes['jstree'] = True
c.includes['select2'] = True  
%>
</%def>
${h.form_save(c.item.id, style="width:100%")}
${h.hidden('mall_id', c.mall_id)}

<h2>${_("Testimiskorra andmed")}</h2>

${h.rqexp()}
<div class="form-wrapper mb-2">
  
<div class="gray-legend p-2 border-base-radius">
  <div class="form-group row">
    ${h.flb3(_("Testimiskorra tähis"), 'f_tahis', rq=True)}
    <div class="col-md-9">
      ${h.text('f_tahis', c.item.tahis, maxlength=10, size=11, pattern='[0-9a-zA-Z]*')}
      <%
        KATSE = 'KATSE'
        is_k = c.item.tahis != KATSE and \
            (model.SessionR.query(model.Testimiskord.id)
               .filter_by(test_id=c.test.id)
               .filter_by(tahis='KATSE')
               .count()) > 0
      %>
      % if not is_k:
      <span class="ml-3">${h.checkbox1('katse', 1, checked=c.item.tahis==KATSE, label=_("Katse"))}</span>
      <script>
        $('#katse').click(function(){ var f=$('#f_tahis'); if($('#katse').prop('checked')) f.val('${KATSE}'); else f.val(''); });
        $('#f_tahis').change(function(){ $('#katse').prop('checked', $('#f_tahis').val() == '${KATSE}'); });
      </script>
      % endif
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Testsessioon"), 'f_testsessioon_id')}
    <div class="col-md-9">
      ${h.select('f_testsessioon_id', c.item.testsessioon_id,
      model.Testsessioon.get_opt(c.test.testiliik_kood), empty=True)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Õppeaasta"), 'f_aasta')}
    <div class="col-md-9">
      <%
        year = (c.item.alates or model.date.today()).year
        opt_aasta = [year, year+1]
        year = c.item.aasta
        if year and year not in opt_aasta:
           opt_aasta.append(year)
           opt_aasta.sort()
      %>
      ${h.select('f_aasta', c.item.aasta, opt_aasta, wide=False, empty=not c.item.aasta)}
    </div>
  </div>

  <% vtk = c.item.valim_testimiskord %>
  % if vtk:
  <div class="text-right">
      ${_("Moodustatud valimina testimiskorrast {s}").format(s=h.link_to(vtk.tahised,
      h.url('test_edit_kord', test_id=c.item.test_id, id=vtk.id)))}
  </div>
  % endif
</div>

<h3>${_("Kuupäevad")}</h3>

<div class="p-2 mb-3 border border-base-radius">
  <div class="form-group row">
    ${h.flb3(_("Vaidlustuse algus"),'f_vaide_algus')}
    <div class="col-md-9">
      ${h.date_field('f_vaide_algus', c.item.vaide_algus, wide=False)}
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("Vaidlustuse lõpp"),'f_vaide_tahtaeg')}
    <div class="col-md-9">
      ${h.date_field('f_vaide_tahtaeg', c.item.vaide_tahtaeg, wide=False)}
      <span class="ml-2">
        ${h.checkbox('f_on_avalik_vaie', 1, checked=c.item.on_avalik_vaie, 
        label=_("Sooritaja saab kuni vaidlustuse lõpukuupäevani avalikus vaates ise vaide esitada"))}
      </span>
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Testi toimumisajad"), 'toimumisajad')}
    <div class="col-md-9" id="toimumisajad">
      <table class="table">
        <tr>
          ${h.th(_("Testiosa"))}
          ${h.th(_("Vastamise vorm"))}
          ${h.th(_("Alates"))}
          ${h.th(_("Kuni"))}
        </tr>
        % for toimumisaeg in c.item.toimumisajad:
        <% testiosa = toimumisaeg.testiosa %>
        <tr>
          <td>${testiosa.tahis}</td>
          <td>${testiosa.vastvorm_nimi}</td>
          <td>${h.str_from_date(toimumisaeg.alates)}</td>
          <td>${h.str_from_date(toimumisaeg.kuni)}</td>
        </tr>
        % endfor
      </table>
    </div>
  </div>
</div>

<h3>${_("Lisavalikud")}</h3>
<div class="p-2 mb-3 border border-base-radius">
  <div class="form-group row">
    ${h.flb3(_("Soorituskeeled"),'lang', rq=True)}
    <div class="col-md-9">
      <%
        test_keeled = c.test.keeled
        k_keeled = c.item.keeled
      %>
      % for lang in test_keeled:
      ${h.checkbox('lang', value=lang, checked=lang in k_keeled, label=model.Klrida.get_str('SOORKEEL', lang))}
      % endfor
      ${h.hidden('lang_err', '')}
    </div>
  </div>
  
  % if c.item.id:
  <div class="form-group row">
    ${h.flb3(_("Soorituspiirkonnad"),'piirkonnad')}
    <div class="col-md-9 d-flex" id="piirkonnad">
    % if c.can_update:
    <div>
    ${h.btn_to_dlg(_("Muuda"), h.url('test_edit_kord', test_id=c.test.id,
    id=c.item.id, sub='prk', partial=True), title=_("Piirkonnad"), width=500, level=2)}
    </div>
      % endif
      ${h.roxt(', '.join(rcd.nimi for rcd in c.item.piirkonnad))}
    </div>
  </div>

  <div class="form-group row">
    ${h.flb3(_("Konsultatsioonid"),'konsultatsioonid')}
    <div class="col-md-9 d-flex" id="konsultatsioonid">
      % if c.can_update:
      <div>
      ${h.btn_to_dlg(_("Muuda"), h.url('test_edit_kord', test_id=c.test.id,
      id=c.item.id, sub='eksam', partial=True), title=_("Testid"), width=500, level=2)}
      </div>
      % endif
      <table width="100%" class="table" >      
        <col width="80"/>
        <col/>
        % for r in c.item.konskorrad:
        <tr>
          <td>
            <% tkord = r.kons_testimiskord %>
            ${h.link_to(tkord.tahised, h.url('konsultatsioon_edit_kord', test_id=tkord.test_id, id=tkord.id))}
          </td>
          <td>${tkord.test.nimi}</td>
        </tr>
        % endfor
      </table>
    </div>
  </div>
  % endif
  % if c.test.testiliik_kood == const.TESTILIIK_RV:
  <div class="form-group row">
    <div class="col-12">
      ${h.checkbox('f_cae_eeltest', value=1, checked=c.item.cae_eeltest,
      label=_("Nõutav CAE eeltest"))}
    </div>
  </div>
  % endif
</div>

<h3>${_("Registreerimine")}</h3>
<div class="p-2 mb-3 border border-base-radius">
  <div class="form-group row">
    ${h.flb3(_("Registreerimise viis"), 'regviis')}
    <div class="col-md-9 row" id="regviis">
      <div class="col-md-6 col-lg-4">
      ${h.checkbox1('f_reg_sooritaja', value=1, checked=c.item.reg_sooritaja, 
      label=_("Sooritaja (EISi kaudu)"))}
      % if c.test.on_tseis:
      ${h.checkbox1('f_reg_xtee', value=1, checked=c.item.reg_xtee, 
      label=_("Sooritaja (eesti.ee kaudu)"))}
      % endif
      </div>
      <div class="col-md-6 col-lg-4">
      ${h.checkbox1('f_reg_kool_eis', value=1, checked=c.item.reg_kool_eis,
      label=_("Õppeasutus"))} 
      ${h.checkbox1('f_reg_kool_valitud', value=1, checked=c.item.reg_kool_valitud,
      label=_("Valitud õppeasutus"))}
      </div>
      <div class="col-md-6 col-lg-4">
      ${h.checkbox('f_reg_ekk', value=1, checked=c.item.reg_ekk, 
      label=_("Eksamikeskus"))}
      </div>
      <script>
        $('input#f_reg_kool_valitud').click(function(){
           if(this.checked) $('#f_reg_kool_eis').prop('checked', false);
        });
        $('input#f_reg_kool_eis').click(function(){
           if(this.checked && $('#f_reg_kool_valitud').prop('checked'))
              $('#f_reg_kool_valitud').click();
        });
      </script>
    </div>
  </div>
  <div class="form-group row tr-regkohad" style="display:none">
    ${h.flb3(_("Õppeasutused"), 'kohad')}
    <div class="col-md-9 d-flex" id="kohad">
      % if c.can_update and c.item.id:
        <div>
          ${h.btn_to_dlg(_("Muuda"), h.url('test_edit_kord', test_id=c.test.id,
          id=c.item.id, sub='regkoht', partial=True), title=_("Õppeasutused"), width=900, level=2)}
        </div>
        % endif
        <div class="regkohad-list readonly">
          <% k_nimed = [r.nimi for r in c.item.regkohad] %>
          ${', '.join(k_nimed)}
        </div>
        <script>
            $(function(){
            $('#f_reg_kool_valitud').click(function(){ $('.tr-regkohad').toggle(this.checked); });
            $('.tr-regkohad').toggle($('#f_reg_kool_valitud').prop('checked'));
            })
        </script>
    </div>
  </div>
  % if c.test.testiliik_kood == const.TESTILIIK_TASE:
  <div class="form-group row">
    ${h.flb3(_("Registreerimise tingimus"), 'regpiirang')}
    <div class="col-md-9" id="regpiirang">
      ${h.checkbox('f_reg_piirang', value=const.REGPIIRANG_H, checkedif=c.item.reg_piirang,
      label=_("Haridustöötajad"))}
    </div>
  </div>
  % endif
  <div class="form-group row">
    <div class="col-12">
      ${h.checkbox1('f_reg_kohavalik', 1,
      checked=c.item.reg_kohavalik, label=_("Soorituskoha valimine registreerimisel"))}
    </div>
  </div>
  <div class="form-group row">
    <div class="col-12">
      ${h.checkbox1('f_reg_voorad', 1,
      checked=c.item.reg_voorad, label=_("Õppeasutus saab registreerida võõraid"))}
    </div>
  </div>
</div>

${h.rqexp(None, _("Registreerimisaja sisestamine on kohustuslik siis, kui vastav registreerimise viis on valitud"))}
<div class="p-2 mb-3 border border-base-radius">
  <div class="form-group row">
    ${h.flb(_("Registreerimisaeg (testisooritaja poolt EISi kaudu registreerimine)"),'f_reg_sooritaja_alates','col-md-5')}
    <div class="col-md-3">
      ${h.date_field('f_reg_sooritaja_alates', c.item.reg_sooritaja_alates)}
    </div>
    <div class="col-md-1">
      ${_("kuni")}
    </div>
    <div class="col-md-3">
      ${h.date_field('f_reg_sooritaja_kuni', c.item.reg_sooritaja_kuni)}
    </div>
  </div>
  % if c.test.on_tseis:
  <div class="form-group row">
    ${h.flb(_("Registreerimisaeg (testisooritaja poolt eesti.ee kaudu registreerimine)"),'f_reg_xtee_alates','col-md-5')}
    <div class="col-md-3">
      ${h.date_field('f_reg_xtee_alates', c.item.reg_xtee_alates)}
    </div>
    <div class="col-md-1">
      ${_("kuni")}
    </div>
    <div class="col-md-3">
      ${h.date_field('f_reg_xtee_kuni', c.item.reg_xtee_kuni)}
    </div>
  </div>
  % endif
  <div class="form-group row">
    ${h.flb(_("Registreerimisaeg (õppeasutuse poolt registreerimine)"),'f_reg_kool_alates','col-md-5')}
    <div class="col-md-3">
      ${h.date_field('f_reg_kool_alates', c.item.reg_kool_alates)}
    </div>
    <div class="col-md-1">
      ${_("kuni")}
    </div>
    <div class="col-md-3">
      ${h.date_field('f_reg_kool_kuni', c.item.reg_kool_kuni)}
    </div>
  </div>    

  <div class="form-group row">
    ${h.flb(_("Eritingimuste märkimine (õppeasutuses)"),'f_erivajadus_alates','col-md-5')}
    <div class="col-md-3">
      ${h.date_field('f_erivajadus_alates', c.item.erivajadus_alates)}
      </div>
    <div class="col-md-1">
      ${_("kuni")} 
    </div>
    <div class="col-md-3">
      ${h.date_field('f_erivajadus_kuni', c.item.erivajadus_kuni)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb(_("Sooritajad avalikus vaates peidetud kuni"),'peidus_kuni','col-md-5')}
    <div class="col-md-3">
      ${h.date_field('peidus_kuni', c.item.sooritajad_peidus_kuni)}
    </div>
    <div class="col-md-1">
      ${_("kell")}
    </div>
    <div class="col-md-3">
      ${h.time('peidus_kell', c.item.sooritajad_peidus_kuni, default='07:00')}
    </div>
  </div>
  <div class="form-group row">
    <div class="col-12">
      ${h.checkbox1('f_korduv_reg_keelatud', 1,
      checked=c.item.korduv_reg_keelatud,
      label=_("Testimiskorrale ei või registreerida sama testi teistele testimiskordade registreerituid"))}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Osalemistasu"),'f_osalemistasu')}
    <div class="col-md-9">
      ${h.float5('f_osalemistasu', c.item.osalemistasu)} €
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Kordusosalemistasu"),'f_kordusosalemistasu')}
    <div class="col-md-9">
      ${h.float5('f_kordusosalemistasu', c.item.kordusosalemistasu)} €
    </div>
  </div>
  <div class="form-group row">
    <div class="col-12">
      ${h.checkbox1('f_kool_testikohaks', 1,
      checked=c.item.kool_testikohaks,
      label=_("Soorituskohtade loomine sooritajate õppeasutustes"))}
    </div>
  </div>
  <div class="form-group row">
    <div class="col-12">
      ${h.checkbox1('f_sisestus_isikukoodiga', 1,
      checked=c.item.sisestus_isikukoodiga,
      label=_("Sisestamine isikukoodiga"))}
    </div>
  </div>
  <div class="form-group row">
    <div class="col-12">
      ${h.checkbox1('f_korraldamata_teated', 1,
      checked=c.item.korraldamata_teated or not c.item.id,
      label=_("Koolile automaatsete korraldamise meeldetuletuste saatmine"))}
    </div>
  </div>
</div>

<div class="p-2 mb-3 border border-base-radius d-flex flex-column">

      ${h.checkbox('f_prot_vorm', const.PROT_VORM_DOKNR, checkedif=c.item.prot_vorm,
      label=_("Toimumise protokoll dok numbritega"))}

      ${h.checkbox('f_prot_vorm', const.PROT_VORM_ATS, checkedif=c.item.prot_vorm,
      label=_("Toimumise protokoll täiendatud puudumise olekutega"))}

      ${h.checkbox('f_prot_vorm', const.PROT_VORM_TULEMUS, checkedif=c.item.prot_vorm,
      label=_("Toimumise protokoll tulemusega"))}

      ${h.checkbox('f_prot_vorm', const.PROT_VORM_YLTULEMUS, checkedif=c.item.prot_vorm,
      label=_("Toimumise protokoll ülesannete tulemustega"))}
      <script>
        $('input[name="f_prot_vorm"]').click(function(){
           $('input[name="f_prot_vorm"]').not(this).prop('checked', false);
        });
      </script>
      ${h.checkbox('f_prot_vorm', const.PROT_VORM_ALATULEMUS, checkedif=c.item.prot_vorm,
      label=_("Toimumise protokoll alatestide tulemustega"))}
      <script>
        $('input[name="f_prot_vorm"]').click(function(){
           $('input[name="f_prot_vorm"]').not(this).prop('checked', false);
        });
      </script>
</div>

<div class="p-2 mb-3 border border-base-radius d-flex flex-column">
  <%
    vastvorm_s = (const.VASTVORM_SH, const.VASTVORM_SP)
    on_suuline = any([r.vastvorm_kood in vastvorm_s for r in c.test.testiosad])
  %>
  % if on_suuline:
      ${h.checkbox1('f_on_helifailid', 1, checked=c.item.on_helifailid,
      label=_("Helifailid"))}
  % endif
      ${h.checkbox1('f_on_turvakotid', 1, checked=c.item.on_turvakotid,
      label=_("Turvakotid"))}

  % if not c.test.diagnoosiv:
  ${h.checkbox1('arvutada_kohe', 1,
      checked=not c.item.arvutada_hiljem,
      label=_("Testi lõpetamisel arvutada kohe tulemused"))}
  % endif
  ${h.checkbox1('f_tulemus_koolile', 1,
      checked=c.item.tulemus_koolile,
      label=_("Koolidel tulemuste vaatamine lubatud"))}

  ${h.checkbox1('f_tulemus_admin', 1,
      checked=c.item.tulemus_admin,
      label=_("Testiadministraatoritel tulemuste vaatamine lubatud"))}

  ${h.checkbox1('f_osalemise_naitamine', 1, checked=c.item.osalemise_naitamine or not c.item.id, label=_("Sooritajale ja koolile näidatakse testil osalemist tehtud testide ja registreerimiste loetelus"))}

  ${h.checkbox1('f_analyys_eraldi', 1,
      checked=c.item.analyys_eraldi,
      label=_("Vastuste analüüs testimiskorra kaupa"))}

  % if c.item.valim_testimiskord_id:
  <div class="d-flex flex-wrap">
    <div class="flex-grow-1">
      ${h.checkbox1('f_stat_valim', 1,
      checked=c.item.stat_valim,
      label=_("Statistikas arvestatav valim"))}
    </div>
    <% mvtk = c.item.valim_testimiskord %>
    <div>${_("See valim on eraldatud testimiskorrast {lnk}").format(lnk=h.link_to(mvtk.tahis, h.url_current('show', id=mvtk.id)))}</div>
  </div>
  % endif
  
  <div class="form-group row">
    ${h.flb3(_("Märkus"))}
    <div class="col-md-9">
      ${h.textarea('f_markus', c.item.markus, maxlength=1000)}
    </div>
  </div>
</div>

% if (c.item.on_mall or c.is_edit) and c.test.testityyp == const.TESTITYYP_EKK:
<div class="p-2 mb-3 border border-base-radius">
  ${h.checkbox1('f_on_mall', 1, checked=c.item.on_mall, label=_("Kasutusel testimiskordade loomise mallina"))}

  <div class="form-group row trmall">
    ${h.flb3(_("Malli nimetus"),'f_nimi')}
    <div class="col-md-9">
      ${h.text('f_nimi', c.item.nimi, max=256)}
    </div>
  </div>
</div>
<script>
  $('#f_on_mall').click(function(){
  $('.trmall').toggle($('#f_on_mall').prop('checked'));
  });
  $('.trmall').toggle($('#f_on_mall').prop('checked'));
</script>
% endif

% if len(c.item.testilepingud) and request.params.get('debug'):
<table  class="table table-borderless table-striped m-3">
  <caption>${_("Läbiviimiseks on vajalik nõustuda lepingutega")}</caption>
  <tbody>
    % for tleping in c.item.testilepingud:
    <% leping = tleping.leping %>
    <tr>
      <td>${tleping.kasutajagrupp_nimi}</td>
      <td>
        ${h.link_to(leping.nimetus, leping.url)}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

## end form-wrapper
</div>

${h.end_form()}

<%def name="buttons()">

% if c.item and c.item.id:
  % if c.user.has_permission('testimiskorrad', const.BT_UPDATE, c.test):
${h.btn_to(_("Kopeeri"), h.url('test_new_kord', test_id=c.test.id,
id=c.item.id), level=2)}
  % endif
  % if c.user.has_permission('tkorddel', const.BT_DELETE):
<%
  cnt = model.SessionR.query(model.sa.func.count(model.Sooritaja.id)).filter_by(testimiskord_id=c.item.id).scalar()
  if cnt:
     message = _("Testimiskorral {s} on {n} sooritajat. Kas oled kindel, et soovid selle testimiskorra koos sooritajate andmetega kustutada?").format(s=c.item.tahis, n=cnt)
  else:
     message = _("Kas oled kindel, et soovid testimiskorra {s} kustutada?").format(s=c.item.tahis)
%>
${h.btn_to(_("Kustuta"), h.url('test_delete_kord', test_id=c.test.id, id=c.item.id), method='delete', confirm=message, level=2)}
  % endif
% endif
% if c.can_update:
  % if c.is_edit:
${h.submit(out_form=True)}
  % elif c.item.id:
${h.btn_to(_("Muuda"), h.url('test_edit_kord', test_id=c.test.id,
id=c.item.id))}
  % endif
% endif

</%def>


