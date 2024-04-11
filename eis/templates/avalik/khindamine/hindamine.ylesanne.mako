${h.not_top()}
<%namespace name="tab" file='/common/tab.mako'/>
<div class="testinst">
  <div id="ylesandehindamine_div" class="mb-3">
    ${self.ylesanded()}
    <div style="display:none">
      <div id="status_table">${self.status_table()}</div>
    </div>
    <script>
      ## liigutame staatuse tabeli oma kohale, see on väljastpool ylesande divi
      $('#status_table_pos').html('').append($('#status_table'));
      $('#status_table select#n1_sooritus_id').change(function(){
      savehkty('tos_'+$(this).val(), 'post');
      });
    </script>
  </div>
  
  % if c.on_kriteeriumid and not c.ainult_yl_vahetub:
  <% c.ty = None %>
  ${self.ty_form()}
  % endif
</div>

<%def name="ylesanded()">   

% if c.ty:
## sakid laia akna korral
<ul class="nav nav-tabs d-md-flex flex-wrap" id="h_navacc0" role="tablist">
  <% c.tabs_mode = 'li' %>
  ${self.h_draw_tabs()}
</ul>

## sakid esimesest kuni jooksva sakini kitsa akna korral
<div class="accordion d-block d-md-none" id="h_navacc1">
  <% c.tabs_mode, c.tabs_current1 = 'accordion1', None %>
  ${self.h_draw_tabs()}
</div>

## valitud saki sisu
<div class="tab-content collapse show" id="h_main_tab_content">
  <div class="tab-pane fade show active" role="tabpanel">
    ${self.ty_form()}
  </div>
</div>

## jooksvale sakile järgnevad sakid kitsa akna korral
<div class="accordion d-block d-md-none" id="h_navacc2">
  <% c.tabs_mode, c.tabs_current2 = 'accordion2', None %>
  ${self.h_draw_tabs()}
</div>
% else:
    ${self.ty_form()}
% endif
<div class="no-initialfocus"></div>
</%def>

<%def name="h_draw_tabs()">
<% c.h_tab = 'ty_%s' % c.ty.id %>
% for ty_id in c.testiylesanded_id:
   <%
     ty = model.Testiylesanne.get(ty_id)
     url = c.f_submit_url(ty_id)
   %>
   ${tab.draw('ty_%s' % ty_id, url, ty.tahis, c.h_tab)}
% endfor
</%def>

<%def name="ty_form()">
<% 
  c.counter = -1
  c.submit_url = c.get_url = None
  if c.ty and c.on_kriteeriumid:
    # hindamiskogumis teise ylesande ettevõtmine ilma salvestamiseta
    c.get_url = c.f_submit_url(None)
  else:
    # ylesande hindamine
    c.submit_url = c.f_submit_url(c.ty and c.ty.id)
%>
<%include file="/common/message.mako"/>
% if c.submit_url:
${h.form(url=c.submit_url, id="form_save_h", multipart=True, method='post', autocomplete='off')}
% elif c.get_url:
${h.form(url=c.get_url, id="form_ty", method='get', autocomplete='off')}
% endif
${h.hidden('partial', '1')}
${h.hidden('ylesanne_id', c.ylesanne and c.ylesanne.id or '')}
${h.hidden('n_sooritus_id', c.sooritus.id)}
${h.hidden('lst', c.lst)}
% if c.hindamine:
## salvestamisel kopeerida väärtus päise märkeruutudest
${h.hidden('ksm_naeb_hindaja', c.hindamine.ksm_naeb_hindaja and 1 or '')}
${h.hidden('ksm_naeb_sooritaja', c.hindamine.ksm_naeb_sooritaja and 1 or '')}
% endif
% if not c.komplekt and c.toimumisaeg:
  % if c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I):
  ${h.alert_error(_("Testi pole sooritatud"), False)}
  % else:
  ${h.alert_info(_("Palun vali ülesandekomplekt"), False)}
  % endif
% elif c.pole_hinnata:
  ${h.alert_notice(_("Pole midagi hinnata"))}
% elif c.ty:
   ${self.testiylesandesisu()}
% else:
   ${self.tbl_hindamine_kriteeriumid()}     
% endif
% if not (c.on_kriteeriumid and c.ty) and not c.pole_hinnata and c.hindamine and c.hindamiskogum:
   ## hindamiskogumiga hindamise korral

  ${self.probleem()}
