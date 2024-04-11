## -*- coding: utf-8 -*- 
## Ristsõna
<%inherit file="baasplokk.mako"/>
<!-- ${self.name} -->
<%namespace name="choiceutils" file="choiceutils.mako"/>

## todo: õiged vastused, pildid vihjena, tõlgitavus, esimeste ridade-veergude lisamine ja eemaldamine, stiiliklassid,
## ridade-veergude vähendamisel rea-veeru tühjuse kontroll

<%def name="block_edit()">
<%
  data, cols, rows = c.item.get_crossword_map(c.lang)
  correct_responses, e_locals = c.block.correct_responses(c.ylesandevastus, lang=c.lang)
  ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') 
%>
<div class="row">
  <% name = 'f_korgus' %>
  ${ch.flb(_("Ridade arv"), name)}
  <div class="col-md-3 col-xl-2">
    ${h.posint5('f_korgus', rows, ronly=not c.is_edit and not c.is_tr)}
  </div>
  <% name = 'f_laius' %>
  ${ch.flb(_("Veergude arv"), name)}
  <div class="col-md-3 col-xl-2">
    ${h.posint5('f_laius', cols, ronly=not c.is_edit and not c.is_tr)}
  </div>

  <% name = 'f_suurus' %>
  ${ch.flb(_("Ruudu suurus"), name)}
  <div class="col-md-3 col-xl-2">
      % if not c.is_edit or c.is_tr:
      ${h.readonly_text(str(c.block.suurus or 50))}
      % else:
      ${h.posint5('f_suurus', c.block.suurus, minvalue=15, maxvalue=250, placeholder=50)}
      % endif
  </div>    
</div>

<script>
  $(function(){
  $('input#f_suurus').change(function(){
     var size = parseInt($('input#f_suurus').val()) || 50;
     $('table.cw-table tr').height(size+'px');
     $('table.cw-table td').height(size+'px').width(size+'px');  
  });
  });
</script>

% if c.item.id and cols and rows:
<p>
${_("Sõna lisamiseks kliki vabal ruudul, olemasoleva sõna muutmiseks kliki sõna vihjel")}
</p>
<%
  size = c.block.suurus
  if size:
     td_style = f'style="width:{size}px;height:{size}px;"'
     tr_style = f'style="height:{size}px;"'
  else:
     td_style = tr_style = ''
%>
<table cellspacing="0" class="cw-table">
  <tbody>
% for n_row in range(rows):
<tr ${tr_style}>
  % for n_col in range(cols):
  <% cell = data[n_row][n_col] %>
  % if cell.words:
   <%
   value = ''
   if cell.fixed_char is not None:
      # fikseeritud täht
      value = cell.fixed_char
      is_fixed_char = True
   else:
      is_fixed_char = False  
      for k_kood, nchar in cell.words:
         kv = correct_responses.get(k_kood)
         if kv:
            for kvs in kv.kvsisud:
               sisu = kvs.sisu
               if sisu and len(sisu) > nchar:
                   ch = sisu[nchar]
                   if ch not in value:
                      value += ch
   %>
  <td data-pos_x="${n_col}" data-pos_y="${n_row}" class="cw-gap" ${td_style}>
  ## tähe koht
  % if is_fixed_char:
  <b>${value}</b>
  % else:
  ${value}
  % endif
  </td>
  % elif cell.title_k:
  <td data-pos_x="${n_col}" data-pos_y="${n_row}" data-kood="${cell.title_k.kood}" class="cw-title" ${td_style}>
    <%
      mo = cell.title_k.sisuobjekt
      t_mo = mo and mo.tran(c.lang)
    %>
    % if mo:
    <img src="${mo.get_url(c.lang, c.url_no_sp)}" title="${cell.title_k.vihje}" ${h.width(t_mo)} ${h.height(t_mo)}/>
    % else:
    ${cell.title_k.tran(c.lang).vihje}
    % endif
  </td>
  % else:
  <td data-pos_x="${n_col}" data-pos_y="${n_row}" class="cw-edit-empty" ${td_style}>
  </td>
  % endif
  % endfor
</tr>
% endfor
  </tbody>
