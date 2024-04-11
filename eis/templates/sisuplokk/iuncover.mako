## -*- coding: utf-8 -*- 
## Pildi avamine
<%inherit file="baasplokk.mako"/>
<%namespace name="graphutils" file="graphutils.mako"/>
<%namespace name="choiceutils" file="choiceutils.mako"/>
<!-- ${self.name} -->

<%def name="block_edit()">
<%
  di_data = c.block.get_json_sisu()
  c.unc_data = c.new_item.create_from_dict(di_data) or c.new_item()
  b_correct, b_locals = c.block.correct_responses(c.ylesandevastus, c.lang)
  mo = c.block.taustobjekt
%>
${graphutils.edit_background(c.block)}

<div class="row mb-1">
  <% name = 'unc.baastyyp' %>
  ${h.flb(_("Väärtuse tüüp"), name, 'col-md-3 col-xl-2 text-md-right')}
  <div class="col-md-3 col-xl-2">
    ${h.select('unc.baastyyp', c.unc_data.baastyyp or const.BASETYPE_INTEGER, c.opt.tulemus_baseType, wide=False)}
  </div>
  <div class="col-md-6 col-xl-4">
    ${h.checkbox('unc.valesti', 1, checked=c.unc_data.valesti, label=_("Kas lubada valesti vastata"))}
  </div>
  <div class="col-md-6 col-xl-4">
    ${h.checkbox('unc.onabi', 1, checked=c.unc_data.onabi, label=_("Kas on ABI nupud"))}
  </div>
  <div class="col-md-6 col-xl-4">
    ${h.checkbox('unc.evast_edasi', 1, checked=c.unc_data.evast_edasi, label=_("Kasuta vastuseid testi edasistes ülesannetes algseisuna"))}
  </div>
  <div class="col-md-6 col-xl-4">
    ${h.checkbox('unc.evast_kasuta', 1, checked=c.unc_data.evast_kasuta, label=_("Kasuta testi varasemate ülesannete vastuseid algseisuna"))}
  </div>
  <div class="col-md-6 col-xl-4">
    ${h.checkbox('unc.evast_kasuta_muutmata', 1, checked=c.unc_data.evast_kasuta_muutmata, label=_("Ära luba muuta varasematest ülesannetest üle võetud vastuseid"))}  
  </div>
</div>

% if mo.has_file:
<div class="floatleft" style="padding-right:25px">
${graphutils.sketchpad(c.block)}
<script>
$(function() {
  ${graphutils.js_sketchpad(c.block)}
% if mo.laius and mo.korgus and c.block.korgus and c.block.laius:
<%
  cell_order = c.unc_data.cell_order or []
  cell_ids = '[%s]' % (','.join(['"%s"' % r for r in cell_order]))
%>
  sketchpad.uncover_draw_grid(${mo.laius}, ${mo.korgus}, ${c.block.korgus}, ${c.block.laius}, ${cell_ids}, false);
% endif
  $('input#f_korgus,input#f_laius').change(function(){
   var cols = parseInt($('input#f_laius').val());
   var rows = parseInt($('input#f_korgus').val());
   var cnt = cols * rows;
   if(!isNaN(cnt)) 
{
    sketchpad.uncover_draw_grid(${mo.laius}, ${mo.korgus}, rows, cols, ${cell_ids}, false);
    $('table#u_tbl>tbody>tr').eq(cnt-1).nextAll().remove();
    for(i=$('table#u_tbl>tbody>tr').length; i < cnt; i++)
    {
       ## lisame rea
       var tr = grid_addrow('u_tbl', 'u-kood', 'U1');
       ## rea jrknr
       tr.find('td.u-seq').text(i+1);                                      
       tr.find('input.u-seq').val(i+1);                                      
       ## vajadusel kirev tekst/lihttekst
       toggle_ckeditor('u', true, -1, {toolbar:'inlinetext',language:'${request.localizer.locale_name}'}, 'u_tbl', 'l.rtf');
    }
    $('table#u_tbl')[0].setAttribute('counter', cnt);
   }
});
});
</script>
</div>

<div class="mt-2 d-flex">
  <div>
  <div class="d-flex flex-wrap">
    <h3 class="flex-grow-1">${_("Avaldised")}</h3>
    <div>