% endif
   ${self.footer_buttons()}
% if not (c.on_kriteeriumid and c.ty):
${self.js_punktid()}
% endif
${h.hidden('lykkamispohjus', '')}
${h.end_form()}
</%def>

<%def name="testiylesandesisu()">
<%include file="testiylesandesisu.mako"/>
% if c.ylesandevastus:
${self.audio_play_all()}
% endif

${self.ty_valuation(c.ty, c.ylesandevastus)}

</%def>

<%def name="ty_valuation(ty, ylesandevastus)">
      <%
        # lahendaja vastus hindamise tabelis kuvamiseks
        if ylesandevastus:
            c.responses = ylesandevastus.get_responses()
        else:
            c.responses = {}
        # kui kasutaja on hindaja, siis leitakse õiged vastused
        c.correct_responses = c.ylesanne.correct_responses(ylesandevastus,
                                                       lang=c.lang,
                                                       naide_only=False,
                                                       hindaja=True,
                                                       naidistega=False)
      %>
        ## hindamiste tabel hindajale ning osade sisuplokkide korral ka õiged vastused või näidisvastused
        % for c.block in c.ylesanne.sisuplokid:      
          % if c.block.staatus != const.B_STAATUS_KEHTETU and not c.block.naide and c.block.is_interaction:
            ## plokk on nähtav, pole näidis ja on vastatav
            <%include file="/sisuplokk/valuation.mako"/>
          % endif
        % endfor
</%def>

<%def name="audio_play_all()">
<%
  # ES-977
  # kas on audio sisuplokke?
  #yv_id_list = [syl.svalik.valitudylesanne.id for syl in c.sooritusylesanded if syl.svalik]
  q = (model.SessionR.query(model.sa.func.count(model.Kvsisu.id))
       .join(model.Kvsisu.kysimusevastus)
       .filter(model.Kysimusevastus.ylesandevastus_id==c.ylesandevastus.id)
       .join((model.Kysimus, model.Kysimus.id==model.Kysimusevastus.kysimus_id))
       .join(model.Kysimus.sisuplokk)
       .filter(model.Sisuplokk.tyyp==const.INTER_AUDIO))
  audio_cnt = q.scalar()
%>
% if audio_cnt > 1:
  ${h.checkbox('all_audio', 1, label=_("Mängi kõik helivastused järjest"), onclick="audio_play_all()")}

<script>
  function audio_play_all()
  {
  var audios = $('iframe.hylesanne').contents().find('.spt-audioInteraction audio');
  audios.off('ended');
  if($('input[name="all_audio"]').prop('checked'))
  {
    for(var i=0; i<audios.length-1; i++){
      $(audios[i]).on('ended', function(){
         audios[audios.index(this)+1].play();
      });                            
    }
    audios[0].play();
   }
  }
</script>
% endif
</%def>

<%def name="tbl_hindamine_kriteeriumid()">
## Hindamiskriteeriumitega hindamiskogumi pallide tabel
<%
  #prefix = 'hkr.'
  kriteeriumid = list(c.hindamiskogum.hindamiskriteeriumid)
  a_max_pallid = sum([kr.max_pallid for kr in kriteeriumid])
  hide_kirj = len(kriteeriumid) > 1
