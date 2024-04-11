## Sobitamine kolme hulgaga kolmikute hindamisega
<%inherit file="baasplokk.mako"/>

<%namespace name="choiceutils" file="choiceutils.mako"/>
<%namespace name="graphutils" file="graphutils.mako"/>
<!-- ${self.name} -->

<%def name="block_before()">
<%
   c.kysimus1 = c.block.get_kysimus(seq=1) 
   c.kysimus2 = c.block.get_kysimus(seq=2) 
   c.kysimus3 = c.block.get_kysimus(seq=3)
   if not c.kysimus1.id and c.kysimus1.min_vastus is None:
      c.kysimus1.min_vastus = 1
%>
</%def>

<%def name="block_edit()">
<div>
<%
   choiceutils.choices(c.kysimus1, c.kysimus1.valikud, 'v1', seosed=True, caption=_("Hulk 1"), gentype='A1')
   choiceutils.choices(c.kysimus2, c.kysimus2.valikud, 'v2', seosed=True, caption=_("Hulk 2"), gentype='B1')
   choiceutils.choices(c.kysimus3, c.kysimus3.valikud, 'v3', seosed=True, caption=_("Hulk 3"), gentype='C1')
   if c.kysimus1.ridu == 2:
      khulk = c.kysimus2
   else:
      khulk = c.kysimus1
   kysimused = c.block.pariskysimused
  %>
</div>

<div class="maatriksid-1">
% for ind, kysimus in enumerate(kysimused):
<div class="rounded border mb-2">
  <div class="d-flex">
    <div class="m-2"><b>${_("Küsimus")}</b></div>
    <div class="m-2">
  % for v in khulk.valikud:
  % if v.kood == kysimus.kood:
  ${h.literal(v.nimi)}
  % endif
  % endfor
    </div>
  </div>
  <%
   choiceutils.hindamismaatriks(kysimus,
                                fix_kood=True,
                                prefix='am-%d' % (ind)
                                )

  %>
</div>
% endfor
</div>

</%def>

<%def name="block_print()">
<table>
  <tr>
    <td>
      ${self.print_matchset(c.kysimus1)}
    </td>
    <td width="50px">
    </td>
    <td>
      ${self.print_matchset(c.kysimus2)}
    </td>
    <td width="50px">
    </td>
    <td>
      ${self.print_matchset(c.kysimus3)}
    </td>
  </tr>
</table>
</%def>

<%def name="block_view()">
${h.qcode(c.kysimus1, nl=True)}

<table id="tbl_${c.block_prefix}" style="position:relative;" class="asblock">
  <col/>
  <col width="100px"/>
  <col/>
  <tr>
    <td>
      ${self.show_matchset(c.kysimus1)}
    </td>
    <td width="100px" id="sketchpad_${c.block_prefix}" valign="top">
      <img src="/static/images/line_white100px.jpg" alt=""/>
      ## seoste joonte koht
    </td>
    <td>
      ${self.show_matchset(c.kysimus2)}
    </td>
    <td width="100px" id="sketchpad_${c.block_prefix}_2" valign="top">
      ## teine seoste joonte koht
      <img src="/static/images/line_white100px.jpg" alt=""/>
    </td>
    <td>
      ${self.show_matchset(c.kysimus3)}
    </td>
  </tr>
</table>
${h.hidden(c.block_result, '')}
<% 
if c.resize_prefixes == '':
   c.resize_prefixes = []
c.resize_prefixes.append((c.y_prefix, c.block_prefix))
%>

</%def>

<%def name="block_view_js()">

function resize_${c.block_prefix}()
{
  if(sketchpads.sketchpad_${c.block_prefix})
     sketchpads.sketchpad_${c.block_prefix}.match_refresh();
}

% if c.prepare_correct:
<%
if c.sh_correct_prefixes == '':
  c.sh_correct_prefixes = []
c.sh_correct_prefixes.append((c.y_prefix, c.block_prefix))  
%>
function sh_correct_${c.block_prefix}(rc)
{
if(rc){
   ${self.js_show_response(c.kysimus1, c.kysimus3, c.correct_responses)}
}
else {
   ${self.js_show_response(c.kysimus1, c.kysimus3, c.responses)}
}
}
% endif

$(function(){
    var sketchpad = new Sketchpad('${c.block_prefix}');
    // kuhu tulemus kirjutada
    sketchpad.result_field = $('#${c.block_result}');
    sketchpad.add_paper('${c.block_prefix}_2');
    sketchpad.min_choices = ${c.kysimus1 and c.kysimus1.min_vastus or 0};
    sketchpad.min_choices_1 = ${c.kysimus2 and c.kysimus2.min_vastus or 0};
    sketchpad.min_choices_2 = ${c.kysimus3 and c.kysimus3.min_vastus or 0};

% if not c.block.read_only:
  ## saab vastata
    sketchpad.set_finished();
    sketchpad.setup_match($('#tbl_${c.block_prefix}'),
        $('#drag_group_${c.block_prefix}_1'), ${c.kysimus1.max_vastus or 0},
        $('#drag_group_${c.block_prefix}_2'), ${c.kysimus2.max_vastus or 0},   
        $('#drag_group_${c.block_prefix}_3'), ${c.kysimus3.max_vastus or 0},
        true);
% endif
    
  % if c.block_correct or c.block.naide:
    ${self.js_show_response(c.kysimus1, c.kysimus3, c.correct_responses)}
  % else:
    ${self.js_show_response(c.kysimus1, c.kysimus3, c.responses)}
  % endif
  is_response_dirty = false;
});

