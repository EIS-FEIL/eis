## -*- coding: utf-8 -*- 
<%inherit file="baasplokk.mako"/>
<!-- ${self.name} -->
<%namespace name="choiceutils" file="choiceutils.mako"/>

<%def name="block_edit()">
<% ronly = not c.is_tr and not c.is_edit %>
<% ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') %>
<div class="row mb-1">
  <% name = 'f_nimi' %>
  ${ch.flb(_("Nimetus"), nimi)}
  <div class="col-md-9 col-xl-10">
    ${h.text('f_nimi', c.item.nimi, maxlength=256, ronly=ronly)}
  </div>

  ${ch.flb(_("Konstandid"), 'konst')}
  <div class="col-md-9 col-xl-10" id="konst">
    ${self.choices(c.block.kysimus, c.block.kysimus.valikud, 'v')}
  </div>

  <% name = 'f_sisu' %>
  ${ch.flb(_("Valem"), name)}
  <div class="col-md-9 col-xl-10">
    ${h.text('f_sisu', c.block.sisu, ronly=ronly)}
  </div>
</div>


${choiceutils.hindamismaatriks(c.block.kysimus, basetype_opt=c.opt.tulemus_baseType_formula, heading1=_("Vastus"), naidis=False)}
</%def>

<%def name="block_view()">
${h.qcode(c.block.kysimus)}
</%def>

<%def name="block_preview()">
${c.block.kysimus.kood} = ${c.block.sisu}
</%def>

<%def name="choices(kysimus, valikud, prefix)">
<table id="choicetbl_${prefix}" class="table table-striped lh-11" > 
  <col width="100px"/>
  <col width="600px"/>
  <thead>
    <tr>
      <th>ID</th>
      <th>${_("Väärtus")}</th>
      <th>${_("Selgitus")}</th>
      <th></th>
    </tr>
  </thead>
  <tbody>

  % if c._arrayindexes != '' and not c.is_tr:
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get(prefix) or []:
        ${choiceutils.row_choices(kysimus, c.new_item(),prefix,'-%s' % cnt, False)}
  %   endfor
  % else:
## tavaline kuva
  %   for cnt,item in enumerate(valikud):
        ${choiceutils.row_choices(kysimus, item,prefix,'-%s' % cnt, False)}
  %   endfor
  % endif

  </tbody>
  <tfoot>
% if c.is_edit and not c.lang:
    <tr>
      <td colspan="6">
${h.button(_("Lisa"), onclick=f"grid_addrow('choicetbl_{prefix}', '{prefix}kood', 'A');")}
<div id="sample_choicetbl_${prefix}" class="invisible">
<!--
   ${choiceutils.row_choices(kysimus, c.new_item(kood='__kood__'),prefix, '__cnt__',False)}
-->
</div>
      </td>
    </tr>
% endif
  </tfoot>
</table>
<br/>
</%def>