%>
   <table width="100%"  class="table vertmar table-align-top">
     <caption>${_("Hindamiskogumi hindamine hindamiskriteeriumite kaupa")}</caption>
     <thead>
     <tr>
       <th>${_("Aspekt")}</th>
       <th>${_("Toorpunktid")}</th>
       <th nowrap>${_("Max")}</th>
       <th>${_("Kaal")}</th>
       % if c.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP) or c.test.aine_kood in c.opt.nullipained:
       <th nowrap>${_("Null punkti põhjus")}</th>
       % endif
       % if c.hindamiskogum.on_markus_sooritajale:
       <th width="70%">${_("Märkus sooritajale")}</th>
       % endif
     </tr>
     </thead>
     % for n_ha, ha in enumerate(kriteeriumid):
         <% 
           krithinne = c.hindamine.get_kriteeriumihinne(ha.id) or None
           a_prefix = 'kr-%d' % (n_ha)
           apunktid = krithinne and krithinne.toorpunktid or None
           kritkirjeldused = list(ha.kritkirjeldused)
         %>
     <tbody class="accordion">
     <tr class="tr-asp accordion-card" id="tr_asp_${ha.id}">
       <td>
         % if kritkirjeldused and hide_kirj:
         <div class="accordion-title">
           <button
             class="btn btn-link collapsed"
             type="button"
             data-toggle="collapse"
             data-target=".tr-pkirj-${ha.id}"
             aria-expanded="true"
             aria-controls=".tr-pkirj-${ha.id}">
             <span class="btn-label"><i class="mdi mdi-chevron-down"></i>
               ${ha.aspekt_nimi}
             </span>
           </button>
         </div>
         % else:
         ${ha.aspekt_nimi}
         % endif
       </td>
       <td>
         ${h.float5('%s.toorpunktid' % a_prefix, krithinne and  krithinne.s_toorpunktid, 
         maxvalue=ha.max_pallid, class_='val-tp asp-punktid')}
         ${h.hidden('%s.a_kood' % a_prefix, ha.aspekt_kood)}
       </td>
       <td>${h.fstr(ha.max_pallid)}</td>
       <td class="val-kaal">${h.fstr(ha.kaal)}</td>
       % if c.testiosa.vastvorm_kood == const.VASTVORM_KP or c.test.aine_kood in c.opt.nullipained:
       <td>
         <%
           bit = c.testiosa.vastvorm_kood == const.VASTVORM_KP and const.NULLIP_BIT_P or const.NULLIP_BIT_E
           defval = krithinne and krithinne.nullipohj_kood
           opt_nullipohj = c.opt.klread_kood('NULLIPOHJ', empty=True, vaikimisi=defval, bit=bit)
         %>
         ${h.select('%s.nullipohj_kood' % a_prefix, 
         krithinne and krithinne.nullipohj_kood, 
         opt_nullipohj,
         wide=False,
         disabled=not krithinne or not krithinne.toorpunktid==0)}
       </td>
       % endif
       % if c.hindamiskogum.on_markus_sooritajale:       
       <td>
         ${h.textarea('%s.markus' % a_prefix, krithinne and krithinne.markus, rows=2, class_='asp-markus')}
       </td>
       % endif
     </tr>
     <%
       if ha.pkirj_sooritajale:
          cbcls = 'asp-pkirj asp-pkirj-j'
       else:
          cbcls = 'asp-pkirj'
     %>    
     % for pk in kritkirjeldused:
     <tr class="tr-pkirj tr-pkirj-${ha.id} ${hide_kirj and 'collapse' or ''}" aria-labelledby="tr_asp_${ha.id}">
       <td class="pl-6">
         <% label = h.fstr(pk.punktid) + 'p' %>
         ${h.radio('%s.pkp' % a_prefix, h.fstr(pk.punktid), class_=cbcls,
         checked=pk.punktid == apunktid, label=label)}
       </td>
       <td colspan="4">
         % if pk.kirjeldus:
         <div class="pkirj-txt">${pk.kirjeldus.replace('\n', '<br/>')}</div>
         % endif
       </td>
     </tr>
     % endfor
     </tbody>
     % endfor
   </table>
</%def>

<%def name="js_punktid()">
      <script>
var wnd_yl = null;
function popup_yl(url)
{
    wnd_yl = window.open(url, "wnd_yl", "directories=0,toolbar=0,location=0,status=0,menubar=0,scrollbars=1");
}
## aspekti punktide järgi leitakse punktide kirjeldus ja kopeeritakse märkuste lahtrisse
function copy_asp_punktikirjeldus(fld)
{
  var markus = fld.closest('tr').find('textarea.asp-markus');
  var punktid = parseFloat(fld.val().replace(',','.')) || 0;
  var spunktid = String(punktid).replace('.',',');
  var radio = fld.closest('tbody').find('.asp-pkirj').filter(function(){
        return this.value == spunktid;
  });
 radio.prop('checked', true);
 if(radio.hasClass('asp-pkirj-j'))
     {
        var kirj = radio.closest('.tr-pkirj').find('.pkirj-txt').text();
        markus.val(kirj);
        markus.prop('readonly', true);
     }
  else
     {
        markus.prop('readonly', false);
     }
}

