## Liugur
<%inherit file="baasplokk.mako"/>
<!-- ${self.name} -->
<%namespace name="choiceutils" file="choiceutils.mako"/>

<%def name="block_before()">
<% c.kyslisa = c.block.kysimus.kyslisa %>
</%def>

<%def name="block_edit()">
<% c.kyslisa = c.block.kysimus.give_kyslisa() %>
<% ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') %>
<div class="row mb-1">
  <% name = 'sl.min_vaartus' %>
  ${ch.flb(_("Vahemiku algus"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.text5('sl.min_vaartus', c.kyslisa.min_vaartus)}
  </div>
  <% name = 'sl.max_vaartus' %>
  ${ch.flb(_("Vahemiku lõpp"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.text5('sl.max_vaartus', c.kyslisa.max_vaartus)}
  </div>

  <% name = 'sl.samm' %>
  ${ch.flb(_("Samm"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.text5('sl.samm', c.kyslisa.samm)}
  </div>
  <% name = 'sl.yhik' %>
  ${ch.flb(_("Ühik"), name)}
  <div class="col-md-3 col-xl-1">
      % if c.lang:
        ${h.lang_orig(c.kyslisa.yhik)}
       <div class="linebreak"></div>
        ${h.lang_tag()}
        ${h.text('sl.yhik', c.kyslisa.tran(c.lang).yhik, maxlength=15, ronly=not c.is_tr)}       
      % else:
        ${h.text('sl.yhik', c.kyslisa.yhik, maxlength=15, ronly=not c.is_tr and not c.is_edit)}       
      % endif
  </div>
</div>
<div class="row mb-1">
  <div class="col-md-3">
    ${h.checkbox1('sl.samm_nimi', 1, checked=c.kyslisa.samm_nimi,
    label=_("Näidata skaalat"))}
  </div>
  <div class="col-md-4">
    ${h.checkbox1('sl.tagurpidi', 1, checked=c.kyslisa.tagurpidi,
    label=_("Näidata vahemikku tagurpidi"))}
    <br/>
    ${h.checkbox1('sl.vertikaalne', 1, checked=c.kyslisa.vertikaalne,
    label=_("Vertikaalne paigutus"))}
  </div>
  <div class="col-md-5">
    ${h.checkbox('sl.asend_vasakul', 1, checked=c.kyslisa.asend_vasakul,
    label=_("Kuvada vastus vasakul"))}
    <br/>
    ${h.checkbox('sl.asend_paremal', 1, checked=c.kyslisa.asend_paremal,
    label=_("Kuvada vastus paremal"))}      
  </div>
</div>

${choiceutils.hindamismaatriks(c.block.kysimus,basetype_opt=c.opt.tulemus_baseType_arv, heading1=_("Vastus"))}
</%def>

<%def name="block_view()">
<%
   kysimus = c.block.kysimus
   kv = c.responses.get(kysimus.kood)
   if kv and len(kv.kvsisud):
      ks = kv.kvsisud[0]
      slider_value = ks.sisu and float(ks.sisu.replace(',','.'))
   else:
      ks = None
      slider_value =  c.kyslisa.min_vaartus
   c.slider_value = slider_value

   if c.kyslisa.vertikaalne:
      slider_height = "300px"
      slider_width = "30px"
      slider_style = "height:100%"
   else:
      slider_height = "30px"
      slider_width = "500px"
      slider_style = "width:100%"

   if c.prepare_correct and ks and ks.on_hinnatud and not c.block.varvimata:
      corr_cls = model.ks_correct_cls(c.responses, kysimus.tulemus, kv, ks, False) or ''
   else:
      corr_cls = ''
%>
${h.qcode(kysimus)}

% if not c.kyslisa.vertikaalne:
## HORISONTAALNE LIUGUR
<table style="padding:10px;" class="${corr_cls}">
  <tr>
    % if c.kyslisa.asend_vasakul:    
    <td></td>
    % endif
    <td>
      ## skaala koht horisontaalse slaideri korral
      ${self.scale_horizontal(c.kyslisa)}
    </td>
    % if c.kyslisa.asend_paremal:        
    <td></td>
    % endif
  </tr>
  <tr height="${slider_height}">
    % if c.kyslisa.asend_vasakul:
    <td width="50px" align="left" nowrap>
      <span id="${c.block_result}2" style="font-weight:bold;">${h.fstr(slider_value)}</span>
      ${c.kyslisa.tran(c.lang).yhik}
    </td>
    % endif
    <td>
      <table width="100%" style="table-layout:fixed;" cellpadding="0" colspacing="0">
        <% width1 = int(50. / c.scale_cnt) %>
        <col width="${width1}%"/>
        <col width="${100 - 2 * width1}%"/>
        <col width="${width1}%"/>
        <tr>
          <td></td>
          <td width="${slider_width}" id="slider_height_${c.block.id}" align="left">
            ## slaideri koht
            <div id="slider_${c.block_prefix}" style="${slider_style}" style="background-color:#ff0000;"></div>
          </td> 
          <td></td>
        </tr>
      </table>
    </td>
    % if c.kyslisa.asend_paremal:    
    <td width="50px" align="right" nowrap>
      ## vastuse koht
      <span id="${c.block_result}" style="font-weight:bold;">${h.fstr(slider_value)}</span>
      ${c.kyslisa.tran(c.lang).yhik}
    </td>
    % endif
  </tr>
</table>
${h.hidden(kysimus.result, slider_value)}
% else:
## VERTIKAALNE LIUGUR
<table style="padding:10px" class="${corr_cls}">
  <tr height="${slider_height}">
    % if c.kyslisa.asend_vasakul:
    <td width="50px" align="left" nowrap>
      ## vastuse koht
      <span id="${c.block_result}2" style="font-weight:bold;">${h.fstr(slider_value)}</span>
      ${c.kyslisa.tran(c.lang).yhik}
    </td>
    % endif
    <td id="scale_height_${c.block.id}">
      ## skaala koht vertikaalse slaideri korral
      ${self.scale_vertical(c.kyslisa)}
    </td>
    <td width="${slider_width}" id="slider_height_${c.block.id}" valign="center">
      <div id="slider_${c.block_prefix}"></div>
    </td>
    % if c.kyslisa.asend_paremal:
    <td width="50px" align="right" nowrap>
      ## vastuse koht
      <span id="${c.block_result}" style="font-weight:bold;">${h.fstr(slider_value)}</span>
      ${c.kyslisa.tran(c.lang).yhik}
    </td>
    % endif
  </tr>
</table>
${h.hidden(kysimus.result, slider_value)}
% endif
<% 
if c.resize_prefixes == '':
   c.resize_prefixes = []
c.resize_prefixes.append((c.y_prefix, c.block_prefix))
%>
</%def>

<%def name="block_view_js()">
<% kysimus = c.block.kysimus %>
function resize_${c.block_prefix}()
{
    var div_sl = $('#slider_${c.block_prefix}');
    var scale = $('table#scale_${c.block_prefix}');

% if c.kyslisa.vertikaalne:
    ## muudame skaala kõik read ühekõrguseks
    var height = $('#slider_height_${c.block.id}').height();
    ##scale.find('tr').css('height', (height-30)/${c.scale_cnt});

    ## liugur olgu skaalast lühem, et skaala otsades olevad arvud jääks otsa peale
    div_sl.height(height*(1-1./${c.scale_cnt})*.95);
% else:
    ## liugur olgu skaalast kitsam, et skaala otsades olevad arvud jääks otsa peale
    var width = scale.width();
    ##div_sl.width(width*(1-1./${c.scale_cnt}));
% endif
}

$(function(){
    var div_sl = $('#slider_${c.block_prefix}');
    var scale = $('table#scale_${c.block_prefix}');
% if c.kyslisa.vertikaalne:
    ## muudame skaala kõik read ühekõrguseks
    var height = $('#slider_height_${c.block.id}').height();
    scale.find('tr').css('height', (height-30)/${c.scale_cnt});
% endif
    resize_${c.block_prefix}();
  
    div_sl.slider({
% if c.kyslisa.min_vaartus is not None:
  min:${c.kyslisa.min_vaartus}, 
% endif
% if c.kyslisa.max_vaartus is not None:
  max:${c.kyslisa.max_vaartus}, 
% endif
% if c.kyslisa.samm:
  step:${c.kyslisa.samm},
% endif
% if c.kyslisa.vertikaalne:
  orientation:'vertical',
% endif
% if c.kyslisa.tagurpidi:
  value: ${c.kyslisa.max_vaartus+c.kyslisa.min_vaartus-c.slider_value},
% else:
  value: ${c.slider_value},
% endif

% if c.block.read_only:
## ei saa vastust muuta
  disabled: 'disabled',
% endif
  slide: function(event, ui){
% if c.kyslisa.tagurpidi:
      var value = ${c.kyslisa.max_vaartus}+${c.kyslisa.min_vaartus}-ui.value;
% else:
      var value = ui.value;
% endif
      $('span[id="${c.block_result}"]').html(fstr(value));
      $('span[id="${c.block_result}2"]').html(fstr(value));
  },
  change: function(event, ui){
% if c.kyslisa.tagurpidi:
      var value = ${c.kyslisa.max_vaartus}+${c.kyslisa.min_vaartus}-ui.value;
% else:
      var value = ui.value;
% endif
      var result = $('input[name="${kysimus.result}"]');
      result.val(value);
      $('span#${c.block_result}').html(fstr(value));
      $('span#${c.block_result}2').html(fstr(value));
      if(typeof response_changed == 'function')
         response_changed(result);
  }
  });
  ## liugurile vastamine on alati lõpetatud
  set_sp_finished($('input[name="${kysimus.result}"]'), true);
  % if c.block_correct or c.block.naide:
  ${self.js_show_response(c.correct_responses)}
  % else:
  ${self.js_show_response(c.responses)}
  % endif
  is_response_dirty = false;
});
</%def>

<%def name="scale_horizontal(kyslisa)">
<table width="100%" style="table-layout:fixed" id="scale_${c.block_prefix}">
% if kyslisa.samm_nimi:
## näidata skaalat
   <% 
      # näidata skaalat
      step = kyslisa.samm or (kyslisa.max_vaartus-kyslisa.min_vaartus)/10
      cnt = c.scale_cnt = int((kyslisa.max_vaartus-kyslisa.min_vaartus)/step) + 1
   %>
   % for n in range(cnt):
   <col width="${'%.2f' % (100./cnt)}%"/>
   % endfor
  <tr>
   % for n in range(cnt):
     <td align="center">
     % if kyslisa.tagurpidi:
     ${h.fstr(kyslisa.max_vaartus-n*step)}
     % else:
     ${h.fstr(kyslisa.min_vaartus+n*step)}
     % endif
     </td>
   % endfor
  </tr>
% else:
## skaalat ei kuva, aga tabel on vajalik, kuna selle laiuse järgi tehakse liugur
  <%
    c.scale_cnt = 50
  %>
  <tr><td></td></tr>
% endif
</table>
</%def>

<%def name="scale_vertical(kyslisa)">
<table height="100%" id="scale_${c.block_prefix}">
% if kyslisa.samm_nimi:
## näidata skaalat
   <% 
      # näidata skaalat
      step = kyslisa.samm or (kyslisa.max_vaartus-kyslisa.min_vaartus)/10
      cnt = c.scale_cnt = int((kyslisa.max_vaartus-kyslisa.min_vaartus)/step)+1
   %>
   % for n in range(cnt):
   <tr height="${'%.2f' % (100./cnt)}%" valign="center">
     <td>
     % if kyslisa.tagurpidi:
     ${h.fstr(kyslisa.min_vaartus+n*step)}
     % else:
     ${h.fstr(kyslisa.max_vaartus-n*step)}
     % endif
     </td>
   </tr>
   % endfor
% else:
   <%
      c.scale_cnt = 50
   %>
   <tr><td></td></tr>
% endif
</table>
</%def>

<%def name="js_show_response(responses)">
<%
  kysimus = c.block.kysimus
  kv = responses.get(kysimus.kood)
%>
  % if kv:
  <%
    if kv and len(kv.kvsisud):
       ks = kv.kvsisud[0]
       value = ks.sisu and float(ks.sisu.replace(',','.'))
    else:
       ks = None
       value = c.kyslisa.min_vaartus
    if c.kyslisa.tagurpidi:
       lvalue = c.kyslisa.max_vaartus + c.kyslisa.min_vaartus - value
    else:
       lvalue = value 
  %>
  $("#slider_${c.block_prefix}").slider({value:${lvalue}});
  $('span#${c.block_result}').html('${h.fstr(value)}');
  $('span#${c.block_result}2').html('${h.fstr(value)}');
  % endif
</%def>
