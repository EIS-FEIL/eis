## kui on registreeritud mõnele rahvusvahelisele eksamile,
## siis on kohustuslik sisestada: aadress, postiindeks,
## telefon, e-post, eksamiteade saata;
## TE/SE on kohustuslik aadress või epost.
<%
  on_rv = c.testiliik in (const.TESTILIIK_RV, const.TESTILIIK_RIIGIEKSAM) and \
     (len([r for r in c.sooritajad if r.test.testiliik_kood == const.TESTILIIK_RV]) > 0)
  on_ts = c.testiliik in (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS)
%>
% if on_ts:
${h.rqexp(text=_("Tärniga * märgitud väljad on kohustuslikud. Kui e-posti aadressi pole, siis seda ei pea sisestama, aga peab sisestama aadressi ja postiindeksi."))}
% else:
${h.rqexp()}
% endif
<div class="form-wrapper mb-3">
  <div class="form-group row">
    ${h.flb3(_("Isikukood ja nimi"))}
    <div class="col-md-9">
      <div class="d-flex flex-wrap">
        <div class="flex-grow-1">
          ${c.kasutaja.isikukood}
          ${c.kasutaja.eesnimi}
          ${c.kasutaja.perenimi}
        </div>
        % if c.kasutaja.isikukood and request.is_ext() and c.submit_rr:
        ${h.submit(_('Päri andmed Rahvastikuregistrist'), id='rr', level=2)}
        % endif
      </div>
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("Aadress"),'aadress_id', rq=on_rv)}
    <div class="col-md-9">
      <%
         c.aadress = c.kasutaja.aadress
         c.aadress_obj = c.kasutaja
      %>
      <%include file="/admin/aadressivalik.mako"/>
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("Postiindeks"),'k_postiindeks', rq=on_rv)}
    <div class="col-md-9">
      ${h.posint('k_postiindeks', c.kasutaja.postiindeks)}
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("Telefon"),'k_telefon', rq=on_rv)}
    <div class="col-md-9">
      ${h.text('k_telefon', c.kasutaja.telefon)}
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("E-post"),'k_epost', rq=True)}
    <div class="col-md-9">
      ${h.text('k_epost', c.kasutaja.epost)}
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("Korda e-posti aadressi"),'epost2', rq=True)}
    <div class="col-md-9">
      ${h.text('epost2', c.kasutaja.epost)}
    </div>
  </div>

% if c.testiliik == const.TESTILIIK_TASE:
  <%
    sooritaja = len(c.sooritajad) and c.sooritajad[0]
  %>
  <div class="form-group row">  
    ${h.flb3(_("Töövaldkond"),'kk_tvaldkond_kood', rq=True)}
    <div class="col-md-3">
      ${h.select('kk_tvaldkond_kood', sooritaja and sooritaja.tvaldkond_kood, 
      c.opt.klread_kood('TVALDKOND', vaikimisi=sooritaja and sooritaja.tvaldkond_kood), 
      empty=True)}
      <script>
        function change_tvaldkond()
        {
          $('.tvaldkond-muu').toggle($('select#kk_tvaldkond_kood').val() == '${const.TVALDKOND_MUU}');
        }
        $(function(){
          change_tvaldkond();
          $('select#kk_tvaldkond_kood').change(change_tvaldkond);
        });
      </script>
    </div>
    <div class="col-md-3 text-right tvaldkond-muu">
      ${h.flb(_("täpsusta:"), 'kk_tvaldkond_muu', rq=True)}
    </div>
    <div class="col-md-3 tvaldkond-muu">
      ${h.text('kk_tvaldkond_muu', sooritaja and sooritaja.tvaldkond_muu, class_='tvaldkond-muu')}
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("Amet"),'kk_amet_muu', rq=True)}
    <div class="col-md-9">
      ${h.text('kk_amet_muu', sooritaja and sooritaja.amet_muu, class_='amet-muu', maxlength=100, pattern='[a-zA-ZõäöüšžÕÄÖÜŠŽ ]*', data_pattern_desc=_("Sisesta korrektne ametinimetus"))}
      ## lubatud on ainult tähed ja tühikud
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("Haridus"),'kk_haridus_kood', rq=True)}
    <div class="col-md-9">
      ${h.select('kk_haridus_kood', sooritaja and sooritaja.haridus_kood, 
      c.opt.klread_kood('HARIDUS', vaikimisi=sooritaja and sooritaja.haridus_kood), 
      empty=True)}
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("Õppisin eesti keelt (valikuid võib olla rohkem kui üks)"), 'te_oppek', rq=True)}
    <div class="col-md-9" id="te_oppek">
      <%include file="/ekk/regamine/te_oppekohtet.mako"/>
    </div>
  </div>
% endif
</div>

% if on_ts:
${h.hidden('epostpuudub','')}
<script>
  $(function(){
  $('form#form_save').on('submit', function(event){
  if(($('#k_epost').val().trim()=='')&&($('#epostpuudub').val()=='')){
     event.preventDefault();
     confirm_dialog("${_("Kas sul on e-posti aadress?")}",
         function(){ close_confirm_dialog(); $('#k_epost').focus();},
         null,
         function(){ close_confirm_dialog(); $('#epostpuudub').val('1'); $('form#form_save').submit();});
  }
  });
  });
</script>
% endif
