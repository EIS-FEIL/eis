## Teekonna märkimine
<%inherit file="baasplokk.mako"/>
<%namespace name="graphutils" file="graphutils.mako"/>
<%namespace name="choiceutils" file="choiceutils.mako"/>
<!-- ${self.name} -->

<%def name="block_before()">
<% c.kyslisa = c.block.kysimus.kyslisa %>
</%def>

<%def name="block_edit()">
<% c.kyslisa = c.block.kysimus.give_kyslisa() %>
${graphutils.edit_background(c.block, min_max=False)}

<% mo = c.block.taustobjekt %>
<% ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') %>

<% kysimus = c.block.kysimus %>
<div class="row mt-1">
  ${ch.flb(_("Ridade arv"), 'lridu')}
  <div class="col-md-3 col-xl-1">
    ${h.posint5('l.ridu', kysimus.ridu)}
  </div>
  ${ch.flb(_("Veergude arv"), 'lpikkus')}
  <div class="col-md-3 col-xl-1">
    ${h.posint5('l.pikkus', kysimus.pikkus)}
  </div>
</div>

% if mo and mo.has_file:
<div class="row mb-1">
  ${ch.flb(_("Algusruut"), 'tlalgus')}
  <div class="col-md-9 col-xl-10">
      ${h.text('tl.algus', c.kyslisa.algus, style="width:80%;display:inline-block", class_='trail')}
      % if not c.is_edit:
      ${h.hidden('tl.algus', c.kyslisa.algus, class_='trail')}
      % endif
      <a href='#' class="zoom" title="${_("Näita")}">
        <i class="mdi mdi-image-search-outline mdi-24px"></i>
      </a>
      
      <script>
        $(function(){
          $('input.trail').change(function(){
          sketchpads.sketchpad_${c.block_prefix}.modify_trailable(
             $('input[name="tl.algus"]').val(),
             $('input[name="tl.labimatu"]').val(),
             $('input[name="tl.lopp"]').val());
          });
          $("input.trail").focus(function(){
             sketchpads.sketchpad_${c.block_prefix}.edit_trail($(this), true);
          });
          $("a.zoom").click(function(){
% if c.is_edit:
            sketchpads.sketchpad_${c.block_prefix}.edit_trail($(this).siblings('input.trail'), true);
% else:
            sketchpads.sketchpad_${c.block_prefix}.show_trail($(this).siblings('input.trail').val(), true);
% endif
            return false;        
           });        
         });
      </script>
  </div>

  ${ch.flb(_("Lõppruut"), 'tllopp')}
  <div class="col-md-9 col-xl-10">
      ${h.text('tl.lopp', c.kyslisa.lopp,  style="width:80%;display:inline-block", class_='trail')}

      % if not c.is_edit:
      ${h.hidden('tl.lopp', c.kyslisa.lopp, class_='trail')}
      % endif
      <a href='#' class="zoom" title="${_("Näita")}">
        <i class="mdi mdi-image-search-outline mdi-24px"></i>
      </a>
  </div>

  ${ch.flb(_("Läbimatud ruudud"), 'tllabimatu')}
  <div class="col-md-9 col-xl-10">
    ${h.text('tl.labimatu', c.kyslisa.labimatu, style="width:80%;display:inline-block", class_='trail')}    
      % if not c.is_edit:
      ${h.hidden('tl.labimatu', c.kyslisa.labimatu, class_='trail')}
      % endif
      <a href='#' class="zoom" title="${_("Näita")}">
        <i class="mdi mdi-image-search-outline mdi-24px"></i>
      </a>
  </div>
</div>

<div class="d-flex flex-wrap">
  <div class="mr-5">
    ${graphutils.sketchpad(c.block)}
  </div>
  ${self.descriptions(kysimus)}
</div>
<script>
$(function() {
  ${graphutils.js_sketchpad(c.block)}
  sketchpad.make_drawable();
  drawGrid();
  $('input[name="l.ridu"],input[name="l.pikkus"]').change(drawGrid);
  ${graphutils.js_trailable(c.block, kysimus)}  
});
  function drawGrid()
  {
  var rows = parseInt($('input[name="l.ridu"]').val());
  var cols = parseInt($('input[name="l.pikkus"]').val());
  if(rows != NaN && rows > 0 && cols != NaN && cols > 0)
     sketchpads.sketchpad_${c.block_prefix}.draw_trail_grid(rows, cols, false);
  }
