## -*- coding: utf-8 -*- 
## Abifunktsioonid pildiküsimuste sisuplokkide jaoks

<%def name="toolbox_area(item)">
<div style="padding-bottom:20px">
      <script>
        function select_tool_${c.block_prefix}(value)
        {
          sketchpads.sketchpad_${c.block_prefix}.tool = value;
        };
      </script>
     <div id="toolbuttons_${c.block_prefix}" class="m-1">
       <%
          if item.tyyp == const.INTER_SELECT:
             shapes = c.opt.shape
             #shapes = c.opt.shape_free
          else:
             shapes = c.opt.shape
       %>
       % for tool in shapes:
       ${h.radio('tool', tool[0], onclick="select_tool_%s('%s')" % (c.block_prefix, tool[0]), label=tool[1])}
      % endfor
     </div>
      ${h.hidden('draw_width', '2')}
      ${h.hidden('draw_stroke', '0000ff')}
</div>
</%def>

<%def name="edit_background(item, min_max=True, kysimus=None)">
<%
  if not kysimus:
     kysimus = item.kysimus
  mo = item.taustobjekt
  ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4')
%>
<div class="row pb-1">
  ${ch.flb(_("Taustapilt"), 'mofiledata')}
  <div class="col-md-9 col-xl-10">
    <%
      files = []
      if mo and mo.has_file:
         files.append((h.url('ylesanne_sisufail', id='%s.%s' % (mo.id, mo.fileext)), mo.filename, mo.filesize))
      if c.lang:
         mot = mo.give_tran(c.lang)
         if mot.has_file:
            files.append((h.url('ylesanne_sisufail', id='%s.%s' % (mo.id, mo.fileext), lang=c.lang), mo.filename, mot.filesize))
    %>
    ${h.file('mo.filedata', value=_("Fail"), files=files)}
  </div>

% if mo:
  ${ch.flb(_("Laius"), 'molaius')}
  <div class="col-md-3 col-xl-1">
    ${h.posint5('mo.laius', mo.laius, maxvalue=900)}
  </div>
  ${ch.flb(_("Kõrgus"), 'mokorgus')}
  <div class="col-md-3 col-xl-1">
    ${h.posint5('mo.korgus', mo.korgus)}
  </div>

% endif

% if item.tyyp == const.INTER_UNCOVER:
  ${ch.flb(_("Ridade arv"), 'f_korgus')}
  <div class="col-md-3 col-xl-1">
    ${h.posint5('f_korgus', c.block.korgus)}
  </div>
  ${ch.flb(_("Veergude arv"), 'f_laius')}
  <div class="col-md-3 col-xl-1">
    ${h.posint5('f_laius', c.block.laius)}
  </div>
% endif   
% if min_max:
  % if item.tyyp == const.INTER_DRAW:
  ${ch.flb(_("Minimaalne kujundite arv"), 'lmin_vastus')}
  <div class="col-md-3 col-xl-1">
    ${h.text5('l.min_vastus', kysimus.min_vastus)}
  </div>
  ${ch.flb(_("Maksimaalne kujundite arv"), 'lmax_vastus')}
  <div class="col-md-3 col-xl-1">
    <%
      max_vastus = kysimus.max_vastus
      if max_vastus is None and not kysimus.id:
         max_vastus = 1
    %>
    ${h.text5('l.max_vastus', max_vastus)}
  </div>

% elif item.tyyp == const.INTER_UNCOVER:
  ${ch.flb(_("Minimaalne valikute arv"), 'lmin_vastus')}
  <div class="col-md-3 col-xl-1">
    ${h.text5('l.min_vastus', kysimus.min_vastus)}
    ${h.hidden('l.max_vastus', '')}
  </div>
    
