## -*- coding: utf-8 -*- 
<%inherit file="baasplokk.mako"/>
<!-- ${self.name} -->
<%namespace name="choiceutils" file="choiceutils.mako"/>
<%def name="block_edit()">
<div>
  ${c.kysimusesisu}
</div>
<div>
<%
  choiceutils.hindamismaatriks(c.kysimus,
                               fix_kood=True,
                               prefix='am1',
                               nocommon=c.block.alamtyyp!='N'
                               )
%>
</div>
</%def>
