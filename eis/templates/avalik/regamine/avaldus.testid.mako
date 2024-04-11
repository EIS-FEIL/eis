<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'testivalik' %>
<%include file="avaldus.tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Eksamile registreerimise taotluse sisestamine")}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_('Registreerimine'), h.url('regamised'))} 
${h.crumb(_('Registreerimise taotluse sisestamine'))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'regamised' %>
</%def>

<%include file="avaldus.teade.mako"/>

% if c.opt_testiliigid:
<h1>${_("Vali test/eksam, kuhu soovid registreeruda")}</h1>

<div class="d-flex flex-wrap">
  <div class="col-md-4 col-lg-3">
    ${h.form_search()}
    % for r in c.opt_testiliigid:
    <div>
      ${h.radio('tliik', r[0], label=r[1], checkedif=c.testiliik)}
    </div>
    % endfor
    <script>
      $('input[name="tliik"]').change(function(){ this.form.submit(); });
    </script>
    ${h.end_form()}
  </div>
  % if c.testiliik:
  <div class="col-md-8 col-lg-9">
    ${h.form_save(None, h.url('regamine_avaldus_testid_testiliik', testiliik=c.testiliik))}
    ## tliik selleks, et vigade korral oleks vormil olemas
    ${h.hidden('tliik', c.testiliik)}
    ${self.testivalik()}
    ${h.end_form()}
  </div>
  % endif
</div>
% endif

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.btn_to(_('Tagasi'), h.url('regamised'), class_='leave-formpage',
    mdicls='mdi-arrow-left-circle', level=2)}
  </div>
  <div id="add" class="invisible">
    ${h.button(_('Jätka'), mdicls2='mdi-arrow-right-circle', id="jatka")}
  </div>
</div>

<div id="tyhistamine" class="d-none" aria-hidden="true">
  <div class="p-2 tyh1">
    ${_("Kas oled kindel, et soovid registreeringu tühistada?")}
  </div>
  <div class="p-2 tyh2">
    ${_("Korraga saab registreerida ainult ühele eksamile. Kas oled kindel, et soovid varasema registreeringu tühistada?")}
  </div>

  ${h.form_save(None, form_name="form_del")}
  <div class="form-group mb-3 div-pohjus">
    ${h.flb3(_("Põhjus"))}
    ${h.textarea('pohjus', '', rows=4, ronly=False)}
  </div>
  <div class="text-right">
    ${h.button(_("Ära tühista"), id="aratyhista")}
    ${h.button(_("Tühista registreering"), id="tyhista")}
  </div>
  ${h.end_form()}
</div>

<%include file="avaldus.katkestus.mako"/>


<%def name="testivalik()">
% if not c.items:
${_("Valitud testiliigiga teste, kuhu saaks registreeruda, praegu rohkem ei ole.")}
% else:

% if c.action == 'tyhista':
<div style="display:none" id="tyhhint">
${h.alert_info(_("Registreeringu tühistamiseks eemalda eksam valikust"), False)}
</div>
% endif
<div class="listdiv">
  <%
    c.opilane = c.kasutaja.opilane
  %>
  % for rcd, sooritaja in c.items:
  <div id="trtk_${rcd.id}">
    <%
       c.testimiskord = rcd
       c.sooritaja = sooritaja
    %>
    <%include file="avaldus.test.mako"/>
  </div>
  % endfor
</div>

<script>
  function toggle_add(){   
         var visible = ($('input:checked.valik_id').length > 0);
         $('#add').toggleClass('invisible', !visible);
         $('input.valik_id').each(function(ind, cb){
             var rcd_id = cb.value;
             $('.rowinput-'+rcd_id).toggle(cb.checked);
         });
  }
  ## regamise tyhistamise kinnituse aknas tyhistamisest loobumine
  function close_form_del(fld){
        ## paneme tagasi linnukese
        var tk_id = $('#form_del').data('value');
        $('input#valik_id_' + tk_id).prop('checked', true).addClass('is-checked');
        close_this_dialog(fld);
  }
  function del_reg(fld, mujalt){
        ## registreeringu tyhistamine - fld on valiku checkbox/radio
        if(($(fld).attr('type') == 'radio'))
        {
           if($(fld).hasClass('is-checked'))
            {
               ## valiku eemaldamine
               $(fld).removeClass('is-checked').prop('checked', false);
            }
           else
            {
               var old = $('input.valik_id.is-checked');
               if(old.length){
                   ## teine test oli juba varem valitud, suuname esmalt seda tyhistama
                   del_reg(old[0], true);
                   return false;
               }
               $(fld).addClass('is-checked');
            }
         }
        var  delurl = $(fld).attr('href');
        if(delurl && !fld.checked){
              ## regatud testimiskorra korral märke eemaldamisel tyhistada regamine
              $('#form_del').attr('action', delurl);
              $('#form_del').data('value', $(fld).val());
              var contents = $('div#tyhistamine');
              ## kui tullakse muu valiku tegemiselt, siis selgitatakse, et saab korraga yheainsa testi valida
              contents.find('.tyh1').toggle(!mujalt);
              ## kui klikiti kohe tyhistataval eksamil, siis on lyhem jutt
              contents.find('.tyh2').toggle(mujalt);
              ## kui regamine on juba kinnitatud, siis kysime ka põhjust
              $('div#tyhistamine .div-pohjus').toggle($(fld).hasClass('reg-kinnitatud'));
              open_dialog({'contents_html': contents.html(),
                           'title': $(fld).siblings('.custom-control-label').text(),
                           'onclose': close_form_del});
              return;
        }
        toggle_add();
  }
  $(function(){

     ## testi valimine/valiku eemaldamine
     $('body').on('click', 'input.valik_id', function(){
        del_reg(this);
     });
     ## valiku eemaldamisel kinnituse kysimise aknas tyhistamine
     $('body').on('click', '#tyhista', function(){
        var tk_id = $('#form_del').data('value');
        toggle_add();
        var target = $('#trtk_' + tk_id);
        submit_dlg(this, target, 'post', true);
        close_this_dialog(this);
     });
     ## valiku eemaldamisel kinnituse kysimise aknas loobumine
     $('body').on('click', '#aratyhista', function(){
        close_form_del(this);
     });

     $('#jatka').click(function(){
       $('#form_save').submit();
     });

     toggle_add();

     ## kui lehele tuldi tyhistamise nupuga ja on ainult 1 test, siis tyhistame selle
  % if c.action == 'tyhista':
     var valitud = $('input.valik_id:checked');
     if(valitud.length == 1) {
        valitud.click();
     } else {
        $('#tyhhint').show();
     }
  % endif
  });
</script>
% endif

</%def>