<%
  bkysimus = c.block.get_baaskysimus()
  is_rtf = bkysimus and bkysimus.rtf
  ronly = not c.is_tr and not c.is_edit or bool(c.block.ylesanne and c.block.ylesanne.lukus)
  toolbar = 'inlinetext'
%>
% if not ronly:
  ${h.checkbox('l.rtf', 1, checked=is_rtf, onclick="toggle_ckeditor('u', true, null, {toolbar:'%s',language:'%s'}, 'u_tbl', 'l.rtf');" % (toolbar, request.localizer.locale_name), label=_("Kirev tekst"))} 
% else:
  ${h.checkbox('l.rtf', 1, checked=is_rtf, disabled=True, label=_("Kirev tekst"))}
% endif

<span id="u_dock_span" style="display:${is_rtf and 'inline' or 'none'}">
  % if not ronly:
  ${h.checkbox('u_dock', 1, checked=None,onclick="$('div#u_ckeditor_top').toggleClass('dock-top')", label=_("Nupurea lukustamine"))}
  % endif
</span>
    </div>
  </div>

  <div id="u_ckeditor_top"></div>
% if not ronly:
  <script>
$(document).ready(function(){
  if($('input#lrtf').is(':checked'))
  {
    toggle_ckeditor('u', false, null, {toolbar:'${toolbar}', language: '${request.localizer.locale_name}'}, 'u_tbl', 'l.rtf');
  }
});
  </script>
% endif


      <table class="table" id="u_tbl">
        <thead>
          <tr>
            <th>${_("Jrk")}</th>
            <th>${_("Küsimuse kood")}</th>
            <th>${_("Etteantud osa")}</th>
            <th>${_("Vastuse osa")}</th>
            <th>${_("Etteantud osa")}</th>
          </tr>
        </thead>
        <tbody>
          <% prefix = 'unck' %>
          % if c._arrayindexes != '' and not c.is_tr:
          ## valideerimisvigade korral
          %   for cnt in c._arrayindexes.get(prefix) or []:
          ${self.row_ucell(c.new_item(), prefix, '-%s' % cnt, b_correct, is_rtf, ronly)}
          %   endfor
          % else:
          ## tavaline kuva
          %   for cnt,kysimus in enumerate(c.block.pariskysimused):
          ${self.row_ucell(kysimus, prefix,'-%s' % cnt, b_correct, is_rtf, ronly)}
          %   endfor
          % endif
        </tbody>
      </table>
      <div id="sample_u_tbl" class="invisible">
<!--
   ${self.row_ucell(c.new_item(kood='__kood__'), prefix, '__cnt__', b_correct, is_rtf, ronly)}
-->
      </div>
  </div>

