## -*- coding: utf-8 -*- 
## Valikvastusega küsimus
<%inherit file="baasplokk.mako"/>
<%namespace name="choiceutils" file="choiceutils.mako"/>
<!-- ${self.name} -->

<%def name="block_edit()">
<% kysimus = c.block.kysimus %>
<% ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') %>
<div class="row mb-1">
  <% name = 'l.min_vastus' %>
  ${ch.flb(_("Minimaalne valikute arv"), name)}
  <div class="col-md-3 col-xl-3">
      <%
        min_vastus = c.block.kysimus.min_vastus
        if min_vastus is None and not kysimus.id:
           min_vastus = 1
      %>
      ${h.posint5('l.min_vastus', min_vastus)}
  </div>
  <% name = 'l.max_vastus' %>
  ${ch.flb(_("Maksimaalne valikute arv"), name)}
  <div class="col-md-3 col-xl-3">
    ${h.posint5('l.max_vastus', kysimus.max_vastus)}
    % if kysimus.max_vastus_arv is not None:
    (${kysimus.max_vastus_arv})
    % endif
  </div>
</div>
<div class="row mb-1">
  <% name = 'l.vastusesisestus' %>
  ${ch.flb(_("Vastuste sisestamine (p-testis)"), name)}
  <div class="col-md-3 col-xl-3">
      <%
         opt_vastusesisestus = [('0', _("Valikväljalt")),
                                ('1', _("Märkeruutudelt"))]
      %>
      ${h.select('l.vastusesisestus', kysimus.vastusesisestus, opt_vastusesisestus)}
  </div>
</div>

<%
   choiceutils.choices(kysimus, kysimus.valikud, 'v')
   choiceutils.hindamismaatriks(kysimus,
                                kood1=kysimus.valikud_opt, 
                                kood1_cls='vkood')
%>
</%def>

<%def name="block_print()">
<table width="100%">
  <% 
    kysimus = c.block.kysimus
    ftype = kysimus.max_vastus == 1 and 'radio' or 'checkbox'
    if c.block.naide or c.block_correct:
        corrects = [entry.kood1 for entry in kysimus.best_entries()]
  %>
  % for n, subitem in enumerate(kysimus.valikud):
  <tr>
    <td width="20px" valign="top">
      % if (c.block.naide or c.block_correct) and subitem.kood in corrects:
      <input type="${ftype}" checked="checked"/>
      % else:
      <input type="${ftype}"/>
      % endif
    </td>
    <td>
      ${h.literal(c.block.replace_img_url(subitem.tran(c.lang).nimi or '', lang=c.lang))}
    </td>
  </tr>
  % endfor
</table>
</%def>

<%def name="block_view()">
<%
  kysimus = c.block.kysimus
  choices = list(kysimus.valikud)
  if kysimus.segamini and c.ylesandevastus:
      kv = c.responses.get(kysimus.kood)
      model.apply_shuffle(choices, kv and kv.valikujrk)
  name = kysimus.result
%>
${h.qcode(kysimus, nl=True)}
<div id="block_${c.block_prefix}" class="asblock">
  % for n, subitem in enumerate(choices):
  <%
    cb_id = f'{name}_{n}_'
    if kysimus.max_vastus == 1:
       cb_cls = 'radio'
    else:
       cb_cls = 'checkbox'
    %>
  <div>
  <div class="custom-control custom-${cb_cls} custom-control-inline correctness m-1">
    <input type="${cb_cls}" class="custom-control-input"
           data_kood="${kysimus.kood}" value="${subitem.kood}"
           name="${name}" id="${cb_id}"/>
    <label class="custom-control-label speech pr-3" lang="${c.lang}" for="${cb_id}">
        ${h.ccode(subitem.kood)}
        ${h.literal(c.block.replace_img_url(subitem.tran(c.lang).nimi or '', lang=c.lang))}
    </label>
  </div>
  </div>
  % endfor
</div>
</%def>

