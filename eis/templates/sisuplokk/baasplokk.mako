## Sisuplokkide baasmall
<!-- ${self.name.split('/')[-1]} b${c.block.id} y${c.block.ylesanne_id} -->
<%
   ## c.responses on dict sellele ülesandele lahendaja poolt antud vastustega
   ## dictis on iga kysimuse koodi kohta list selle kysimuse vastuste objektidest
   if not c.responses:
      c.responses = {}
 
   ## view korral on eelnevalt on juba seatud c.y_prefix ja 
   ## c.block_prefix on unikaalne ja sisaldab ylesande prefiksit
   c.block_prefix = '%s%s' % (c.y_prefix, c.block.get_prefix())
   c.block_result = c.block.get_result()
%>
${self.block_before()}

% if c.is_sp_edit:
## sisuploki koostamine (ülesande koostaja vaade)
${self.block_edit()}

% elif c.is_sp_print:
## sisuploki eksportimine HTMLis p-ülesande lähtematerjaliks
${self.start_block_element()}
${self.block_print()}
${self.end_block_element()}

% elif c.is_sp_preview:
## sisuploki kuvamine ülesande koostajale kõigi teiste sisuplokkidega koos
${self.start_block_element()}
${self.block_preview()}
${self.end_block_element()}

% elif c.is_sp_analysis:
## sisuploki vastuste analüüsimine
${self.block_analysis()}

% elif c.is_sp_view:
## sisuploki kuvamine ülesande lahendajale või soorituse vaatajale või hindajale
${self.start_block_element()}
${self.block_view()}
${self.end_block_element()}

## kui toimub hindamine, siis hindamise väljade jaoks ankrud
% if not c.block_correct and c.on_hindamine and c.block.is_interaction:
## ei tee ankruid lynga korral, kuna siis kuvatakse hindamise väljad dialoogiaknas
${self.block_valuate()}
% endif

% elif c.is_sp_view_js:
## sisuploki javascripti osa genereerimine ülesande lahendajale või soorituse vaatajale või hindajale
${self.block_view_js()}

% elif c.is_sp_entry:
## sisuploki lahendaja antud vastuste sisestamine p-testi paberilt
${self.block_entry()}

% endif

<%def name="start_block_element()">
## sisuploki elemendi algus lahendajavaates
<%
  cls = 'sisuplokk eis-sp-%s spt-%s' % (c.block.tahis or c.block.seq, c.block.type_name)
  if c.block.naide:
      cls += ' example'
  if c.block.nahtavuslogi:
      cls += ' vbtimable'
  if c.is_sp_view and not c.on_hindamine and not c.hindamine and not c.block_correct and c.block.staatus==const.B_STAATUS_NAHTAMATU:
      cls += ' eis-sphidden'
  is_finished = c.block.is_interaction and 'null' or 'true'

  lang = c.lang
  if not lang:
     ylesanne = c.ylesanne or c.block.ylesanne
     lang = ylesanne.lang
%>
<div data-finished="${is_finished}" id="sp_${c.block.get_prefix()}" class="${cls}" lang="${lang}"><div class="eis-spbody">
% if c.block.nahtavuslogi:
${h.hidden('vbtimer_%s' % c.block.get_prefix(), '', class_="vbtimer")}
##${h.text('vbtimer_%s' % c.block.get_prefix(), '', class_="vbtimer")}
% endif
${self.show_prompt(lang)}
</%def>

<%def name="end_block_element()">
## sisuploki elemendi lõpp lahendajavaates
</div></div>
</%def>

<%def name="show_prompt(lang)">
## töökäsu kuvamine
<%
  tookask = c.block.tran(lang).nimi
  tookask = c.block.replace_img_url(tookask or '', lang=c.lang)
  if c.block.tookask_kood:
     tehn_tookask = model.Klrida.get_str('TOOKASK', c.block.tookask_kood, c.block.tyyp, lang=lang)
  else:
     tehn_tookask = c.block.tran(lang).tehn_tookask
  tookask_nl = tookask and c.block.tyyp not in (const.BLOCK_CUSTOM, const.INTER_TEXT)
