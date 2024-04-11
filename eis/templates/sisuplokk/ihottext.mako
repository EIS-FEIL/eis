## -*- coding: utf-8 -*- 
## Tekstiosa valik
<%inherit file="baasplokk.mako"/>
<%namespace name="choiceutils" file="choiceutils.mako"/>
<!-- ${self.name} -->

<%def name="block_edit()">
% if c.item.id:
   % if c.lang:
       ${h.lang_orig(h.literal(c.block.sisu), c.orig_lang)}
       <div class="linebreak"></div>
       ${h.lang_tag()}
       ${h.ckeditor('f_sisu', c.block.tran(c.lang).sisu, 'hottext', ronly=not c.is_tr and not c.is_edit, baseHref='lang/%s/' % c.lang)}
   % elif c.is_edit or c.is_tr:
       ${h.ckeditor('f_sisu', c.block.sisu, 'hottext', ronly=False)}
   % endif

% elif c.is_edit:
${h.alert_notice(_("Märgitavaid tekstiosi saab lisada peale sisuploki esmast salvestamist"))}
${h.ckeditor('f_sisu', c.block.sisu, ronly=False)}
% endif

% if c.is_edit or c.is_tr:
<%include file="ihottext.transformer.mako"/>
% endif

% if c.block.sisuvaade:
<span class="px-3">
  ${h.checkbox('f_kujundus', const.KUJUNDUS_TAUSTATA, checkedif=c.item.kujundus, label=_("Tekstiosad ilma halli taustata"))}
</span>
<div class="p-3 my-3 border border-base-radius ${c.block.kujundus == const.KUJUNDUS_TAUSTATA and 'sp-hottext-nobackground' or 'sp-hottext-background'}">
    <h3>${_("Eelvaade")}
      % if c.is_edit:
      (${_("uueneb salvestamisel")})
      % endif
    </h3>
    <div class="ylesanne" style="position:relative">
          ${h.literal(c.block.replace_img_url(c.block.tran(c.lang).sisuvaade or '', lang=c.lang))}
    </div>
<script>
$(function(){
   ${self.js_block_preview_hottext()}  
   $('input.toggle-ctulemus').change(function(){
      $(this).closest('table').find('tr.ctulemus').toggleClass('nodisplay3');
   });
   $.each($('input.toggle-ctulemus'), function(n, item){
      $(item).closest('table').find('tr.ctulemus').toggleClass('nodisplay3', item.checked);
   });
});
</script>
</div>
% endif

% for ind, kysimus in enumerate(c.block.kysimused):
<div class="rounded border m-1">
${choiceutils.hindamismaatriks(kysimus, heading1='Tekstiosa ID', kood1=kysimus.valikud_opt, prefix='am-%d' % ind, fix_kood=True)}
</div>
% endfor
</%def>

<%def name="block_print()">
<div style="position:relative" class="asblock ${c.block.kujundus == const.KUJUNDUS_TAUSTATA and 'sp-hottext-nobackground' or 'sp-hottext-background'}">
${h.literal(c.block.replace_img_url(c.block.tran(c.lang).sisuvaade or '', lang=c.lang))}
</div>
</%def>

<%def name="block_view()">
<div id="block_${c.block_prefix}" class="asblock ${c.block.kujundus == const.KUJUNDUS_TAUSTATA and 'sp-hottext-nobackground' or 'sp-hottext-background'}">
% for kysimus in c.block.kysimused:
${h.qcode(kysimus)}
% endfor
${h.literal(c.block.replace_img_url(c.block.tran(c.lang).sisuvaade or '', lang=c.lang))}
</div>
% for kysimus in c.block.kysimused:
${h.hidden(kysimus.result, '')}
% endfor
</%def>

<%def name="block_view_js()">
function clear_${c.block_prefix}()
{
## eemaldame kõik valikud
  <% hottext_filter = 'div#block_%s .hottext.inter-b%s' % (c.block_prefix, c.block.id) %>
  $.each($('${hottext_filter}'), function(i,field)
  {
    click_on_hottext($(field), '${hottext_filter}', null, false, null); 
  });
}

function hottext_set_finished_${c.block_prefix}()
{
  var is_finished = true;
  var block = $('div#block_${c.block_prefix}');  
  % for kysimus in c.block.kysimused:
  <% hottext_filter = '.hottext.inter-b%s[group="%s"]' % (c.block.id, kysimus.kood) %>  
  var k_cnt = block.find('${hottext_filter}.hottext-selected').length;
  % if kysimus.min_vastus:
  is_finished &= (k_cnt >= ${kysimus.min_vastus});
  % else:
  if(k_cnt == 0)
  {
    ## kui muidu võib lõpetada, siis kontrollime veel yle, kas on tingimusi, mis seda takistavad
    $.each(mandatory, function(n, row){
        var k_kood = row[0];
        var is_mandatory = row[2];
        if((k_kood=='${kysimus.kood}') && is_mandatory)
        {
           is_finished = false;
        }
    });
  }
  % endif
  % endfor
  set_sp_finished(block, is_finished);        
}
  