% elif item.tyyp not in (const.INTER_POS, const.INTER_POS2, const.INTER_COLORAREA):
        ## teistel tyypidel on ainult 1 kysimus, 
        ## aga piltide lohistamisel on iga pilt eraldi kysimus
        ## ja ploki kysimust pole
  ${ch.flb(_("Minimaalne valikute arv"), 'lmin_vastus')}
  <div class="col-md-3 col-xl-1">
    ${h.text5('l.min_vastus', kysimus.min_vastus)}
  </div>
  ${ch.flb(_("Maksimaalne valikute arv"), 'lmax_vastus')}
  <div class="col-md-3 col-xl-1">  
    <%
      max_vastus = kysimus.max_vastus
      if max_vastus is None and not kysimus.id:
         max_vastus = 1
    %>
    ${h.text5('l.max_vastus', max_vastus)}
  </div>
% endif
% endif
</div>
<div class="row pb-3">
  ${ch.flb(_("Soovituslik pealkiri"), 'motiitel')}
  <div class="col-md-9 col-xl-10">
    ${h.text('mo.tiitel', mo.tiitel)}
  </div>
</div>
</%def>

<%def name="edit_drag_images_pos(item, is_masonry=False)">
% if c.block.tyyp in (const.INTER_TXPOS, const.INTER_TXPOS2, const.INTER_TXGAP, const.INTER_TXASS):
${_("Lohistatavate tekstide asukoht:")}
% else:
${_("Lohistatavate piltide asukoht:")}
% endif
<% mo = item.taustobjekt %>
${h.radio('mo.asend', model.Sisuobjekt.ASEND_PAREMAL, checked=not mo.asend, label=_("paremal"))}
${h.radio('mo.asend', model.Sisuobjekt.ASEND_ALL, checkedif=mo.asend, label=_("all"))}
% if c.block.tyyp != const.INTER_TXASS:
${h.radio('mo.asend', model.Sisuobjekt.ASEND_VASAKUL, checkedif=mo.asend, label=_("vasakul"))}
${h.radio('mo.asend', model.Sisuobjekt.ASEND_YLEVAL, checkedif=mo.asend, label=_("üleval"))}
% endif
<br/>
% if c.block.tyyp in (const.INTER_TXPOS, const.INTER_TXPOS2, const.INTER_TXGAP, const.INTER_TXASS):
${_("Lohistatavate tekstide järjekord:")}
% else:
${_("Lohistatavate piltide järjekord:")}
% endif
${h.radio('mo.segamini', 1, checked=mo.segamini, label=_("juhuslik"))}
${h.radio('mo.segamini', '', checked=not mo.segamini, label=_("säilib"))}
% if is_masonry:
<br/>
${h.checkbox1('mo.masonry_layout', 1, checked=mo.masonry_layout, label=_("Müürpaigutus"))}              
% endif
</%def>

<%def name="btn_undo(sketchpad_id)">
% if not c.prepare_correct or c.block.naide:
${h.button(_("Tühista"), onclick=f"sketchpads.sketchpad_{sketchpad_id}.undo()",
class_="btny undosvg_%s" % sketchpad_id, level=2, style="display:none",
id='undosvg_%s' % sketchpad_id)}
${h.button(_("Tühista kõik"), onclick=f"sketchpads.sketchpad_{sketchpad_id}.clear()",
class_="btny undosvg_%s" % sketchpad_id, level=2, style="display:none",
id='undosvg_all_%s' % sketchpad_id)}
% endif
</%def>

<%def name="sketchpad(item)">
<% mo = item.taustobjekt %>
% if mo:
      <div id="sketchpad_${c.block_prefix}" class="sketchpad mb-1" style="position:relative;min-width:${mo.laius}px;min-height:${mo.korgus}px;">
      </div>
      ${h.origin(mo.tran(c.lang).tiitel)}
% endif
</%def>

<%def name="sketchpad_in_dragtbl(item, bkysimus)">
## tekstide lohistamine (pank on väljaspool sketchpadi)
<%
  mo = item.taustobjekt
  
