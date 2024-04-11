## Mitme valikuga tabel
<%inherit file="baasplokk.mako"/>

<%namespace name="choiceutils" file="choiceutils.mako"/>
<!-- ${self.name} -->

<%def name="block_edit()">
<%
  # kysimuste hulk
  c.kysimus1 = c.block.give_baaskysimus(seq=1)
  # valikvastuste hulk
  c.kysimus2 = c.block.give_baaskysimus(seq=2)
%>

% for ind, valista_kood in enumerate(c.ylesanne.get_kysimus_koodid(c.block, True)):
${h.hidden('valista%d' % ind, valista_kood, class_='valista')}
% endfor

<% ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') %>
<div class="row mb-2">
  <% name = 'f_laius' %>
  ${ch.flb(_("Valikvastuste arv"), name)}
  <div class="col-md-9 col-xl-2 mb-1">
      <%
        if not c.block.laius:
           c.block.laius = 2 # vaikimisi valikute arv
      %>
      ${h.posint5('f_laius', c.block.laius or 1, ronly=not c.is_edit and not c.is_tr, max=26)}
      <span class="needsave brown" style="display:none">${_("Muudatus rakendub peale salvestamist")}</span>
      <script>
        $('#f_laius').change(function(){
          ## kuvame teate, et vaja salvestada
          $(this).closest('td').find('.needsave').show();
          ## lisame liigsetele valikutele märke, et nimi ei oleks kohustuslik
          var cnt = parseInt($(this).val()) || 2;
          $('.v2-removed').each(function(n, fld){
             var ind = parseInt($(fld).attr('data-ind'));
             $(fld).val(ind >= cnt ? '1' : '');
          });
        });
      </script>
  </div>
  <% name = 'f_alamtyyp' %>
  ${ch.flb(_("Hindamise seaded"), name)}
  <div class="col-md-9 col-xl-5">
      ${h.radio('f_alamtyyp', '1', checked=c.block.alamtyyp!='N',
      label=_("ühetaolised kõigile küsimustele"))}
      ${h.radio('f_alamtyyp', 'N', checked=c.block.alamtyyp=='N',
      label=_("igal küsimusel eraldi"))}      
  </div>
</div>

<div>
  ${choiceutils.choices(c.kysimus1, c.kysimus1.valikud, 'v1', valista=True, gentype='K01', caption=_("Küsimused"))}
</div>


<% kysimused = list(c.block.pariskysimused) %>
% if len(kysimused) > 0 and c.block.alamtyyp != 'N':
<div class="bg-gray-50 p-3">
<%
  # kui on yhetaotlised hindamise seaded, siis kuvatakse esimese kysimuse seaded
  kysimus = kysimused[0]
  ind = 0
  tulemus = kysimus.tulemus or c.new_item(max_vastus=None)
  if not tulemus.id:
     tulemus.arvutihinnatav = True
  choiceutils.tulemus(kysimus, tulemus, 'am1.', common=True, caption=_("Hindamise seaded"))
%>
  ${h.hidden('am1.kysimus_id', '')}
</div>
% endif

<script>
$(function(){
  $('.checkboxparent').click(function(event){
    if(!$(event.target).is(':input,a,button'))
    {
        $(this).find('input.checkboxchild').click();
        return false;
    }
  });
});
</script>
</%def>


<%def name="block_print()">
${self.block_view()}
</%def>

<%def name="block_view()">
<%
  c.kysimus1 = c.block.get_baaskysimus(seq=1) # kysimuste tekstid
  kvalikud = list(c.kysimus1.valikud)
  if c.kysimus1.segamini and c.ylesandevastus:
      kv = c.responses.get(c.kysimus1.kood)
      model.apply_shuffle(kvalikud, kv and kv.valikujrk)
  kysimused = {k.kood: k for k in c.block.pariskysimused}
  
  c.kysimus2 = c.block.get_baaskysimus(seq=2) # valikud
  valikud = list(c.kysimus2.valikud)  

  colwidths = (c.block.get_json_sisu() or {}).get('colwidths') or []
