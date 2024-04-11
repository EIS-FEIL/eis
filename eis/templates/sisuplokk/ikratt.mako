## Kratt

<%inherit file="baasplokk.mako"/>
<%namespace name="choiceutils" file="choiceutils.mako"/>
<!-- ${self.name} -->

<%def name="block_edit()">
<%
  k = c.block.give_kysimus()
  if not k.kood:
     k.kood = c.ylesanne.gen_kood()
  tulemus = k.tulemus or c.new_item(kood=k.kood, arvutihinnatav=False)
  di_data = c.block.get_json_sisu()
  c.kdata = c.new_item.create_from_dict(di_data) or c.new_item()
  kuulamine = c.kdata.krati_kuulamine
  has_response = not kuulamine and True or kuulamine.record
%>

${self.krati_kysimused(c.kdata)}

<div class="row mb-1">
  <div class="col-md-6 col">
    <% name = 'krk.audio_seadistamine' %>
    ${h.checkbox1(name, value=1, checked=c.kdata.audio_seadistamine, class_="audio-setup",
    label=_("Audio seadistamine"))}
  </div>
</div>
<div class="row mb-1">
  <div class="col-md-6 col">
    <% name = 'krk.krati_kuulamine_record' %>
    ${h.checkbox1(name, value=1, checked=has_response, class_="audio-record",
    label=_("Helivastuse salvestamine"))}
  </div>
  <% name = 'krk.krati_kuulamine_audio_piiraeg' %>
  <div class="col">
    <div class="has-response">
      <div class="d-flex flex-wrap">
        ${h.flb(_("Vastamise piiraeg"), name)}
        <div>
          ${h.timedelta_sec(name, kuulamine and kuulamine.audio_piiraeg, wide=False)}
        </div>
      </div>
    </div>
  </div>
</div>
<script>
  ## need välistavad teineteist
  $('input.audio-setup').click(function(){
    if(this.checked) $('input.audio-record').prop('checked', false);
  });
  $('input.audio-record').click(function(){
    if(this.checked) $('input.audio-setup').prop('checked', false);
  });  
</script>

<div class="has-response" style="display:none">
${h.hidden('am1.kysimus_id', k.id)}
<div class="gbox hmtable overflow-auto d-flex flex-wrap">
  <div class="bg-gray-50 p-3">      
    ${choiceutils.tulemus(k, tulemus, 'am1.', maatriks=False)}
  </div>
  <div class="flex-grow-1 p-3">
    ${choiceutils.naidisvastus(k, tulemus, 'am1.', rows=3, naha=False)}
  </div>
</div>
</div>

<script>
  $('.has-response').toggle(${has_response and 'true' or 'false'});
  $('input[name="krk.krati_kuulamine_record"]').click(function(){
    $('.has-response').toggle($(this).is(':checked'));
  });
</script>
</%def>

<%def name="krati_kysimused(kdata)">
<%
  q = (model.Session.query(model.Piltobjekt.filename)
       .join(model.Piltobjekt.sisuplokk)
       .filter(model.Sisuplokk.ylesanne_id==c.ylesanne.id)
       .filter(model.Sisuplokk.tyyp==const.BLOCK_IMAGE)
       .filter(model.Piltobjekt.fileversion!=None)
       .order_by(model.Piltobjekt.filename))
  c.opt_img = [('images/%s' % fn, fn) for fn, in q.all()]  

  choicetbl_id = 'krkys'
  prefix = 'krk.kysimused'
%>
<table class="table table-borderless table-striped" id="${choicetbl_id}">
  <caption>${_("Krati küsimused")}</caption>
  <tbody>
          % if c._arrayindexes != '' and not c.is_tr:
          ## valideerimisvigade korral
          %   for cnt in c._arrayindexes.get(prefix) or []:
            ${self.krati_kysimus(c.new_item(), prefix, '-%s' % (cnt))}
          %   endfor
          % else:
          ## tavaline kuva
          %   for cnt, item in enumerate(kdata.krati_kysimused):
            ${self.krati_kysimus(item, prefix, '-%s' % (cnt))}
          %   endfor
          % endif
    
  </tbody>
</table>
% if c.is_edit and not c.lang:
${h.button(_("Lisa"), onclick=f"grid_addrow('{choicetbl_id}')", level=2, mdicls='mdi-plus')}
      <div id="sample_${choicetbl_id}" class="invisible">
        <!--
        ${self.krati_kysimus(c.new_item(), prefix, '__cnt__')}
        -->
      </div>
% endif

<table class="table table-borderless table-striped">
  <caption>${_("Krati lõppsõna")}</caption>
  <tbody>
    <% item = kdata.krati_outro or c.new_item() %>
    ${self.krati_kysimus(item, 'krk.outro', '')}
  </tbody>
</table>
      
</%def>

