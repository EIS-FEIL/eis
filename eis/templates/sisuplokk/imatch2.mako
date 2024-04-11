## Sobitamine
<%inherit file="baasplokk.mako"/>

<%namespace name="choiceutils" file="choiceutils.mako"/>
<%namespace name="graphutils" file="graphutils.mako"/>
<!-- ${self.name} -->

<%def name="block_edit()">
<%
   c.kysimus1 = c.block.give_baaskysimus(seq=1) 
   c.kysimus2 = c.block.give_baaskysimus(seq=2)
   if not c.kysimus1.id and not c.kysimus1.min_vastus:
      c.kysimus1.min_vastus = 1
   if not c.kysimus1.ridu:
      c.kysimus1.ridu = 1
   if c.kysimus1.ridu == 2:
      khulk = c.kysimus2
      vhulk = c.kysimus1
   else:
      khulk = c.kysimus1
      vhulk = c.kysimus2
   kysimused = c.block.pariskysimused
%>

% for ind, valista_kood in enumerate(c.ylesanne.get_kysimus_koodid(c.block)):
${h.hidden('valista%d' % ind, valista_kood, class_='valista')}
% endfor

<% ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') %>
<div class="row">
  <% name = 'l.min_vastus' %>
  ${ch.flb(_("Minimaalne paaride arv"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.text5('l.min_vastus', c.kysimus1.min_vastus)}
  </div>
  <% name = 'l.max_vastus' %>
  ${ch.flb(_("Maksimaalne paaride arv"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.text5('l.max_vastus', c.kysimus1.max_vastus or '')}
  </div>

  <% name = 'l.ridu' %>
  ${ch.flb(_("Küsimuste hulk"), name)}
  <div class="col-md-9 col-xl-4">
    ${h.radio('l.ridu', 1, checkedif=c.kysimus1.ridu, label=_("Hulk 1"))}
    ${h.radio('l.ridu', 2, checkedif=c.kysimus1.ridu, label=_("Hulk 2"))}        
    <script>
          $('input[name="l.ridu"]').change(function(){
             $('td.maatriksid-'+$(this).val()).show();
             $('td.maatriksid-'+(3-$(this).val())).hide();          
          });
    </script>
  </div>
</div>

% if c.kysimus1.ridu == 2:         
<%
   choiceutils.choices(c.kysimus1, c.kysimus1.valikud, 'v1', seosed=True, caption=_("Hulk 1"), gentype='1')
   choiceutils.choices(c.kysimus2, c.kysimus2.valikud, 'v2', seosed=True, caption=_("Hulk 2"), gentype='A', valista=True)
%>
% else:
<%
   choiceutils.choices(c.kysimus1, c.kysimus1.valikud, 'v1', seosed=True, caption=_("Hulk 1"), gentype='A', valista=True)
   choiceutils.choices(c.kysimus2, c.kysimus2.valikud, 'v2', seosed=True, caption=_("Hulk 2"), gentype='1')
%>
% endif
% if c.block.id:
    <div class="maatriksid-${c.kysimus1.ridu}">
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

% endif
</%def>


<%def name="block_print()">
<%
c.kysimus1 = c.block.get_baaskysimus(seq=1) 
c.kysimus2 = c.block.get_baaskysimus(seq=2)
%>
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
  </tr>
</table>
</%def>

<%def name="block_view()">
<%
c.kysimus1 = c.block.get_baaskysimus(seq=1) 
c.kysimus2 = c.block.get_baaskysimus(seq=2)
%>
<table id="tbl_${c.block_prefix}" style="position:relative" class="asblock">
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
   ${self.js_show_response(c.correct_responses)}
}
else {
   ${self.js_show_response(c.responses)}
}
}
% endif


$(function(){
    var sketchpad = new Sketchpad('${c.block_prefix}');
    // kuhu tulemus kirjutada
    sketchpad.result_field = $('#${c.block_result}');
    // max vastuste arv hulkade vahel
    sketchpad.min_choices = ${c.kysimus1 and c.kysimus1.min_vastus or 0};
  
% if not c.block.read_only:
  ## saab vastata
    sketchpad.set_finished();
    sketchpad.setup_match($('#tbl_${c.block_prefix}'),
        $('#drag_group_${c.block_prefix}_1'), ${c.kysimus1.max_vastus or 0},
        $('#drag_group_${c.block_prefix}_2'), ${c.kysimus2.max_vastus or 0});
% endif
  
  % if c.block_correct or c.block.naide:
    ${self.js_show_response(c.correct_responses)}
  % else:
    ${self.js_show_response(c.responses)}
  % endif
  is_response_dirty = false;
});

</%def>

<%def name="block_entry()">
## eelnevalt on seatud c.responses ja c.prefix

    <%
      valikuhulk1 = c.block.get_kysimus(seq=1)
      valikuhulk2 = c.block.get_kysimus(seq=2)

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

</%def>

<%def name="js_show_response(responses)">
   var sketchpad1=sketchpads.sketchpad_${c.block_prefix};
   sketchpad1.clear();
<%
   if c.kysimus1.ridu == 2:
      khulk_seq = 2
      vhulk_seq = 1
   else:
      khulk_seq = 1
      vhulk_seq = 2
%>
   % for kysimus in c.block.pariskysimused:
      <% kv = responses.get(kysimus.kood) %>
      % if kv:
      % for ks in kv.kvsisud:
         <%
            sel1 = h.literal('#drag_group_%s_%s .draggable[kood="%s"]' % \
              (c.block_prefix, khulk_seq, kysimus.kood))
            sel2 = h.literal('#drag_group_%s_%s .draggable[kood="%s"]' % \
              (c.block_prefix, vhulk_seq, h.chk_w(ks.kood1)))
         %>
         var line = sketchpad1.match_connect($('${sel1}'), $('${sel2}'), 1);

         % if c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
         <% on_max_p = model.ks_on_max_p(responses, kysimus.tulemus, kv, ks, True) %>
         % if on_max_p is not None:
         sketchpad1.show_node_correct(line, ${on_max_p and 'true' or 'false'});
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
            class="draggable">
          <div class="border-draggable match-draggable">
            % if c.kysimus1.ridu == kysimus.seq:
            % if c.show_q_code:
            <% subkys = c.block.get_kysimus(subitem.kood) %>
            % if subkys:
            ${h.qcode(subkys)}
            % endif
            % endif
            % else:
            ${h.ccode(subitem.kood)}
            % endif
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