%>
% if tookask:
% if tookask_nl:
<p style="margin-top:3px">
% endif
<b class="speech" lang="${c.lang}">${tookask}</b>
% if tookask_nl:
</p>
% endif
% endif
% if tehn_tookask:
<p style="padding-bottom:6px">
<i class="speech" lang="${c.lang}">${tehn_tookask}</i>
</p>
% endif
</%def>

<%def name="block_before()">
## mida teha enne kõiki teisi tegevusi

</%def>

<%def name="block_edit()">
</%def>

<%def name="block_print()">
${self.block_view()}
</%def>

<%def name="block_preview()">
${self.block_print()}
</%def>

<%def name="block_analysis()">
<div class="border p-3 mb-2">
  <h3>${_("Sisuplokk")} ${c.block.seq} (${c.block.tyyp_nimi})</h3>
  <div class="mt-2">
    <b>${c.block.tran(c.lang).nimi}</b>
    ${self.block_view()}
  </div>
  <%include file="analysis.mako"/>
</div>
<script>
  ${self.block_view_js()}
</script>
</%def>

<%def name="block_view()">
</%def>

<%def name="block_view_js()">
</%def>

<%def name="block_valuate()">
## teeme ankrud, et kysimuste hindamistabel tõsta peaaknast siia ankru juurde
<div>
% for kysimus in c.block.kysimused:
% if kysimus.tulemus:
  <a id="b${c.block.id}q${kysimus.id}" class="hinded"></a>
% endif
% endfor
</div>
</%def>

<%def name="block_entry()">
## vastuste sisestamine
## eelnevalt on seatud c.responses ja c.prefix
% for kysimus in c.block.kysimused:
  % if kysimus.tulemus:
    <%
      baastyyp = kysimus.tulemus.baastyyp
      kv = c.responses.get(kysimus.kood)
      kv2 = c.prefix2 and c.responses2.get(kysimus.kood)
    %>
    % if c.is_correct or not c.block.on_sisestatav:
        ## sisestatakse, kas vastus on õige või vale
        ${self.block_entry_correct(kysimus, kv, kv2)}
    % elif baastyyp == const.BASETYPE_IDENTIFIER:
        ${self.block_entry_identifier(kysimus, kv, kv2)}
    % elif baastyyp == const.BASETYPE_PAIR:
        ${self.block_entry_pair(kysimus, kv, kv2)}  
    % elif baastyyp == const.BASETYPE_DIRECTEDPAIR:
        ## tuleks üle laadida, et lisada opt1 ja opt2
        ${self.block_entry_pair(kysimus, kv, kv2)}  
    ##% elif baastyyp == const.BASETYPE_POINT:
    ##    ${self.block_entry_point(kysimus, kv, kv2)}  
    % elif baastyyp in (const.BASETYPE_STRING, const.BASETYPE_INTEGER, const.BASETYPE_FLOAT): 
        ${self.block_entry_string(kysimus, kv, kv2)}  
    % endif

  % endif
% endfor
</%def>

<%def name="block_entry_correct(kysimus, kv, kv2)">
## õige/vale sisestamine
  <%
      kvsisud = kv and list(kv.kvsisud) or []
      kvsisud2 = kv2 and list(kv2.kvsisud) or []
  %>
% for i in range(kysimus.max_vastus or 1):
     <% 
       if len(kvsisud) > i:
          correct = kvsisud[i].oige
       else:
          correct = None

       if len(kvsisud2) > i:
          correct2 = kvsisud2[i].oige
       else:
          correct2 = None

       err = correct is not None and correct2 is not None and correct != correct2 and 'form-control is-invalid' or ''
    %>
<div class="td-sis-value">
   ${self.block_entry_kood(kysimus)}
    <table cellpadding="0" cellspacing="0" class="showerr ${err}">
      <tr>
        <td>
##${kvsisud[i].id}
         ${h.select_entry('%s.%s-%d.oige' % (c.prefix, kysimus.kood, i),correct,
         c.opt.oige_vale)}
        </td>
      </tr>
        % if c.prefix2:
      <tr>
        <td>
##${kvsisud2[i].id}
         ${h.select_entry('%s.%s-%d.oige' % (c.prefix2, kysimus.kood, i),correct2,
         c.opt.oige_vale)}
        </td>
      </tr>
        % endif
    </table>
</div>
% endfor
</%def>

