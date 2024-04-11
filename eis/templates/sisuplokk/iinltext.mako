## Avatud lünk(tekst)
<%inherit file="baasplokk.mako"/>
<%namespace name="choiceutils" file="choiceutils.mako"/>
<!-- ${self.name} -->

<%def name="block_edit()">
% if c.item.id:
<div>
   % if c.lang:
   <div class="eelvaade">
       ${h.lang_orig(h.literal(c.block.sisu))} 
       ${h.lang_tag()}
   </div>
   % endif  
    <% baseHref = c.lang and 'lang/%s/' % c.lang or None %>       
   ${h.ckeditor('f_sisu', c.block.tran(c.lang).sisu, 'inlinetext',ronly=False, baseHref=baseHref)}
</div>
% else:
${h.alert_notice(_("Lünki saab lisada peale sisuploki esmast salvestamist"))}
${h.ckeditor('f_sisu', c.block.sisu, ronly=False)}
% endif

% if c.block.sisuvaade:
<div class="p-3 my-3 border border-base-radius ylesanne mt-3" id="block_${c.block_prefix}">
  <h3>${_("Eelvaade")}
  % if c.is_edit or c.is_tr:
  (${_("uueneb salvestamisel")})
    % endif
  </h3>
  <div class="ylesanne eelvaade mb-3" style="position:relative">
    ${h.literal(c.block.replace_img_url(c.block.tran(c.lang).sisuvaade or '', lang=c.lang))}
  </div>
</div>

% endif

<script>
## eemaldame mustri eelvaates näidatavatelt väljadelt
## kuna välja sees võidakse näidata küsimuse koodi vms, mis mustrile ei vasta
$(function(){
   $('.eelvaade').find('input[pattern],textarea[pattern]').removeAttr('pattern');
% if c.block.on_math_kysimusi:
  ${self.js_init_math(True)}
% endif
});
</script>
</%def>

<%def name="block_preview()">
<div style="position:relative" class="eelvaade asblock" id="block_${c.block_prefix}">
  ${h.literal(c.block.replace_img_url(c.block.tran(c.lang).sisuvaade or '', lang=c.lang))}
</div>
<script>
## eemaldame mustri eelvaates näidatavatelt väljadelt
## kuna välja sees võidakse näidata küsimuse koodi vms, mis mustrile ei vasta
$(function(){
  $('.eelvaade').find('input[pattern],textarea[pattern]').removeAttr('pattern');
% if c.block.on_math_kysimusi:
  ${self.js_init_math(True)}
% endif
});
</script>
</%def>

<%def name="block_print()">
<div class="inputlines" style="position:relative">
  ${h.literal(c.block.replace_img_url(c.block.tran(c.lang).sisuvaade or '', lang=c.lang))}
</div>
</%def>

<%def name="block_view()">
% if c.block.on_rtf_kysimusi:
<div id="${c.block_prefix}_ckeditor_top"></div>
% endif
<div id="block_${c.block_prefix}" class="asblock ${c.block.kleepekeeld and 'nopaste' or ''}">
${h.literal(c.block.replace_img_url(c.block.tran(c.lang).sisuvaade or '', lang=c.lang))}

% if c.read_only and c.prepare_correct:
${self.tip_correct()}
% endif
</div>
</%def>