%>
% if mo:
<div id="dragtbl_${c.block_prefix}" class="dragtbl" style="position:relative;">
  <table cellpadding="0" cellspacing="0">
        % if mo.asend == model.Sisuobjekt.ASEND_YLEVAL:
        <tr>
          <td style="padding-bottom:8px">
            ${self.add_drag_txelems(item, bkysimus, False)}
          </td>
        </tr>
        % endif
        <tr>
          % if mo.asend == model.Sisuobjekt.ASEND_VASAKUL:
          <td style="padding-right:8px">
            ${self.add_drag_txelems(item, bkysimus, True)}
          </td>
          % endif
          <td style="vertical-align:top">
            % if c.is_sp_print or c.is_sp_preview:
            ${self.print_hotspots(c.block, False)}
            % else:
            ${self.sketchpad(item)}
            % endif
          </td>
          % if mo.asend == model.Sisuobjekt.ASEND_PAREMAL:
          <td style="padding-left:8px" class="bank-td">
            % if c.block.tyyp == const.INTER_TXASS:
            ${self.add_ass_txelems(item, bkysimus, True)}
            % else:
            ${self.add_drag_txelems(item, bkysimus, True)}
            % endif
          </td>
          % endif
        </tr>
        % if mo.asend == model.Sisuobjekt.ASEND_ALL:
        <tr>
          <td style="padding-top:8px">
            % if c.block.tyyp == const.INTER_TXASS:
            ${self.add_ass_txelems(item, bkysimus, False)}
            % else:
            ${self.add_drag_txelems(item, bkysimus, False)}
            % endif
          </td>
        </tr>
        % endif
  </table>
</div>
% endif
</%def>

<%def name="add_drag_txelems(item, bkysimus, is_vertical)">
## lohistatavad tekstid
<%
  valikud = list(bkysimus.valikud)
  mo = item.taustobjekt
  if mo.segamini:
     model.random.shuffle(valikud)
%>
<div class="bank">
% for v in valikud:
<%
  value = v.tran(c.lang).nimi 
  cls = is_vertical and 'linebreak' or ''
%>
<div name="${v.kood}" id="dtx_${c.block.id}_${v.kood}" data-asobject_id="${v.kood}"
     class="dragtxpos dragtxpos-inbank dragtxpos-border ${cls}">
  ${value}
</div>
 % if v.max_vastus:
<%
  style = ''
  if not v.eraldi:
     cls += ' dragtxpos-copypos'
     style = 'position:absolute;left:-1000;'
  if style:
     style = 'style="%s"' % style
%>
% for seq in range(1, v.max_vastus):
<div name="${v.kood}" id="dtx_${c.block.id}_${v.kood}_${seq}" data-asobject_id="${v.kood}#${seq}"
     ${style} class="dragtxpos dragtxpos-inbank dragtxpos-border ${cls}">
  ${h.literal(c.block.replace_img_url(value or '', lang=c.lang))}
</div>
 % endfor
 % endif
% endfor
</div>
</%def>

<%def name="add_ass_txelems(item, bkysimus, is_vertical)">
## kujunditega seostatavad tekstid
<%
  valikud = list(bkysimus.valikud)
  mo = item.taustobjekt
  if mo.segamini:
     model.random.shuffle(valikud)
%>
<div class="bank">
% for v in valikud:
<%
  value = v.tran(c.lang).nimi 
  cls = is_vertical and 'linebreak' or ''
%>
<div name="${v.kood}" id="dtx_${c.block.id}_${v.kood}" data-asobject_id="${v.kood}"
     class="dragtxpos dragtxpos-inbank dragtxpos-border ${cls}"
     min_v="${v.min_vastus}" max_v="${v.max_vastus}">
  ${value}
</div>
% endfor
</div>
</%def>

<%def name="js_sketchpad(item, require_id=True, drag_images=False, result_id=None)">
<% mo = item.taustobjekt %>
% if mo:
     <%
       c.img_pos, louend_laius, louend_korgus, taust_x, taust_y = item.louend_pos(c.lang, drag_images)
       if not result_id:
          result_id = c.block_result
     %>
  var sketchpad = new Sketchpad('${c.block_prefix}', 
                  ${louend_laius or 100},
                  ${louend_korgus or 100},
                  "${mo.get_url(c.lang, c.url_no_sp)}",
                  ${taust_x},
                  ${taust_y},
                  ${mo.laius or 100}, 
                  ${mo.korgus or 100},
                  ${require_id and 'true' or 'false'},
                  $('#${result_id}'));