$(function(){
var set_nullipohj = function()
{
    var nullipohj = $(this).closest('tr').find('select[name$=nullipohj_kood]');
    if(nullipohj.length){
       var is_zero = $(this).val() == '0';
       nullipohj.attr('disabled', !is_zero);
       if(is_zero) nullipohj.focus(); else nullipohj.val('');
    }
};
$('input[name$="toorpunktid"]').change(set_nullipohj).keyup(set_nullipohj);

$('input.val-tp').change(function(){
  ## antud toorpunktide jooksev kokkuliitmine
  var y_div = $('div.div_ty');
  var total=0;
  var flds_parent = y_div.find('input.val-tp,span.val-tp');
  var flds_iframe = y_div.find('iframe.hylesanne').contents().find('input.val-tp,span.val-tp');
  $.merge(flds_parent, flds_iframe).each(function(){
     var v = ($(this).is('input') ? $(this).val() : $(this).text());
     if((v != '') && !isNaN(v))
     {
        var punktid = Number(v.replace(',','.'));
        var fld_kaal = $(this).closest('tr').find('td.val-kaal');
        if(fld_kaal.length) {
            var kaal = Number(fld_kaal.text().replace(',','.'));
            total += punktid * kaal;
        } else {
            total += punktid; 
        }
     }
  });
  if(total < 0) total = 0;
  y_div.find('.val-total-tp').text(fstr(total));
  var koefitsient=Number(y_div.find('.val-koef').text().replace(',','.'));
  y_div.find('.val-total-p').text(fstr(total*koefitsient));
});


## aspektipunktide muutmisel kopeerida aspekti punktide kirjeldus märkuse lahtrisse
  $('input.asp-punktid').change(function(){ copy_asp_punktikirjeldus($(this)); })
  .each(function(){ copy_asp_punktikirjeldus($(this)); });
## punktikirjelduse valiku korral kopeerida punktid ja vajadusel kirjeldus 
  $('input.asp-pkirj').change(function(){
     var tr = $(this).closest('tbody').find('.tr-asp');
     tr.find('input.asp-punktid').val(this.value).change();
  });
             
  ## tõstame hinnete plokid väljastpoolt iframe sisse kysimuse vastuse juurde
  copy_valuation_to_iframe($('iframe.hylesanne'));

});
      </script>
</%def>

<%def name="probleem()">
<div class="p-2">
  ${h.checkbox1('on_probleem', 1, checked=c.hindamine.on_probleem, label=_("Probleem"))}
  <span class="onprob">
  ${h.text('probleem_varv', c.hindamine.probleem_varv or '#fff',
  style="display:none", class_='prob-spectrum')}
  </span>
  <div style="display:none" class="onprob">
    ${h.textarea('probleem_sisu', c.hindamine.probleem_sisu)}
  </div>
   <script>
     var setprobl = function(){
        var checked = $('#on_probleem').prop('checked');
        $('.onprob').toggle(checked);
        var c = $('#probleem_varv').val();
        c = ((!checked || c == '#fff') ? 'initial' : c);
        $('#hindamine_hk_div .tab-pane').css('background-color', c);
     }
     $('input#on_probleem').click(setprobl);
     setprobl();
      
     $("input.prob-spectrum").spectrum({
      preferredFormat: "hex",
      showPalette: true,
      showPaletteOnly: true,
      ##showInput: true,
      hideAfterPaletteSelect: true,
      allowEmpty: true,
      palette: [
        ["#fff","#f6e3c7","#fafacf","#ccf2cc","#d3fcfc","#dee5fa","#fae9fa","#fce1e1"],
        ["#f4cccc","#fce5cd","#fff2cc","#d9ead3","#d0e0e3","#cfe2f3","#d9d2e9","#ead1dc"],
        ["#ea9999","#f9cb9c","#ffe599","#b6d7a8","#a2c4c9","#9fc5e8","#b4a7d6","#d5a6bd"],
        ["#e06666","#f6b26b","#ffd966","#93c47d","#76a5af","#6fa8dc","#8e7cc3","#c27ba0"],
    ]
      }).change(setprobl);
   </script>
</div>
</%def>

<%def name="footer_buttons()">
<div class="m-2 d-flex flex-wrap">
<%
  disabled = not c.hindaja
  prev_ty_id = next_ty_id = prev_url = next_url = None
  found = False
  if c.ty:
     for ty_id in c.testiylesanded_id:
       if found:
          next_ty_id = ty_id
          break
       elif ty_id == c.ty.id:
          found = True
       else:
          prev_ty_id = ty_id