<%def name="block_view_js()">
function clear_${c.block_prefix}()
{
## eemaldame kõik väärtused
## välja arvatud tühja välja title väärtus 
## (mille tunneme ära klassi example järgi)
  var block = $('div#block_${c.block_prefix}');
  var fields = block.find('input[type="text"]:not(.example)').filter(
## jätame välja need väljad, mis on meie alla sattunud mõne alamsisuploki koosseisus
     function(){
        return $(this).closest('.asblock').attr('id')=='block_${c.block_prefix}';
     })
  $.each(fields, function(i, field){
    $(field).val('');
  });
}
<% on_math_kysimusi = c.block.on_math_kysimusi %>
${self.js_math_icons()}
$(function(){
    var block = $('div#block_${c.block_prefix}');
    var f_in_block = function(){
        return $(this).closest('.asblock').attr('id')=='block_${c.block_prefix}';
    };
% if c.block_correct or c.block.naide:
    ${self.js_show_response(c.correct_responses)}
% else:
    ${self.js_show_response(c.responses)}
% endif

    var fields = block.find('input[type="text"],textarea')
      .filter(':not(.noresponse):not(.val-tp)')
      .filter(f_in_block);
% if on_math_kysimusi:
   var fields_math_h = block.find('input[type="hidden"].math-editable')
      .filter(':not(.noresponse):not(.val-tp)')
      .filter(f_in_block);
% endif

% if c.show_q_code:
     ## iga lynga juurde lisame kollase kysimuse koodi
     ## ja sellel klikkides avatakse kysimuse hindamise dialoog
     var h_fields = fields.filter(':not(.arvutihinnatud)');
     $.each(h_fields, function(n, item){
       $(item).addClass('hinnatavlynk');
       $('<span class="kysimus link">'+item.id+'</span>').
           insertBefore(item).
           click(function(){
              var ref = 'div.hinded[data-name="b${c.block.id}k'+item.id+'"]';
              var contents = $(ref);
              if(contents.length > 0)
              {
                 parent.dialog_ref(contents, item.id, '700px');
              }
       });
     });
% if on_math_kysimusi:
     $.each(fields_math_h, function(n, item){
       var wrapper = $(item).closest('.gap-math-wrap');
       wrapper.addClass('hinnatavlynk');
       $('<span class="kysimus link">'+item.id+'</span>').
           insertBefore(wrapper).
           click(function(){
              var ref = 'div.hinded[data-name="b${c.block.id}k'+item.id+'"]';
              var contents = $(ref);
              if(contents.length > 0)
              {
                 parent.dialog_ref(contents, item.id, '700px');
              }
       });
     });
% endif
% endif

% if c.prepare_correct or c.block_correct or c.block.naide or c.block.read_only:
## ei saa vastust muuta
   ## bugzilla 241 - hindaja peab saama vastust kopeerida, mistõttu disabled ei sobi
   fields.prop('readonly',true);
% endif

% if c.ylesanne.spellcheck:
  fields.attr('spellcheck', 'true');
% else:
  fields.attr('spellcheck', 'false');
% endif

% if c.block.on_math_kysimusi:
  ${self.js_init_math(c.is_edit)}
% endif

% if c.block.on_rtf_kysimusi:
  CKEDITOR.on("instanceReady", function(event)
  {
    if(typeof resized === "function")
       resized();
  });

$.each(fields.filter('textarea'), function(n, item){
     ## et lynk ei läheks eraldi reale, paneme inline-block divi ymber
     var wrapper = $('<div/>').addClass("gap-ckeditor-wrap").css({'display':'inline-block','vertical-align':'middle'});
     if($(item).hasClass('corr1r')) wrapper.addClass('corr1r');
     if($(item).hasClass('corr0r')) wrapper.addClass('corr0r');
     $(item).wrap(wrapper);
     var id = item.id;
     var rows = (item.rows || 1);
     var cols = Math.max(item.cols || 10, 10);
% if c.is_edit and not c.read_only:
     var tb_custom = ${h.ckeditor_icons(c.block.ylesanne.get_ckeditor_icons())};
% else:
     var tb_custom = [];
% endif
     var title = $(item).attr('title') || $(item).attr('data-original-title');
     var params = {width: cols*10 + 'px',
                  height: (rows*24 + 8) + 'px',
                  toolbar:'custom',
                  toolbar_custom: tb_custom,
                  resize_enabled:false,
                  sharedSpaces: {top:'y_ckeditor_top'},
                  removePlugins: 'maximize,forms,entities,showborders,magicline',
                  bodyClass: $(item).prop('class'), // text-align-*
                  enterMode: CKEDITOR.ENTER_BR,
                  disableObjectResizing: true, // et firefox ei kuvaks tabeli ymber raami
                  placeholder: title,
                  disableNativeSpellChecker: ${c.ylesanne.spellcheck and 'false' or 'true'},
                  language: "${request.localizer.locale_name}"
                 };
     if($(item).attr('maxlength')){
        params['extraPlugins'] = 'wordcount';
        params['wordcount'] = {showParagraphs: false,
                               showCharCount: false, 
                               showWordCount: false, 
                               countHTML: true,
                               countSpacesAsChars: true,
                               maxCharCount: $(item).attr('maxlength'),
                              }
     }
     ckeditor_js(id, params, null, false);
     CKEDITOR.instances[id].on('change', function(){
        var field = $('textarea#' + id);
% if not c.read_only:
        var hasvalue = this.getData() != '';
        field.toggleClass('hasvalue', hasvalue);
        if(!hasvalue) field.val('');
        input_set_finished(field); 
% endif
        response_changed(field);
     });
     CKEDITOR.instances[id].on('focus', function(e){
         $('#y_ckeditor_ttop').show().position({
                my: 'left bottom',
                at: 'left top',
                of: $(this.element.$.parentElement)});
     });
     CKEDITOR.instances[id].on('blur', function(e){
        $('#y_ckeditor_ttop').hide();
     });
  });
% endif

% if not c.block.read_only:
    fields.keyup(function(){
        input_set_finished($(this))
    });
    fields.change(function(){ response_changed($(this)); });
  % if on_math_kysimusi:
    block.on('keyup', '.mq-textarea textarea', function(){
        input_set_finished($(this))
    });
    input_set_finished($.merge(fields, fields_math_h));
  % else:
    input_set_finished(fields);
  % endif
% endif


% if c.is_edit and not c.is_sp_analysis:
     ## sõnade lugemine kireva teksti väljadel
     fields.filter('.ck-wordcounting').each(function(){
          var name = this.id, editor = CKEDITOR.instances[name],
              counter = $(this).closest('.ks-outer').find('.wordcount');
          count_words(counter, editor.getData(), true);
          editor.on('change', function(){
             count_words(counter, this.getData(), true);
          });
      });
      ## sõnade lugemine lihtteksti väljadel
      fields.filter('.wordcounting').each(function(){
          var name = this.name, fld = $(this),
              counter = $(this).closest('.ks-outer').find('.wordcount');
          count_words(counter, fld.val(), false);
          fld.keyup(function(){count_words(counter, fld.val(), false);});        
      });
% endif
});
</%def>