% endif
</%def>

<%def name="js_show_drag_images(item, read_only=False)">
################ Aluspildile lohistatavad detailid
% if item.taustobjekt:
  var sketchpad = sketchpads.sketchpad_${c.block_prefix};
  <% min_choice_info = [] %>
## kuvame pildid
% for subitem in item.piltobjektid:
  <%
     if subitem.min_vastus:
        min_choice_info.append('["%s", %d]' % (subitem.kood, subitem.min_vastus))
  %>
    % for seq in range(subitem.max_vastus or 1):
     <% 
        x, y = c.img_pos[subitem.id, seq] 
        img_t = subitem.tran(c.lang)
        if not (img_t and img_t.has_file):
           img_t = subitem
     %>
  sketchpad.add_drag_image("${subitem.get_url(c.lang, c.url_no_sp)}", ${x}, ${y}, ${img_t.laius or 30}, ${img_t.korgus or 30}, '${subitem.kood}', ${seq}, ${read_only and 'true' or 'false'}, ${c.show_r_code and 'true' or 'false'});
    % endfor
% endfor
% if min_choice_info:
  sketchpad.min_choice_info = [${','.join(min_choice_info)}];
  sketchpad.set_finished();             
% endif
% endif
</%def>

<%def name="js_show_hotspots(sisuplokk, nahtamatu=None, kysimus=None)">
     var sketchpad = sketchpads.sketchpad_${c.block_prefix};
<%
  if kysimus is None:
      kysimus = sisuplokk.get_kysimus(seq=1)
  valikupiirkonnad = list(kysimus.valikud)

  ## ES-1750 - pildil järjestamises hindajale piirkonna koodi mitte näidata
  show_r_code = c.show_r_code and not (c.hindamine and c.block.tyyp == const.INTER_GR_ORDER)
%>
% for item in valikupiirkonnad:
  sketchpad.drawShapeId(eval('${item.koordinaadid}'),
                        '${item.kujund}',
                        '${item.kood}',
                        ${show_r_code and 'true' or 'false'},
   % if sisuplokk.tyyp in (const.INTER_HOTSPOT, const.INTER_GR_ASSOCIATE):
## nähtamatu, kontuurita
                        false, ${nahtamatu!=False and item.nahtamatu and 'true' or 'false'},
   % else:
                        ${nahtamatu!=False and item.nahtamatu and 'true' or 'false'}, false,
   % endif
                        ${item.max_vastus or 'null'}, null, null, true);
% endfor
</%def>

<%def name="js_show_hindamismaatriks_pt(tulemus)">
  var sketchpad = sketchpads.sketchpad_${c.block_prefix};
% if tulemus:
% for item in tulemus.hindamismaatriksid:
  % if item.sallivus:
  sketchpads.sketchpad_${c.block_prefix}.settings_normal['stroke-width'] = ${item.sallivus};
  sketchpads.sketchpad_${c.block_prefix}.settings_normal['stroke-opacity'] = 0.5;         
  % endif
  var node = sketchpad.drawShapeId(eval('${item.koordinaadid}'), '${item.kujund}', '${item.id}');
% endfor
% endif
</%def>

<%def name="js_selectable(item, kysimus)">
## aluspildile joonistatud kujundid muudetakse valitavateks
  sketchpads.sketchpad_${c.block_prefix}.make_selectable(${kysimus.min_vastus or 0},${kysimus.max_vastus or 0});
</%def>

<%def name="js_trailable(item, kysimus)">
  <% kyslisa = kysimus.kyslisa %>
  sketchpads.sketchpad_${c.block_prefix}.make_trailable(0, 0, "${kyslisa.algus or ''}", "${kyslisa.labimatu or ''}", "${kyslisa.lopp or ''}");
