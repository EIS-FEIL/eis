<%
  test = c.testiosa.test
  on_kirjalik = c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE)

  on_proctorio = c.toimumisaeg and c.toimumisaeg.on_proctorio
  if on_proctorio:
     q = (model.Session.query(model.Proctoriolog.id)
          .filter_by(toimumisaeg_id=c.toimumisaeg.id))
     if not q.first():
         on_proctorio = False
%>
% if on_proctorio:
${h.btn_to(_("Proctorio ülevaade"), h.url('proctorio_review', test_id=test.id, toimumisaeg_id=c.toimumisaeg.id, testiruum_id=c.testiruum.id), target="_blank", level=2, class_="mb-2")}
% endif

% if not c.items:
${h.alert_notice(_("Ühtki sooritajat pole määratud"), False)}

% else:
<%include file="sooritajad_list.mako"/>

<div>
% if c.can_update:
% if c.test.staatus == const.T_STAATUS_KINNITATUD:
  % if not c.veel_ei_toimu:
      % if on_kirjalik:
  ${h.button(_("Luba alustada"), class_=f'valikuline vst-{const.S_STAATUS_REGATUD}', id="luba")}
      % endif
      % if c.testiruum and c.testiruum.arvuti_reg and on_kirjalik:
${h.button(_("Unusta arvuti"), class_=f'valikuline vst-{const.S_STAATUS_POOLELI} vst-{const.S_STAATUS_KATKESTATUD}', id="unusta")}
      % endif
${h.button(_("Eemalda sooritamiselt"), class_='valikuline vst-all', id="eemalda")}
      % if on_kirjalik:
  ${h.button(_("Lõpeta test"), class_=f'valikuline vst-{const.S_STAATUS_REGATUD} vst-{const.S_STAATUS_ALUSTAMATA} vst-{const.S_STAATUS_POOLELI} vst-{const.S_STAATUS_KATKESTATUD}', id="lopeta")}
      % endif
      % if not c.toimumisaeg or c.toimumisaeg.jatk_voimalik:
${h.button(_("Ava lõpetatud test"), class_=f'valikuline vst-{const.S_STAATUS_TEHTUD} vst-{const.S_STAATUS_PUUDUS} vst-{const.S_STAATUS_EEMALDATUD} vst-{const.S_STAATUS_KATKESPROT}', id="ava")}
      % endif
  % endif
  % if c.toimumisaeg and c.toimumisaeg.keel_admin and (len(c.test.keeled) > 1):
    ${h.button(_("Muuda soorituskeel"), class_=f'valikuline vst-{const.S_STAATUS_ALUSTAMATA} vst-{const.S_STAATUS_REGATUD} vst-{const.S_STAATUS_POOLELI} vst-{const.S_STAATUS_KATKESTATUD}', id="muudakeel")}
  % endif
  % if on_kirjalik and (c.toimumisaeg or c.user.on_pedagoog or c.user.on_avalikadmin or c.user.on_koolipsyh):
${h.button(_("Testiparoolid"), class_='valikuline vst-all', id="testiparoolid")}
  % endif
% endif
% endif

% if c.test.staatus == const.T_STAATUS_KINNITATUD:
% if c.nimekiri and c.user.has_permission('omanimekirjad', const.BT_UPDATE, c.nimekiri):
  ${h.btn_to(_("Lisa sooritajad"), h.url('test_nimekiri',test_id=c.test_id, testiruum_id=c.testiruum_id, id=c.nimekiri.id),
  mdicls='mdi-plus')}
% endif
% if c.toimumisaeg and c.toimumisaeg.verif and not c.veel_ei_toimu and on_kirjalik:
  ${h.button(_("Luba sooritada isikut tõendamata"), class_='valikuline vrf-0', onclick="change_status(this, 'veriff1')")}
  ${h.button(_("Tühista luba sooritada isikut tõendamata"), class_='valikuline vrf-1', onclick="change_status(this, 'veriff0')")}  
% endif
% endif

% if c.toimumisaeg and c.toimumisaeg.prot_admin and not c.veel_ei_toimu:
<div class="float-right">
  <% protokollid = c.toimumisaeg.on_ruumiprotokoll and c.testiruum.toimumisprotokollid or c.testikoht.toimumisprotokollid %>
  % for tprot in protokollid:
  ${h.link_to(_("Testi toimumise protokoll") + " " + tprot.tahistus,
  h.url('protokoll_osalejad', toimumisprotokoll_id=tprot.id, testiruum_id=c.testiruum_id))}
  % endfor
