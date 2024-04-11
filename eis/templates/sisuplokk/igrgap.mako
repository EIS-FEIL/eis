## -*- coding: utf-8 -*- 
## Piltide lohistamine kujunditele
<%inherit file="baasplokk.mako"/>
<%namespace name="graphutils" file="graphutils.mako"/>
<%namespace name="dragimg" file="igrgap.dragimg.mako"/>
<%namespace name="choiceutils" file="choiceutils.mako"/>
<!-- ${self.name} -->

<%def name="block_edit()">
${graphutils.edit_background(c.block)}
% if c.block.taustobjekt.has_file:
${graphutils.sketchpad(c.block)}
${graphutils.toolbox_area(c.block)}
${choiceutils.edit_hotspots(c.block, invisible=True, maxvastus=True)}
<%
   kysimus = c.block.give_kysimus(1)
   bkysimus2 = c.block.give_baaskysimus(2, True)
   choiceutils.hindamismaatriks(kysimus,
                                kood1=c.block.piltobjektid_opt, 
                                kood2=kysimus.valikud_opt, 
                                kood2_cls='hskood',
                                heading1=_("Pildi ID"), 
                                heading2=_("Piirkonna ID"))
%>
${dragimg.edit_drag_images(c.block, bkysimus2)}
% endif

<script>
  $(function() {
% if c.block.taustobjekt.has_file:  
  ${graphutils.js_sketchpad(c.block)}
  sketchpad.make_drawable();
  ${graphutils.js_show_hotspots(c.block, False)}
% endif
  });
</script>

</%def>


<%def name="block_view()">
${h.qcode(c.block.kysimus, nl=True)}
${graphutils.sketchpad(c.block)}
${h.hidden(c.block_result, '', readonly=True)}
</%def>

<%def name="block_view_js()">
<% kysimus = c.block.kysimus %>
$(function(){
  ${graphutils.js_sketchpad(c.block, drag_images=True)}
  ${graphutils.js_show_hotspots(c.block, kysimus=kysimus)}
  ${graphutils.js_droppable_hotspots(c.block, kysimus)}
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
##   ${self.block_entry_kood(kysimus)}

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
  sketchpad.clear_drag_images();
  sketchpad.clear_selectables();
  sketchpad.clear();

## liigutame pildid sinna, kuhu kasutaja need pani
  <% 
    pilt_cnt = {}
    kysimus = c.block.kysimus
    kv = responses.get(kysimus.kood)
    tulemus = kysimus.tulemus
    corrects = []
  %>
  % if kv:
  % for ks in kv.kvsisud:
       <% 
          pt = ks.punkt 
       %>
       % if pt:
       <%
          if ks.kood1 in pilt_cnt:
             pilt_cnt[ks.kood1] += 1
          else:
             pilt_cnt[ks.kood1] = 0
          n = pilt_cnt[ks.kood1]

          if n > 0:
             image_id = '%s#%s' % (ks.kood1, n)
          else:
             image_id = ks.kood1
          if c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
             corrects.append((image_id, model.ks_on_max_p(responses, tulemus, kv, ks, False)))
       %>
        sketchpad.move_drag_image('${image_id}',${pt[0]}, ${pt[1]}, '${h.chk_w(ks.kood2)}');
       % endif
  % endfor
  % for image_id, on_max_p in corrects:
       % if on_max_p is not None:
       <%
          is_correct = on_max_p and 'true' or 'false'
       %>
       sketchpad.show_drag_image_correct('${image_id}', ${is_correct});
       % endif
  % endfor

  % endif
% endif
</%def>