<%def name="block_view_js()">
<% kysimus = c.block.kysimus %>
function clear_${c.block_prefix}()
{
  $('div#block_${c.block_prefix} input[name="${kysimus.result}"]').prop('checked',false);
}

$(function(){
   var block = $('div#block_${c.block_prefix}');
   var fields = block.find('input[name="${kysimus.result}"]');
% if c.block.read_only:
## vastust muuta ei saa
   fields.prop('disabled','disabled');
% else:
## saab vastata

% if kysimus.max_vastus and kysimus.max_vastus > 1:
   fields.click(function(){
            var max = ${kysimus.max_vastus};
            if(this.checked)
             {
               if(block.find('input[name="' + this.name + '"]:checked').length >  max)
               {
                  this.checked = false;
                  alert_dialog(eis_textjs.choice_cnt, eis_textjs.choice_max.format(${kysimus.max_vastus}));
               }
             }
        });
  % endif
% endif

% if c.block_correct or c.block.naide:
${self.js_show_response(c.correct_responses)}
% else:
${self.js_show_response(c.responses)}
${self.js_show_response(c.correct_responses, False)}                                                                  
% endif

  toggle_sp_${c.block.id}();
% if not c.block.read_only:
  var fields = block.find('input[name="${kysimus.result}"]');
  fields.change(function(){
     toggle_sp_${c.block.id}();
     set_finished_${c.block.id}();
     response_changed($('input[name="' + this.name + '"]'));
  });
  k_check_finished["${kysimus.kood}"] = set_finished_${c.block.id};
  set_finished_${c.block.id}();
% endif
  is_response_dirty = false;
});
% if not c.block.read_only:
function set_finished_${c.block.id}()
{
   var block = $('div#block_${c.block_prefix}');
   var fields = block.find('input[name="${kysimus.result}"]');

## kontrollime tingimusi, mis valikust sõltuvalt muudavad teiste kysimuste kohustuslikkust
% if c.block.ylesanne.lahendada_lopuni:
  % for valik in kysimus.valikud:
  % for k_kood in (valik.kohustuslik_kys or '').split(','):
  % if k_kood:
## märgime, et kysimus k_kood on valiku valik.kood poolt kohustuslik või mitte
     set_mandatory('${k_kood}', '${kysimus.kood}.${valik.kood}', fields.filter('[value="${valik.kood}"]').is(':checked'));
  % endif
  % endfor
  % endfor
% endif

## kontrollime selle (valiku) kysimuse kohustuslikkust
  var responsecount = fields.filter(':checked').length;
  var is_finished = responsecount >= ${kysimus.min_vastus or 0};
% if not kysimus.min_vastus:
  if(responsecount == 0)
  {
    // kui muidu võib lõpetada, siis kontrollime veel yle, kas on tingimusi, mis seda takistavad
    $.each(mandatory, function(n, row){
        var k_kood = row[0];
        var is_mandatory = row[2];
        if((k_kood=='${kysimus.kood}') && is_mandatory)
        {
          var m_fields = filter_by_kood(fields, k_kood);
          var m_finished = m_fields.filter(':checked');
          if(m_finished.length == 0)
          {
            is_finished = false;
          }
        }
    });
  }
% endif
  set_sp_finished(fields, is_finished);
}
% endif

function toggle_sp_${c.block.id}()
{
  var block = $('div#block_${c.block_prefix}');
  var fields = block.find('input[name="${kysimus.result}"]');
## kuvame ja peidame teisi sisuplokke vastavalt valikule
  % for valik in kysimus.valikud:
  % if valik.sp_peida or valik.sp_kuva:
     <%
         sp_hide = ','.join([('.sisuplokk.eis-' + x) for x in (valik.sp_peida or '').split(',') if x] or [''])
         sp_show = ','.join([('.sisuplokk.eis-' + x) for x in (valik.sp_kuva or '').split(',') if x] or [''])
     %>
     if(block.find('input[name="${kysimus.result}"][value="${valik.kood}"]').is(':checked'))
     {
        toggle_sp('${sp_hide}', '${sp_show}');
     }
  % endif
  % endfor
}
</%def>