</div>
% endif
% endif

</div>
<div id="msgdiv" class="m-2"></div>

% if c.toimumisaeg and c.toimumisaeg.keel_admin:
## keele muutmise dialoog
<div id="chlang" style="display:none">
  <div class="my-2 started-warn" style="display:none">
    ${h.alert_warning(_("Soorituskeele muutmisel kustutatakse juba tehtud ülesannete vastused ja need ülesanded tuleb uuesti teha!"), False)}
  </div>
  % for lang in c.toimumisaeg.testimiskord.keeled:
  <div>
    ${h.radio('lang', lang, label=model.Klrida.get_lang_nimi(lang))}
  </div>
  % endfor
</div>
% endif

<div id="chstat" style="display:none">
  <% 
    if c.nimekiri:
       url = h.url('testid_labiviimine', test_id=c.test_id, id=c.testiruum.id, sub='tos2st')
    else:
       url = h.url('klabiviimine_toimumisaeg', id=c.testiruum.id, sub='tos2st')
  %>
  ${h.form(url, id="fchstat")}
  ${h.flb(_("Põhjus"), "stpohjus")}
  ${h.text('stpohjus', '', maxlength=100)}
  ${h.end_form()}
  <div class="d-flex pt-2">
    <div class="flex-grow-1">
      ${h.button(_("Katkesta"), class_="bcancel", level=2)}
    </div>
    ${h.button(_("Salvesta"), class_="bsave")}
  </div>
</div>

% if c.items:
<script>
function show_status(data)
{
  ## jätame meelde elemendi, millel on fookus
  var focus = $(':focus');
  var scroll = $(window).scrollTop();
  var contents = $(data);

  ## tõstame teated nähtavale 
  $('#msgdiv').html(contents.find('.refr-msg'));

  $('.listdiv #arvutid_tbl').replaceWith(contents.find('#arvutid_tbl'));
  var cpto = $('.listdiv #sooritajad_tbl>tbody');
  contents.find('#sooritajad_tbl>tbody>tr').each(function(){
      var id = $(this).prop('id');
      var tr = cpto.find('tr#' + id);
      if(tr.length > 0){
          if(tr.find('input.sooritus').prop('checked'))
             $(this).find('input.sooritus').prop('checked', true);
          tr.replaceWith($(this));
      } else {
          cpto.append($(this));
      }
  });
  block_is_ready();
  toggle_valikuline();
  timeout_status();
  $(window).scrollTop(scroll);                                       
  ## taastame fookuse
  if(focus.length) focus.focus();
}

function change_status(btn, status)
{
  var data = $('input.sooritus').serialize();
  if(!data)
  {
     alert_dialog("${_("Vali sooritajad")}");
     return;
  }
  data += '&_method=put&staatus=' + status+'&r='+Math.random();
  var url = $('form#fchstat').prop('action');
  var f_ok = function(){
      set_spinner_dlg($('.modal-footer'));
      $('.modal-footer button').prop('disabled', true);
      $.ajax({url:url,
              data: data,
              type: 'post',
              success: function(data){
                 close_confirm_dialog(); show_status(data);
              }
            });
  };
  confirm_dialog('${_("Kas oled kindel?")}', f_ok);
}

function change_status_pohjus(btn, status)
{
  if($('input.sooritus:checked').length == 0)
  {
     alert_dialog("${_("Vali sooritajad")}");
     return;
  }
  var frm = $('div#chstat');
  frm.find('input[name="staatus"]').val(status);
  frm.find('#stpohjus').val('');
  frm.find('button.bsave').hide();
  open_dialog({'title': $(btn).text(),
               'contents_elem': frm,
               'dialog_id': 'chstat_dlg'
               });

  var change_status_ok = function(){
   set_spinner_dlg($('.modal-footer'));
   $('.modal-footer button').prop('disabled', true);
      var url = $('form#fchstat').prop('action');
      var data = $('input.sooritus').serialize() + '&staatus=' + status + '&' + $('form#fchstat').serialize();
      $.ajax({url:url,
              data: data,
              type: 'post',
              success: function(data){
                 close_dialog('chstat_dlg'); show_status(data);
              }
            });
  }

  $('#chstat button.bsave').click(change_status_ok);
  $('#chstat button.bcancel').click(function(){ close_dialog('chstat_dlg'); });
  ## staatuse salvestamise nupp nähtav ainult siis, kui põhjus sisestatud
  $('#chstat #stpohjus').keyup(function(){ $('#chstat .bsave').toggle($(this).val().trim() != ''); });
}

