## -*- coding: utf-8 -*- 
<%inherit file="baasplokk.mako"/>
<!-- ${self.name} -->
<%namespace name="choiceutils" file="choiceutils.mako"/>
<%def name="block_edit()">
<%
  ## wysiwyg=False (ei luba ckeditori) seepärast, et kui avada ja sulgeda ühes
  ## aknas mitmeid dialoogiaknais, siis pärast ei saa enam ckeditori väljalt
  ## teksti kätte.
   choiceutils.choices(c.kysimus, c.valikud, 'v', size=45, wysiwyg=False)
   ##c.valikud_opt = [v.kood for v in c.valikud]
   choiceutils.hindamismaatriks(c.kysimus, 
                                #kood1=c.valikud_opt,
                                #kood1_cls='vkood',
                                tulemus=c.tulemus)
  %>
<div class="form-group row">
  <% name = 'l.laad' %>
  ${h.flb(_("Laad"), name, 'col-md-3 col-xl-2 text-md-right')}
  <div class="col-md-9 col-xl-10">
      % if c.lang:
      ${h.hidden('l.laad', c.kysimus.laad)}
      % else:
      ${h.text('l.laad', c.kysimus.laad, maxlength=256)}
      % endif
  </div>
</div>
</%def>