<script>
  $('.expr1,.expr2').change(function(){
  ## õige vastuse arvutamine eeldusel, et sisestati tehted
  var tr = $(this).closest('tr');
  var get_expr = function(field){
     return field.val().replace(/x/g,'*').replace(/:/g,'/').replace(/^\s+|\s+$/g,'');
  }
  var expr1 = get_expr(tr.find('input.expr1'));
  var expr2 = get_expr(tr.find('input.expr2'));
  var value = NaN;
  try {
     if(expr1.match(/=$/))
     {
        var value1 = eval(expr1.replace(/=$/,''));
        if(!expr2) value = value1;
        else if (expr2.match(/^\+/)) value = value1 - eval(expr2.replace(/^\+/,''));
        else if (expr2.match(/^\-/)) value = value1 + eval(expr2.replace(/^\-/,''));
        else if (expr2.match(/^\*/)) value = value1 / eval(expr2.replace(/^\*/,''));
        else if (expr2.match(/^\//)) value = value1 * eval(expr2.replace(/^\//,''));  
     }
     else if(expr2.match(/^=/))
     {
        var value3 = eval(expr2.replace(/^=/,''));
        if(!expr1) value = value2;
        else if (expr1.match(/\+$/)) value = value2 - eval(expr1.replace(/\+$/,''));
        else if (expr1.match(/\-$/)) value = eval(expr1.replace(/\-$/,'')) - value;
        else if (expr1.match(/\*$/)) value = value2 / eval(expr1.replace(/\*$/,''));
        else if (expr1.match(/\/$/)) value = value2 * eval(expr1.replace(/\/$/,''));
     }
  } catch(e) {
     console.log(e);
  }  
  if(!isNaN(value))
  {
     tr.find('input.expresp').val(value);
  }
  });
</script>
</div>
% endif

</%def>

<%def name="row_ucell(kysimus, baseprefix, ind, b_correct, is_rtf, ronly)">
<%
  prefix = '%s%s' % (baseprefix, ind)
  vdata = {valik.kood: valik.tran(c.lang).nimi for valik in kysimus.valikud}
  kv_correct = b_correct.get(kysimus.kood)
  r_correct = ''
  if kv_correct:
     for kvs_correct in kv_correct.kvsisud:
         r_correct = kvs_correct.sisu
         break
%>
<tr>
    <td class="u-seq">${kysimus.seq}</td>
    <td>
      % if c.is_tr:
      ${kysimus.kood}
      ${h.hidden(prefix + '.kood', kysimus.kood)}
      % else:
      ${h.text5(prefix + '.kood', kysimus.kood, class_="u-kood")}
      % endif
      ${h.hidden(prefix + '.seq', kysimus.seq, class_="u-seq")}
    </td>
    <td>
       ${self.text_rtf(prefix, vdata.get('expr1'), 'expr1', is_rtf, ronly)}
    </td>
    <td>
      ${h.text(prefix + '.expresp', r_correct, class_='expresp', size=12,
      style="background-color:#efefef;")}
    </td>
    <td>
       ${self.text_rtf(prefix, vdata.get('expr2'), 'expr2', is_rtf, ronly)}
    </td>
  </tr>
</%def>

<%def name="text_rtf(prefix, value, cls, is_rtf, ronly)">
     % if ronly:
        % if is_rtf:
          ${h.literal(value)}
        % else:
          ${value}
        % endif
     % elif is_rtf:
          ${h.textarea('%s.%s_rtf' % (prefix, cls), value, cols=80, rows=3, ronly=ronly, class_='editable')}
          ${h.text('%s.%s' % (prefix, cls), '', ronly=ronly, class_='editable %s' % cls, size=12, style="display:none")}
     % else:
          ${h.textarea('%s.%s_rtf' % (prefix, cls), '', cols=80, rows=3,
                       ronly=ronly, class_='editable', style="display:none")}
          ${h.text('%s.%s' % (prefix, cls), value, ronly=ronly, class_='editable %s' % cls, size=12)}
     % endif
</%def>

<%def name="block_view()">
<%
  di_data = c.block.get_json_sisu()
  c.unc_data = c.new_item.create_from_dict(di_data) or c.new_item()
%>
<div id="block_${c.block_prefix}" class="asblock">
 <table width="100%">
   <tr>
     <td>
       ${graphutils.sketchpad(c.block)}
     </td>
     <td>
       <div class="message"> </div>
       <%
         try:
             # MemSisuplokk
             li_correct = c.block.list_correct_responses
             b_correct = {r.kood: r for r in li_correct}
         except AttributeError:
             # Sisuplokk
             b_correct, b_locals = c.block.correct_responses(c.lang)
       %>
       % for kysimus in c.block.pariskysimused:
       ${self.block_view_k(kysimus, b_correct)}
       % endfor
     </td>
   </tr>
</table>
</%def>

<%def name="block_view_k(kysimus, b_correct)">
## kysimuse kuvamine lahendajale: avaldis, lynk, abi-nupp
<%
  name = kysimus.result
  vdata = {valik.kood: valik.tran(c.lang).nimi for valik in kysimus.valikud}
  tulemus = kysimus.tulemus
  kv_correct = b_correct.get(kysimus.kood)
  r_correct_b64 = ''
  if kv_correct:
     for kvs_correct in kv_correct.kvsisud:
         r_correct_b64 = h.b64encode2s(kvs_correct.sisu.encode('utf-8'))
         break
  
  value = kood2 = ''
  if c.block.naide or c.block_correct:
     responses = c.correct_responses
  else:
     responses = c.responses
  kv = responses.get(kysimus.kood)
  if kv and len(kv.kvsisud):
     ks = kv.kvsisud[0]
     value = ks.sisu
     kood2 = ks.kood2
  else:
     ks = None

  if c.prepare_correct and ks and ks.on_hinnatud and not c.block.varvimata:
     corr_cls = model.ks_correct_cls(responses, kysimus.tulemus, kv, ks, False) or ''
  else:
     corr_cls = ''
  # kui sooritamine käib ja eespoolt vastus olemas ja kui eelmisi vastuseid võib kasutada nii, et neid ei saa muuta
  kv_read_only = c.unc_data.evast_kasuta_muutmata and (kysimus.kood in c.evast_koodid)
%>
<table class="border float-left m-3">
  <tr class="uncover-k" data-expr="${r_correct_b64}" data-seq="${kysimus.seq}">
    <td>${vdata.get('expr1')}</td>
    <td class="${corr_cls}">
      % if not c.block.read_only and kv_read_only and (value or kood2):
      ${h.escape_script(value)}
      ${h.hidden(name, value)}
      % elif tulemus and tulemus.baastyyp == const.BASETYPE_INTEGER:
      ${h.int5(name, value, class_="expresp")}
      % elif tulemus and tulemus.baastyyp == const.BASETYPE_FLOAT:
      ${h.float5(name, value, class_="expresp")}
      % else:
      ${h.text5(name, value, class_="expresp")}
      % endif
    </td>
    <td>${vdata.get('expr2')}</td>
    % if c.unc_data.onabi:
    <td class="uchelp">
      % if not (kv_read_only and (value or kood2)):
      ${h.button(_("ABI"), class_="uchelp")}
      % endif
      ## abi kasutamise loendur
      ${h.hidden(name + '_hlp_', kood2, class_='kood2')}
    </td>
    % endif
  </tr>
</table>
</%def>

<%def name="block_print()">
<table>
  <tr>
    <td valign="top">
      ${graphutils.print_hotspots(c.block)}
    </td>
    <td valign="top">
% for kysimus in c.block.pariskysimused:
<%
  vdata = {valik.kood: valik.nimi for valik in kysimus.valikud}
%>
<table class="border">
  <tr>
    <td>${vdata.get('expr1')}</td>
    <td>${h.print_input(4)}</td>
    <td>${vdata.get('expr2')}</td>
  </tr>
</table>
% endfor

    </td>
  </tr>
</table>
</%def>


<%def name="block_view_js()">
<% 
  mo = c.block.taustobjekt 
  min_vastus = c.block.kysimus.min_vastus or 'null'
  cell_order = c.unc_data.cell_order or []
  cell_ids = '[%s]' % (','.join(['"%s"' % r for r in cell_order]))
%>
$(function(){
  ${graphutils.js_sketchpad(c.block, drag_images=True)}
  sketchpad.uncover_draw_grid(${mo.laius}, ${mo.korgus}, ${c.block.korgus or 0}, ${c.block.laius or 0}, ${cell_ids}, true);
  % if c.block_correct or c.block.naide:
  ${self.js_show_response(c.correct_responses)}
  % else:
  ${self.js_show_response(c.responses)}
  % endif
  is_response_dirty = false;
  var block = $('div#block_${c.block_prefix}')
  sketchpad.uncover_set_finished(block, ${min_vastus});
  sketchpad.uncover_setup(block, ${c.unc_data.valesti and 'true' or 'false'}, ${min_vastus});
});
</%def>

<%def name="block_entry()">
## eelnevalt on seatud c.responses ja c.prefix
    <%
      kysimus = c.block.kysimus
      kv = c.responses.get(kysimus.kood) or []
      kv2 = c.responses2 and c.responses2.get(kysimus.kood) or []
    %>

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
var block = $('div#block_${c.block_prefix}');
% for kysimus in c.block.pariskysimused:
<%
  value = None
  kv = responses.get(kysimus.kood)
  if kv and len(kv.kvsisud):
     value = kv.kvsisud[0].sisu
%>
% if value:
     sketchpad.uncover_cell("${kysimus.seq}");
% endif
% endfor
</%def>
