## Järjestamine
<%inherit file="baasplokk.mako"/>
<%namespace name="choiceutils" file="choiceutils.mako"/>
<!-- ${self.name} -->
<%def name="block_edit()">
<% kysimus = c.block.kysimus %>
<div class="row mb-1">
  <% name = 'l.ridu' %>
  ${h.flb(_("Valikute kuvamine"), name, 'col-md-3 col-xl-2 text-md-right')}
  <div class="col-md-4 col-xl-5">
      ${h.radio('l.ridu', 1, checked=kysimus.ridu==1, label=_("kõrvuti"))}
      ${h.radio('l.ridu', 2, checked=not(kysimus.ridu==1),
      label=_("üksteise all"))}
  </div>
</div>

${choiceutils.choices(kysimus, kysimus.valikud, 'v', fikseeritud=True)}
${choiceutils.hindamismaatriks(kysimus,
                               kood1=kysimus.valikud_opt, 
                               kood1_cls='vkood',
                               ordered=True)}
</%def>

<%def name="block_preview()">
<%
  kysimus = c.block.kysimus
  if kysimus.ridu == 1:
       # horisontaalne paigutus
       sortables_cls = 'sortables d-flex flex-row'
  else:
       # vertikaalne paigutus
       sortables_cls = 'sortables d-inline-block'
%>
<div class="${sortables_cls}">
% for subitem in kysimus.valikud:
    <div class="sortable border-sortable">
      ${h.literal(c.block.replace_img_url(subitem.tran(c.lang).nimi or '', lang=c.lang))}
    </div>
% endfor
</div>
</%def>

<%def name="block_print()">
  % for n, subitem in enumerate(c.block.kysimus.valikud):
    <p>
    ${h.print_input(3)}
      ${h.literal(c.block.replace_img_url(subitem.tran(c.lang).nimi or '', lang=c.lang))}
    </p>
  % endfor
</%def>

<%def name="block_view()">
  <%
    valikud = []
    jarjestus = []
    kysimus = c.block.kysimus
    if c.block_correct or c.block_naide:
       ## kuvame õiget vastust
       responses = c.correct_responses
    else:
       ## kuvame antud vastust
       responses = c.responses
    kv = responses.get(kysimus.kood)
    if kv and len(kv.kvsisud):
       ks = kv.kvsisud[0]
       jarjestus = ks.jarjestus
    else:
       ks = None

    corr_cls = ''
    el_corr_cls = []
    if ks and c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
      tulemus = kysimus.tulemus
      if tulemus.kardinaalsus != const.CARDINALITY_ORDERED and ks.hindamisinfo:
          # raam ymber jada iga elemendi
          for ch in ks.hindamisinfo:
              el_corr_cls.append(ch == '1' and 'corr1r' or ch == '0' and 'corr0r' or '')
      else:
          # kogu järjekord peab olema õigesti, raam ymber kogu jada
          corr_cls = model.ks_correct_cls(responses, kysimus.tulemus, kv, ks, False) or ''
    
    if jarjestus:
      # lisame need, mida maatriksis polnud
      for v in kysimus.valikud:
         if v.kood not in jarjestus:
            jarjestus.append(v.kood)
      valikud = [kysimus.get_valik(kood) for kood in jarjestus]
    if not valikud:
        valikud = list(kysimus.valikud)
        if kysimus.segamini and c.ylesandevastus:
            kv = c.responses.get(kysimus.kood)
            model.apply_shuffle(valikud, kv and kv.valikujrk)

    str_valikud = ';'.join(['i_%s' % v.id for v in valikud if v])

    if kysimus.ridu == 1:
       # horisontaalne paigutus
       block_cls = ''
       dir_cls = 'd-flex flex-row'
    else:
       # vertikaalne paigutus
       block_cls = 'd-inline-block'
       dir_cls = ''

    opened = closed = False
  %>
  ${h.qcode(kysimus, nl=True)}
  <div class="d-inline-block">