<%def name="js_math_icons()">
% for k in c.block.kysimused:
% if k.matriba:
var matheditor_buttons_me_${k.kood} = ${model.json.dumps(c.ylesanne.get_math_icons(k.matriba))};
% endif
% endfor
var matheditor_buttons = ${model.json.dumps(c.ylesanne.get_math_icons())};  
</%def>

<%def name="js_init_math(is_edit)">
  var block = $('#block_${c.block_prefix}');
  % if is_edit:
  block.find('.math-view-edit').addClass('math-edit');
  % else:
  block.find('.math-view-edit').addClass('math-view');
  % endif
  init_math_editor(block);
  ## et mat lyngad ei läheks igayks omaette reale
  block.find('.matheditor-wrapper')
  % if not c.is_sp_edit:
     .filter(function(){
        return $(this).closest('.asblock').attr('id')=='block_${c.block_prefix}';
     })
  % endif
     .css('display', 'inline-block');
</%def>

<%def name="js_show_response(responses, for_resp=True)">
<% kysimused = {k.id: k for k in c.block.kysimused} %>
             var block = $('div#block_${c.block_prefix}');
% for kood in responses.keys():
<%
  kv = responses[kood]
  kysimus = kv and kysimused.get(kv.kysimus_id)
%>
   % if kv and kysimus:
      % for ks in kv.kvsisud:
         <%
           name = kysimus.result
           tulemus = kysimus.tulemus
           value = h.jsparam(ks.sisu)
           if value:
               value = h.escape_script(value) or ''
         %>
         % if ks.sisu:
             block.find('input[name="${name}"],textarea[name="${name}"]').val("${value}").removeClass('example');
             % if kysimus.sonadearv:
             block.find('input[name="${name}"],textarea[name="${name}"]').closest('.ks-outer').find('.wordcount').text("${ks.sonade_arv or '0'}");
             % endif
             % if kysimus.vastus_taisekraan and not c.is_edit:
             var bmax = $('<img title="${_("Maksimeerimine")}" class="ks-fullscreen" src="/static/images/maximize.png" border="0"/>')
                  .click(function(){inltext_toggle_fullscreen(this);});
             block.find('input[name="${name}"],textarea[name="${name}"]').closest('.ks-outer').find('.ks-icons').prepend(bmax);
             % endif
         % endif         
         % if c.on_hindamine and kv.arvutihinnatud:
             block.find('input[name="${name}"],textarea[name="${name}"]').addClass("arvutihinnatud");         
         % endif
         % if (c.prepare_correct or c.on_hindamine and kv.arvutihinnatud) and ks.on_hinnatud and not c.block.varvimata:
           <% corr_cls = model.ks_correct_cls(responses, kysimus.tulemus, kv, ks, False, for_resp) %>                      
           % if tulemus.baastyyp == const.BASETYPE_MATH:
             block.find('div.math-view-edit,div.math-view').filter('[name="${name}"]').addClass("${corr_cls}");
           % else:
             block.find('input[name="${name}"],textarea[name="${name}"]').addClass("${corr_cls}");
             block.find('textarea[name="${name}"]').parent('.gap-ckeditor-wrap').addClass("${corr_cls}");
           % endif
         % endif
      % endfor
   % endif
% endfor
</%def>

<%def name="tip_correct()">
<div style="height:0px;overflow:hidden;">
<div style="visibility:hidden">
<% any_tip = False %>
% for kysimus in c.block.pariskysimused:
<%
  kood = kysimus.kood
  kv = c.correct_responses.get(kood)
  tulemus = kysimus.tulemus
  is_math = tulemus.baastyyp == const.BASETYPE_MATH
%>
   % if kv:
   % for ks in kv.kvsisud:
   % if ks.sisu:
<% any_tip = True %>
<div class="tip-correct" id="_DC_${kood}">
  % if is_math:
  <div class="math-view">
    ${ks.sisu}
  </div>
  % else:
  ${ks.sisu}
  % endif
</div>
   % endif
   % endfor
   % endif
% endfor
</div>
</div>
% if any_tip:
<script>
$(function(){
  var block = $('div#block_${c.block_prefix}');
  block.find('input,textarea').tooltip({
     title: function(){ var f = $('.tip-correct#_DC_' + this.id); if(f.length) return f.clone(); }
  });
  block.find('div.gap-ckeditor-wrap').tooltip({
     html: true,
##trigger:'manual',
     title: function(){
       var f = $('.tip-correct#_DC_' + $(this).find('textarea').prop('id')); if(f.length) return f.clone();
     }
  });
  block.find('div.gap-math-wrap').tooltip({
     html: true,
     title: function(){
       var f = $('.tip-correct#_DC_' + $(this).find('input.math-editable').prop('id')); if(f.length) return f.clone();
     }
  });
});
</script>
% endif
</%def>
