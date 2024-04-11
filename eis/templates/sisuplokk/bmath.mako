## -*- coding: utf-8 -*- 
<%inherit file="baasplokk.mako"/>

<%def name="block_edit()">
<div class="row">
  ${h.flb(_("Matemaatiline tekst"), 'f_sisu', 'col-md-3 col-xl-2 text-md-right')}
  <div class="col-md-9 col-xl-10">
% if c.lang:
${h.lang_tag(c.orig_lang)}
<span class="lang-orig math-view" id="orig_sisu">${c.block.sisu}</span>
<br/>
${h.lang_tag()}
${h.hidden("f_sisu", c.block.tran(c.lang).sisu)}
% else:
${h.hidden("f_sisu", c.block.sisu)}
% endif
<div style="min-width:300px" id="mathexpr" id="f_sisu" name="f_sisu" class="${(c.is_edit or c.is_tr) and 'math-edit' or 'math-view'}">${c.block.tran(c.lang).sisu}</div>
  </div>
</div>
</%def>

<%def name="block_view()">
<div class="math-view">${c.block.tran(c.lang).sisu}</div>
</%def>