function timeout_status()
{
% if c.is_devel:
  return;
% else:
  var timer = setTimeout("refresh_status()", 20000);
% endif
  ## peale dialoogiaknast naasmist võib tekkida mitu taimerit
  for(var i=0;i<timer; i++) clearTimeout(i);
}
function refresh_status()
{
  % if c.nimekiri:
  var url="${h.url('testid_labiviimine', test_id=c.test_id, id=c.testiruum.id, sub='refr', partial=True)}";
  % else:
  var url="${h.url('klabiviimine_toimumisaeg', id=c.testiruum.id, sub='refr', partial=True)}";
  % endif
  ## IE puhverdamisest hoidumiseks
  url += "&r=" + Math.random();
  $.ajax({url:url,
          success: show_status,
          error: function(response){
             if((response.status != 401) && (response.status != 403))
                 ## kui ei ole õiguse puudumise viga (nt kasutaja logis välja)
                 timeout_status();
          }
  });        
}

function gen_pwd()
{
  var data = 'sub=parool';
  $.each($('input.sooritus:checked'), function(n, elem){
      data += '&sooritus_id=' + elem.value;
  });
  open_dialog({'title': "${_("Testiparoolid")}", 'url': "${h.url_current('edit')}", 'method': 'get', 'params': data});
}      
function change_lang()
{
  var data = $('input.sooritus').serialize();
  if(!data)
  {
     alert_dialog("${_("Vali sooritajad")}");
     return;
  }
  % if c.nimekiri:
  var url="${h.url('testid_labiviimine', test_id=c.test_id, id=c.testiruum.id, sub='chlang')}";
  % else:
  var url="${h.url('klabiviimine_toimumisaeg', id=c.testiruum.id, sub='chlang')}";
  % endif
  var f_ok = function(){
      var lang = $('#chlang input[name="lang"]:checked').val();
      if(!lang)
      {
          alert_dialog("${_("Vali keel!")}");
          return;
      }
      data += '&lang=' + lang+'&r='+Math.random();
      set_spinner_dlg($('.modal-footer'));
      $('.modal-footer button').prop('disabled', true);
      $.ajax({url:url,
              data: data,
              type: 'post',
              success: function(data){
                 close_dialog('chlang_dlg'); show_status(data);
              }});
  }
  var any_started = $('tr[data-vst="${const.S_STAATUS_POOLELI}"],tr[data-vst="${const.S_STAATUS_KATKESTATUD}"]')
    .find('input.sooritus:checked').length > 0;
  $('div#chlang .started-warn').toggle(any_started);
    
  var buttons = {'Salvesta': f_ok};                     
  open_dialog({'title': "${_("Muuda soorituskeel")}",
               'contents_elem': $('div#chlang'),
               'dialog_id': 'chlang_dlg',
               'buttons': buttons});
}
function toggle_valikuline()
{
  var flds = $('input.sooritus:checked');
  $('.valikuline').hide();                     
  if(flds.length > 0)
  {
      var clist = '.vst-all';
      for(var i=0; i<flds.length; i++)
      {
          var tr = flds.eq(i).closest('tr');
          var cls = '.vst-' + tr.attr('data-vst');
          if(clist.indexOf(cls) == -1)
             clist = clist + ',' + cls;
          cls = '.vrf-' + tr.attr('data-vrf');
          if(clist.indexOf(cls) == -1)
             clist = clist + ',' + cls;
      }
      $('.valikuline').filter(clist).show();
  }
}
$(function(){
% if on_kirjalik and not c.veel_ei_toimu:
  timeout_status();
% endif
  $('body').on('click', '#alls', function(){                                  
     $('input.sooritus').prop('checked', $(this).prop('checked'));
     toggle_valikuline();
  });
  $('body').on('click', 'input.sooritus', toggle_valikuline);
  toggle_valikuline();

  ## nupud
  $('button#luba').click(function(){ change_status(this, '${const.S_STAATUS_ALUSTAMATA}');});
  $('button#unusta').click(function(){ change_status(this, 'arvutita');});
  $('button#eemalda').click(function(){ change_status_pohjus(this, '${const.S_STAATUS_EEMALDATUD}');});
  $('button#lopeta').click(function(){ change_status(this, '${const.S_STAATUS_TEHTUD}');});
  $('button#ava').click(function(){ change_status(this, 'ava');});
  $('button#muudakeel').click(function(){ change_lang(); });
  $('button#testiparoolid').click(function(){ gen_pwd(); });
});
</script>
% endif
