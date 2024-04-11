## -*- coding: utf-8 -*- 
<%inherit file="baasplokk.mako"/>

<%def name="block_edit()">
${_("Täiendav HTML lähtekood, mis paigutatakse veebilehe <head> osa sisse")}
<br/>
  % if c.lang:
  ${c.block.sisu}
<div class="linebreak"></div>
  ${h.lang_tag(c.lang)}
  % endif
  ${h.textarea('f_sisu', c.block.tran(c.lang).sisu, rows=25, ronly=not c.is_tr and not c.is_edit)}
</%def>