</%def>

<%def name="block_entry()">
## eelnevalt on seatud c.responses ja c.prefix

    <%
      valikuhulk1 = c.block.get_kysimus(seq=1)
      valikuhulk2 = c.block.get_kysimus(seq=2)
      valikuhulk3 = c.block.get_kysimus(seq=3)

      kysimus = valikuhulk1
      kv = c.responses.get(kysimus.kood)
      kv2 = c.prefix2 and c.responses2.get(kysimus.kood)
    %>
  
    % if c.is_correct:
        ## sisestatakse, kas vastus on õige või vale
        ${self.block_entry_correct(kysimus, kv, kv2)}
    % else:

      ${self.block_entry_pair(kysimus, kv, kv2,
        valikuhulk1.valikud_opt, valikuhulk2.valikud_opt)}
    % endif

      <%
        kysimus = valikuhulk3
        kv = c.responses.get(kysimus.kood)
        kv2 = c.prefix2 and c.responses2.get(kysimus.kood)
      %>
      % if c.is_correct:
        ## sisestatakse, kas vastus on õige või vale
        ${self.block_entry_correct(kysimus, kv, kv2)}
      % else:

        ${self.block_entry_pair(kysimus, kv, kv2,
          valikuhulk2.valikud_opt, valikuhulk3.valikud_opt)}
      % endif
</%def>

<%def name="js_show_response(kysimus1, kysimus3, responses)">
    var sketchpad1=sketchpads.sketchpad_${c.block_prefix};
    sketchpad1.clear();
% for kysimus in c.block.pariskysimused:
   <% kv = responses.get(kysimus.kood) %>
% if kv:
% for ks in kv.kvsisud:
   % if ks.kood1:
     <%
     sel1 = h.literal('#drag_group_%s_1 .draggable[kood="%s"]' % (c.block_prefix, h.chk_w(ks.kood1)))     
     sel2 = h.literal('#drag_group_%s_2 .draggable[kood="%s"]' % (c.block_prefix, h.chk_w(kysimus.kood)))
     paper = 1
     %>
     var line = sketchpad1.match_connect($('${sel1}'), $('${sel2}'), ${paper}, true);
     % if c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
      <% on_max_p = model.ks_on_max_p(responses, kysimus.tulemus, kv, ks, True) %>
     % if on_max_p is not None:
      sketchpad1.show_node_correct(line, ${on_max_p and 'true' or 'false'});
     % endif
     % endif
   % endif
   % if ks.kood2:
     <%
     sel1 = h.literal('#drag_group_%s_2 .draggable[kood="%s"]' % (c.block_prefix, h.chk_w(kysimus.kood)))     
     sel2 = h.literal('#drag_group_%s_3 .draggable[kood="%s"]' % (c.block_prefix, h.chk_w(ks.kood2)))
     paper = 2
     %>
     var line = sketchpad1.match_connect($('${sel1}'), $('${sel2}'), ${paper}, true);
     % if c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
      <% on_max_p = model.ks_on_max_p(responses, kysimus.tulemus, kv, ks, True) %>
     % if on_max_p is not None:
      sketchpad1.show_node_correct(line, ${on_max_p and 'true' or 'false'});
     % endif
     % endif
   % endif
% endfor   
% endif
% endfor      
</%def>

<%def name="show_matchset(kysimus)">
      <div id="drag_group_${c.block_prefix}_${kysimus.seq}" data-set="${kysimus.seq}" class="draggables" style="padding:0px;margin:0">
        % for subitem in kysimus.valikud:
        <div id="i_${subitem.id}" kood="${subitem.kood}"
            % if subitem.min_vastus is not None:
            min="${subitem.min_vastus}"
            % endif
            % if subitem.max_vastus is not None:
            max="${subitem.max_vastus}"
            % endif
            % if kysimus.seq == 2:
            max1="1" max2="1"
            % endif
            class="draggable">
          <div class="border-draggable match-draggable">
            ${h.ccode(subitem.kood)}
            ${h.literal(c.block.replace_img_url(subitem.tran(c.lang).nimi or '', lang=c.lang))}
          </div>
        </div>
        % endfor
      </div>
</%def>

<%def name="print_matchset(kysimus)">
        % for subitem in kysimus.valikud:
         <div class="border-draggable">
            ${h.literal(c.block.replace_img_url(subitem.tran(c.lang).nimi or '', lang=c.lang))}
         </div>
         % endfor
 </%def>