%>
<div id="block_${c.block_prefix}">
<table class="table" style="width:auto">
  % if colwidths:
  % for colwidth in colwidths:
  <col width="${colwidth}"/>
  % endfor
  % endif
  <thead>
    <tr>
      <%
        width = colwidths and colwidths[0] or None
        width_attr = width and 'width="%s"' % width or ''
      %>
      <th ${width_attr}>${c.block.tran(c.lang).sisuvaade}</th>
      % for ind, valik in enumerate(valikud):
      <%
        width = colwidths and len(colwidths) >= ind + 1 and colwidths[ind+1] or None
        width_attr = width and 'width="%s"' % width or ''
      %>
      <th class="speech" lang="${c.lang}" align="center" ${width_attr} style="text-align:center">
        ${valik.tran(c.lang).nimi}
        <div>${h.ccode(valik.kood)}</div>
      </th>
      % endfor
    </tr>
  </thead>
  <tbody>
    % for kvalik in kvalikud:
    <%
      kvalik_kood = kvalik.kood
      kysimus = kysimused.get(kvalik_kood)
    %>
    % if kysimus:
    <%
      min_vastus = kysimus.min_vastus
      max_vastus = kysimus.max_vastus
      cb_cls = max_vastus == 1 and len(valikud) > 1 and 'radio' or 'checkbox'
      name = kysimus.result
    %>
    <tr>
      <td class="speech" lang="${c.lang}">
        ${h.qcode(kysimus)}
        ${kvalik.tran(c.lang).nimi}
      </td>
      % for ind_v, valik in enumerate(valikud):
      <% cb_id = name + '_%d' % ind_v %>
      <td class="checkboxparent" align="center">
        <div class="custom-control custom-${cb_cls} custom-control-inline correctness m-1">
          <input type="${cb_cls}" class="custom-control-input checkboxchild"
                 data_kood="${kvalik_kood}" value="${valik.kood}" min_vastus="${min_vastus or ''}" max_vastus="${max_vastus or ''}"
                 name="${name}" id="${cb_id}"/>
          <label class="custom-control-label mchoice-cb-label pr-3" lang="${c.lang}" for="${cb_id}">
          </label>
        </div>
      </td>
      % endfor
    </tr>
    % endif
    % endfor
  </tbody>
</table>
</div>
</%def>

<%def name="block_view_js()">
function clear_${c.block_prefix}()
{
   $('div#block_${c.block_prefix}').find('input[type="radio"],input[type="checkbox"]').prop('checked',false);
}
function set_finished_${c.block.id}()
{
  var fields = $('div#block_${c.block_prefix}').find('input[type="radio"],input[type="checkbox"]');
  var is_finished = true;
  for(var i=0; i<fields.length; i++){
    var field = $(fields[i]);
    var minv = parseInt(field.attr('min_vastus'));
    if(!isNaN(minv))
    {
       var name = field.attr('name');
       var nchecked = fields.filter('input:checked[name="'+name+'"]').length;
       if(nchecked < minv)
         {
            is_finished = false;
            break;
         }
    }
  }
  set_sp_finished(fields, is_finished);                                 
}
function handle_click_${c.block.id}(event)
{
   var allfields = $('div#block_${c.block_prefix}').find('input[type="radio"],input[type="checkbox"]');
   var is_input = $(event.target).is(':input');
   $(this).find('input.checkboxchild').each(function(i, fld){
         var fields = allfields.filter('input[name="' + fld.name + '"]');
         ## max vastuse kontroll
         ## kui target on input, siis on väärtus juba seatud
         var is_check = (is_input ? fld.checked : !fld.checked);
         if(($(fld).prop('type') == 'checkbox') && is_check)
         {            
            var maxv = parseInt($(fld).attr('max_vastus'));
            if(!isNaN(maxv))
            {

               var nchecked = fields.filter(':checked:not([id="'+fld.id+'"])').length;
               if(nchecked >= maxv)
               {
                  if(is_input)                 
                     fld.checked = false;
                  alert_dialog(eis_textjs.choice_cnt, eis_textjs.choice_max.format(maxv));
                  return;                 
               }
            }
         }
         ## kui kontroll edukalt läbitud
         fld.checked = is_check;
         response_changed(fields);
         is_response_dirty = true;
   });
   set_finished_${c.block.id}();               
   if(!is_input)
   {
      return false;
   }
}
$(function(){

% if c.block_correct or c.block.naide:
${self.js_show_response(c.correct_responses)}
% else:
${self.js_show_response(c.responses)}
${self.js_show_response(c.correct_responses, False)}
% endif

var fields = $('div#block_${c.block_prefix}').find('input[type="radio"],input[type="checkbox"]');
% if c.block.read_only:
fields.prop('disabled','disabled');
## vastust muuta ei saa

% else:
## saab vastata
  $('div#block_${c.block_prefix}').find('.checkboxparent').click(handle_click_${c.block.id});
  set_finished_${c.block.id}();
% endif
});
</%def>

<%def name="js_show_response(responses, for_resp=True)">
% if for_resp:
clear_${c.block_prefix}();
% endif
% for kysimus in c.block.pariskysimused:
<%
   kv = responses.get(kysimus.kood)
   tulemus = kysimus.tulemus
%>
 % if kv:
 % for ks in kv.kvsisud:
 $('input[name="${kysimus.result}"][value="${h.chk_w(ks.kood1)}"]')
 % if for_resp:
 .prop('checked',true)
 % endif
 % if c.prepare_correct and ks.on_hinnatud and not c.block.varvimata:
 .parent('.correctness').addClass('${model.ks_correct_cls(responses, tulemus, kv, ks, False, for_resp)}')
 % endif
 ;
% endfor
% endif
% endfor

</%def>

