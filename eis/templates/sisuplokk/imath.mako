## Matemaatilise teksti sisestamine
<%inherit file="baasplokk.mako"/>
<!-- ${self.name} -->
<%namespace name="choiceutils" file="choiceutils.mako"/>

<%def name="block_edit()">
<% bkysimus = c.block.kysimus %>
<% ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') %>
<div class="row">
  <% name = 'l.pikkus' %>
  ${ch.flb(_("Eeldatav vastuse pikkus"), name)}
  <div class="col-md-9 col-xl-1">
    ${h.posint5(name, bkysimus.pikkus)}
  </div>

  <% name = 'l.max_vastus' %>
  ${ch.flb(_("Vastuste arv"), name, 'col-md-3 col-xl-1 text-md-right')}
  <div class="col-md-3 col-xl-1">
    ${h.posint5('l.max_vastus', bkysimus.max_vastus or 1)}
  </div>
  <% name = 'l.min_vastus' %>
  ${ch.flb(_("Minimaalne vastuste arv"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.posint5('l.min_vastus', bkysimus.min_vastus)}
  </div>

  <% name = 'l.n_asend' %>
  ${ch.flb(_("Nupurea asend"), name)}
  <div class="col-md-3 col-xl-2">
    ${h.radio('l.n_asend', 1, checked=bkysimus.n_asend==1 or bkysimus.n_asend is None, label=_("all"))}
    ${h.radio('l.n_asend', 0, checkedif=bkysimus.n_asend, label=_("paremal"))}
  </div>
</div>
<div class="row">
  <%
    name = 'l.vihje'
    id = 'wmvihje'
  %>
  ${ch.flb(_("Vastuse algväärtus"), name)}
  <div class="col">
    <div id="me_${h.toid(name)}" name="${name}" n_asend="${bkysimus.n_asend}"
     style="min-width:${bkysimus.pikkus and bkysimus.pikkus * 10 or 300}px"
     class="${c.is_edit and 'math-edit' or 'math-view'}">${h.html_lt(bkysimus.vihje)}</div>
    ${h.hidden(name, bkysimus.vihje)}
  </div>
</div>

${choiceutils.hindamismaatriks(bkysimus, heading1=_("Vastus"), matheditor=True, basetype=const.BASETYPE_MATH, naidis=True)}
% if c.is_edit:
<script>
## kasutab matheditor.js
var matheditor_buttons = ${model.json.dumps(c.ylesanne.get_math_icons())};
</script>
% endif
</%def>

<%def name="block_print()">
     <div height="200px"></div>     
</%def>

<%def name="block_view()">
<% kysimus = c.block.kysimus %>
<div id="block_${c.block_prefix}" class="asblock">
${h.qcode(kysimus, nl=True)}
<%
  if c.block.naide or c.block_correct:
     ## õige vastuse näitamine
     responses = c.correct_responses
  else:
     responses = c.responses
  kv = responses.get(kysimus.kood)
  kvsisud = kv and list(kv.kvsisud) or []
  max_vastus = kysimus.max_vastus
  name = kysimus.result
%>
<table width="100%" cellspacing="0" colpadding="0" colspacing="0">
  <col width="${max_vastus and max_vastus > 1 and '20px' or '1px'}"/>
  <tbody>
% for n in range(max_vastus or 1):
<%
  field_id = h.toid(f'{name}_{n}_')
  ks = len(kvsisud) > n and kvsisud[n] or None
  response = ks and ks.sisu or ''
  if not response and not c.read_only and not ks and kysimus.algvaartus and kysimus.vihje:
     response = kysimus.vihje
  corr_cls = ''
  if c.prepare_correct and ks and ks.on_hinnatud and not c.block.varvimata:
     corr_cls = model.ks_correct_cls(responses, kysimus.tulemus, kv, ks, False) or ''
%>
<tr>
  <td>
    % if max_vastus and max_vastus > 1:
    ${n+1}.
    % endif
  </td>
  <td style="padding:0">
    <div id="${field_id}" name="${name}" n_asend="${kysimus.n_asend}" data-n="${n}"
     style="min-width:${kysimus.pikkus and kysimus.pikkus * 10 or 300}px"
     class="${c.is_edit and 'math-edit' or 'math-view'} ${corr_cls}">${h.html_lt(response)}</div>
    ${h.hidden(name, response, id=field_id + 'r_', data_kood=kysimus.kood, data_n=n)}
  </td>
</tr>
% endfor
</tbody>
</table>
</div>
</%def>

<%def name="block_view_js()">
% if c.is_edit:
<% kysimus = c.block.kysimus %>
## kasutab matheditor.js
var matheditor_buttons = ${model.json.dumps(c.ylesanne.get_math_icons())};
$(function(){
   var math_set_finished = function(){
   var fields = $('#block_${c.block_prefix} input[data-kood="${kysimus.kood}"]');
   var finished = fields.filter(function(){
       return ($(this).val() != '' || $(this).hasClass('example'));
   });
   var is_finished = finished.length >= ${kysimus.min_vastus or 0};
   var block = $('#block_${c.block_prefix}');
   set_sp_finished(block, is_finished);
  }
  $('#block_${c.block_prefix}').on('keyup', '.mq-textarea textarea', math_set_finished);
  math_set_finished();
});
% endif
</%def>