%>
  <div class="flex-grow-1">
  % if c.toimumisaeg and not (c.on_kriteeriumid and c.ty) and c.testiylesanded_id:
    ${h.button(_("Lükkan hindamise tagasi"), id='lykka', disabled=disabled, level=2)}
   <div id="lykka_dlg" style="display:none">
     <p>${_("Kas oled kindel, et ei soovi seda tööd hinnata? Kui jah, siis palun kirjuta põhjus.")}</p>
     <p>
       ${h.textarea('d_lykkamispohjus', '', rows=6)}
     </p>
     ${h.button(_("Jätkan töö hindamist"), id='eilykka')}
     ${h.button(_("Lükkan hindamise tagasi"), id='jahlykka', style="display:none")}
   </div>
  % endif
  </div>

  % if prev_ty_id:
  <div>
    ${h.button(_("Eelmine ülesanne"), id=f'prev_{prev_ty_id}', class_='prevty', mdicls='mdi-arrow-left-circle')}
  </div>
  % endif
  % if not (c.on_kriteeriumid and c.ty) and c.testiylesanded_id:
  <div>
    ${h.button(_("Salvesta"), id='peata', class_='hbsave')}
  </div>
  % endif
  % if next_ty_id:
  <div>
    ${h.button(_("Järgmine ülesanne"), id=f'next_{next_ty_id}', class_='nextty', mdicls2='mdi-arrow-right-circle')}
  </div>
  % elif not (c.on_kriteeriumid and c.ty):
  % if c.testiosa.vastvorm_kood == const.VASTVORM_KP or c.is_next:
  ${self.next_tahis()}  
  <div>
    ${h.button(_("Järgmine töö"), id='jargminetoo', class_='nexth', mdicls2='mdi-arrow-right-circle', disabled=disabled)}
  </div>
  % endif
  % endif
</div>
<script>
  function savehkty(op, method){
    var container = $('#hindamine_hk_div');
    var form = $('form#form_save_h');
    var iframe = $('iframe.hylesanne');
    copy_valuation_from_iframe(iframe,form);
  
    form.find('#lykkamispohjus').val($('#d_lykkamispohjus').val());
    ## ksm vaatamise lubade kopeerimine päisest
    form.find('input[type="hidden"][name="ksm_naeb_hindaja"]')
      .val($('.ksm-naeb input[name="ksm_naeb_hindaja"]').prop('checked') ? '1' : '');
    form.find('input[type="hidden"][name="ksm_naeb_sooritaja"]')
      .val($('.ksm-naeb input[name="ksm_naeb_sooritaja"]').prop('checked') ? '1' : '');
    var data = form.serialize() + '&op=' + op;
    dialog_load(form.attr('action'), data, method, container);
  }
  % if not c.omahindamine and not (c.on_kriteeriumid and c.ty):
  ## tagasilykkamine
  $('button#lykka').click(function(){
    var elem = $('#lykka_dlg');
    open_dialog({contents_elem: elem});
    $('#d_lykkamispohjus').keyup(function(){
       $('#jahlykka').toggle($(this).val().trim() != '');
    });
    $('#eilykka').click(function(){
       close_this_dialog(this);
    });
    $('#jahlykka').click(function(){
       if(!is_dblclick($(this)))
          savehkty('lykka','post');
    });
  });
  % endif
  % if not c.on_kriteeriumid and c.hindamine:
  ## ei ole kriteeriumitega hindamiskogum ja toimub hindamine
  var hbtns = $('button.nextty,button.prevty,button.hbsave,button.nexth');
  % elif not c.ty and c.hindamine:
  ## kriteeriumite salvestamine
  var hbtns = $('button.hbsave,button.nexth');
  % else:
  ## ylesande vahetamine
  var hbtns = $('button.nextty,button.prevty');
  % endif

  hbtns.click(function(){
    if(!is_dblclick(hbtns))
    {
      savehkty(this.id, 'post');
    }
  });

  % if c.ty:
  $('#h_navacc0 a.nav-link,#h_navacc1 a.nav-link').click(function(){
     ## kasutaja klikkis sakil
   % if c.on_kriteeriumid or not c.hindamine:
     ### siin ei salvestata (salvestatakse mujal kriteeriume või on ekspertvaatamine)
     var container = $('#hindamine_hk_div');
     var form = $('form#form_ty');
     var data = form.serialize() + '&op=' + this.id;
     dialog_load(form.attr('action'), data, 'get', container);
   % else:
     ## hindamise salvestamine
     savehkty(this.id, 'post');
   % endif
      return false;
  });
  % endif
  % if not c.pole_hinnata:
  ${self.js_update_r_tabs()}
  % endif
  $(function(){
     hkh_resize();
     ## kõrguse kontroll veidi hiljem, kui ckeditor jm on laaditud
     setTimeout(hkh_resize, 4000);
   });
