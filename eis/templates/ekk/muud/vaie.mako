<%inherit file="/common/page.mako"/>
<%def name="require()">
<% c.includes['idcard'] = True %>
</%def>
<%def name="requirenw()">
<% c.pagenw = True %>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'muud' %>
</%def>

<%def name="page_title()">
${_("Vaided")} | ${c.kasutaja.nimi}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Vaided"), h.url('muud_vaided'))}
${h.crumb(c.kasutaja.nimi)}
</%def>

## Digiallkirjastamise väljad ja vormid
<div id="pluginLocation"></div>
<div id="error" style="color:red;"></div>

${h.form_save(c.item.id, form_name='form_prepare')}
${h.hidden('sub', 'prepare_signature')}
${h.hidden('cert_hex', '')}
${h.hidden('cert_id', '')}
${h.hidden('phoneno', c.user.telefon)}
${h.hidden('dformat', '')}
${h.end_form()}

${h.form_save(c.item.id, form_name='form_finalize')}
${h.hidden('sub', 'finalize_signature')}
${h.hidden('signature', '')}
${h.hidden('signature_id', '')}
${h.hidden('container_id', '')}
${h.hidden('dformat', '')}
${h.end_form()}


## Põhivorm
${h.form_save(c.item.id, multipart=True)}
${h.hidden('sub', 'kontakt')}
<div class="form-wrapper pb-2">

  % if c.item.vaide_nr:
  <div class="form-group row">
    ${h.flb3(_("Vaie nr"))}
    <div class="col">
      ${c.item.vaide_nr}
    </div>
  </div>
  % endif
  <div class="form-group row">
    ${h.flb3(_("Vaidlustatud test"))}
    <div class="col">
      ${c.test.nimi}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Testi sooritaja"))}
    <div class="col">
      % if c.kasutaja.isikukood:
      ${c.kasutaja.isikukood}
      % else:
      ${h.str_from_date(c.kasutaja.synnikpv)}
      % endif
      ${c.kasutaja.nimi}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Aadress"))}
    <div class="col">
      <%
         c.aadress = c.kasutaja.aadress
         c.aadress_obj = c.kasutaja
      %>
      <%include file="/admin/aadressivalik.mako"/>
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Postiindeks"))}
    <div class="col-md-3">
      ${h.int5('k_postiindeks', c.kasutaja.postiindeks)}
    </div>
    ${h.flb3(_("Telefon"),'k_telefon','text-md-right')}
    <div class="col-md-3">${h.text('k_telefon', c.kasutaja.telefon, size=20)}</div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("E-post"))}
    <div class="col err-parent">
      <div class="d-flex flex-wrap">
        <div class="flex-grow-1 pr-5">
          ${h.text('k_epost', c.kasutaja.epost)}
        </div>
        ${h.checkbox1('otsus_epostiga', 1, checked=c.item.otsus_epostiga, label=_("Otsus saadetakse e-postiga"))}
      </div>
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Põhjendus"))}
    <div class="col">
      ${c.item.markus}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Lisafail"))}
    <div class="col">
      % if c.is_edit:
      ${h.file('vfail')}
      % endif
      % for vf in c.item.vaidefailid:
      <div>
        ${h.link_to(vf.filename, h.url_current('downloadfile', id=c.item.id, file_id=vf.id, format=vf.fileext))}
        % if c.is_edit:
        ${h.grid_s_remove('div', confirm=True, onremove='function(){vfdel(%s);}' % vf.id)}
        % endif
      </div>
      % endfor
      ${h.hidden('vfdel_id', '')}
      <script>
        ## vaidefail märgitakse kustutamiseks
        function vfdel(vf_id){ $('#vfdel_id').val(vf_id);}
      </script>
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Vaidlustuse aeg"))}
    <div class="col-md-3">${h.str_from_date(c.item.esitamisaeg)}</div>
    <div class="col text-right">
      % if c.is_edit:
      ${h.submit(_("Salvesta kontaktandmed"))}
        % if c.item.staatus <= const.V_STAATUS_MENETLEMISEL:
      ${h.btn_remove(None, id=c.item.id, value=_("Tühista vaie"), 
      confirm=_("Kas oled kindel, et soovid vaide tühistada?"))}
        % endif
      % endif
    </div>
  </div>
</div>
${h.end_form()}

###################################################
## Vaide andmed


${h.form_save(c.item.id, multipart=True)}
${h.hidden('op','')}

