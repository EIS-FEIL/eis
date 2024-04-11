## -*- coding: utf-8 -*- 
## Sobitamine pildil
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
   graphutils.toolbox_area(c.block)
   choiceutils.edit_hotspots(c.block, invisible=True)
   choiceutils.hindamismaatriks(c.block.kysimus,
                                kood1=c.block.kysimus.valikud_opt, 
                                kood1_cls='hskood',  
                                kood2=c.block.kysimus.valikud_opt,
                                kood2_cls='hskood')
%>
% endif
</%def>


<%def name="block_view()">
<% kysimus = c.block.kysimus %>
${h.qcode(kysimus)}
${graphutils.sketchpad(c.block)}
${h.hidden(kysimus.result, '', id=c.block_result, readonly=True)}
</%def>

<%def name="block_view_js()">
<% kysimus = c.block.kysimus %>
$(function(){
  ${graphutils.js_sketchpad(c.block)}
  sketchpad.make_drawable();
  ${graphutils.js_show_hotspots(c.block)}
  % if not c.block.read_only:
  ${graphutils.js_associable(c.block, kysimus)}
  % endif

  % if c.block_correct or c.block.naide:
    ${self.js_show_response(c.correct_responses)}
  % else:
    ${self.js_show_response(c.responses)}
% endif
  resized();
  is_response_dirty = false;
});
</%def>


<%def name="block_print()">
${graphutils.print_hotspots(c.block)}
</%def>


<%def name="block_entry()">
## eelnevalt on seatud c.responses ja c.prefix
    <%
      kysimus = c.block.kysimus
      kv = c.responses.get(kysimus.kood) or []
      kv2 = c.prefix2 and c.responses2.get(kysimus.kood) or []
    %>
##   ${self.block_entry_kood(kysimus)}
    % if c.is_correct:
        ## sisestatakse, kas vastus on õige või vale
        ${self.block_entry_correct(kysimus, kv, kv2)}
    % else:
        ${self.block_entry_pair(kysimus, kv, kv2,
                                kysimus.valikud_opt,
                                kysimus.valikud_opt)}
    % endif
</%def>

<%def name="js_show_response(responses)">
  var sketchpad = sketchpads.sketchpad_${c.block_prefix};
  sketchpad.clear();
<%
  kysimus = c.block.kysimus
  tulemus = kysimus.tulemus
  kv = responses.get(kysimus.kood)
%>
% if kv:
    % for ks in kv.kvsisud:
       % if ks.kood1 and ks.kood2:      
         var line = sketchpad.associate(sketchpad.find_shape_node('${h.chk_w(ks.kood1)}'), 
                                        sketchpad.find_shape_node('${h.chk_w(ks.kood2)}'), true);

         % if c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
         <% on_max_p = model.ks_on_max_p(responses, tulemus, kv, ks, False) %>
         % if on_max_p is not None:
         sketchpad.show_node_correct(line, ${on_max_p and 'true' or 'false'});
         % endif
         % endif

      % endif
    % endfor
% endif
</%def>
