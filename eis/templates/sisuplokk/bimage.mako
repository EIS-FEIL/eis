## -*- coding: utf-8 -*- 
<%inherit file="baasplokk.mako"/>
<%namespace name="dragimg" file="bimage.dragimg.mako"/>

<%def name="block_edit()">
${dragimg.edit_images(c.block)}
</%def>

<%def name="block_view()">
% for obj in c.block.piltobjektid:
<%
  tr_obj = obj.tran(c.lang)
  width = tr_obj and tr_obj.laius or obj.laius
  height = tr_obj and tr_obj.korgus or obj.korgus
%>
<image src="${obj.get_url(c.lang, c.url_no_sp)}"
       alt="${_("Pilt")}"
       ${h.width(width)} ${h.height(height)}
       title="${obj.tran(c.lang).tiitel}"/>
% endfor
</%def>

<%def name="block_print()">
% for obj in c.block.piltobjektid:
<%
  tr_obj = obj.tran(c.lang)
  width = tr_obj and tr_obj.laius or obj.laius
  height = tr_obj and tr_obj.korgus or obj.korgus
%>
<image src="${obj.get_url(c.lang, c.url_no_sp)}"
       alt="${_("Pilt")}"
       ${h.width(width)} ${h.height(height)}
       style="${h.width(width, True)} ${h.height(height, True)}"
       title="${obj.tran(c.lang).tiitel}"/>
% endfor
</%def>

<%def name="block_preview()">
% for obj in c.block.piltobjektid:
<div style="display:inline-block">
     <image src="${obj.get_url(c.lang, c.url_no_sp)}"
            alt="${_("Pilt")}" ${h.width(obj)} style="max-width:100%"
            title="${obj.tran(c.lang).tiitel}"/>
     <br/>
     images/${obj.filename}
</div>
% endfor
</%def>
