## Pangaga lünktekst
<%inherit file="baasplokk.mako"/>
<%namespace name="choiceutils" file="choiceutils.mako"/>
<!-- ${self.name} -->

<%def name="block_edit()">
<%
  bkysimus = c.block.give_kysimus(0)
  btulemus = bkysimus.tulemus
  ch = h.colHelper('col-md-3', 'col-md-9')
%>

<div class="form-group row">
  ${ch.flb(_("Lahendaja saab pangast lohistada:"), 'dridu')}
  <div class="col-md-9" id="dridu">
      ${h.radio('l.ridu', 0, checked=not bkysimus.ridu,
      label=_("lünkadesse"))}
      ${h.radio('l.ridu', 2, checked=bkysimus.ridu==2,
      label=_("teksti sisse sõnade vahele"))}
      <script>
        $('input[name="l.ridu"]').change(function(){
           $('div.btulemus').toggle($(this).val()=='2');
        });
        $(function(){
           $('div.btulemus').toggle($('input[name="l.ridu"]:checked').val()=='2');
        });
      </script>
  </div>
</div>
<div class="form-group row">
  <% name = 'l.n_asend' %>
  ${ch.flb(_("Panga asend"), name)}
  <div class="col">
    ${h.radio('l.n_asend', model.Kysimus.ASEND_ALL,
    checked=bkysimus.n_asend==model.Kysimus.ASEND_ALL or bkysimus.n_asend is None, label=_("all"))}
    ${h.radio('l.n_asend', model.Kysimus.ASEND_PAREMAL,
    checkedif=bkysimus.n_asend, label=_("paremal, paigal"))}
    ${h.radio('l.n_asend', model.Kysimus.ASEND_PAREMAL_S,
    checkedif=bkysimus.n_asend, label=_("paremal, liigub akna kerimisel"))}
  </div>
</div>
<div class="form-group row">
  <div class="col">
  ${h.checkbox('l.erand346', 1, checked=bkysimus.erand346,
        label=_("Vaikimisi punkte ei anta, kui on üks õige ja üks vale vastus"))}
  </div>
</div>

% if c.item.id:
   % if c.lang:
       ${h.lang_orig(h.literal(c.block.sisu))} 
       <div class="linebreak"></div>
       ${h.lang_tag()}
       ${h.ckeditor('f_sisu', c.block.tran(c.lang).sisu, 'gapmatch', ronly=False,
                    css='body{line-height:30px}',
                    baseHref='lang/%s/' % c.lang)}
   % else:
       ${h.ckeditor('f_sisu', c.block.sisu, 'gapmatch', ronly=False,
                    css='body{line-height:30px}')}
   % endif

% else:
${h.alert_notice(_("Lünki saab lisada peale sisuploki esmast salvestamist"))}
${h.ckeditor('f_sisu', c.block.sisu)}
% endif
       <div class="mb-3"></div>
       
<%
   choiceutils.choices(bkysimus, bkysimus.valikud, 'v', seosed=True, gentype='1', toolbar='gapmatchspan', joondus=bkysimus.gap_lynkadeta)
%>
<div class="btulemus" style="display:none">
<%
   btulemus = bkysimus.tulemus or c.new_item(kood=bkysimus.kood)
   c.is_edit_orig = c.is_edit
   c.is_edit = c.is_edit_hm
%>
  ${h.hidden('am1.kysimus_id', bkysimus.id)}
  ${choiceutils.tulemus(bkysimus, btulemus, 'am1.', caption=_("Muu vastuse (väljaspool lünka) hindamine"))}
<%
  c.is_edit = c.is_edit_orig
%>
</div>

% if c.block.sisuvaade and bkysimus.ridu==2:
<div class="floatleft">
  <table class="border" style="min-width:600px">
    <caption>${_("Vastuste analüüsis kuvatavate indeksite asukohad")}
      % if c.is_edit:
      (${_("uueneb salvestamisel")})
      % endif
    </caption>
    <tr>
      <td>
        <div class="ylesanne" style="position:relative">
          <%
             buf = c.block.tran(c.lang).sisuvaade or ''
          %>
          ${h.literal(c.block.replace_img_url(buf, lang=c.lang))}
        </div>
        <script>
          $(document).ready(function(){
             $.each($('div.ylesanne span.droppable-pos'), function(n, item){
                 var seq = $(item).attr('id').substr(4);
                 $(item).html(' <sub>'+seq+'</sub> ');
             });
          });
        </script>
      </td>
    </tr>
  </table>
</div>
% endif

</%def>


<%def name="block_print()">
${self.block_view(False)}
</%def>