</table>
<br/>
% if c.is_tr:
## dialoog põhikeelse kysimuse koodi valimiseks 
<% opt_kysimus = [k.kood for k in c.block.kysimused if not k.pseudo and k.pos_x is not None] %>
<div style="display:none">
  <div id="choose_k">
    ${h.select('kood', '', opt_kysimus, empty=True, class_="choose_kood", ronly=False)}
  </div>
</div>
% endif
<script>
% if c.is_edit:
  $('td.cw-edit-empty').click(function(){
    var url = get_dialog_url(null, '', 'crossword', $(this).data('pos_x'), $(this).data('pos_y'));
    open_dialog({'title': "${_("Sõna")}", 'url': url, size: 'lg'});
  });
% elif c.is_tr:
  $('td.cw-edit-empty').click(function(){
     ## esmalt avaneb dialoog kysimuse koodi valimiseks, seejärel kysimuse dialoog
     var x = $(this).data('pos_x'), y = $(this).data('pos_y');
     var el = $('#choose_k').clone().attr('id','choose_k2');
     el.find('select.choose_kood').change(function(){
       ## valitud kysimuse dialoogi avamise URL
       var url = get_dialog_url($(this).val(), '', 'crossword', x, y);
       open_dialog({'title': "${_("Sõna")}", 'url': url, size: 'lg'});
     });
     open_dialog({contents_elem: el, title: "${_("Küsimuse ID")}", size:'lg'});
  });
% endif
% if c.is_edit or c.is_tr:
  $('td.cw-gap').click(function(){
    var url = get_dialog_url('', 'CHAR:'+$(this).text().trim(), 'crossword', $(this).data('pos_x'), $(this).data('pos_y'));
    open_dialog({'title': "${_("Etteantud täht")}", 'url': url, 'size': 'lg'});
  });
% endif
$('td.cw-title').click(function(){
    var url = get_dialog_url($(this).data('kood'), '', 'crossword', $(this).data('pos_x'), $(this).data('pos_y'));
    open_dialog({'title': "${_("Sõna")}", 'url': url, 'size': 'lg'});
  });  
</script>

% if c.is_edit or c.is_tr:
${_("Nihuta ristsõna ruudustiku suhtes {n} ruudu võrra").format(n=h.posint5('move_cnt', 0, ronly=False))}
${h.radio('move_dir', const.DIRECTION_LEFT, checkedif=c.move_dir or 'left', label=_("vasakule"), ronly=False)}
${h.radio('move_dir', const.DIRECTION_RIGHT, checkedif=c.move_dir, label=_("paremale"), ronly=False)}
${h.radio('move_dir', const.DIRECTION_UP, checkedif=c.move_dir, label=_("üles"), ronly=False)}
${h.radio('move_dir', const.DIRECTION_DOWN, checkedif=c.move_dir, label=_("alla"), ronly=False)}
% endif

% else:
<p>${h.alert_notice(_("Sisesta ridade ja veergude arv ning salvesta"))}</p>
% endif
</%def>

<%def name="block_preview()">
${self.block_view()}
</%def>

<%def name="block_print()">
${self.block_view()}
</%def>

<%def name="block_view()">
<%
  lang = c.lang != c.ylesanne.lang and c.lang or None
  data, cols, rows = c.block.get_crossword_map(lang)
  if c.block_correct or c.block.naide:
     responses = c.correct_responses
  else:
     responses = c.responses

  size = c.block.suurus
  if size:
     td_style = f'style="width:{size}px;height:{size}px;"'
     tr_style = f'style="height:{size}px;"'
  else:
     td_style = tr_style = ''
%>
% if cols and rows:
<table cellspacing="0" id="block_${c.block_prefix}" class="asblock cw-table">
<tbody>
  % for n_row in range(rows):
