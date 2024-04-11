## Seostamine
<%inherit file="baasplokk.mako"/>
<%namespace name="choiceutils" file="choiceutils.mako"/>
<!-- ${self.name} -->

<%def name="block_edit()">
<%
  kysimus = c.block.kysimus
  valikud_opt = kysimus.valikud_opt
%>
<div class="row mb-1">
  <% name = 'l.max_vastus' %>
  ${h.flb(_("Paaride arv"), name, 'col-md-3 col-xl-2 text-md-right')}
  <div class="col-md-9 col-xl-10">
    ${h.text5('l.max_vastus', kysimus.max_vastus)}
  </div>
</div>
${choiceutils.choices(kysimus, kysimus.valikud, 'v', seosed=True)}
${choiceutils.hindamismaatriks(kysimus, 
                               kood1=valikud_opt, 
                               kood1_cls='vkood',
                               kood2=valikud_opt,
                               kood2_cls='vkood')}
</%def>

<%def name="block_view()">
<% kysimus = c.block.kysimus %>
<div id="block_${c.block_prefix}" class="asblock">
${h.qcode(kysimus, nl=True)}     
      <div id="drag_group_${c.block_prefix}" class="draggables droppable floatleft border">
        % for subitem in kysimus.valikud:
        <div id="i_${subitem.id}" kood="${subitem.kood}" class="draggable floatleft"
             min="${subitem.min_vastus}"
             max="${subitem.max_vastus}">
          <div class="border-draggable">
            ${h.ccode(subitem.kood)}
            ${h.literal(c.block.replace_img_url(subitem.tran(c.lang).nimi or '', lang=c.lang))}
          </div>
        </div>
        % endfor
      </div>
      <br/>
      <table border="1" width="100%">
        <tbody>
          % for i in range(kysimus.max_vastus):
          <tr height="40px">
            <td class="droppable" align="right" data-pos="${i}_1" width="50%">
              &nbsp;
            </td>
            <td class="droppable" align="left" data-pos="${i}_2" width="50%">
              &nbsp;
            </td>      
          </tr>
          % endfor
        </tbody>
      </table>
% if c.is_sp_view:
     ## Vastuse väljad vormil
          % for i in range(kysimus.max_vastus):
              ${h.hidden('%s_%s_1' % (c.block_result, i), '', class_='cell_result')}
              ${h.hidden('%s_%s_2' % (c.block_result, i), '', class_='cell_result')}
          % endfor
% endif
</div>

<div id="trash" class="d-none"></div>
</%def>

<%def name="block_view_js()">
var iassociate_${c.block.id} = null;
function set_finished_${c.block.id}()
{
  if(iassociate_${c.block.id})
    iassociate_${c.block.id}.set_finished($('div#block_${c.block_prefix}'));
}
$(function(){
   iassociate_${c.block.id} = new iassociate_setup('${c.block_prefix}', '${c.block_result}', ${not c.block.read_only and 'true' or 'false'});
% if not c.block.read_only:    
   set_finished_${c.block.id}();
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
<% kysimus = c.block.kysimus %>
      % for subitem in kysimus.valikud:
      <div class="border-draggable">
        <b>${subitem.kood}.</b> 
            ${h.literal(c.block.replace_img_url(subitem.tran(c.lang).nimi or '', lang=c.lang))}
      </div>
      % endfor
      <br/>
      <table border="1" width="100%">
        <tbody>
          % for i in range(kysimus.max_vastus):
          <tr height="40px">
            <td width="50%">
              &nbsp;
            </td>
            <td width="50%">
              &nbsp;
            </td>
          </tr>
          % endfor
        </tbody>
      </table>

</%def>

<%def name="block_entry()">
## eelnevalt on seatud c.responses ja c.prefix
    <%
      kysimus = c.block.kysimus
      kv = c.responses.get(kysimus.kood)
      kv2 = c.responses2 and c.responses2.get(kysimus.kood)
    %>

    % if c.is_correct:
        ## sisestatakse, kas vastus on õige või vale
        ${self.block_entry_correct(kysimus, kv, kv2)}
    % else:
        ${self.block_entry_pair(kysimus, kv, kv2,
                                kysimus.valikud_opt, kysimus.valikud_opt)}
    % endif
</%def>

<%def name="js_show_response(responses)">
##   iassociate_${c.block.id}.clear();
<%
  kysimus = c.block.kysimus
  tulemus = kysimus.tulemus
  kv = responses.get(kysimus.kood)
%>
   % if kv:
   % for n, ks in enumerate(kv.kvsisud):
      <% 
         sel_cell1 = h.literal('div#block_%s td[data-pos="%s_1"]' % (c.block_prefix, n))
         sel_item1 = h.literal('div#drag_group_%s div[kood="%s"]' % (c.block_prefix, h.chk_w(ks.kood1)))
         sel_cell2 = h.literal('div#block_%s td[data-pos="%s_2"]' % (c.block_prefix, n))
         sel_item2 = h.literal('div#drag_group_%s div[kood="%s"]' % (c.block_prefix, h.chk_w(ks.kood2)))
      %>
      % if ks.kood1:
      iassociate_${c.block.id}.associate_drop($('${sel_item1}'), $('${sel_cell1}'));
      % endif
      % if ks.kood2:
      iassociate_${c.block.id}.associate_drop($('${sel_item2}'), $('${sel_cell2}'));
      % endif

      % if c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
      $('${sel_cell1},${sel_cell2}').addClass('${model.ks_correct_cls(responses, tulemus, kv, ks, False)}');
      % endif
    % endfor
   % endif
</%def>
