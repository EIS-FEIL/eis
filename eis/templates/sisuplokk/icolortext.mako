## Tekstiosa värvimine
<%inherit file="baasplokk.mako"/>
<%namespace name="choiceutils" file="choiceutils.mako"/>
<!-- ${self.name} -->

<%def name="block_edit()">
<script>
  ## et uue tekstiosa loomisel vaikimisi ei oleks märkeruut
  var default_uitype = "underline";
</script>
  
% if c.item.id:
   % if c.lang:
       ${h.lang_orig(h.literal(c.block.sisu), c.orig_lang)}
       <div class="linebreak"></div>
       ${h.lang_tag()}
       ${h.ckeditor('f_sisu', c.block.tran(c.lang).sisu, 'hottext', ronly=not c.is_tr and not c.is_edit, baseHref='lang/%s/' % c.lang)}
   % elif c.is_edit:
       ${h.ckeditor('f_sisu', c.block.sisu, 'hottext')}
   % endif

% elif c.is_edit:
${h.alert_notice(_("Märgitavaid tekstiosi saab lisada peale sisuploki esmast salvestamist"))}
${h.ckeditor('f_sisu', c.block.sisu, ronly=False)}
% endif

% if c.is_edit or c.is_tr:
<%include file="ihottext.transformer.mako"/>
<div style="height:7px"></div>
% endif

<%
   bkysimus = c.block.give_baaskysimus()
   color_opt = bkysimus.valikud_opt       
   choiceutils.choices(bkysimus, bkysimus.valikud, 'v', wysiwyg=False, can_rtf=False, caption=_("Värvid"))
%>

% if c.block.sisuvaade:
${self.block_edit_preview()}
% endif

<%
  bkysimus = c.block.give_baaskysimus()
  color_opt = bkysimus.valikud_opt
  for ind, kysimus in enumerate(c.block.pariskysimused):
     choiceutils.hindamismaatriks(kysimus,
                                  heading1='Tekstiosa ID',
                                  heading2=_("Värv"),
                                  kood1=kysimus.valikud_opt,
                                  kood2=color_opt,
                                  kood2_cls='vkood',
                                  prefix='am-%d' % ind,
                                  fix_kood=True)
%>

</%def>

<%def name="block_edit_preview()">
  ${h.checkbox('f_kujundus', const.KUJUNDUS_TAUSTATA, checkedif=c.item.kujundus, label=_("Tekstiosad ilma halli taustata"))}
<div class="p-3 my-3 border border-base-radius floatleft ${c.block.kujundus == const.KUJUNDUS_TAUSTATA and 'sp-hottext-nobackground' or 'sp-hottext-background'}">
       
  <h3>${_("Eelvaade")}
      % if c.is_edit:
      (${_("uueneb salvestamisel")})
      % endif
  </h3>
  <div class="d-flex flex-wrap-reverse">
    <div class="ylesanne" style="position:relative; min-width:200px;">
      ${h.literal(c.block.replace_img_url(c.block.tran(c.lang).sisuvaade or '', lang=c.lang))}
    </div>
    <div>
        ${self.view_colortable()}
    </div>
  </div>
</div>
<script>
$(function(){
$('.colors div.ca-pick-color').click(function()
{
    $(this).closest('.colors').find('.ca-current-color').removeClass('ca-current-color');
    $(this).addClass('ca-current-color');
});
$('.hottext').click(function(){
      var color_el = $('.colors div.ca-pick-color.ca-current-color');
      var curr_color = color_el.data('color');
      var curr_color_k = color_el.data('kood');
      click_on_hottext(this, 
                       '.hottext',
                       null,
                       null,
                       null,
                       true,
                       curr_color,
                       curr_color_k);
     if($(this).hasClass('custom-control'))
        return false;
   });
   $('input.toggle-ctulemus').change(function(){
      $(this).closest('table').find('tr.ctulemus').toggle(!this.checked);
   });
   $.each($('input.toggle-ctulemus'), function(n, item){
      $(item).closest('table').find('tr.ctulemus').toggle(!item.checked);
   });
});
</script>
</div>
</%def>

<%def name="block_print()">
<div style="position:relative" class="asblock ${c.block.kujundus == const.KUJUNDUS_TAUSTATA and 'sp-hottext-nobackground' or 'sp-hottext-background'}">
${h.literal(c.block.replace_img_url(c.block.tran(c.lang).sisuvaade or '', lang=c.lang))}
</div>
</%def>

<%def name="block_view()">
<div id="block_${c.block_prefix}" class="asblock ${c.block.kujundus == const.KUJUNDUS_TAUSTATA and 'sp-hottext-nobackground' or 'sp-hottext-background'}">
  % for kysimus in c.block.pariskysimused:
  ${h.qcode(kysimus)}
  % endfor
  <div class="d-flex flex-wrap-reverse">
    <div class="pr-2">
      ${h.literal(c.block.replace_img_url(c.block.tran(c.lang).sisuvaade or '', lang=c.lang))}
    </div>
    <div>
      ${self.view_colortable()}
    </div>
  </div>
  % for kysimus in c.block.pariskysimused:
  ${h.hidden(kysimus.result, '')}
  % endfor
