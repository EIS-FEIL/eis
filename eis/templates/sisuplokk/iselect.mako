## -*- coding: utf-8 -*- 
## Märkimine pildil
<%inherit file="baasplokk.mako"/>
<%namespace name="graphutils" file="graphutils.mako"/>
<%namespace name="choiceutils" file="choiceutils.mako"/>
<!-- ${self.name} -->

<%def name="block_edit()">
<% kysimus = c.block.kysimus %>
${graphutils.edit_background(c.block)}
% if c.block.taustobjekt.has_file:
${graphutils.sketchpad(c.block)}
<script>
  $(function() {
  ${graphutils.js_sketchpad(c.block)}
  sketchpad.make_drawable();
  ${graphutils.js_show_hindamismaatriks_pt(kysimus.tulemus)}
  ${graphutils.js_show_hotspots(c.block)}
  });
</script>
${graphutils.toolbox_area(c.block)}
${choiceutils.hindamismaatriks_pt(kysimus, 'am1')}

% endif
</%def>

<%def name="block_print()">
${graphutils.print_img(c.block.taustobjekt)}
</%def>

<%def name="block_view()">
<% kysimus = c.block.kysimus %>
${h.qcode(kysimus, nl=True)}
${graphutils.sketchpad(c.block)}
${h.hidden(kysimus.result, '', id=c.block_result, readonly=True)}
% if not c.block_correct and not c.block.naide and not c.prepare_correct:
${graphutils.btn_undo(c.block_prefix)}
% endif
</%def>

<%def name="block_view_js()">
$(function(){
  ${graphutils.js_sketchpad(c.block, require_id=False, drag_images=False)}
  % if not c.block.read_only:
  ${graphutils.js_pointable(c.block, c.block.kysimus)}
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

<%def name="js_show_response(responses)">
  var sketchpad = sketchpads.sketchpad_${c.block_prefix};
  sketchpad.clear();
<%
  kysimus = c.block.kysimus
  kv = responses.get(kysimus.kood)
%>
  % if kv:
  % for ks in kv.kvsisud:
      % if ks.punkt is not None:
      var node = sketchpad.add_point(${ks.punkt[0]},${ks.punkt[1]});

         % if c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
         <% on_max_p = model.ks_on_max_p(responses, kysimus.tulemus, kv, ks, False) %>
         % if on_max_p is not None:
         sketchpad.show_node_correct(node, ${on_max_p and 'true' or 'false'});
         % endif
         % endif
  
      % endif
  % endfor
  % endif
</%def>
