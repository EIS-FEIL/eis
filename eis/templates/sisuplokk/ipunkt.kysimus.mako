<%inherit file="baasplokk.mako"/>
<!-- ${self.name} -->
<%namespace name="choiceutils" file="choiceutils.mako"/>
<%def name="block_edit()">
<div class="mb-2">
<% tulemus = c.kysimus.tulemus %>
% if c.kood2:
## lynga hindamismaatriks
${h.hidden('kood2', c.kood2)}
${h.hidden('am1.kysimus_id', c.kysimus.id)}
${h.hidden('am1.kood', c.kysimus.kood)}
${h.hidden('am1.min_pallid','')}
${h.hidden('am1.max_pallid','')}
## toggle_ckeditor() otsib rtf märkeruutu:
<span style="display:none">${h.checkbox1('l.rtf', 1, checked=True)}</span>
${choiceutils.hindamismaatriks_tbl_pag(c.kysimus, 
                                  tulemus=tulemus,
                                  prefix='am1',
                                  maatriks=1)}
% else:
## kogu lause hindamise seaded
${h.hidden('am1.kysimus_id', c.kysimus.id)}
${choiceutils.tulemus(c.kysimus, tulemus, 'am1.')}
% endif
</div>
</%def>
