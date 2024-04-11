## -*- coding: utf-8 -*- 
## Piltide lohistamine
<%inherit file="baasplokk.mako"/>
<%namespace name="graphutils" file="graphutils.mako"/>
<%namespace name="dragimg" file="ipos.dragimg.mako"/>
<%namespace name="choiceutils" file="choiceutils.mako"/>
## Piltide lohistamine
<!-- ${self.name} -->

<%def name="block_edit()">
${graphutils.edit_background(c.block)}

% if c.block.taustobjekt and c.block.taustobjekt.has_file:
${graphutils.sketchpad(c.block)}

<script>
$(function() {
  ${graphutils.js_sketchpad(c.block)}
  sketchpad.make_drawable();
  % for item in c.block.piltobjektid:
  ${graphutils.js_show_hindamismaatriks_pt(item.tulemus)}
  % endfor
});
</script>
${graphutils.toolbox_area(c.block)}
${dragimg.edit_drag_images(c.block)}
% endif
</%def>

<%def name="block_view()">
${graphutils.sketchpad(c.block)}
${h.hidden(c.block_result, '', readonly=True)}
</%def>

<%def name="block_view_js()">
$(document).ready(function(){
  ${graphutils.js_sketchpad(c.block, drag_images=True)}
  ${graphutils.js_droppable_paper(c.block)}
  ${graphutils.js_show_drag_images(c.block, c.block.read_only)}

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
        ${graphutils.print_img(c.block.taustobjekt)}
      </td>
      <td valign="top">
        ${graphutils.print_drag_images(c.block)}
      </td>
    </tr>
  </table>
</%def>

<%def name="js_show_response(responses)">
% if c.block.taustobjekt:
  var sketchpad = sketchpads.sketchpad_${c.block_prefix};
  sketchpad.clear_drag_images();
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
           sketchpad.move_drag_image('${image_id}',${pt[0]}, ${pt[1]});
           % if c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
           <%
             on_max_p = None
             if c.prepare_correct and ks.on_hinnatud:
                on_max_p = model.ks_on_max_p(responses, tulemus, kv, ks, True)
             if on_max_p is None:
                is_correct = 'null'
             else:
                is_correct = on_max_p and 'true' or 'false'
           %>
           sketchpad.show_drag_image_correct('${image_id}', ${is_correct});
           % endif
           % endif
      % endfor
  % endif
  % endfor
% endif
</%def>
