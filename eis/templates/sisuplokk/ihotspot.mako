## -*- coding: utf-8 -*- 
## Pildil oleva piirkonna valik
<%inherit file="baasplokk.mako"/>
<%namespace name="graphutils" file="graphutils.mako"/>
<%namespace name="choiceutils" file="choiceutils.mako"/>
<!-- ${self.name} -->

<%def name="block_edit()">
${graphutils.edit_background(c.block)}
% if c.block.taustobjekt.has_file:
${graphutils.sketchpad(c.block)}
<script>
  $(function() {
  ${graphutils.js_sketchpad(c.block)}
  sketchpad.make_drawable();
  ${graphutils.js_show_hotspots(c.block, False)}
  });
</script>
<%
   kysimus = c.block.kysimus
   graphutils.toolbox_area(c.block)
   choiceutils.edit_hotspots(c.block, invisible=True)
   choiceutils.hindamismaatriks(kysimus,
                                kood1=kysimus.valikud_opt,
                                kood1_cls='hskood')
%>
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
  <% kysimus = c.block.kysimus %>
  ${graphutils.js_sketchpad(c.block)}
  ${graphutils.js_show_hotspots(c.block, None, kysimus)}
  % if not c.block.read_only:
  ${graphutils.js_selectable(c.block, kysimus)}
  % endif

  % if c.block_correct or c.block.naide:
    ${self.js_show_response(c.correct_responses)}
  % else:
    ${self.js_show_response(c.responses)}
  % endif
is_response_dirty = false;
try{ top.window.unset_unsaved($('iframe.ylesanne')); } catch(e) {};
});
</%def>

<%def name="block_print()">
${graphutils.print_hotspots(c.block)}
</%def>

<%def name="js_show_response(responses)">
  var sketchpad = sketchpads.sketchpad_${c.block_prefix};
  sketchpad.clear_selectables();
  sketchpad.clear();
  <%
  kysimus = c.block.kysimus
  kv = responses.get(kysimus.kood)
  tulemus = kysimus.tulemus
  %>
  % if kv:
  % for ks in kv.kvsisud:
    var node = sketchpad.find_shape_node('${h.chk_w(ks.kood1)}');
    sketchpad.click_on_selectable(node, true);
  % if c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
    <% on_max_p = model.ks_on_max_p(responses, tulemus, kv, ks, False) %>
    % if on_max_p is not None:
    sketchpad.show_node_correct(node, ${on_max_p and 'true' or 'false'});
    % endif
  % endif
  % endfor
  % endif
</%def>