</div>
</%def>

<%def name="view_colortable()">
<%
  bkysimus = c.block.get_baaskysimus()
  varvid = [(v.kood, v.varv, v.tran(c.lang).nimi) for v in bkysimus.valikud]
  no_title = len([r for r in varvid if r[2]]) == 0
%>
<div class="colors ${no_title and 'd-flex flex-wrap' or ''}">
  % for kood, varv, nimi in varvid:
  <div data-kood="${kood}" data-color="${varv}" class="d-flex align-items-center ca-pick-color">
    <div style="background-color:${varv}" class="ca-sample"></div>
    % if nimi:
    <div class="ml-1 mr-2">${nimi}</div>
    % endif
  </div>
  % endfor
</div>
</%def>

<%def name="block_view_js()">
function clear_${c.block_prefix}()
{
## eemaldame kõik valikud
  <% hottext_filter = 'div#block_%s .hottext.inter-b%s' % (c.block_prefix, c.block.id) %>
  $.each($('${hottext_filter}'), function(i,field)
  {
     click_on_hottext($(field), '${hottext_filter}', null, false, null, true); 
  });
}

function hottext_set_finished_${c.block_prefix}()
{
  var is_finished = true;
  var block = $('div#block_${c.block_prefix}');  
  % for kysimus in c.block.pariskysimused:
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
% if c.block.read_only:
## vastust muuta ei saa
    block.find('input').filter(function(){
       ## ei mõjuta alamsisuplokkide välju
       return ($(this).closest('div.asblock').is('div#block_${c.block_prefix}'));
    }).attr('disabled','disabled');    
% else:
## saab vastata
  % for kysimus in c.block.pariskysimused:
    <% hottext_filter = '.hottext.inter-b%s[group="%s"]' % (c.block.id, kysimus.kood) %>
  block.find('${hottext_filter}').click(function(){
      var color_el = block.find('.colors div.ca-pick-color.ca-current-color');
      var curr_color = color_el.data('color');
      var curr_color_k = color_el.data('kood');
      click_on_hottext(this, 
                       'div#block_${c.block_prefix} ${hottext_filter}', 
                       $('input[name="${kysimus.result}"]'),
                       null,
                       ${kysimus.max_vastus or 'null'},
                       true,
                       curr_color,
                       curr_color_k);
      hottext_set_finished_${c.block_prefix}();
      if($(this).hasClass('custom-control'))
         return false;
  });
  k_check_finished["${kysimus.kood}"] = hottext_set_finished_${c.block_prefix};
  % endfor
  hottext_set_finished_${c.block_prefix}();
% endif
   
   % if c.show_r_code:
     ## koodide kuvamine
  $.each(block.find('.hottext'), function(n, item){
     $(item).prepend('<span class="kood">'+item.id+'</span>');        
  });
   % endif
% if not c.block.read_only:
  $('div#block_${c.block_prefix}.asblock .colors div.ca-pick-color').click(function()
  {
    $(this).closest('.colors').find('.ca-current-color').removeClass('ca-current-color');
    $(this).addClass('ca-current-color');
  });
% endif
    
% if c.block_correct or c.block.naide:
${self.js_show_response(c.correct_responses)}
% else:
${self.js_show_response(c.responses)}
${self.js_show_response(c.correct_responses, False)}                                                                      
% endif
});
</%def>

<%def name="js_show_response(responses, for_resp=True)">
% if for_resp:
clear_${c.block_prefix}();
% endif
<%
  bkysimus = c.block.get_baaskysimus()
  colors = {v.kood: v.varv for v in bkysimus.valikud}
%>
% for kysimus in c.block.pariskysimused:
    <% 
       hottext_filter = 'div#block_%s .hottext.inter-b%s[group="%s"]' % (c.block_prefix, c.block.id, kysimus.kood)
       kv = responses.get(kysimus.kood)
       tulemus = kysimus.tulemus
    %>
    % if kv:
    % for ks in kv.kvsisud:
       var field = $('${hottext_filter}[name="${h.chk_w(ks.kood1)}"]');
       % if for_resp:
       click_on_hottext(field[0],
                       '${hottext_filter}',
                        $('input[name="${kysimus.result}"]'),
                        true,
                        null,                        
                        true,
                        '${colors.get(ks.kood2)}',
                        '${h.chk_w(ks.kood2)}');
       % endif
    % if c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
       field.addClass('${model.ks_correct_cls(responses, tulemus, kv, ks, False, for_resp)}').removeClass('hottext-selected-bg');
    % endif
    % endfor
    % endif
  % endfor
</%def>