<div class="form-wrapper pb-2">
  <div class="form-group row">
    ${h.flb3(_("Vaide olek"))}
    <div class="col-md-3">${c.item.staatus_nimi}</div>
    ${h.flb3(_("Hindamise olek"),'hst','text-md-right')}
    <div class="col" id="hst">${c.sooritaja.hindamine_staatus_nimi}</div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Testiosasooritused"))}
    <div class="col">
      <table class="table" >
        <thead>
        <tr>
          <th>${_("Toimumisaeg")}</th>
          <th>${_("Soorituse tähis")}</th>
          <th>${_("Soorituse olek")}</th>
          <th>${_("Hindamise olek")}</th>
        </tr>
        </thead>
        <tbody>
        % for tos in c.sooritaja.sooritused:
        <tr>
          <td>
            % if tos.toimumisaeg:
            ${tos.toimumisaeg.tahised}
            % endif
          </td>
          <td>${tos.tahised}<!--${tos.id}--></td>
          <td>${tos.staatus_nimi}</td>
          <td>
            % if tos.staatus == const.S_STAATUS_TEHTUD:
            ${tos.hindamine_staatus_nimi}
            % endif
          </td>
        </tr>
        % endfor
        </tbody>
      </table>
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Vaidlustatud tulemus"))}
    <div class="col">${h.fstr(c.item.pallid_enne)} ${_("palli")}</div>
  </div>

  % if c.item.pallid_parast is not None:
  <div class="form-group row">
    ${h.flb3(_("Vaidlustusjärgne tulemus"))}
    <div class="col">${h.fstr(c.item.pallid_parast)} ${_("palli")}</div>
  </div>
  % endif


% if c.item.avaldus_dok or c.item.ettepanek_dok:
  % if c.item.avaldus_dok:
  <div class="form-group row">
    ${h.flb3(_("Vaide avaldus"))}
    <div class="col d-flex flex-wrap">
      <div class="mr-5 mb-2">
      ${h.btn_to(_("Laadi alla"), h.url('muud_vaie', id='%s.ddoc' % c.item.id, liik='avaldus'))}
      % if c.can_edit:
      % if c.item.staatus == const.V_STAATUS_ESITAMATA:
      ${h.submit(_("Registreeri"), id='edastaavaldus')}
      % elif c.item.staatus == const.V_STAATUS_ESITATUD:
      ${h.submit(_("Võta menetlusse"), id='menetlusse')}
      % elif c.item.staatus in (const.V_STAATUS_MENETLEMISEL, const.V_STAATUS_ETTEPANDUD) and c.kasutaja.epost:
      ${h.submit(_("Saada sooritajale menetlusse võtmise teade"), id='menetlussesooritajale')}
      % endif
      % endif
      </div>
      <div class="flex-grow-1 d-flex align-items-end justify-content-end">
        ${self.vaidelogid(model.Vaidelogi.TEGEVUS_MENETLUSSE)}
      </div>
    </div>
  </div>
% endif
</div>


% if c.item.staatus not in (const.V_STAATUS_OTSUSTATUD, const.V_STAATUS_ESITAMATA) or c.item.tagasivotmine_ext:
<div class="form-wrapper pb-2">
  <div class="form-group row">
    ${h.flb3(_("Vaide tagasi võtmine"))}
    <div class="col">
      <div class="col d-flex flex-wrap">
        <div class="mr-5 mb-2">
            ${_("Avaldus vaide tagasi võtmiseks")}
            % if c.item.tagasivotmine_ext:
            ${h.btn_to(_("Laadi alla"), h.url('muud_vaie', id='%s.%s' % (c.item.id, c.item.tagasivotmine_ext), liik='votatagasi'))}
            % endif
         % if c.can_edit:
            % if c.item.staatus not in (const.V_STAATUS_OTSUSTATUD, const.V_STAATUS_ESITAMATA, const.V_STAATUS_TAGASIVOETUD):
            ${h.file('tagasivotmine_dok', value=_("Fail"))}
            ${h.submit(_("Võta vaie tagasi"), id='votatagasi')}
            % elif c.item.staatus == const.V_STAATUS_TAGASIVOETUD:
            ${h.submit_confirm(_("Võta vaie uuesti menetlusse"), id='uuesti', 
            confirm=_("Kas võtta vaie uuesti menetlusse?"))}
            % endif
         % endif
        </div>
        <div class="flex-grow-1 d-flex align-items-end justify-content-end">
          ${self.vaidelogid(model.Vaidelogi.TEGEVUS_TAGASIVOTMINE)}
        </div>
      </div>
    </div>
  </div>
</div>
% endif
    