<tr ${tr_style}>
  % for n_col in range(cols):
  <% cell = data[n_row][n_col] %>
  % if cell.words:
  ## tähe sisestamise lahter
  <td class="cw-gap cw-gap-${n_row}-${n_col}" ${td_style}>
    <%
      value = ''
      fixed_char = cell.fixed_char
      if not fixed_char:
         for k_kood, nchar in cell.words:
            kv = responses.get(k_kood)
            if kv:
               for kvs in kv.kvsisud:
                  sisu = kvs.sisu
                  if sisu and len(sisu) > nchar:
                      value = sisu[nchar]
                      break
            if value:
               break
         if value == '_':
            value = ''
      koodid = ' '.join(['%s#%s' % (k_kood, nchar) for (k_kood, nchar) in cell.words])
    %>
    % if fixed_char:
    <b>${fixed_char}</b>
    % elif not c.is_sp_preview:
       % if c.is_edit:
       ${h.text('xch', value, class_="cw-char", maxlength=1, next=cell.next)}
       % else:
       ${value}
       % endif
    % endif
    <span class="cw-wordlist" style="display:none">${koodid}</span>
  </td>
  % elif cell.title_k:
  ## vihje lahter
  <td class="cw-title" ${td_style}>
    <%
      title_k = cell.title_k
      mo = title_k.sisuobjekt
    %>
    % if mo:
    <img src="${mo.get_url(c.lang, c.url_no_sp)}" title="${title_k.vihje}" ${h.width(mo)} ${h.height(mo)}/>
    % else:
    ${title_k.tran(c.lang).vihje}
    % endif
    <%
      value = title_k.init_value
      kv = responses.get(title_k.kood)
      if kv and len(kv.kvsisud):
         v_value = kv.kvsisud[0].sisu
         if v_value:
             value = v_value
    %>
    ${h.hidden(title_k.result, value)}
  </td>
  % else:
  ## kasutamata lahter
  <td ${td_style}></td>
  % endif
  % endfor
</tr>
% endfor
</tbody>
</table>
<% 
if c.resize_prefixes == '':
   c.resize_prefixes = []
c.resize_prefixes.append((c.y_prefix, c.block_prefix))
%>
% endif
</%def>

<%def name="block_view_js()">
$(function(){
var block = $('table.asblock#block_${c.block_prefix}');
cw_setup(block);
is_response_dirty = false;
${self.block_view_js_correct()}
});
function resize_${c.block_prefix}()
{
$('.corr-cw-${c.block_prefix}').each(function(n, div){
var block = $('table.asblock#block_${c.block_prefix}');
  var td_start = block.find('td.' + $(div).attr('td_start'));
  var td_end = block.find('td.' + $(div).attr('td_end'));
  if(td_start.length && td_end.length){
    $(div).position({my: 'left+4 top+4', at: 'left top', of: td_start})
          .width(td_end.position().left + td_end.width() - td_start.position().left - 8)
          .height(td_end.position().top + td_end.height() - td_start.position().top - 8);
  }
});
}
</%def>

<%def name="block_view_js_correct()">
% if c.prepare_correct:
var block = $('table.asblock#block_${c.block_prefix}');
% for kysimus in c.block.kysimused:
<%
  t_kysimus = kysimus.tran(c.lang)
  tulemus = kysimus.tulemus
%>
% if tulemus:
<% kv = c.responses.get(tulemus.kood) %>
% if kv:
% for ks in kv.kvsisud:
% if ks.on_hinnatud and not c.block.varvimata:
<% corr_cls = model.ks_correct_cls(c.responses, tulemus, kv, ks, True) %>
% if corr_cls:
<%
  start_x = end_x = t_kysimus.pos_x
  start_y = end_y = t_kysimus.pos_y
  size = len(ks.sisu)
  if t_kysimus.joondus == const.DIRECTION_DOWN:
     start_y += 1
     end_y = start_y + size - 1
  elif t_kysimus.joondus == const.DIRECTION_UP:
     end_y -= 1
     start_y = end_y - size + 1
  elif t_kysimus.joondus == const.DIRECTION_RIGHT:
     start_x += 1
     end_x = start_x + size - 1
  elif t_kysimus.joondus == const.DIRECTION_LEFT:
     end_x -= 1
     start_x = end_x - size + 1
%>
var td_start = block.find('td.cw-gap-${start_y}-${start_x}');
$('<div class="${corr_cls} corr-cw-${c.block_prefix}" td_start="cw-gap-${start_y}-${start_x}" td_end="cw-gap-${end_y}-${end_x}"></div>')
.css('position','absolute').appendTo(td_start);
% endif
% endif
% endfor
% endif
% endif
% endfor
resize_${c.block_prefix}();
% endif
</%def>