<%def name="block_entry_identifier(kysimus, kv, kv2)">
      % for i in range(kysimus.max_vastus or 1):
         <% 
            kvsisud = kv and list(kv.kvsisud) or []
            value = len(kvsisud) > i and kvsisud[i].kood1 or '' 
            kvsisud2 = kv2 and list(kv2.kvsisud) or []
            value2 = kvsisud2 and len(kvsisud2) > i and kvsisud2[i].kood1 or '' 
            err = value and value2 and value != value2 and 'form-control is-invalid' or ''
         %>
<div class="td-sis-value">
   ${self.block_entry_kood(kysimus)}
    <table cellpadding="0" cellspacing="0" class="showerr ${err}">
      <tr>
        <td>
         ${h.select_entry('%s.%s-%d.kood1' % (c.prefix, kysimus.kood, i), value,
         kysimus.valikud_opt)}
        </td>
      </tr>
        % if c.prefix2:
      <tr>
        <td>
         ${h.select_entry('%s.%s-%d.kood1' % (c.prefix2, kysimus.kood, i), value2,
         kysimus.valikud_opt)}
        </td>
      </tr>
        % endif
    </table>
</div>
      % endfor
</%def>

<%def name="block_entry_pair(kysimus, kv, kv2, opt1=None, opt2=None)">    
  <%
      kvsisud = kv and list(kv.kvsisud) or []
      kvsisud2 = kv2 and list(kv2.kvsisud) or []
  %>
      % for i in range(kysimus.max_vastus or 1):
         <% 
            if len(kvsisud) > i:
               kood1 = kvsisud[i].kood1
               kood2 = kvsisud[i].kood2
            else:
               kood1 = kood2 = ''

            if kvsisud2 and len(kvsisud2) > i:
               kood1_2 = kvsisud2[i].kood1
               kood2_2 = kvsisud2[i].kood2
            else:
               kood1_2 = kood2_2 = ''

            err1 = kood1 and kood1_2 and kood1 != kood1_2 and 'form-control is-invalid' or ''
            err2 = kood2 and kood2_2 and kood2 != kood2_2 and 'form-control is-invalid' or ''
            err = err1 or err2 or ''
         %>
<div class="td-sis-value2">
   ${self.block_entry_kood(kysimus)}
         <table cellpadding="0" cellspacing="0" class="showerr ${err}">
           <tr>
             <td>
               ${i+1}.
             </td>
             <td>
               % if opt1 == None:
               ${h.text5('%s.%s-%d.kood1' % (c.prefix, kysimus.kood, i),
               kood1)}
               % else:
               ${h.select_entry('%s.%s-%d.kood1' % (c.prefix, kysimus.kood, i), kood1,
               opt1)}
               % endif
             </td>
             <td>
               % if opt2 == None:
               ${h.text5('%s.%s-%d.kood2' % (c.prefix, kysimus.kood, i), kood2)}
               % else:
               ${h.select_entry('%s.%s-%d.kood2' % (c.prefix, kysimus.kood, i), kood2,
               opt2)}
               % endif
             </td>
           </tr>
           % if c.prefix2:
           <tr>
             <td>
             </td>
             <td>
               % if opt1 == None:
               ${h.text5('%s.%s-%d.kood1' % (c.prefix2, kysimus.kood, i), kood1_2)}
               % else:
               ${h.select_entry('%s.%s-%d.kood1' % (c.prefix2, kysimus.kood, i), kood1_2,
               opt1)}
               % endif
             </td>
             <td>
               % if opt2 == None:
               ${h.text5('%s.%s-%d.kood2' % (c.prefix2, kysimus.kood, i), kood2_2)}
               % else:
               ${h.select_entry('%s.%s-%d.kood2' % (c.prefix2, kysimus.kood, i), kood2_2,
               opt2)}
               % endif
             </td>
           </tr>
           % endif
         </table>
</div>
      % endfor
</%def>

