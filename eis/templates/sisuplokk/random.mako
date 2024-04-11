## -*- coding: utf-8 -*- 
<%inherit file="baasplokk.mako"/>
<!-- ${self.name} -->
<%namespace name="choiceutils" file="choiceutils.mako"/>

<%def name="block_edit()">
<%
  ronly = not c.is_tr and not c.is_edit
  kysimus = c.block.kysimus
  tulemus = kysimus.tulemus or c.new_item(kood=kysimus.kood, max_vastus=None)
  c.kyslisa = kysimus.give_kyslisa() 
%>
${h.hidden('am1.kysimus_id', kysimus.id)}
${h.hidden('am1.min_pallid', '')}
${h.hidden('am1.max_pallid', '')}

## rndtable 
<% ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') %>
<div class="row">
  <% name = 'am1.kood' %>
  ${ch.flb(_("Juhuarvu ID"), name)}
  <div class="col-md-3 col-lg-3 col-xl-4">
        ${h.text('am1.kood', tulemus.kood, class_="identifier")}
        % if not c.is_edit:
        ${h.hidden('am1.kood', tulemus.kood)}
        % endif
  </div>

  <% name = 'am1.baastyyp' %>
  ${ch.flb(_("Väärtuse tüüp"), name, colextra='ctulemus')}
  <div class="col-md-3 col-xl-4 ctulemus">
    ${h.select('am1.baastyyp', tulemus.baastyyp, c.opt.tulemus_baseType_arv, wide=False, 
              class_='baastyyp', onclick="showbasetype($(this))")}
        % if not c.is_edit and c.lang:
        ${h.hidden('am1.baastyyp', tulemus.baastyyp, class_='baastyyp')}
        % endif
        <script>
          function showbasetype(fld)
          {
             var val = fld.val();
             $('.basetype-integer').toggle(val == "${const.BASETYPE_INTEGER}")
             $('.basetype-float').toggle(val == "${const.BASETYPE_FLOAT}")
          }
          $(function(){ showbasetype($('[name="am1.baastyyp"]'))});
        </script>
  </div>

  <% name = 'sl.min_vaartus' %>
  ${ch.flb(_("Vahemiku algus"), name)}
  <div class="col-md-3 col-xl-4">
    ${h.text5('sl.min_vaartus', c.kyslisa.min_vaartus)}
  </div>
  <% name = 'sl.max_vaartus' %>
  ${ch.flb(_("Vahemiku lõpp"), name)}
  <div class="col-md-3 col-xl-4">
    ${h.text5('sl.max_vaartus', c.kyslisa.max_vaartus)}
  </div>
</div>
<div class="row mb-1">
  <% name = 'sl.samm' %>
  ${ch.flb(_("Samm"), name, colextra='basetype basetype-integer')}
  <div class="col-md-9 col-xl-4 basetype basetype-integer">
    ${h.posint5('sl.samm', c.kyslisa.samm)}
  </div>

  <% name = 'am1.ymard_komakohad' %>
  ${ch.flb(_("Komakohtade arv"), name, colextra='basetype basetype-float')}
  <div class="col-md-9 col-xl-4 basetype basetype-float">
    ${h.posint5('am1.ymard_komakohad', tulemus.ymard_komakohad)}
  </div>
</div>
<div class="row mb-1">
  <% name = 'am1.k_selgitus' %>
  ${ch.flb(_("Selgitus"), name)}
  <div class="col-md-9">
    ${h.text('am1.k_selgitus', kysimus.selgitus, maxlength=255, class_='selgitus')}
  </div>
</div>
</%def>

<%def name="block_view()">
${h.qcode(c.block.kysimus)}
</%def>

<%def name="block_preview()">
${c.block.kysimus.kood} 
</%def>