</script>
<%
   choiceutils.hindamismaatriks_trail(c.block.kysimus,'am1', maatriks=True)
%>
% endif
</%def>

<%def name="descriptions(kysimus)">
% if kysimus.ridu and kysimus.pikkus:
<table>
  <caption>${_("Ruutude selgitused")}</caption>
  <thead>
    <tr>
      <th></th>
      % for x in range(kysimus.pikkus):
      <td class="text-center">${x}</td>
      % endfor
    </tr>
  </thead>
  <tbody>
    <%
      seq = -1
      valikud = {v.kood: v for v in kysimus.valikud}
    %>
    % for y in range(kysimus.ridu):
    <tr>
      <td class="px-3">${y}</td>
      % for x in range(kysimus.pikkus):
      <td>
        <%
          seq += 1
          kood = f'{x}_{y}'
          v = valikud.get(kood)
          value = v and v.selgitus or None
        %>
        ${h.text('v-%d.selgitus' % seq, value, size=8, placeholder=kood)}
        ${h.hidden('v-%d.kood' % seq, kood)}
        ${h.hidden('v-%d.nimi' % seq, kood)}
        ${h.hidden('v-%d.id' %seq, v and v.id or '')}
      </td>
      % endfor
    </tr>
    % endfor
  </tbody>
</table>
% endif  
</%def>

<%def name="block_view()">
<% kysimus = c.block.kysimus %>
${h.qcode(kysimus, nl=True)}
${graphutils.sketchpad(c.block)}
${h.hidden(kysimus.result, '', id=c.block_result, readonly=True)}
</%def>

<%def name="block_view_js()">
$(function(){
  ${graphutils.js_sketchpad(c.block, drag_images=True)}
  <% kysimus = c.block.kysimus %>
  var sketchpad = sketchpads.sketchpad_${c.block_prefix};
  sketchpad.draw_trail_grid(${kysimus.ridu or 0}, ${kysimus.pikkus or 0}, null, ${c.block.read_only and 'true' or 'false'});

  % if not c.block.read_only:
  ${graphutils.js_trailable(c.block, kysimus)}
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
  <table>
    <tr>
      <td valign="top">
        ${graphutils.print_hotspots(c.block)}
      </td>
      <td valign="top">
        ${graphutils.print_drag_images(c.block)}
      </td>
    </tr>
  </table>
</%def>


<%def name="block_entry()">
## eelnevalt on seatud c.responses ja c.prefix
    <%
      kysimus = c.block.kysimus
      kv = c.responses.get(kysimus.kood) or []
      kv2 = c.responses2 and c.responses2.get(kysimus.kood) or []
    %>
    % if c.is_correct:
        ## sisestatakse, kas vastus on õige või vale
        ${self.block_entry_correct(kysimus, kv, kv2)}
    % else:
        ${self.block_entry_pair(kysimus, kv, kv2,
                                kysimus.valikud_opt,
                                c.block.piltobjektid_opt)}
    % endif
</%def>

<%def name="js_show_response(responses)">
% if c.block.taustobjekt:
  var sketchpad = sketchpads.sketchpad_${c.block_prefix};
  sketchpad.clear_trailables();
  sketchpad.clear();

## liigutame pildid sinna, kuhu kasutaja need pani
  <% 
    pilt_cnt = {} 
    kysimus = c.block.kysimus
    kv = responses.get(kysimus.kood)
  %>
  % if kv:
  % for ks in kv.kvsisud:
  <%
    # ks.sisu - vastaja vastus; ks.kood1 - hindamismaatriksi õige vastus
    trail_resp = h.js_str1(ks.sisu or ks.kood1)
  %>
    sketchpad.show_trail('${trail_resp}');

  % if c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
    <% on_max_p = model.ks_on_max_p(responses, kysimus.tulemus, kv, ks, False) %>
    % if on_max_p is not None:
    sketchpad.show_trail_correct('${trail_resp}', ${on_max_p and 'true' or 'false'});
    % endif
  % endif
  
  % endfor
  % endif
  % if not c.block.read_only:  
    sketchpad.serialize_result();
  % endif
% endif
</%def>
