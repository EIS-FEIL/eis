## -*- coding: utf-8 -*- 
<%inherit file="baasplokk.mako"/>
<!-- ${self.name} -->
<%namespace name="choiceutils" file="choiceutils.mako"/>
<%def name="block_edit()">
<% t_kysimus = c.kysimus.tran(c.lang) %>
% if c.pos_x != '' and c.pos_y != '':
## selle ruudu koordinaadid, kus klikiti
${h.hidden('l.pos_x', c.pos_x)}
${h.hidden('l.pos_y', c.pos_y)}
% else:
## andmebaasis olevad kysimuse koordinaadid
${h.hidden('l.pos_x', t_kysimus.pos_x)}
${h.hidden('l.pos_y', t_kysimus.pos_y)}
% endif
<% ch = h.colHelper('col-md-3 col-lg-2 text-md-right', 'col-md-3 col-xl-4') %>
## sõna, päris kysimus
<div class="row">
  <% name = 'l.vihje' %>
  ${ch.flb(_("Vihje"), name)}
  <div class="col-md-9 col-lg-10">
      % if c.lang:
        ${h.lang_orig(c.kysimus.vihje)}<br/>
        ${h.lang_tag()}${h.text('l.vihje', t_kysimus.vihje, size=20, maxlength=256, ronly=not c.is_tr)}
      % else:
        ${h.text('l.vihje', c.kysimus.vihje, size=20, maxlength=256, ronly=not c.is_tr and not c.is_edit)}
      % endif
  </div>
</div>
<div class="row">
  <% name = 'mo.filedata' %>
  ${ch.flb(_("Pildifail"), name)}
  <div class="col-md-9 col-lg-3">
      <%
        mo = c.kysimus.sisuobjekt
        t_mo = mo and mo.tran(c.lang)
        files = []
        if mo and mo.has_file:
           files = [(mo.get_url(c.lang, c.url_no_sp), mo.filename, mo.filesize)]
      %>
      ${h.file('mo.filedata', value=_("Fail"), files=files)}
      % if mo and c.kysimus.id:
      <table>
        <tr>
          <td>
            <img src="${mo.get_url(c.lang, c.url_no_sp)}" title="${t_kysimus.vihje}" ${h.width(t_mo)} ${h.height(t_mo)}/>
          </td>
          <td>
            ${h.grid_remove()}
            ${h.hidden('mo_id', mo.id)}
          </td>
        </tr>
      </table>
      % endif
  </div>

  <% name = 'mo.laius' %>
  ${ch.flb(_("Laius"), name, 'col-md-3 col-lg-2 text-md-right')}
  <div class="col-md-2 col-lg-1">
    % if c.lang:
    ${h.posint5('mo.laius', t_mo and t_mo.laius, ronly=not c.is_tr, maxvalue=900)}
    % else:
    ${h.posint5('mo.laius', mo and mo.laius, ronly=not c.is_edit, maxvalue=900)}
    % endif
  </div>

  <% name = 'mo.korgus' %>
  ${ch.flb(_("Kõrgus"), name, 'col-md-3 col-lg-2 text-md-right')}
  <div class="col-md-2 col-lg-1">
    % if c.lang:
    ${h.posint5('mo.korgus', t_mo and t_mo.korgus, ronly=not c.is_tr)}
    % else:
    ${h.posint5('mo.korgus', mo and mo.korgus, ronly=not c.is_edit)}
    % endif
  </div>
</div>
<div class="row">
  <% name = 'l.pikkus' %>
  ${ch.flb(_("Tähtede arv"), name, 'col-md-3 col-lg-2 text-md-right')}
  <div class="col-md-9 col-lg-2">
      % if c.lang:
        ${h.lang_orig(c.kysimus.pikkus)}<br/>
        ${h.lang_tag()}${h.text5('l.pikkus', t_kysimus.pikkus, ronly=not c.is_tr)}
      % else:
        ${h.text5('l.pikkus', c.kysimus.pikkus, ronly=not c.is_tr and not c.is_edit)}
      % endif
  </div>

  <% name = 'l.joondus' %>
  ${ch.flb(_("Suund"), name)}
  <div class="col">
    ${h.select_radio('l.joondus', t_kysimus.joondus or c.opt.suund[0][0], c.opt.suund, ronly=not c.is_tr and not c.is_edit)}
  </div>

</div>
${choiceutils.hindamismaatriks(c.kysimus, tulemus=c.tulemus, heading1=_("Vastus"))}

</%def>
