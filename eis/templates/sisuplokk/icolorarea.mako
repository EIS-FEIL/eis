## Alade värvimine
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
  ${self.js_show_hotspots(c.block, False)}
});
</script>
<%
   bkysimus = c.block.give_baaskysimus()
   color_opt = bkysimus.valikud_opt
   graphutils.toolbox_area(c.block)
   choiceutils.edit_hotspots(c.block, invisible=True, minvastus1=True)

   choiceutils.choices(bkysimus, bkysimus.valikud, 'v', wysiwyg=True, can_rtf=True, caption=_("Värvid"))

   for ind, kysimus in enumerate(c.block.pariskysimused):
       choiceutils.hindamismaatriks(kysimus,
                                    kood1=color_opt,
                                    kood1_cls='vkood',
                                    prefix='am-%d' % ind,
                                    fix_kood=True)
%>
% endif
</%def>

<%def name="block_view()">
<div id="block_${c.block_prefix}" class="asblock">
% for k in c.block.pariskysimused:
  ${h.qcode(k, nl=True)}
  ${h.hidden(k.result, '', class_='blockresult')}
% endfor
<div class="d-flex flex-wrap-reverse">
  <div class="pr-2">
    ${graphutils.sketchpad(c.block)}
  </div>
  <div>
    ${self.view_colortable()}
  </div>
</div>
</div>
</%def>

<%def name="block_print()">
<div class="d-flex flex-wrap">
  <div>
    ${graphutils.print_hotspots(c.block)}
  </div>
  <div>
      ${self.view_colortable()}
  </div>
</div>
</%def>

<%def name="view_colortable()">
<%
  bkysimus = c.block.get_baaskysimus()
  varvid = [(v.kood, v.varv, v.tran(c.lang).nimi) for v in bkysimus.valikud]
  no_title = len([r for r in varvid if r[2]]) == 0
%>
<div class="colors ${no_title and 'd-flex flex-wrap' or ''}">
  % for kood, varv, nimi in varvid:
  <div data-kood="${kood}" data-color="${varv}" class="d-flex align-items-center ca-pick-color">
    <div style="background-color:${varv}" class="ca-sample"></div>
    % if nimi:
    <div class="ml-1 mr-2">${nimi}</div>
    % endif
  </div>
  % endfor
</div>
</%def>

<%def name="block_view_js()">
$(function(){
  <% bkysimus = c.block.get_baaskysimus() %>
  ${graphutils.js_sketchpad(c.block, drag_images=True)}
  ${self.js_show_hotspots(c.block)}
  ${graphutils.js_colorable_hotspots(c.block, bkysimus, c.block.read_only)}

  % if c.block_correct or c.block.naide:
  ${self.js_show_response(c.correct_responses)}
  % else:
  ${self.js_show_response(c.responses)}
  % endif
  is_response_dirty = false;

% if not c.block.read_only:
  $('div#block_${c.block_prefix}.asblock .colors div.ca-pick-color').click(function()
  {
    sketchpads.sketchpad_${c.block_prefix}.color = $(this).data('color');
    sketchpads.sketchpad_${c.block_prefix}.current_value = $(this).data('kood');
    $(this).closest('.colors').find('div.ca-pick-color').removeClass('ca-current-color');
    $(this).addClass('ca-current-color');
  });
% endif
});

</%def>

<%def name="js_show_hotspots(sisuplokk, nahtamatu=None)">
     var sketchpad = sketchpads.sketchpad_${c.block_prefix};
<%
     valikupiirkonnad = [k.valikud[0] for k in sisuplokk.pariskysimused if len(k.valikud)]
%>
% for item in valikupiirkonnad:
     sketchpad.drawShapeId(eval('${item.koordinaadid}'),
                          '${item.kujund}',
                          '${item.kood}',
                          ${c.show_r_code and 'true' or 'false'},
                          ${nahtamatu!=False and item.nahtamatu and 'true' or 'false'},
                          null,
                          1,
                          ${item.min_vastus or 'null'},
                          $('input[type="hidden"][name="${const.RPREFIX + item.kood}"]'));
% endfor
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
<%
  bkysimus = c.block.get_baaskysimus()
  colors = {v.kood: v.varv for v in bkysimus.valikud}
%>
var sketchpad = sketchpads.sketchpad_${c.block_prefix};
% for kysimus in c.block.pariskysimused:
<% kv = responses.get(kysimus.kood) %>
% if kv:
% for ks in kv.kvsisud:
% if ks.kood1:
    var node = sketchpad.find_shape_node("${kysimus.kood}");
    sketchpad.click_on_colorable(node, "${colors[ks.kood1]}", "${h.chk_w(ks.kood1)}");

    % if c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
    <% on_max_p = model.ks_on_max_p(responses, kysimus.tulemus, kv, ks, False) %>
    % if on_max_p is not None:
    sketchpad.show_node_correct(node, ${on_max_p and 'true' or 'false'}, true);
    % endif
    % endif

% endif
% endfor
% endif
% endfor

% endif
</%def>