% if c.item.ettepanek_dok:
<% on_hinnatud = c.item.tulemus_arvutatud %>
<div class="form-wrapper pb-2">
  <div class="form-group row">
    ${h.flb3(_("Ettepanek"))}
    <div class="col">
      <p>
        ${c.item.gen_ettepanek_txt()}
        <br/>
        ${h.html_nl(c.item.ettepanek_pohjendus)}
      </p>
      <div class="d-flex flex-wrap">
        <div>
            ${h.btn_to(_("Laadi alla"), h.url('muud_vaie', id='%s.ddoc' % c.item.id, liik='ettepanek'))}
            &nbsp;
            % if c.can_edit and c.item.staatus == const.V_STAATUS_ETTEPANDUD:
            ${h.submit(_("Arvuta tulemused"), id='arvuta')}
            % endif
        </div>
        <div class="flex-grow-1 d-flex align-items-end justify-content-end">
          ${self.vaidelogid(model.Vaidelogi.TEGEVUS_ARVUTUSED)}
        </div>
      </div>
    </div>
  </div>
</div>
<div class="form-wrapper pb-2">
  <div class="form-group row">
    ${h.flb3(_("Otsuse eelnõu"))}
    <div class="col">
      <p>
        ${c.item.gen_ettepanek_txt()}<br/>

        % if c.item.staatus == const.V_STAATUS_ETTEPANDUD and on_hinnatud:
        ${h.textarea('eelnou_pohjendus', c.item.eelnou_pohjendus or c.item.ettepanek_pohjendus, rows=4)}
        % else:
        ${c.item.eelnou_pohjendus}
        % endif
      </p>

      <div class="d-flex flex-wrap mb-2">
        <div class="nowrap">
        % if c.can_edit and c.item.staatus == const.V_STAATUS_ETTEPANDUD and on_hinnatud:
        ${_("Ärakuulamise tähtaeg")}
        ${h.date_field('arakuulamine_kuni', c.item.arakuulamine_kuni or (model.date.today() + model.timedelta(days=3)), wide=False)}
        <div>
          ${h.submit(_("Loo otsuse eelnõu"), id='eelnou')}
        </div>
        % elif c.item.arakuulamine_kuni:
        ${_("Ärakuulamise tähtaeg")} ${h.str_from_date(c.item.arakuulamine_kuni)}
        % endif
        </div>
        <div class="flex-grow-1 d-flex align-items-end justify-content-end">
          ${self.vaidelogid(model.Vaidelogi.TEGEVUS_EELNOU)}
        </div>
      </div>
  
      % if c.item.eelnou_pdf:
      <div class="d-flex flex-wrap">
        <div>
          ${h.btn_to(_("Laadi alla"), h.url('muud_vaie', id='%s.%s' % (c.item.id, 'pdf'), liik='eelnou'))}

          % if c.can_edit and c.item.staatus == const.V_STAATUS_ETTEPANDUD:
          % if c.kasutaja.epost:
            ${h.submit(_("Saada eelnõu sooritajale"), id='edastaeelnou')}
          % endif
          % if c.item.arakuulamine_kuni:
              % if c.item.arakuulamine_kuni >= model.date.today():
                 ${h.submit_confirm(_("Lõpeta ärakuulamine"), id='otsustamisel',
                 confirm=_("Tähtaeg pole veel käes. Kas oled kindel, et soovid ärakuulamise lõpetada enne tähtaega?"))}
              % else:
                 ${h.submit(_("Lõpeta ärakuulamine"), id='otsustamisel')}
              % endif
          % endif
          % endif
        </div>
        <div class="flex-grow-1 d-flex align-items-end justify-content-end">
          <div>
          ${self.vaidelogid(model.Vaidelogi.TEGEVUS_EELNOU_EDASTA)}
          ${self.vaidelogid(model.Vaidelogi.TEGEVUS_OTSUSTAMISEL)}
          </div>
        </div>
      </div>
      % endif
    </div>
  </div>
</div>
% endif