$(function(){
   var block = $('div#block_${c.block_prefix}');
% if c.block_correct or c.block.naide:
${self.js_show_response(c.correct_responses)}
% else:
${self.js_show_response(c.responses)}
% endif

% if c.block.read_only:
## vastust muuta ei saa
    block.find('input').filter(function(){
       ## ei mõjuta alamsisuplokkide välju
       return ($(this).closest('div.asblock').is('div#block_${c.block_prefix}'));
    }).attr('disabled','disabled');    
% else:
## saab vastata
  ${self.js_block_hottext()}
% endif

% if c.show_r_code:
    ## koodide kuvamine
    var h_fields = block.find('.hottext');
    % if c.on_hindamine:
    h_fields = h_fields.filter(':not(.arvutihinnatud)');
    % endif
    $.each(h_fields, function(n, item){
        $(item).prepend('<span class="kood">'+item.id+'</span>');        
     });
% endif
});
</%def>

<%def name="js_block_preview_hottext()">
   var block = $('div.ylesanne');  
   % for kysimus in c.block.kysimused:
    <% hottext_filter = '.hottext.inter-b%s[group="%s"]' % (c.block.id, kysimus.kood) %>
    block.find('${hottext_filter}').click(function(){
       if(!is_btn_clicked($(this), 600))
       {
            set_btn_clicked($(this));
       }
       if($(this).hasClass('custom-control'))
          return false;
    });
  % endfor
  % if is_edit:
    hottext_set_finished_${c.block_prefix}();
  % endif
</%def>  

<%def name="js_block_hottext()">
  % for kysimus in c.block.kysimused:
    <% hottext_filter = '.hottext.inter-b%s[group="%s"]' % (c.block.id, kysimus.kood) %>
    block.find('${hottext_filter}').click(function(){
       if(!is_btn_clicked($(this), 600))
       {
            set_btn_clicked($(this));
            click_on_hottext(this, 
                       'div#block_${c.block_prefix} ${hottext_filter}', 
                       $('input[name="${kysimus.result}"]'),
                       null,
                       ${kysimus.max_vastus or 'null'});
            hottext_set_finished_${c.block_prefix}();
       }
       if($(this).hasClass('custom-control'))
          return false;
    });
    k_check_finished["${kysimus.kood}"] = hottext_set_finished_${c.block_prefix};    
  % endfor
  hottext_set_finished_${c.block_prefix}();
</%def>  

<%def name="js_show_response(responses, for_resp=True)">
% if for_resp:
clear_${c.block_prefix}();
% endif
% for kysimus in c.block.kysimused:
  <% 
       hottext_filter = 'div#block_%s .hottext.inter-b%s[group="%s"]' % (c.block_prefix, c.block.id, kysimus.kood)
       kv = responses.get(kysimus.kood)
       tulemus = kysimus.tulemus
       chosen = [] 
  %>
  % if kv:
    % for ks in kv.kvsisud:
       <% chosen.append(ks.kood1) %>
       var field = $('${hottext_filter}[name="${h.chk_w(ks.kood1)}"]');
       % if for_resp:
       click_on_hottext(field[0],'${hottext_filter}',
                        $('input[name="${kysimus.result}"]'));                        
       % endif
       % if c.on_hindamine and kv.arvutihinnatud:
       field.addClass('arvutihinnatud');
       % endif
       % if (c.prepare_correct or c.on_hindamine and kv.arvutihinnatud) and ks.on_hinnatud and not c.block.varvimata:
       field.addClass('${model.ks_correct_cls(responses, tulemus, kv, ks, True, for_resp)}').removeClass('hottext-selected-bg');
       % endif
    % endfor
    % if (c.prepare_correct or c.on_hindamine and kv.arvutihinnatud) and kysimus.max_vastus != 1:       
       ## vastamata vastuste värvimine
       ## ei värvi siis, kui on raadionupp (max_vastus=1)
       % for valik in kysimus.valikud:
       % if valik.kood not in chosen:
       var field = $('${hottext_filter}[name="${valik.kood}"]');       
       % if c.on_hindamine and kv.arvutihinnatud:
       field.addClass('arvutihinnatud');
       % endif
       field.addClass('${model.ks_cls(model.vastamata_on_oige(responses, tulemus, kv, valik.kood, True), for_resp)}');       
       % endif
       % endfor
    % endif
  % endif
% endfor
</%def>