<%def name="block_entry_identifier(kysimus, kv, kv2)">
% if kysimus.vastusesisestus:
  ## sisestatakse sarnaselt lahendamisega
  ${self.block_entry_identifier_view(kysimus, kv, kv2)}
% else:
  <% 
    cnt = kysimus.max_vastus or len(kysimus.valikud) 
    kvsisud = kv and list(kv.kvsisud) or []
    kvsisud2 = kv2 and list(kv2.kvsisud) or []
  %>
  % for i in range(cnt):
         <% 
            if len(kvsisud) > i:
               kood1 = kvsisud[i].kood1
            else:
               kood1 = ''

            if len(kvsisud2) > i:
               kood1_2 = kvsisud2[i].kood1
            else:
               kood1_2 = ''

            err = kv2 and kood1 != kood1_2 and 'form-control is-invalid' or ''
         %>
<div class="td-sis-value">
   ${self.block_entry_kood(kysimus, i+1, cnt)}
      <table cellpadding="0" cellspacing="0" class="showerr ${err}">
        <tr>
          <td>
            ${h.select_entry('%s.%s-%d.kood1' % (c.prefix, kysimus.kood, i), kood1,
            kysimus.valikud_opt, wide=False, empty=True, class_='jumper jumper-entry')}
          </td>
        </tr>
        % if c.prefix2:
        <tr>
          <td>
            ${h.select_entry('%s.%s-%d.kood1' % (c.prefix2, kysimus.kood, i),
            kood1_2, kysimus.valikud_opt, wide=False, empty=True, class_='jumper jumper-entry')}
          </td>
        </tr>
        % endif
      </table>
</div>
  % endfor      
% endif
</%def>

<%def name="block_entry_identifier_view(kysimus, kv, kv2)">
  <% 
    cnt = len(kysimus.valikud) 
    kvsisud = kv and list(kv.kvsisud) or []
    kvsisud2 = kv2 and list(kv2.kvsisud) or []
    koodid1 = kvsisud and [kvs.kood1 for kvs in kvsisud] or []
    koodid2 = kvsisud2 and [kvs.kood1 for kvs in kvsisud2] or []
  %>
  % for i, subitem in enumerate(kysimus.valikud):
         <% 
            checked1 = subitem.kood in koodid1
            checked2 = subitem.kood in koodid2
            err = kv2 and checked1 != checked2 and 'form-control is-invalid' or ''
            
         %>
<div class="td-sis-value">
   ${self.block_entry_kood(kysimus, i+1, 1)}
      <table cellpadding="0" cellspacing="0" class="showerr ${err}">
        <tr>
          <td>
            ${h.checkbox('%s.%s-%d.kood1' % (c.prefix, kysimus.kood, i), 
            subitem.kood, checked=checked1, class_='jumper')}
            ${subitem.kood}
            ##${subitem.get_sisestusnimi()}
          </td>
        </tr>
        % if c.prefix2:
        <tr>
          <td>
            ${h.checkbox('%s.%s-%d.kood1' % (c.prefix2, kysimus.kood, i), 
            subitem.kood, checked=checked2, class_='jumper')}
            ${subitem.kood}
            ##${subitem.get_sisestusnimi()}
          </td>
        </tr>
        % endif
      </table>
</div>
  % endfor
</%def>

<%def name="js_show_response(responses, for_resp=True)">
% if for_resp:
clear_${c.block_prefix}();
% endif
<%
   kysimus = c.block.kysimus
   kv = responses.get(kysimus.kood)
   tulemus = kysimus.tulemus
%>
 var block = $('div#block_${c.block_prefix}');
% if kv:
 % for ks in kv.kvsisud:
 block.find('input[name="${kysimus.result}"][value="${h.chk_w(ks.kood1)}"]')
 % if for_resp:
 .prop('checked',true)
 % endif
 % if c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
 .parent('.correctness').addClass('${model.ks_correct_cls(responses, tulemus, kv, ks, False, for_resp)}')
 % endif
 ;
 % endfor
 % endif
</%def>
