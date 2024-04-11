## -*- coding: utf-8 -*- 
<%inherit file="baasplokk.mako"/>

<%def name="block_edit()">
% if c.lang:
${h.lang_tag(c.orig_lang)}
<span class="lang-orig" id="orig_sisu">${c.block.sisu}</span>
<br/>
${h.lang_tag()}
<% value = c.block.tran(c.lang).sisu %>
% else:
<% value = c.block.sisu %>
% endif
${h.hidden("f_sisu", value, id="inp_mw_%s" % c.block_prefix)}

% if c.is_edit or c.is_tr:
<div id="mw_${c.block_prefix}" style="min-width:300px;height:300px;" class="wmath-edit" lang="${request.locale_name}"></div>
% else:
<div id="mw_${c.block_prefix}" style="min-width:300px;min-height:200px;" class="wmath-view" lang="${request.locale_name}">${value}</div>
% endif
</%def>

<%def name="block_view()">
##<div id="mw_${c.block_prefix}" class="wmath-view" lang="${request.locale_name}">${c.block.tran(c.lang).sisu}</div>
<div id="mw_${c.block_prefix}">
  ${c.block.tran(c.lang).sisu}
</div>
</%def>



