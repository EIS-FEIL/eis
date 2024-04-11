## Tekstide lohistamine
<%inherit file="baasplokk.mako"/>
<%namespace name="graphutils" file="graphutils.mako"/>
<%namespace name="choiceutils" file="choiceutils.mako"/>
## Tekstipiltide lohistamine
<!-- ${self.name} -->

<%def name="block_edit()">
${graphutils.edit_background(c.block)}
<% mo = c.block.taustobjekt %>
% if mo and mo.has_file:
${graphutils.sketchpad(c.block)}
<%
  bkysimus = c.block.kysimus # seq==1
  kysimused = [k for k in c.block.kysimused if k.seq > 1]
%>
<script>
$(function() {
  ${graphutils.js_sketchpad(c.block)}
  sketchpad.make_drawable();
  % for kysimus in kysimused:
  ${graphutils.js_show_hindamismaatriks_pt(kysimus.tulemus)}
  % endfor
});
</script>
${graphutils.toolbox_area(c.block)}

% for i, kysimus in enumerate(kysimused):
<% valik = bkysimus.get_valik(kysimus.kood) %>
<div class="rounded border m-3 p-3">
  % if valik:
  <div class="dragtxpos dragtxpos-border">
    ${valik.tran(c.lang).nimi}
  </div>
  <div style="clear:both"></div>
  % endif
  ${choiceutils.hindamismaatriks_pt(kysimus, 'am-%s' % i)}
</div>
% endfor

<div class="linebreak" style="height:8px;"></div>
${choiceutils.choices(bkysimus, bkysimus.valikud, 'v', caption=_("Lohistatavad tekstid"), ck_height='100', txpos=True, toolbar='basic', valista=True)}
<div>
  ${graphutils.edit_drag_images_pos(c.block, True)}
</div>

% for ind, valista_kood in enumerate(c.ylesanne.get_kysimus_koodid(c.block)):
${h.hidden('valista%d' % ind, valista_kood, class_='valista')} 
% endfor
% endif
</%def>

<%def name="block_view()">
<% bkysimus = c.block.kysimus %>
${graphutils.sketchpad_in_dragtbl(c.block, bkysimus)}
${h.hidden(c.block_result, '', readonly=True)}
</%def>

<%def name="block_view_js()">
<% mo = c.block.taustobjekt %>
% if mo:
$(function(){
<%
  kysimus = c.block.kysimus
  min_choice_info = []
  for v in kysimus.valikud:
     if v.min_vastus:
        min_choice_info.append('["%s", %d]' % (v.kood, v.min_vastus))
%>
  ${graphutils.js_sketchpad(c.block, drag_images=False)}
  sketchpad.make_txelems($('#dragtbl_${c.block_prefix}'), true, ${kysimus.min_vastus or 0}, ${kysimus.max_vastus or 0}, ${mo.masonry_layout and 'true' or 'false'});
% if c.is_edit:
  sketchpad.make_txelems_draggable();
% endif
% if min_choice_info:
  sketchpad.min_choice_info = [${','.join(min_choice_info)}];
  sketchpad.set_finished();             
% endif

% if c.block_correct or c.block.naide:
  ${self.js_show_response(c.correct_responses)}
% else:
  ${self.js_show_response(c.responses)}
% endif
  is_response_dirty = false;
  resized();
});
% endif
</%def>

<%def name="block_print()">
${self.block_view()}
</%def>

<%def name="js_show_response(responses)">
% if c.block.taustobjekt:
  var sketchpad = sketchpads.sketchpad_${c.block_prefix};
  sketchpad.clear_selectables();
  sketchpad.clear();
<% kysimused = {k.id: k for k in c.block.kysimused} %>
## liigutame pildid sinna, kuhu kasutaja need pani
  % for kood, kv in responses.items():
       <%
         kysimus = kysimused.get(kv.kysimus_id)
         tulemus = kysimus and kysimus.tulemus
       %>
       % if kysimus:
       % for n, ks in enumerate(kv.kvsisud):
           <% pt = ks.punkt %>
           % if pt:
           <%
             if n > 0:
               image_id = '%s#%s' % (kood, n)
             else:
               image_id = kood
           %>
           sketchpad.show_txelem('${image_id}', ${pt[0]}, ${pt[1]});
           % if c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
           sketchpad.find_txelem('${image_id}').addClass('${model.ks_correct_cls(responses, tulemus, kv, ks, True)}');
           % endif
           % endif
       % endfor
       % endif    
    % endfor

  % endif
</%def>

