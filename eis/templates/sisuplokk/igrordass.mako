## Võrguülesanne
<%inherit file="baasplokk.mako"/>
<%namespace name="graphutils" file="graphutils.mako"/>
<%namespace name="choiceutils" file="choiceutils.mako"/>
<!-- ${self.name} -->

<%def name="block_edit()">
${graphutils.edit_background(c.block, min_max=False)}
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
                                ordered=False)
%>

<div>
<% kysimus2 = c.block.get_kysimus(seq=2) %>
<div class="incorrect-resp">
<%
   kysimus2 = kysimus2 or c.new_item() 
%>
  ${choiceutils.hindamismaatriks(kysimus2, prefix='am2',
                                 basetype_opt=((const.BASETYPE_INTEGER, _("Täisarv")),),
                                 heading1=_("Vastuste arv"),
                                 caption=_("Valede vastuste arv"),
                                 hm_caption=_("Valede vastuste arvu hindamismaatriks")
  )}
</div>
</div>
% endif
</%def>


<%def name="block_view()">
<% kysimus = c.block.kysimus %>
<div id="block_${c.block_prefix}" class="asblock">
${h.qcode(kysimus)}
${graphutils.sketchpad(c.block)}
${h.hidden(c.block_result, '', readonly=True)}
</div>
</%def>

<%def name="block_view_js()">
<% kysimus = c.block.kysimus %>
$(function(){
  ${graphutils.js_sketchpad(c.block)}
  ${graphutils.js_show_hotspots(c.block)}
  ${graphutils.js_assorderable(c.block, kysimus, c.block.read_only)}

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
   $(document).ready(function(){
      var block = $('div#block_${c.block_prefix}');    
      assorder_select_setup(block.find('select[name^="${'%s.%s-' % (c.prefix, kysimus.kood)}"]'));
      assorder_select_setup(block.find('select[name^="${'%s.%s-' % (c.prefix2, kysimus.kood)}"]'));
   });
</script>
</%def>

<%def name="js_show_response(responses)">
  var sketchpad = sketchpads.sketchpad_${c.block_prefix};
  sketchpad.clear();
<%
   kv = responses.get(c.block.kysimus.kood)
   ks = kv and len(kv.kvsisud) and kv.kvsisud[0] or None
%>
% if ks:
    % for kood in ks.jarjestus:
       sketchpad.click_on_assorderable(sketchpad.find_shape_node('${h.chk_w(kood)}'), true);
    % endfor
% endif
</%def>