<%def name="block_view(is_view=True)">
<% block_id=c.block.id %>
<% bkysimus = c.block.get_kysimus(seq=0) %>
<div id="block_${c.block_prefix}" class="asblock">
% if bkysimus.n_asend in (model.Kysimus.ASEND_PAREMAL, model.Kysimus.ASEND_PAREMAL_S):
  <div class="d-flex">
    <div style="padding:10px; line-height:30px" class="gaptext">
      ${h.literal(c.block.replace_img_url(c.block.tran(c.lang).sisuvaade or '', lang=c.lang))}
    </div>
    <div>
      ${self.block_view_bank(bkysimus)}
    </div>
  </div>
% else:
  <div style="padding:10px; line-height:30px" class="gaptext">
    ${h.literal(c.block.replace_img_url(c.block.tran(c.lang).sisuvaade or '', lang=c.lang))}
  </div>
  ## reavahetus
  <div style="clear:both;height:10px;"></div>
  ${self.block_view_bank(bkysimus)}
% endif

% if is_view:
## Vastuse väljad vormil
<% bkysimuskood = bkysimus.kood or 'X' %>
% if bkysimus.gap_lynkadeta:
  ${h.hidden(c.block_result, '', class_="blockresult-key")}
% else:
  % for k in c.block.kysimused:
  % if k != bkysimus:
     ${h.hidden(k.result, '', class_='blockresult', min_vastus=k.min_vastus)}
  % endif
  % endfor
% endif

% if c.read_only and c.prepare_correct:
${self.tip_correct()}
% endif
% endif
</div>
<div id="trash" class="invisible"></div>
</%def>

<%def name="block_view_bank(bkysimus)">
<%
  if bkysimus.n_asend == model.Kysimus.ASEND_PAREMAL_S:
      bcls = 'bank-right bank-sticky'
  elif bkysimus.n_asend == model.Kysimus.ASEND_PAREMAL:
      bcls = 'bank-right'
  else:
      bcls = 'bank-down'
%>
<div class="${bcls}">
  <div>${_("Vastuste pank")}</div>
  <div class="table">
      <div class="draggables p-3" style="line-height:30px">
        <%
          is_rtf = bkysimus.rtf
          gap_lynkadeta = bkysimus.gap_lynkadeta
          is_inlblock = is_rtf or not gap_lynkadeta
          valikud = list(bkysimus.valikud)
          if bkysimus.segamini and c.ylesandevastus:
             kv = c.responses.get(bkysimus.kood)
             model.apply_shuffle(valikud, kv and kv.valikujrk)

          valikud2 = []
          for subitem in valikud:
             sisu = subitem.tran(c.lang).nimi or ''
             if bkysimus.rtf:
                 sisu = h.literal(c.block.replace_img_url(sisu, lang=c.lang))
             if ' ' in sisu:
                 is_inlblock = True
             valikud2.append((sisu, subitem))
        %>
        % for sisu, subitem in valikud2:
        <%
           if subitem.joondus == const.JUSTIFY_CENTER:
              cls_joondus = 'drag-pos-c'
           elif subitem.joondus == const.JUSTIFY_RIGHT:
              cls_joondus = 'drag-pos-r'
           else:
              cls_joondus = 'drag-pos-l'

           # pikema teksti korral on vajalik, et lyngal ja lohistataval oleks display:inline-block
           # komade (vms ilma tyhikuteta lihttekst) lohistamise korral ei peaks seda olema
           # sest muidu võib koma jääda tekstis rea algusse          
           cls_inlblock = is_inlblock and 'inlblock' or ''
           if gap_lynkadeta:
               # tekitame koha, kust on lubatud rida poolitada
               if subitem.joondus == const.JUSTIFY_RIGHT:
                   sisu = ' ' + sisu
               else:
                   sisu = sisu + ' '
        %>
        % if gap_lynkadeta:
        <span id="i_${subitem.id}" kood="${subitem.kood}" draggable="true" class="draggable draggable-pos ${cls_inlblock}"
              max_vastus="${subitem.max_vastus}" min_vastus="${subitem.min_vastus}"><span class="border-draggable mayborder-draggable ${cls_joondus} ${cls_inlblock}">${h.ccode(subitem.kood)}${sisu}</span></span>
        % else:
        <span id="i_${subitem.id}" kood="${subitem.kood}" 
             class="draggable draggable-gap inlblock"
             max_vastus="${subitem.max_vastus}"
             min_vastus="${subitem.min_vastus}">
## et raam oleks samal real tekstiga, siis on siin ees yks tyhik
##          &nbsp;
         <span class="border-draggable mayborder-draggable inlblock">${h.ccode(subitem.kood)}${sisu}</span>
        </span>
        % endif
        % endfor
      </div>
  </div>
</div>
</%def>

<%def name="block_view_js()">
var igap_${c.block.id} = null;

