## -*- coding: utf-8 -*- 
## Järjestamine pildil
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
  ${graphutils.js_show_hotspots(c.block)}
  });
</script>
<%
   kysimus = c.block.kysimus
   graphutils.toolbox_area(c.block)
   choiceutils.edit_hotspots(c.block)
   choiceutils.hindamismaatriks(kysimus,
                                kood1=kysimus.valikud_opt,
                                kood1_cls='hskood',
                                ordered=True)
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
<% kysimus = c.block.kysimus %>
$(function(){
  ${graphutils.js_sketchpad(c.block)}
  ${graphutils.js_show_hotspots(c.block)}

  % if not c.block.read_only:
  ${graphutils.js_orderable(c.block, kysimus)}
  % endif

  % if c.block_correct or c.block.naide:
    ${self.js_show_response(c.correct_responses)}
  % else:
    ${self.js_show_response(c.responses)}
  % endif
  is_response_dirty = false;
});
</%def>

<%def name="block_print()">
${graphutils.print_hotspots(c.block)}
</%def>


<%def name="block_entry()">
  <%
    kysimus = c.block.kysimus
    kv = c.responses.get(kysimus.kood) or []
    kv2 = c.prefix2 and c.responses2.get(kysimus.kood) or []
  %>
##  ${self.block_entry_kood(kysimus)}

% if c.is_correct:
   ## sisestatakse, kas vastus on õige või vale
   ${self.block_entry_correct(kysimus, kv, kv2)}
% else:
  <%
    responses = responses2 = []
    if kv and len(kv.kvsisud):
       responses = kv.kvsisud[0].jarjestus
    if kv2 and len(kv2.kvsisud):
       responses2 = kv2.kvsisud[0].jarjestus
    cnt = len(kysimus.valikud)
  %>
  % for i in range(cnt):
    <% 
       value = len(responses) > i and responses[i] or None 
       value2 = responses2 and len(responses2) > i and responses2[i] or None 
       err = value and value2 and value != value2 and 'form-control is-invalid' or ''
    %>
<div class="td-sis-value">
   ${self.block_entry_kood(kysimus, i+1, cnt)}
    <table cellpadding="0" cellspacing="0" class="showerr ${err}">
      <tr>
        <td>
          ${h.select_entry('%s.%s-%d' % (c.prefix, kysimus.kood,i), value,
          kysimus.valikud_opt, wide=False, empty=True, class_='jumper jumper-entry')}
        </td>
      </tr>
      % if c.prefix2:
      <tr>
        <td>
          ${h.select_entry('%s.%s-%d' % (c.prefix2, kysimus.kood,i), value2,
          kysimus.valikud_opt, wide=False, empty=True, class_='jumper jumper-entry')}
        </td>
      </tr>
      % endif
    </table>
</div>
  % endfor
% endif
<script>
  $(function(){
      var block = $('div#block_${c.block_prefix}');    
      order_select_setup(block.find('select[name^="${'%s.%s-' % (c.prefix, kysimus.kood)}"]'));
      order_select_setup(block.find('select[name^="${'%s.%s-' % (c.prefix2, kysimus.kood)}"]'));
   });
</script>

</%def>

<%def name="js_show_response(responses)">
  var sketchpad = sketchpads.sketchpad_${c.block_prefix};
  sketchpad.clear();

  <% 
     kysimus = c.block.kysimus
     kv = responses.get(kysimus.kood)
     ks = kv and len(kv.kvsisud) and kv.kvsisud[0] or None

     el_corr_cls = []
     if ks and c.prepare_correct and ks.on_hinnatud and ks.hindamisinfo and not c.block.varvimata:
        tulemus = kysimus.tulemus
        for ch in ks.hindamisinfo:
            el_corr_cls.append(ch == '1' and 'true' or ch == '0' and 'false' or 'null')
    %>
  % if ks:
    % for ind, kood in enumerate(ks.jarjestus):
       var node = sketchpad.find_shape_node('${h.chk_w(kood)}');
       sketchpad.click_on_orderable(node);
       % if el_corr_cls and len(el_corr_cls) > ind:
       sketchpad.show_node_correct(node, ${el_corr_cls[ind]});
       % endif
    % endfor
  % endif
</%def>