</script>
</%def>

<%def name="js_update_r_tabs()">
## kui vormi vasakul poolel ylesanne muutus,
## siis muuta parema poole sisu
<%
  yid = c.ylesanne and c.ylesanne.id or ''
%>
$(function(){
  ## kui ylesanne muutus, siis muuta lehe parem pool
  var r_div = $('#hindamine_r_div'),
      r_div_tabs = r_div.find('.hindamine_r_tabs'),
      prev_yid = r_div_tabs.attr('data-yid');
  if(r_div_tabs.length == 0 || prev_yid != "${yid}" ) {
     var l=[${','.join([f"['{tabname}','{url}']" for tabname, url, label in c.r_tabs_data])}];
     ## aktiivne sakk või selle puudumisel esimene sakk laaditakse uuesti
     var tab_active = r_div_tabs.find('.nav-link.active').attr('id'), url = null;
     for(var n=0; n<l.length; n++){
        url = l[n][1];
        if(!tab_active || l[n][0] == tab_active.substr(4)) 
          break;
     }
     if(url){
        ## urli ja c.r_tabs_data ei ole siis, kui testi pole sooritatud
       data = 'sooritus_id=' + $('input#n_sooritus_id').val();
       dialog_load(url, data, 'GET', r_div);
     }
  }
});
</%def>


<%def name="next_tahis()">
## kasutatakse hindamisel järgmise töö valimise vormi jaoks
% if c.testiosa.vastvorm_kood == const.VASTVORM_KP and not c.omahindamine:
<%
  sisestuskogum = c.hindamiskogum.sisestuskogum
  on_skannimine = sisestuskogum and sisestuskogum.on_skannimine
%>
% if not on_skannimine:

<div class="d-flex flex-wrap">
  % if c.toimumisaeg.testimiskord.sisestus_isikukoodiga:
  <div class="item ml-4 mr-1 text-nowrap">
    ${h.flb(_("Järgmine isikukood"),'isikukood')}
    ${h.text('isikukood', c.isikukood, class_=c.focus and 'initialfocus' or None)}
    <% if c.focus: c.focus = None %>
  </div>
  % endif
  <div class="item ml-4 mr-1 text-nowrap">
    ${h.flb(_("Järgmise töö tähis"), 'tahised')}
    ${h.text('tahised', c.tahised, maxlength=7, pattern='\d+-\d+',
        class_=c.focus and 'initialfocus' or None)}
  </div>
</div>

% endif
% endif
</%def>