% if c.item.otsus_dok or c.item.staatus >= const.V_STAATUS_OTSUSTAMISEL:
<div class="form-wrapper pb-2">
  <div class="form-group row">
    ${h.flb3(_("Otsus"))}
    <div class="col">
      % if c.item.ettepanek_dok:
      <p>
        % if c.item.staatus >= const.V_STAATUS_OTSUSTAMISEL:
        ${c.item.gen_ettepanek_txt()}<br/>
        % endif
        
        % if c.item.staatus == const.V_STAATUS_OTSUSTAMISEL and on_hinnatud:
        ${h.textarea('otsus_pohjendus', c.item.otsus_pohjendus or c.item.eelnou_pohjendus or c.item.ettepanek_pohjendus, rows=4)}
        % else:
        ${h.html_nl(c.item.otsus_pohjendus)}
        % endif
      </p>
      % endif
      <div class="d-flex flex-wrap">
        <div>
        % if c.can_edit and c.item.staatus == const.V_STAATUS_OTSUSTAMISEL and on_hinnatud:
            ${_("Otsuse kuupäev")} ${h.date_field('otsus_kp', c.item.otsus_kp or c.today, wide=False)}
            <div>
            % if c.item.allkirjad:
              ${h.submit_confirm(_("Loo otsus uuesti"), id='otsus',
               confirm=_("Kas oled kindel, et soovid luua uut otsust ja kustutada eelnevalt antud allkirjad?"))}
            % else:
               ${h.submit(_("Loo otsus"), id='otsus')}
            % endif
            </div>
        % elif c.item.otsus_kp:
            ${_("Otsuse kuupäev")} ${h.str_from_date(c.item.otsus_kp)}
        % endif
        </div>
        <div class="flex-grow-1 d-flex align-items-end justify-content-end">
            ${self.vaidelogid(model.Vaidelogi.TEGEVUS_OTSUS)}
        </div>
      </div>

      % if c.item.otsus_pdf or c.item.otsus_dok:
      <div class="d-flex flex-wrap">
        <div>
            ${h.btn_to(_("Laadi alla"), h.url('muud_vaie', id='%s.%s' % (c.item.id, c.item.otsus_ext or 'pdf'), liik='otsus'))}

            <% allkirjad = list(c.item.vaideallkirjad) %>
            % if allkirjad:
            ## allkirjade kirjed puuduvad enne mai 2022 genereeritud otsustel
            <table class="table my-1">
              <thead>
                <tr>
                  <th>${_("Allkirjastaja")}</th>
                  <th class="text-nowrap">${_("Allkirjastanud")} (${c.item.allkirjad or 0})</th>
                </tr>
              </thead>
              <tbody>
                % for va in allkirjad:
                <tr>
                  <td>${va.kasutaja.nimi}</td>
                  <td>${va.allkirjastatud and _("Jah") or _("Ei")}
                </tr>
                % endfor
              </tbody>
            </table>
            % endif
            
            % if c.item.staatus == const.V_STAATUS_OTSUSTAMISEL and c.can_sign:
             <br/>
              % if c.item.otsus_ext != const.DDOC:
              <p>
              ${h.button(_("Allkirjasta smart-ID abil"), onclick='smartidSign()')}
              ${h.button(_("Allkirjasta mobiil-ID abil"), onclick='mobileSign()')}
              ${h.button(_("Allkirjasta ID-kaardiga"), onclick='getCertBdoc()')}
             </p>
             % endif
             <div>
            ${h.file('otsus_dok', value=_("Fail"))}
            ${h.submit(_("Laadi üles"), id='upload')}
            </div>
             % endif
        </div>
        <div class="flex-grow-1 d-flex align-items-end justify-content-end">
            <div id="ddoc_status" class="ddoc"> </div>
            ${self.vaidelogid(model.Vaidelogi.TEGEVUS_ALLKIRI)}
        </div>
      </div>
      % endif

      % if c.item.otsus_dok:
      <div class="d-flex flex-wrap">
        <div>
            % if c.can_edit and c.item.staatus == const.V_STAATUS_OTSUSTATUD and c.kasutaja.epost:
            ${h.submit(_("Saada otsus sooritajale"), id='otsussooritajale')}
            % endif
        </div>
        <div class="flex-grow-1 d-flex align-items-end justify-content-end">
          ${self.vaidelogid(model.Vaidelogi.TEGEVUS_EDASTA)}
        </div>
      </div>

      <div class="d-flex flex-wrap">
        <div>
            % if c.can_edit and c.item.staatus == const.V_STAATUS_OTSUSTAMISEL and c.all_signed:         
            ${h.submit(_("Märgi vaidemenetlus lõpetatuks"), id='lopeta')}
            % endif
        </div>
        <div class="flex-grow-1 d-flex align-items-end justify-content-end">
          ${self.vaidelogid(model.Vaidelogi.TEGEVUS_LOPETA)}
        </div>
      </div>
      % endif

      % if c.can_edit and c.item.staatus == const.V_STAATUS_OTSUSTATUD:
      ${h.submit_confirm(_("Võta vaie uuesti menetlusse"), id='uuesti', 
      confirm=_("Kas võtta vaie uuesti menetlusse ja tühistada varasem otsuse dokument?"))}
      % endif
    </div>
  </div>
  % endif
</div>
% endif

${h.end_form()}

<%def name="vaidelogid(tegevus)">
<table class="box">
  <col/>
  <col width="150"/>
  <col width="200"/>
% for r in c.item.vaidelogid:
  % if r.tegevus == tegevus:
<tr>
  <td class="pr-2">${r.kasutaja.nimi}</td>
  <td class="pr-2">${h.str_from_datetime(r.created)}</td>
  <td>${r.tegevus_nimi}
    % if r.tapsustus:
    (${r.tapsustus})
    % endif
  </td>
</tr>
  % endif
% endfor
</table>
</%def>