<div class="asblock ${corr_cls} ${dir_cls}" id="block_${c.block_prefix}">
  % for ind, subitem in enumerate(valikud):
  <% v_fixed = bool(subitem.fikseeritud) %>
  % if not v_fixed and not opened:
   <div class="sortables ${dir_cls}">
    <% opened = True %>
  % elif v_fixed and opened:
   </div>
    <% closed = True %>
  % endif 

    <div id="i_${subitem.id}" kood="${subitem.kood}" class="${v_fixed and 'unsortable' or 'sortable'}">
      <div class="${v_fixed and "border-unsortable" or "border-sortable"} ${len(el_corr_cls)>ind and el_corr_cls[ind] or ''}">
        ${h.ccode(subitem.kood)}
        ${h.literal(c.block.replace_img_url(subitem.tran(c.lang).nimi or '', lang=c.lang))}
      </div>
    </div>
 % endfor
 % if opened and not closed:
  </div>
  % endif
  </div>
</div>
${h.hidden(kysimus.result, str_valikud)}
</%def>

<%def name="block_view_js()">
<% kysimus = c.block.kysimus %>
% if not c.block.read_only and not kysimus.muutmatu:
## saab vastata
$(function(){
  var sortables = $("#block_${c.block_prefix}>.sortables");
  function serialize_b${c.block.id}(){
    var items = $("#block_${c.block_prefix}>.sortables>.sortable,#block_${c.block_prefix}>.unsortable");
    for(var s='', i=0; i<items.length; i++) { s += ';' + items[i].id; }
    if(s != '') s = s.substring(1);
    $('input[name="${kysimus.result}"]').val(s);
  }
  new Sortable(sortables[0], {
    animation: 150,
    ghostClass: 'sortable-ghost',
    chosenClass: 'sortable-chosen',
    filter: '.unsortable',
    onUpdate: function(evt){
         var resf = $('input[name="${kysimus.result}"]');
         serialize_b${c.block.id}();
         if(window.response_changed) response_changed(resf);
         set_sp_finished(resf, true);
    }    
  });
  serialize_b${c.block.id}();
  $("#block_${c.block_prefix}").disableSelection();
});
% endif
</%def>

<%def name="block_entry()">
  <%
    kysimus = c.block.kysimus
    kv = c.responses.get(kysimus.kood)
    kv2 = c.prefix2 and c.responses2.get(kysimus.kood)
  %>

% if c.is_correct:
   ## sisestatakse, kas vastus on õige või vale
   ${self.block_entry_correct(kysimus, kv, kv2)}
% else:
  <%
    if kv and len(kv.kvsisud):
       responses = kv.kvsisud[0].jarjestus
    else:
       responses = []
    if kv2 and len(kv2.kvsisud):
       responses2 = kv2.kvsisud[0].jarjestus
    else:
       responses2 = []
    cnt = len(kysimus.valikud)
    script_printed = False
  %>
  % for i in range(cnt):
    <% 
       value = len(responses) > i and responses[i] or None 
       value2 = responses2 and len(responses2) > i and responses2[i] or None 
       err = value and value2 and value != value2 and 'form-control is-invalid' or ''
    %>
<div class="td-sis-value">
  ${self.block_entry_kood(kysimus, i+1, cnt)}
    <table cellpadding="0" cellspacing="0" class="showerr ${err}">
      <tr>
        <td>
          ${h.select_entry('%s.%s-%d' % (c.prefix, kysimus.kood,i), value,
          kysimus.valikud_opt, wide=False, empty=True, class_='jumper jumper-entry')}
        </td>
      </tr>
      % if c.prefix2:
      <tr>
        <td>
          ${h.select_entry('%s.%s-%d' % (c.prefix2, kysimus.kood,i), value2,
          kysimus.valikud_opt, wide=False, empty=True, class_='jumper jumper-entry')}
        </td>
      </tr>
      % endif
    </table>

   % if not script_printed:
     <% script_printed = True %>
   <script>
   $(function(){
      order_select_setup($('select[name^="${'%s.%s-' % (c.prefix, kysimus.kood)}"]'));
      order_select_setup($('select[name^="${'%s.%s-' % (c.prefix2, kysimus.kood)}"]'));
   });
    </script>
   % endif
</div>
  % endfor
% endif
</%def>
