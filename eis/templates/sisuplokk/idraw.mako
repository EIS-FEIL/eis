## -*- coding: utf-8 -*- 
## Joonistamine
<%inherit file="baasplokk.mako"/>
<%namespace name="choiceutils" file="choiceutils.mako"/>
<%namespace name="graphutils" file="graphutils.mako"/>
<!-- ${self.name} -->

<%def name="block_before()">
<%
   ## joonistustarbed
   kysimus = c.block.kysimus
   c.joonistamine = kysimus.joonistamine
   if not c.joonistamine and c.is_edit:
      c.joonistamine = kysimus.give_joonistamine()
   tool_list = c.joonistamine and c.joonistamine.tarbed_list or []
   if len(tool_list) > 0: 
      c.default_tool = tool_list[0]
   else:
      c.default_tool = '' 
   c.arvutihinnatav = c.joonistamine and c.joonistamine.on_arvutihinnatav
%>
</%def>

<%def name="block_edit()">
  ${graphutils.edit_background(c.block, min_max=c.arvutihinnatav)}

<% ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') %>
<div class="row">
  <div class="col-md-4">
    ${h.checkbox1('jo.on_arvutihinnatav', 1, checked=c.arvutihinnatav, 
    label=_("Arvutihinnatav joon"), class_="nosave", onchange='dirty=false;this.form.submit()')}

    % if c.arvutihinnatav:
    ${h.hidden('jo.on_seadistus','')}
    % else:
    <br/>
    ${h.checkbox1('jo.on_seadistus', checked=c.joonistamine.on_seadistus, label=_("Seadistamine lubatud"))}
    % endif
  </div>
  <div class="col-md-8 d-flex flex-wrap">
    <b class="mr-3">${_("Joonistustarbed")}</b>
    <div>
    <%
      tools = c.arvutihinnatav and c.opt.tools_line or c.opt.tools 
    %>
    % for tool in tools:
    ${h.checkbox('jo.tarve', value=tool[0], checkedif=c.joonistamine.tarbed_list, label=tool[1])}
    % endfor
    </div>
  </div>
</div>

<% mo = c.block.taustobjekt %>
% if mo and mo.has_file:
  ${graphutils.sketchpad(c.block)}
  ${h.hidden(c.block_result, c.block.sisuvaade)}

  ## hindamismaatriksi vastuse joonistamise tööriistad
   ${graphutils.btn_undo(c.block_prefix)}
  <div class="d-inline-block p-2 rounded border" >
    <% c.joonistamine.on_seadistus = True %>
    ${self.toolbox_draw(c.block, c.joonistamine, True)}
  </div>

  ## hindamismaatriks
  ${choiceutils.hindamismaatriks_pt(c.block.kysimus, 'am1', is_sallivus=True, naidis=True, naidis_naha=False, maatriks=c.arvutihinnatav)}
  
  % if c.arvutihinnatav:
  <script>
  $(function() {
  ${graphutils.js_sketchpad(c.block)}
  sketchpad.make_drawable();  
  ${graphutils.js_show_hindamismaatriks_pt(c.block.kysimus.tulemus)}
  sketchpads.sketchpad_${c.block_prefix}.tool = '${c.default_tool or "polyline"}';
  });
  </script>

  % else:
  ## pole arvutihinnnatav, aga koostaja saab sisestada näidisvastuse
  <script>
  $(function() {
    ${graphutils.js_sketchpad(c.block, require_id=False, drag_images=False)}
    sketchpad.make_drawable();
    % if c.default_tool:
    select_tool_${c.block_prefix}('${c.default_tool}');
    % endif
    ${self.js_show_sample()}
  });
  </script>
  % endif
% endif

</%def>


<%def name="block_view()">
<%
  kysimus = c.block.kysimus
%>
${h.qcode(kysimus)}
${graphutils.sketchpad(c.block)}
${h.hidden(kysimus.result, '', id=c.block_result, readonly=True)}

% if not c.block.read_only:
   ${graphutils.btn_undo(c.block_prefix)}
   ${self.toolbox_draw(c.block, c.joonistamine, len(c.joonistamine.tarbed_list)>0)}
% endif
</%def>

<%def name="block_view_js()">
<% kysimus = c.block.kysimus %>
$(function(){
  ${graphutils.js_sketchpad(c.block, require_id=False)}
  % if c.arvutihinnatav:
    % if not c.block.read_only:
    sketchpad.save_shapes = true;   
    sketchpad.min_choices = ${kysimus.min_vastus or 0};
    sketchpad.max_choices = ${kysimus.max_vastus or 'null'};
    % endif
  % endif
  % if not c.block.read_only:
      % if c.default_tool:
    select_tool_${c.block_prefix}('${c.default_tool}');
      % endif
    sketchpad.make_drawable();
  % else:
    $('table#toolbox_${c.block_prefix} :input').attr('disabled','disabled');
    $('table#toolbox_${c.block_prefix} a').removeAttr('onclick');
  % endif

  % if c.block_correct or c.block.naide:
    ${self.js_show_response(c.correct_responses)}
  % else:
    ${self.js_show_response(c.responses)}
  % endif
  is_response_dirty = false;
  resized();
});
</%def>

<%def name="block_print()">
 ${graphutils.print_img(c.block.taustobjekt)}  
</%def>

<%def name="block_preview()">
 ${graphutils.print_img(c.block.taustobjekt)}  
</%def>


