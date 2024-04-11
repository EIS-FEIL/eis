## -*- coding: utf-8 -*- 
## Matemaatilise teksti sisestamine WIRIS MathType abil
<%inherit file="baasplokk.mako"/>
<!-- ${self.name} -->
<%namespace name="choiceutils" file="choiceutils.mako"/>

<%def name="block_edit()">
<% bkysimus = c.block.kysimus %>
<% ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') %>
<div class="form-group row">
  <% name = 'l.max_vastus' %>
  ${ch.flb(_("Vastuste arv"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.posint5('l.max_vastus', bkysimus.max_vastus or 1)}
  </div>
  <% name = 'l.min_vastus' %>
  ${ch.flb(_("Minimaalne vastuste arv"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.posint5('l.min_vastus', bkysimus.min_vastus)}
  </div>
</div>
<%
  lahendusjuhis = c.ylesanne.lahendusjuhis
  wmatriba = lahendusjuhis and lahendusjuhis.wmatriba
  wmath_toolbar = wmatriba and wmatriba.split('|')[-1] or None
%>
<script>
var wmath_toolbar = '${wmath_toolbar}';
</script>
<div class="form-group row">
  <%
    name = 'l.vihje'
    id = 'wmvihje'
  %>
  ${ch.flb(_("Vastuse algväärtus"), name)}
  <div class="col">
    % if c.is_edit:
    <div id="${id}" name="${name}" class="wmath-edit" style="height:200px">
    </div>
    ${h.hidden(name, bkysimus.vihje, id="inp_%s" % id)}
    % else:
    <div id="${id}" name="${name}" class="wmath-view">
      ${bkysimus.vihje}
    </div>
    % endif
  </div>
</div>

${choiceutils.hindamismaatriks(bkysimus, heading1=_("Vastus"), matheditor=True, basetype=const.BASETYPE_MATHML, naidis=True)}
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
  #model.log.debug(kvsisud)
  lahendusjuhis = c.ylesanne.lahendusjuhis
  wmatriba = lahendusjuhis and lahendusjuhis.wmatriba
  wmath_toolbar = wmatriba and wmatriba.split('|')[-1] or None
%>
<script>
var wmath_toolbar = '${wmath_toolbar}';
</script>

% for n in range(max_vastus or 1):
<%
  name = kysimus.result
  id = f'wm_{name}_{n}_'
  ks = len(kvsisud) > n and kvsisud[n] or None
  response = ks and ks.sisu or ''
  if not response and not c.read_only and not ks and kysimus.algvaartus and kysimus.vihje:
     response = kysimus.vihje
  corr_cls = ''
  if c.prepare_correct and ks and ks.on_hinnatud and not c.block.varvimata:
     corr_cls = model.ks_correct_cls(responses, kysimus.tulemus, kv, ks, False) or ''
%>
<div class="d-flex">
    <div width="20px" class="pr-2">
    % if max_vastus and max_vastus > 1:
      ${n+1}.
    % endif
    </div>
    <div class="flex-grow-1">
    <div id="tbl_${id}"></div>
    % if c.is_edit:
    <div id="${id}" name="${name}" class="wmath-edit">
    </div>
    ${h.hidden(name, response, data_kood=kysimus.kood, id="inp_%s" % id)}
    % else:
    <div id="${id}" name="${name}" class="wmath-view ${corr_cls}">
      ${h.escape_script(response)}
    </div>
    % endif
    </div>
</div>
% endfor

</div>
</%def>

<%def name="block_view_js()">
<% kysimus = c.block.kysimus %>

$(function(){
% if c.is_edit:
  var math_set_finished = function(arg){
   var fields = $('#block_${c.block_prefix} input[name="${kysimus.result}"]');
   var finished = fields.filter(function(){
       return ($(this).val() != '' || $(this).hasClass('example'));
   });
   var is_finished = finished.length >= ${kysimus.min_vastus or 0};
   var block = $('#block_${c.block_prefix}');
   set_sp_finished(block, is_finished);
   if(arg)
       response_changed(fields);
  }
  $('#block_${c.block_prefix}').on('keyup', '.wrs_editor', math_set_finished);
  math_set_finished(null);
% endif
});
</%def>