<%def name="block_entry_point(kysimus, kv, kv2)">        
  <%
      kvsisud = kv and list(kv.kvsisud) or []
      kvsisud2 = kv2 and list(kv2.kvsisud) or []
      cnt = kysimus.max_vastus or 1
  %>

      % for i in range(cnt):
         <%          
            if len(kvsisud) > i and kvsisud[i].punkt:
               x, y = kvsisud[i].punkt
            else:
               x = y = ''

            if kvsisud2 and len(kvsisud2) > i and kvsisud2[i].punkt:
               x2, y2 = kvsisud2[i].punkt
            else:
               x2 = y2 = ''               

            err1 = x and x2 and x != x2 and 'form-control is-invalid' or ''
            err2 = y and y2 and y != y2 and 'form-control is-invalid' or ''
            err = err1 or err2 or ''
         %>
<div class="td-sis-value2">
   ${self.block_entry_kood(kysimus, i+1, cnt)}
         <table cellpadding="0" cellspacing="0" class="showerr ${err}">
           <tr>
             <td>
               x ${h.posint5('%s.%s-%d.x' % (c.prefix, kysimus.kood, i), x)}
             </td>
             <td>
               y ${h.posint5('%s.%s-%d.y' % (c.prefix, kysimus.kood, i), y)}
             </td>
           </tr>
           % if c.prefix2:
           <tr>
             <td>
               x ${h.posint5('%s.%s-%d.x' % (c.prefix2, kysimus.kood, i), x2)}
             </td>
             <td>
               y ${h.posint5('%s.%s-%d.y' % (c.prefix2, kysimus.kood, i), y2)}
             </td>
           </tr>
           % endif
         </table>
</div>
      % endfor
</%def>

<%def name="block_entry_string(kysimus, kv, kv2)">    
  <%
      baastyyp = kysimus.tulemus.baastyyp
      pattern = None
      if baastyyp == const.BASETYPE_INTEGER:
         pattern = '([*]|-?[0-9]*)'
      elif baastyyp == const.BASETYPE_FLOAT:
         pattern = '([*]|-?[0-9]*[.,]?[0-9]*)'
      kvsisud = kv and list(kv.kvsisud) or []
      kvsisud2 = kv2 and list(kv2.kvsisud) or []
  %>
      % for i in range(kysimus.max_vastus or 1):
         <% 
            value = '' 
            if len(kvsisud) > i:
               if kvsisud[i].tyyp==const.RTYPE_CORRECT:
                  if kvsisud[i].oige == const.C_LOETAMATU:
                     value = const.ENTRY_LOETAMATU_STR
                  elif kvsisud[i].oige == const.C_VASTAMATA:
                     value = const.ENTRY_VASTAMATA_STR
               else:
                  value = kvsisud[i].sisu or '' 

            value2 = '' 
            if len(kvsisud2) > i:
               if kvsisud2[i].tyyp==const.RTYPE_CORRECT:
                  if kvsisud2[i].oige == const.C_LOETAMATU:
                     value2 = const.ENTRY_LOETAMATU_STR
                  elif kvsisud2[i].oige == const.C_VASTAMATA:
                     value2 = const.ENTRY_VASTAMATA_STR
               else:
                  value2 = kvsisud2[i].sisu or '' 

            #value2 = len(kvsisud2) > i and kvsisud2[i].sisu or ''
            err = value and value2 and value != value2 and 'form-control is-invalid' or ''         
         %>
<div class="td-sis-value">
   ${self.block_entry_kood(kysimus)}
         <table cellpadding="0" cellspacing="0" class="showerr ${err}">
           <tr>
             <td>  
               ${h.text('%s.%s-%d.sisu' % (c.prefix, kysimus.kood, i), 
               value, pattern=pattern, size=kysimus.pikkus or 20)}
             </td>
           </tr>
           % if c.prefix2:
           <tr>
             <td>
               ${h.text('%s.%s-%d.sisu' % (c.prefix2, kysimus.kood, i),
               value2, pattern=pattern, size=kysimus.pikkus or 20)}
             </td>
           </tr>
           % endif
         </table>
</div>
      % endfor
</%def>

<%def name="block_entry_kood(kysimus, n=None, cnt=None)">
## vastuste sisestamisel kysimuse koodi kuvamine
## r_error on selleks, et oleks koht, kuhu salvestamisel kuvada
## veateade sisestuserinevuse kohta

    % if n and cnt and cnt>1:
    ${kysimus.kood}(${n})
    % else:
    ${kysimus.kood}
    % endif
</%def>
