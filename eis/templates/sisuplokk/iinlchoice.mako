## Valikvastusega lünktekst
<%inherit file="baasplokk.mako"/>

<%namespace name="choiceutils" file="choiceutils.mako"/>
<!-- ${self.name} -->

<%def name="block_edit()">

<div class="mb-1 row">
  <div class="col-md-3 col-xl-2"></div>
  <div class="col">
    ${h.checkbox('f_select_promptita', 1, checked=c.block.select_promptita, label=_('Peida "--Vali--"'))}
  </div>
</div>

% if c.item.id:
   % if c.lang:
      ## jätame välja HTML kujul sisestatud valikud
      <% orig_sisu = h.re.sub(r'(<select [^>]*rtf="1"[^>]*><option>[^<]*</option>)(<option value=[^>]+>[^<]*</option>){1,}', '\\1', c.block.sisu) %>
      ${h.lang_orig(h.literal(orig_sisu))}       
      <div class="linebreak"></div>
       ${h.lang_tag()}
   % endif  
    <% baseHref = c.lang and 'lang/%s/' % c.lang or None %>
   ${h.ckeditor('f_sisu', c.block.tran(c.lang).sisu, 'inlinechoice',ronly=False, baseHref=baseHref)}
% else:
${h.alert_notice(_("Lünki saab lisada peale sisuploki esmast salvestamist"))}
${h.ckeditor('f_sisu', c.block.sisu, ronly=False)}
% endif

% if c.block.sisuvaade:

<div class="ylesanne">
  <div class="p-3 my-3 border border-base-radius" id="block_${c.block_prefix}">
    <h3>${_("Eelvaade")}
    % if c.is_edit:
      (${_("uueneb salvestamisel")})
    % endif
    </h3>
    <div class="ylesanne" style="position:relative">
      ${h.literal(c.block.replace_img_url(c.block.tran(c.lang).sisuvaade or '', lang=c.lang))}
    </div>
    <script>
      var block = $('div#block_${c.block_prefix}');          
      var fields = block.find('.dropdown');
      ## valikväli teha sama laiaks kui kõige laiem valik
      fields.each(function(){
        var ddm = $(this).find('.dropdown-menu'); w = ddm.width(),
           iw = $(this).find('button>i.mdi').width();
        $(this).width(w + iw);  ddm.width(w + iw);
      });
      fields.find(".dropdown-item").click(function(){
         ## valiku valimisel panna valitud valik nupu tekstiks ja väärtus väärtuse väljale
         var drd = $(this).parents('.dropdown');
         drd.find('.btn-select label').html($(this).html());
         drd.parents(".dropdown").find('input[type="hidden"]').val($(this).data('value'));
         drd.tooltip('hide');
      });
    </script>
  </div>
</div>

% endif

## Hindamismaatriks on igal lahtril eraldi ja avaneb eraldi aknas
</%def>

<%def name="block_preview()">
<div style="position:relative">
${h.literal(c.block.tran(c.lang).sisuvaade or '')}
</div>
</%def>

<%def name="block_print()">
<div class="inputlines" style="position:relative">
  ${h.literal(c.block.replace_img_url(c.block.tran(c.lang).sisuvaade or '', lang=c.lang))}
</div>
</%def>

<%def name="block_view()">
<div id="block_${c.block_prefix}" class="asblock">
  ${h.literal(c.block.replace_img_url(c.block.tran(c.lang).sisuvaade or '', lang=c.lang))}
  % if c.read_only and c.prepare_correct:
  ${self.tip_correct()}
  % endif
</div>
</%def>

<%def name="block_view_js()">