</%def>

<%def name="js_orderable(item, kysimus)">
## aluspildile joonistatud kujundid muudetakse järjestatavateks
  sketchpads.sketchpad_${c.block_prefix}.make_orderable(${kysimus.min_vastus or 0}, ${kysimus.max_vastus or 0});
  $('.undosvg_${c.block_prefix}').hide();
</%def>

<%def name="js_assorderable(item, kysimus, readonly)">
## aluspildile joonistatud kujundid muudetakse järjestatavateks
<%
try:
    # MemSisuplokk
    entries = kysimus.list_correct_entries
except AttributeError:
    # Kysimus
    entries = kysimus.correct_entries()
allowed = ["'%s'" % (entry.kood1) for entry in entries]
%>
  sketchpads.sketchpad_${c.block_prefix}.make_assorderable([${','.join(allowed)}], ${readonly and 'true' or 'false'});
  $('.undosvg_${c.block_prefix}').hide();
</%def>

<%def name="js_associable(item, kysimus)">
## aluspildile joonistatud kujundid muudetakse seostatavateks
  sketchpads.sketchpad_${c.block_prefix}.make_associable(${kysimus.min_vastus or 0}, ${kysimus.max_vastus or 0});
  $('.undosvg_${c.block_prefix}').hide();
</%def>

<%def name="js_pointable(item, kysimus)">
## aluspildil lubatakse kohti märkida
  sketchpads.sketchpad_${c.block_prefix}.make_pointable(${kysimus.min_vastus or 0}, ${kysimus.max_vastus or 0});
</%def>

<%def name="js_droppable_hotspots(item, kysimus)">
## muudetakse kujundid sellisteks, kuhu saab pilte lohistada
  sketchpads.sketchpad_${c.block_prefix}.make_droppable(${kysimus and kysimus.min_vastus or 0}, ${kysimus and kysimus.max_vastus or 0});
</%def>

<%def name="js_droppable_paper(item)">
## muudetakse aluspilt selliseks, kuhu saab pilte lohistada
  sketchpads.sketchpad_${c.block_prefix}.make_droppable_paper(0,0);
</%def>

<%def name="js_colorable_hotspots(item, kysimus, read_only=False)">
## muudetakse kujundid sellisteks, mida saab klikiga värvida
  sketchpads.sketchpad_${c.block_prefix}.make_colorable(${kysimus.min_vastus or 0}, ${kysimus.max_vastus or 0}, ${read_only and 'true' or 'false'});
</%def>

<%def name="print_img(obj)">
  % if obj:
    <% 
       laius = obj.laius
       korgus = obj.korgus
       if c.lang:
          laius = obj.tran(c.lang).laius or laius
          korgus = obj.tran(c.lang).korgus or korgus
    %>
     <img src="${obj.get_url(c.lang, c.url_no_sp)}" ${h.width(laius)} ${h.height(korgus)} style="${h.width(obj, True)}${h.height(obj, True)}"/>
  % endif
</%def>  

<%def name="print_hotspots(block, with_hotspots=True)">
  % if block.taustobjekt:
    ## avame pildi
    ## lisame hotspotid
    ## salvestame failiks
    ## anname faili tagasi?
    ##${self.print_img(block.taustobjekt)}
     <% obj = block.taustobjekt %>
     <img src="${obj.get_url(c.lang, c.url_no_sp, with_hotspots=with_hotspots)}" ${h.width(obj)} ${h.height(obj)} style="${h.width(obj, True)}${h.height(obj, True)}"/>
  % endif
</%def>  

<%def name="print_drag_images(block)">
  % for subitem in block.piltobjektid:
    <% cnt = not subitem.eraldi and 1 or subitem.max_vastus or 1 %>
    % for n in range(cnt):
      ${self.print_img(subitem)}<br/>
      % endfor
  % endfor
</%def>  
