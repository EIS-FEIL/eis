## -*- coding: utf-8 -*- 
<%inherit file="baasplokk.mako"/>
<!-- ${self.name} -->
<%namespace name="choiceutils" file="choiceutils.mako"/>
<%def name="block_edit()">
<% kood1_opt = c.block.kysimus.valikud_opt + [('', _("Tühi"))] %>
${choiceutils.hindamismaatriks(c.kysimus,
                               heading1=_("Valiku ID"),
                               kood1=kood1_opt,
                               kood1_cls='vkood')}

<div class="form-group row">
  <% name = 'l.laad' %>
  ${h.flb(_("Laad"), name, 'col-md-3 col-xl-2 text-md-right')}
  <div class="col-md-9 col-xl-10">
      % if c.lang:
      ${h.hidden('l.laad', c.kysimus.laad)}
      % else:
      ${h.text('l.laad', c.kysimus.laad, maxlength=256, class_="wide")}
      % endif
  </div>
</div>

</%def>