<%def name="toolbox_draw(item, jo, is_show)">
     <script>
     function select_tool_${c.block_prefix}(value)
     {
        var box = $('#toolbox_${c.block_prefix}');
        sketchpads.sketchpad_${c.block_prefix}.tool = value;
     % if jo.on_seadistus:
        if(value == 'text')
        {
           box.find('.box_text').show();
           box.find('.box_shape').hide();
        }
        else if(value == 'line')
        {
           box.find('.box_shape').show();
           box.find('.box_fill').hide();
           box.find('.box_text').hide();
        }
        else
        {
           box.find('.box_shape').show();
           box.find('.box_fill').show();       
           box.find('.box_text').hide();
        }
     % else:
        box.find('.box_text_settings').hide();
        if(value == 'text')
        {
           box.find('.box_text').show();
        }
        else
        {
           box.find('.box_text').hide();
        }
        box.find('.box_fill').hide();
        box.find('.box_fill_color').hide();
        box.find('.box_shape').hide();
     % endif
        resized();
     };
     </script>
% if is_show:
<div id="toolbox_${c.block_prefix}" class="my-2">
  <div id="toolbuttons">
    % if len(jo.tarbed_list) > 1:
        <% tools = c.arvutihinnatav and c.opt.tools_line or c.opt.tools %>
        % for tool in tools:
        % if tool[0] in jo.tarbed_list:
        <% onclick = "select_tool_%s('%s')" % (c.block_prefix, tool[0]) %>
        ${h.radio('radio', '', onclick=onclick, id='tool_%s' % tool[0], label=tool[1])}
        % endif
        % endfor
    % endif
  </div>

  <% ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') %>

  <div class="row">
    <div class="col-12 col-md-3 box_shape">
      ${h.flb(_("Joone laius"), "draw_width")}
      ${h.select('draw_width', jo.stroke_width or 2, range(1,20), class_="noresponse")}
    </div>
    <div class="col-12 col-md-3 box_shape">
      ${h.flb(_("Joone värv"), "draw_stroke")}
      ${h.text('draw_stroke', jo.stroke_color or '0000ff', class_='colorwell noresponse jscolor')}
    </div>

    <div class="col-12 col-md-3 box_fill">
      <br/>
      ${h.checkbox1('draw_fill_none', 1, checked=jo.fill_none, class_='noresponse', onclick='$("#box_fill_color").toggle(!this.checked);', label=_("Täide puudub"))}
    </div>
    <div class="col-12 col-md-3 box_fill box_fill_color">
      ${h.flb(_("Täitevärv"), 'draw_fill')}
      ${h.text('draw_fill', jo.fill_color or '0000ff', class_='colorwell noresponse jscolor')}
    </div>
    <div class="col-2 col-md-3 box_fill box_fill_color">
      ${h.flb(_("Läbipaistvus"), 'draw_fill_opacity')}
      ${h.select('draw_fill_opacity', jo.fill_opacity and jo.fill_opacity or '.5', ['.1','.2','.3','.4','.5','.6','.7','.8','.9','1'], class_='noresponse')}
    </div>
    <div class="col-12 col-md-3 box_text box_text_settings">
      ${h.flb(_("Teksti suurus"), 'draw_fontsize')}
      ${h.select('draw_fontsize', jo.fontsize or 14, [8,10,12,14,16,18,20,24,28,32,36], class_='noresponse')}
    </div>
    <div class="col-12 col-md-3 box_text box_text_settings">
      ${h.flb(_("Värv"), 'draw_textfill')}
      ${h.text('draw_textfill', jo.textfill_color or '0000ff', class_='colorwell noresponse jscolor')}
    </div>
    <div class="col box_text">
      ${h.flb(_("Tekst"), 'keycatcher')}
      ${h.text('keycatcher', '', class_="noresponse")}
    </div>
  </div>
</div>
% endif
</%def>

<%def name="block_entry()">
<div class="td-sis-value2">${_("Joonistus pole sisestatav")}</div>
</%def>

<%def name="js_show_response(responses)">
  var sketchpad = sketchpads.sketchpad_${c.block_prefix};
  sketchpad.clear();
<%
  kysimus = c.block.kysimus
  kv = responses.get(kysimus.kood)
%>
   % if kv:
   % for ks in kv.kvsisud:
      % if c.arvutihinnatav:
           ## arvutihinnatav
           <%
             points = ks.koordinaadid
             shape = ks.kujund or 'polyline'
           %>
           var node = sketchpad.drawShapeId(${points}, '${shape}');
           sketchpad.result.push(['${shape}', '${points}']);
          % if c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
           <% on_max_p = model.ks_on_max_p(responses, kysimus.tulemus, kv, ks, False) %>
           % if on_max_p is not None:
           sketchpad.show_node_correct(node, ${on_max_p and 'true' or 'false'});
           % endif
          % endif
       % else:
           ## pole arvutihinnatav
           ## vastus on skript
           with(sketchpad){
             ${h.literal(ks.sisu)}
             save_image();
           }
          % if c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
           <% corr_cls = model.ks_correct_cls(responses, kysimus.tulemus, kv, ks, False) %>
           % if corr_cls:
           $(sketchpad.div).addClass('${corr_cls}');
           % endif
          % endif
      % endif
   % endfor
   % endif
    sketchpad.save_image();
    sketchpad.set_finished();           
</%def>

<%def name="js_show_sample()">
  var sketchpad = sketchpads.sketchpad_${c.block_prefix};
  sketchpad.clear();
  with(sketchpad){
  ${h.literal(c.block.sisuvaade or '')}
  save_image();
  }
</%def>
