## -*- coding: utf-8 -*- 
## Lühivastusega küsimus
<%inherit file="baasplokk.mako"/>
<!-- ${self.name} -->
<%namespace name="choiceutils" file="choiceutils.mako"/>

<%def name="block_edit()">
<% bkysimus = c.block.kysimus %>
<% ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') %>
<div class="row pt-1">
  <% name = 'l.pikkus' %>
  ${ch.flb(_("Eeldatav vastuse pikkus"), name)}
  <div class="col-md-9 col-xl-4">
    ${h.posint5('l.pikkus', bkysimus.pikkus)}
  </div>

  <% name = 'l.mask' %>
  ${ch.flb(_("Mask"), name)}
  <div class="col-md-9 col-xl-4">
    ${h.text('l.mask', bkysimus.mask)}
  </div>

  <% name = 'l.vihje' %>
  ${ch.flb(_("Vihje"), name)}
  <div class="col-md-3 col-xl-4">
      % if c.lang:
        ${h.lang_orig(bkysimus.vihje)}
       <div class="linebreak"></div>
        ${h.lang_tag()}
        ${h.text('l.vihje', bkysimus.tran(c.lang).vihje, size=35, maxlength=256, ronly=not c.is_tr)}
      % else:
        ${h.text('l.vihje', bkysimus.vihje, size=35, maxlength=256, ronly=not c.is_tr and not c.is_edit)}
      % endif
  </div>
  <div class="col-md-12 col-lg-6 col-xl-6 d-flex justify-content-end">
    ${h.checkbox('l.algvaartus', 1, checked=bkysimus.algvaartus, label=_("Vihje jääb vastuse algväärtuseks"))}
  </div>
</div>
<div class="row pb-1">
  <% name = 'l.max_vastus' %>
  ${ch.flb(_("Vastuste arv"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.posint5('l.max_vastus', bkysimus.max_vastus or 1, wide=False)}
  </div>
  <% name = 'l.min_vastus' %>
  ${ch.flb(_("Minimaalne vastuste arv"), name)}
  <div class="col-md-3 col-xl-1">
    ${h.posint5('l.min_vastus', bkysimus.min_vastus, wide=False)}
  </div>
  <div class="col-md-6 col-xl-6 pl-3">
    ${choiceutils.joondus(bkysimus)}
  </div>
</div>

${choiceutils.hindamismaatriks(bkysimus, basetype_opt=c.opt.tulemus_baseType, heading1=_("Vastus"), naidis=True, naidis_naha=False)}
</%def>

<%def name="block_view()">
<%
  kysimus = c.block.kysimus
  if c.block.naide or c.block_correct:
     responses = c.correct_responses
  else:
     responses = c.responses
  kv = responses.get(kysimus.kood)
  kvsisud = kv and list(kv.kvsisud) or []
  kvskannid = kv and list(kv.kvskannid) or []
  max_vastus = kysimus.max_vastus or 1

  bcls = 'asblock'
  if c.block.kleepekeeld:
      bcls += ' nopaste'  
%>
% if max_vastus == 1:
<span id="block_${c.block_prefix}" class="${bcls}">
  ${h.qcode(kysimus)}
  ${self.view_input(kysimus, responses, kv, kvsisud, kvskannid, 0)}
</span>
% else:
<table id="block_${c.block_prefix}" class="${bcls}">
  <col width="20px"/>
  <tbody>
    % for n in range(max_vastus):
    <tr>
      <td>${n+1}.</td>
      <td>
        ${self.view_input(kysimus, responses, kv, kvsisud, kvskannid, n)}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
</%def>

<%def name="view_input(kysimus, responses, kv, kvsisud, kvskannid, n)">
<%
  name = kysimus.result
  field_id = f'{name}_{n}_'
  tulemus = kysimus.tulemus
  ks = len(kvsisud) > n and kvsisud[n]
  skann = len(kvskannid) > n and kvskannid[n]

  value = ''
  if ks:
     value = ks.sisu
  elif kysimus.algvaartus:
     value = kysimus.tran(c.lang).vihje
  
  class_ = ''
  if kysimus.joondus:
     class_ = ' text-align-%s' % (kysimus.joondus)
  # käsitsihinnatav lynk kuvatakse hindajale kollase hinnatavlynk-klassiga
  # arvutihinnatav kuvatakse hindajale õigsuse värviga (ES-1748)
  if c.on_hindamine and kv and not kv.arvutihinnatud:
     class_ += ' hinnatavlynk'
  if (c.prepare_correct or c.on_hindamine and kv and kv.arvutihinnatud) and ks and ks.on_hinnatud and not c.block.varvimata:
     class_ += model.ks_correct_cls(responses, tulemus, kv, ks, False, not c.block_correct) or ''
  class_ = class_.strip() or None
%>
% if skann:
    <div ${class_ and 'class="%s"' % class_ or ''}>
    ${h.image(h.url('tulemus_kvskann', sooritus_id=c.sooritus.id,
     id=skann.id), width=skann.laius_orig and skann.laius_orig/4)}
    </div>
% elif kysimus.vorming_kood == const.BASETYPE_INTEGER:
    ${h.int10(name, value, id=field_id, size=kysimus.pikkus,
     maxlength=kysimus.pikkus, title=kysimus.tran(c.lang).vihje,
    pattern=kysimus.mask, datafield=False, readonly=not c.is_edit, class_=class_,
    data_kood=kysimus.kood)}
% elif kysimus.vorming_kood == const.BASETYPE_FLOAT:
    ${h.float10(name, value, id=field_id, size=kysimus.pikkus,
     maxlength=kysimus.pikkus, title=kysimus.tran(c.lang).vihje,
    pattern=kysimus.mask, datafield=False, readonly=not c.is_edit, class_=class_,
    data_kood=kysimus.kood)}
% else:
    ${h.text(name, value, id=field_id, size=kysimus.pikkus,
     maxlength=kysimus.pikkus, title=kysimus.tran(c.lang).vihje,
    pattern=kysimus.mask, datafield=False, readonly=not c.is_edit, class_=class_,
    spellcheck=c.ylesanne.spellcheck,
    data_kood=kysimus.kood)}
% endif
</%def>    

<%def name="block_view_js()">
<%
  kysimus = c.block.kysimus
  name = kysimus.result
%>
$(function(){
  var fields = $('input[name="${name}"]');
% if c.block.read_only:
## ei saa vastust muuta
  fields.prop('readonly',true);
% else:
  fields.keyup(function(){
        input_set_finished($(this), ${kysimus.min_vastus or 0})
  }).change(function(){
        ## muutmine märkida kõigis sama kysimuse vastustes
        response_changed($('input[name="${name}"]'));
  });
  input_set_finished(fields, ${kysimus.min_vastus or 0});
% endif
  is_response_dirty = false;
});
</%def>


<%def name="block_preview()">
<% kysimus = c.block.kysimus %>
% for n in range(kysimus.max_vastus or 1):
${h.text('input', '', size=kysimus.pikkus or 20, wide=False, pattern=kysimus.mask)}
% endfor
</%def>

<%def name="block_print()">
<%
  kysimus = c.block.kysimus
  value = ''
  if kysimus.kood:
     for entry in kysimus.best_entries():
         value = entry.kood1   
         break
%>
    % if c.block.naide and value:
       <b>${value}</b>
    % else:
      ${h.print_input(kysimus.pikkus or 20)}
    % endif
</%def>