function clear_${c.block_prefix}()
{
## viime kõik panka tagasi
  $.each($('div#block_${c.block_prefix} div.gaptext .draggable'), function(i, item){
    if(igap_${c.block.id})
       igap_${c.block.id}.igap_bank_drop($(item));
  });
}
function set_finished_${c.block.id}()
{
  if(igap_${c.block.id})
    igap_${c.block.id}.igap_set_finished($('div#block_${c.block_prefix}'));
}
$(function(){
## saab vastata
  ## muudame valikud lohistatavateks ja lüngad lohistatavaid vastu võtvateks
   igap_${c.block.id} = new igap_setup('${c.block_prefix}', ${not c.block.read_only and 'true' or 'false'});
% if not c.block.read_only:    
   set_finished_${c.block.id}();
% endif

  % if c.show_q_code:
  ## iga lynga ees kuvatakse lynga kood
  % if c.block.kysimus.gap_lynkadeta:
  <%
      # kui lynka pole, siis positsiooni nr; kui on lynk, siis lynga kysimuse kood 
      map2k = dict()
      for k in c.block.kysimused:
          if k.seq > 0: map2k[k.seq] = k.kood
  %>
  $.each($('div#block_${c.block_prefix} span.droppable-pos'), function(n, item){
       var seq = $(item).attr('id').substr(4);
       var h_kood = ' <sub>' + seq + '</sub> ';
       % for key, val in map2k.items():
       if(seq == '${key}') h_kood = ' <span class="kysimus">${val}</span> ';
       % endfor
       $(item).html(h_kood);
  });
  % else:
  $.each($('div#block_${c.block_prefix} .droppable-gap'), function(n, item){
   $(item).before('<span class="kysimus">'+item.id+'</span>');
  });
  % endif
  % endif

  % if c.block_correct or c.block.naide:
    ${self.js_show_response(c.correct_responses)}
  % else:
    ${self.js_show_response(c.responses)}
  % endif
  is_response_dirty = false;
});
</%def>

<%def name="js_show_response(responses, for_resp=True)">
clear_${c.block_prefix}();
<% bkysimus = c.block.get_kysimus(seq=0) %>
% for k in c.block.kysimused:
<% kv = responses.get(k.kood) %>
  % if kv:
   <%
     tulemus = k.tulemus
     kvsisud = kv.get_kvsisud()
   %>
    % for ks in kvsisud:
        ${self.js_show_response_item(responses, k, kv, tulemus, ks, ks.sisu, ks.kood1, for_resp)}
    % endfor
  % endif
% endfor
</%def>

<%def name="js_show_response_item(responses, k, kv, tulemus, ks, lyngata_seq, v_kood, for_resp)">
<%
  sel_item = h.literal('div#block_%s .draggables span[kood="%s"]' % (c.block_prefix, h.chk_w(v_kood)))
  if lyngata_seq:
      # lynkadeta
      cell_id = '_seq%s' % lyngata_seq
  else:
      cell_id = k.kood
  sel_cell = h.literal('div#block_%s span[id="%s"]' % (c.block_prefix, cell_id))
%>
  % if cell_id:
     var cell = $('${sel_cell}').filter(
       function(){
          return $(this).closest('.asblock').attr('id')=='block_${c.block_prefix}';
     });
     var item = $('${sel_item}').filter(
       function(){
          return $(this).closest('.asblock').attr('id')=='block_${c.block_prefix}';
     });
   % if v_kood:
     igap_${c.block.id}.igap_drop(item, cell);
   % endif
   % if c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
     % if v_kood:
     $('${sel_cell}>.draggable[kood="${v_kood}"]').addClass('${model.ks_correct_cls(responses, tulemus, kv, ks, True, for_resp)}');
     % else:
     ## tyhi lynk, vastamata vastus
     $('${sel_cell}').addClass('${model.ks_correct_cls(responses, tulemus, kv, ks, False, for_resp)}');
     % endif
   % endif
  % endif
</%def>

<%def name="tip_correct()">
## õige vastuse kuvamine
<% any_tip = False %>
% for kysimus in c.block.pariskysimused:
<%
  kood = kysimus.kood
  kv = c.correct_responses.get(kood)
%>
   % if kv:
   % for ks in kv.kvsisud:
<% any_tip = True %>
<div class="tip-correct" id="_DC_${kood}" data-value="${ks.kood1}"> </div>
   % endfor
   % endif
% endfor
% if any_tip:
<script>
$(function(){
  var block = $('div#block_${c.block_prefix}');
  var fields = block.find('.droppable-gap').filter(
     function(){
        return $(this).closest('.asblock').attr('id')=='block_${c.block_prefix}';
     });
  fields.tooltip({
     html: true,
     title: function(){ 
          var id = this.id, v = $('.tip-correct#_DC_' + id).data('value'),
          f = block.find('.draggable[kood="' + v + '"]');
          if(f.length) return f.clone().removeClass('draggable').removeClass('draggable-gap');
     }
  });
});
</script>
% endif
</%def>