<%def name="status_table()">
<div class="flex-grow-1 question-status p-0 d-flex flex-wrap justify-content-between mb-2 mr-1">
  <div class="item mr-4 p-2">
    ${h.flb(_("Test"),'test_nimi')}
    <div id="test_nimi">
      ${c.test.nimi} ${c.testiosa.tahis}
    </div>
  </div>
 
  % if c.toimumisaeg:
  <div class="item mr-4 p-2">
    ${h.flb(_("Testitöö kood"), 'too_kood')}
    <div id="too_kood">
      ${c.sooritus.tahised}<!--${c.sooritus.id}-->
    </div>
  </div>
  <div class="item mr-4 p-2">
    ${h.flb(_("Ülesandekomplekt"),'komplekt_id')}
    <div>
      % if c.testiosa.vastvorm_kood == const.VASTVORM_KP:
      ${h.form(h.url_current(), method='get')}
      ${h.select('komplekt_id', c.hindamine and c.hindamine.komplekt_id,
      c.opt_komplektid, wide=False, ronly=False, 
      empty=not c.hindamine or not c.hindamine.komplekt_id, onchange='this.form.submit()')}    
      ${h.end_form()}
      % elif c.hindamine and c.hindamine.komplekt:
      <div id="komplekt_id">
        ${c.hindamine.komplekt.tahis}
      </div>
      % else:
      <i id="komplekt_id">määramata</i>
      % endif
    </div>
  </div>
  % else:
  <div class="item mr-4 p-2">
    % if c.opt_sooritused:
    ${h.flb(_("Sooritaja"),'n1_sooritus_id')}
    <div>
      ${h.select('n1_sooritus_id', c.sooritus.id, c.opt_sooritused)}
    </div>
    % else:
    ${h.flb(_("Sooritaja"),'n1_sooritus_id')}
    <div id="n1_sooritus_id">
      <% sooritaja = c.sooritus.sooritaja %>
      ${sooritaja.eesnimi} ${sooritaja.perenimi}
    </div>
    % endif
  </div>
  % endif
  <div class="item mr-4 p-2">
    ${h.flb(_("Soorituskeel"), 'soorituskeel')}
    <div id="soorituskeel">
      ${model.Klrida.get_lang_nimi(c.sooritus.sooritaja.lang)}
    </div>
  </div>

  <% erivajadused = c.sooritus.get_str_erivajadused() %>
  % if erivajadused:
  <div class="item mr-4 p-2">
    ${h.flb(_("Eritingimused"),'erivajadused')}
    <div id="erivajadused" class="alert-warning p-1">
      ${erivajadused}
    </div>
  </div>
  % endif

  <div class="item mr-4 p-2">
    ${h.flb(_("Sooritamise olek"), 'staatus_nimi')}
    <div id="staatus_nimi">
      ${c.sooritus.staatus_nimi}
    </div>
  </div>
  % if c.hindamine:
  <div class="item mr-4 p-2">
    ${h.flb(_("Hindamise olek"), 'h_staatus')}
    <div id="h_staatus">
      ${c.hindamine.staatus_nimi}
    </div>
  </div>
  % endif

  <% solekud = [r for r in c.sooritus.sisestusolekud if r.skann] %>
  % if len(solekud):
  <div class="item mr-4 p-2">
    ${h.flb(_("Skannitud testitöö"),'skann_link')} 
    <div id="skann_link">
    % for r in solekud:
    ${h.link_to(r.sisestuskogum.nimi,
    h.url('tulemus_skskann', sooritus_id=c.sooritus.id, id=r.id))}
    % endfor
    </div>
  </div>
  % endif

  % if c.cnt_hinnatud != '':
  <div class="d-flex flex-wrap justify-content-between bg-gray-50">
  <div class="item mr-4 p-2">
    ${h.flb(_("Hindamata"), 'alustamata')}
    <span class="helpable" id="hindamata"></span>
    <div id="alustamata">
      ${c.alustamata or '0'}
    </div>
  </div>
  <div class="item mr-4 p-2">
    ${h.flb(_("Pooleli"),'pooleli')}
    <div id="pooleli">
    ${c.cnt_pooleli}
    </div>
  </div>
  % if c.toimumisaeg:
  <div class="item mr-4 p-2">
    ${h.flb(_("Kinnitamiseks valmis"),'valmis')}
    <div id="valmis">
      ${c.cnt_valmis}
    </div>
  </div>
  % endif
  <div class="item mr-4 p-2">
    ${h.flb(_("Kinnitatud"),'hinnatud')}
    <div id="hinnatud">
      ${c.cnt_hinnatud}
    </div>
  </div>
  </div>
  % endif

  ## mcomments
  % if c.hindamine:
  <div class="item mr-4 p-2 ksm-naeb" style="display:none">
    % if c.toimumisaeg and model.Seade.get_value('ksm.luba.hindaja'):
    <div>
      ${h.checkbox('ksm_naeb_hindaja', 1, checked=c.hindamine.ksm_naeb_hindaja,
      label=_("Teised hindajad näevad avatud vastusesse märgitud vigu"))}
    </div>
    % endif
    % if not c.toimumisaeg or model.Seade.get_value('ksm.luba.sooritaja'):
    <div>
      ${h.checkbox('ksm_naeb_sooritaja', 1, checked=c.hindamine.ksm_naeb_sooritaja,
      label=_("Sooritaja näeb avatud vastusesse märgitud vigu"))}
    </div>
    % endif
  </div>
  % endif
</div>
% if c.hindamine and c.hindamine.staatus == const.H_STAATUS_LYKATUD and c.hindamine.lykkamispohjus:
${h.flb(_("Tagasi lükkamise põhjus"),'lykkamispohjus')}
<div id="lykkamispohjus">
  ${h.alert_warning(c.hindamine.lykkamispohjus, False)}
</div>
% endif
</%def>