function clear_${c.block_prefix}()
{
## eemaldame kõik valikud
  var block=$('div#block_${c.block_prefix}');
  var fields = block.find('.dropdown').filter(
     function(){
        return $(this).closest('.asblock').attr('id')=='block_${c.block_prefix}';
     });
  $.each(fields, function(i, field){
    var vali = $(field).find('.dropdown-item[data-value=""]').html();
    $(field).find('label').html(vali);
    $(field).find('input[type="hidden"]').val('');
  });
}
$(function(){
  var block = $('div#block_${c.block_prefix}');
  % if c.block_correct or c.block.naide:
    ${self.js_show_response(c.correct_responses)}
  % else:
    ${self.js_show_response(c.responses, is_resp=True)}
  % endif

  var fields = block.find('.dropdown').filter(
     function(){
        return $(this).closest('.asblock').attr('id')=='block_${c.block_prefix}';
     });

  % if c.show_q_code or c.show_r_code:
    ## koodide kuvamine
    var h_fields = fields.filter(':not(.arvutihinnatud)');
    $.each(h_fields, function(n, item){
        var btn = $(item).find('button.btn-select');
   % if c.show_q_code:
        btn.before('<span class="kysimus">'+btn.prop('id')+'</span>');
   % endif
   % if c.show_r_code:
        $.each($(item).find('.dropdown-item[data-value!=""]'), function(m, item2){
          $(item2).insert(0, $('<span>['+$(item2).data('value')+']</span>'));
        });
   % endif
     });
  % endif
  % if c.prepare_correct or c.block.naide or c.read_only:
    ## ei saa vastust muuta
    ## eemaldame ka fookuse, kui on, et fookus ei varjaks õige/vale raami
    fields.find('.dropdown-menu').hide();
    fields.find('.btn-select').filter(':focus').blur();
  % endif

  ## muudame valikvälja sama laiaks kui kõige laiem valik
  fields.each(function(){
      var ddm = $(this).find('.dropdown-menu'); w = ddm.width(),
          iw = $(this).find('button>i.mdi').width();
      $(this).width(w + iw);  ddm.width(w + iw);
  });
% if not c.block.read_only:
  input_set_finished(fields);
% endif
  is_response_dirty = false;
});
</%def>

<%def name="js_show_response(responses, for_resp=True, is_resp=False)">
<% kysimused = {k.id: k for k in c.block.kysimused} %>
% if for_resp:
clear_${c.block_prefix}();
% endif
var block = $('div#block_${c.block_prefix}');
%    for kood in responses.keys():
<%
  kv = responses[kood]
  kysimus = kysimused.get(kv.kysimus_id)
%>
    %      if kv and kysimus:
     <% tulemus = kysimus.tulemus %>
    %        for ks in kv.kvsisud:
                var inp = block.find('input[id="${kood}"]'),
                    drd = inp.closest('.dropdown'),
                    btn = drd.find('.btn-select'),
                    title = drd.find('.dropdown-item[data-value="${h.chk_w(ks.kood1)}"]').html();
    %         if ks.kood1:
                btn.find('>label').html(title);
                inp.val("${h.chk_w(ks.kood1)}");
    %         endif
    %         if c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
                btn.addClass('${model.ks_correct_cls(responses, tulemus, kv, ks, False, for_resp)}');
    %         endif
    %         if c.on_hindamine and kv.arvutihinnatud:
                drd.addClass('arvutihinnatud');
    %         endif
    %         if (c.prepare_correct or c.on_hindamine and kv.arvutihinnatud) and ks.on_hinnatud and not c.block.varvimata:
                btn.addClass('${model.ks_correct_cls(responses, tulemus, kv, ks, False, for_resp)}');
    %         endif
    %        endfor
    %      endif
    %    endfor
</%def>

<%def name="tip_correct()">
<% any_tip = False %>
% for kysimus in c.block.pariskysimused:
<%
  kood = kysimus.kood
  kv = c.correct_responses.get(kood)
%>
   % if kv:
   % for ks in kv.kvsisud:
<% any_tip = True %>
<div class="tip-correct" id="_DC_${kood}" data-value="${h.chk_w(ks.kood1)}"> </div>
   % endfor
   % endif
% endfor
% if any_tip:
<script>
$(function(){
  var block = $('div#block_${c.block_prefix}');
  var fields = block.find('.dropdown').filter(
     function(){
        return $(this).closest('.asblock').attr('id')=='block_${c.block_prefix}';
     });
  fields.tooltip({
     html: true,
     title: function(){ 
          var id = $(this).find('>input[type="hidden"]').prop('id'), v = $('.tip-correct#_DC_' + id).data('value'),
          f = $(this).closest('.dropdown').find('.dropdown-item[data-value="' + v + '"]');
          if(f.length) return f.clone().removeClass('dropdown-item');
     }
  });
});
</script>
% endif
</%def>
