<%inherit file="/common/dlgpage.mako"/>
<div id="pluginLocation"></div>
<div id="error" style="color:red;"></div>

<% 
  c.kasutaja = c.item.kasutaja
  c.test = c.item.test
  on_te = c.test.testiliik_kood == const.TESTILIIK_TASE
%>
% if c.is_edit:
${h.form_save(c.item.id)}
% else:
## vorm, mille action on muutmise url (kasutab nupp Muuda)
${h.form(h.url_current('edit'), method='get')}
% endif
<div>
  <%include file="/common/message.mako"/>
  % if c.vaie.id and c.vaie.esitamisaeg and c.vaie.staatus and c.vaie.staatus > const.V_STAATUS_ESITAMATA:
  ${h.alert_success(_("Vaie on esitatud {s}").format(s=h.str_from_date(c.vaie.esitamisaeg)), False)}
  % endif

  <% ch = h.colHelper('col-md-3', 'col-md-9') %>

  ${h.alert_warning(_("NB! Vaide esitamiseks on vaja avaldus digitaalselt allkirjastada! Palun veenduge, et teil on olemas digiallkirjastamise võimalus, enne kui alustate avalduse täitmist. Kui sulgete veebilehe enne vaide allkirjastamist, siis jääb teie vaie esitamata."), False)}
  
  % if on_te:
  ${h.alert_warning(_("NB! Kui esitate vaide eksami tulemuse vaidlustamiseks, siis hinnatakse uuesti kogu eksamitöö ning seda ka juhul, kui soovite vaidlustada üksnes konkreetse ülesande või eksamiosa hindamistulemust. Vaidekomisjon võib eksamitöö tulemust tõsta või selle muutmata jätta."), False)}
  % else:
  ${h.alert_warning(_("NB! Kui esitate apellatsiooni eksami tulemuse vaidlustamiseks, siis vaadatakse üle kogu eksamitöö ning seda ka juhul, kui soovite vaidlustada üksnes konkreetset ülesannet või eksamiosa. Apellatsioonikomisjon võib eksamitöö tulemust tõsta, selle muutmata jätta või seda langetada."), False)}
  % endif
  
  % if c.vaie.id:
  <div class="form-group row">
    ${ch.flb(_("Vaide olek"),'staatus_nimi')}
    <div class="col-md-9" id="staatus_nimi">
      <b>
        % if c.vaie.staatus == const.V_STAATUS_ESITAMATA:
        <span style="color:#ff0000">
          ${c.vaie.staatus_nimi}
        </span>
        % else:
        ${c.vaie.staatus_nimi}
        % endif
      </b>
    </div>
  </div>
  % endif

  <div class="form-group row">
    ${ch.flb(_("Isikukood"),'isikukood')}
    <div class="col-md-9" id="isikukood">${c.kasutaja.isikukood}</div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Eesnimi"),'eesnimi')}
    <div class="col-md-9" id="eesnimi">
      ${c.kasutaja.eesnimi}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Perekonnanimi"), 'perenimi')}
    <div class="col-md-9" id="perenimi">
      ${c.kasutaja.perenimi}
    </div>
  </div>    
  <div class="form-group row">
    ${ch.flb(_("Aadress"),'diaadress')}
    <div class="col-md-9" id="diaadress">
      <%
         c.aadress = c.kasutaja.aadress
         c.aadress_obj = c.kasutaja
      %>
      <%include file="/admin/aadressivalik.mako"/>
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Postiindeks"), 'k_postiindeks')}
    <div class="col-md-9">
      ${h.int5('k_postiindeks', c.kasutaja.postiindeks)}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Telefon"), 'k_telefon')}
    <div class="col-md-9">
      ${h.text('k_telefon', c.kasutaja.telefon, size=20)}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("E-post"), 'k_epost')}
    <div class="col-md-9 err-parent">
      ${h.text('k_epost', c.kasutaja.epost, size=40)}
    </div>
  </div>
  <div class="form-group row">
    <div class="col">
      <% if c.vaie.otsus_epostiga is None: c.vaie.otsus_epostiga = True %>
      ${h.checkbox('f_otsus_epostiga', 1, checked=c.vaie.otsus_epostiga, label=_("Soovin otsust e-postiga"))}
    </div>
  </div>

  <p>
    <b>
    ${_("Kinnitan, et soovin vaidlustada testi {s} tulemuse {p} hindepalli").format(s=c.test.nimi, p=h.fstr(c.item.pallid))}
    </b>
  </p>

  <div class="form-group row pb-3">
    ${ch.flb(_("Põhjendus"), 'f_markus')}
    <div class="col">
      ${h.textarea('f_markus', c.vaie.markus, cols=80, rows=6)}
    </div>
  </div>

  % if not c.is_edit and c.vaie.staatus > const.V_STAATUS_ESITAMATA:
  <div class="py-3">
    <div>
      ${h.link_to(_("Vaide avaldus"), h.url_current('downloadfile', id=c.item.id, file_id='avaldus', format=c.vaie.avaldus_ext))}
    </div>
    % for vf in c.vaie.vaidefailid:
    <div>
      ${h.link_to(vf.filename, h.url_current('downloadfile', id=c.item.id, file_id=vf.id, format=vf.fileext))}
    </div>
    % endfor

    % if c.vaie.otsus_dok:
    <div>
      ${h.link_to(_("Vaide otsus"), h.url_current('downloadfile', id=c.item.id, file_id='otsus', format=c.vaie.otsus_ext))}
    </div>
    % endif
  </div>
  % endif
  
  <div class="py-3 d-flex flex-wrap">
    <div class="flex-grow-1">
    % if c.vaie.staatus == const.V_STAATUS_ESITAMATA:
    ${h.button(_("Tühista"), id="tyhista")}
    % if not c.is_edit:
    ${h.submit_dlg(_("Muuda"), method='get', level=2)}
    % endif
    % endif
    </div>
    <div>
    % if c.is_edit:
      ${h.submit_dlg(_("Allkirjastama"))}
    % elif c.vaie.staatus == const.V_STAATUS_ESITAMATA:
      ${h.button(_("Allkirjasta smart-ID abil"), onclick='smartidSign()')}    
      ${h.button(_("Allkirjasta mobiil-ID abil"), onclick='mobileSign()')}
      ${h.button(_("Allkirjasta ID-kaardiga"), onclick='getCertBdoc()')}
    % else:
      ${h.button(_("Sule aken"), onclick="close_dialog('dvaie')")}
    % endif
    </div>
  </div>
      
  <div id="ddoc_status" class="pt-3"> </div>
</div>
${h.end_form()}

% if c.vaie.id:

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


% endif

% if c.vaie.staatus == const.V_STAATUS_ESITAMATA:
<script>
   $('#dvaie button#tyhista, #dvaie button.close').click(function(){
         var btns = {"${_("Jätka esitamist")}": function(){ close_dialog(); },
                     "${_("Tühista vaie")}": function(){
                            $.ajax({type: 'post',
                                    url: "${h.url_current('delete')}",
                                    success: function(){
                                        close_dialog('dvaie');
                                        close_dialog(); }
                                   });
                      }};
         open_dialog({contents_text: "${_("Vaie on esitamata, kas soovid vaide esitamise katkestada?")}",
                      buttons: btns});
         return false;
   });
</script>
% endif