<%def name="krati_kysimus(item, baseprefix, cnt)">
       <% prefix = '%s%s' % (baseprefix, cnt) %>
         <tr id="${prefix.replace('.','')}" name="${prefix}">
           <td>
             <div class="row">
               ${h.flb3(_("Suuline kõne"), class_="text-md-right")}
               <div class="col">
                 ${h.text("%s.speak" % (prefix), item.speak)}
               </div>
             </div>
             <div class="row">
               ${h.flb3(_("Kirjalik tekst"), class_="text-md-right")}
               <div class="col">
                 ${h.text("%s.text" % (prefix), item.text)}
               </div>
             </div>
             <div class="row">
               ${h.flb3(_("Max korduste arv"), class_="text-md-right")}
               <div class="col">
                 ${h.posint5("%s.kordus" % (prefix), item.kordus)}
               </div>
             </div>
             % if c.opt_img or item.img_url:
             <div class="row">
               ${h.flb3(_("Pilt"), class_="text-md-right")}
               <div class="col-md-6">
                 ${h.select('%s.img_url' % prefix, item.img_url, c.opt_img, empty=True)}
               </div>
               <div class="col-md-3">
                 % if item.img_url:
                 <img src="${item.img_url}" style="max-width:100%"/>
                 % endif
               </div>
             </div>
             % endif
             <div class="row">
               ${h.flb3(_("Ettevalmistusaeg"), class_="text-md-right")}
               <div class="col">
                 ${h.timedelta_sec("%s.ooteaeg" % prefix, item.ooteaeg, wide=False)}
               </div>
             </div>
             <div class="row">
               ${h.flb3(_("Vastamisaeg"), class_="text-md-right")}
               <div class="col">
                 ${h.timedelta_sec("%s.vastamisaeg" % prefix, item.vastamisaeg, wide=False)}
               </div>
             </div>
           </td>
           % if c.is_edit:
           <td width="20px" class="align-top">${h.grid_remove()}</td>
           % endif
         </tr>
</%def>            


<%def name="block_view()">
<%
  kysimus = c.block.get_kysimus()
%>
% if kysimus:
${h.qcode(kysimus, nl=True)}
 % if not c.block.read_only:
   ${h.hidden(kysimus.result, '', class_="statusurl")}
##   ${h.hidden(kysimus.result + '_text_', '', class_="audiotext")}
 % endif
% endif
% if c.read_only:
   ${self.block_view_response()}
% else:
<div id="applet_container_${c.block.id}">
</div>
% endif
</%def>

<%def name="block_view_js()">
% if not c.read_only:
## kratt kuvatakse ainult siis, kui lahendamine veel käib
<%
  kysimus = c.block.get_kysimus()
  ##jsonurl = datafile/kratt.json
  jsonurl = h.url_current('datafile', filename='kratt.dat', task_id=c.block.ylesanne_id, m=c.block.modified.timestamp())
%>
var kratt_continue = null, kratt_result = null, kratt_allowed = false;
$(function(){
  init_kratt({element: 'applet_container_${c.block.id}',
              url: '${jsonurl}',
     % if kysimus:
              urlresult: '${kysimus.result}',
##              audioresult: '${kysimus.result}',
##              textresult: '${kysimus.result}_text_'
     % endif
            });
  is_response_dirty = false;
});
% endif
</%def>

<%def name="block_print()">
<%
  di_data = c.block.get_json_sisu()
  c.kdata = di_data and c.new_item.create_from_dict(di_data) or c.new_item()
  outro = c.kdata.krati_outro
%>
% for item in c.kdata.krati_kysimused:
<div class="p-3">${item.text}</div>
% endfor
% if outro:
<div class="p-3">${outro.text}</div>
% endif
</%def>

<%def name="block_view_response()">
<%
  kysimus = c.block.kysimus
  noplay = False
%>
<div class="showresponse" onclick="return false">
    % if c.prepare_response and kysimus:
      <% 
         kv = c.responses.get(kysimus.kood)
         responded = ready = False
      %>
      % if kv and not noplay:
        ${_("Krati salvestatud vastus")}
        % for kvs in kv.kvsisud:
           <%
             if kvs.koordinaat or kvs.has_file:
                responded = True
           %>
           % if kvs.has_file:
               <%
                 mimetype = 'audio/mp3'
                 ready = True
               %>
               <div>
                 ${self.play_audio(kvs.url, mimetype)}
               </div>
           % endif
           % if kvs.sisu:
               <% ready = True %>    
               <div>
                 ${h.readonly_textarea(kvs.sisu)}
               </div>
           % endif
        % endfor
      % endif
      % if c.read_only and not responded:
         ${h.alert_notice(_("Vastuse salvestist ei ole"), False)}
      % elif c.read_only and not ready:        
         <div class="alert alert-secondary fade show" role="alert">
           <span class="pr-3">
              ${_("Kratt pole veel helivastuse töötlemist lõpetanud")}
           </span>
           % if not c.sooritus_id and c.refresh_showtask_url:
             ## ilma testita lahendamisel võimalus leht uuesti laadida
             ${h.button(_("Laadi kratilt vastus"), level=2, onclick="$('body').trigger('eis:refresh_showtask')")}
           % endif
      % endif
   % endif
</div>
</%def>

<%def name="play_audio(o_url, mimetype)">
<audio controls>
  <source src="${o_url}" type="${mimetype}">
</audio>
</%def>

<%def name="block_entry()">
<div class="td-sis-value2">${_("Kratile antud vastust ei sisestata")}</div>
</%def>
