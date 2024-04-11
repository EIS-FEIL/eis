## -*- coding: utf-8 -*- 
## Kõne salvestamine
<%inherit file="baasplokk.mako"/>
<!-- ${self.name} -->
<%namespace name="choiceutils" file="choiceutils.mako"/>

<%def name="block_edit()">
<%
  kysimus = c.block.kysimus
  tulemus = kysimus.tulemus or c.new_item(kood=kysimus.kood)
%>
${h.hidden('am1.kysimus_id', c.block.kysimus.id)}
<% ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') %>
<div class="row mb-1">
  <% name = 'autostart' %>
  ${ch.flb(_("Kõne salvestamise algus"), name)}
  <div class="col-md-9 col-xl-10 row">
    <% opts = list(c.item.autostart_opt or '') %>
    <div class="col-12">
      ${h.hidden('autostart_err','')}
    </div>
    <div class="col-md-6 col-xl-4">
      ${h.checkbox('autostart', model.Sisuplokk.AUTOSTART_LOAD, checkedif=opts,
      label=_("Ülesande avamisel"))}
    </div>
    <div class="col-md-6 col-xl-4">    
      ${h.checkbox('autostart', model.Sisuplokk.AUTOSTART_SEQ, checkedif=opts,
      label=_("Eelmise helisalvestuse või multimeedia lõppemisel"))}
    </div>
    <div class="col-md-6 col-xl-4">    
      ${h.checkbox('autostart', model.Sisuplokk.AUTOSTART_MEDIASTART, checkedif=opts,
      label=_("Koos eespool oleva multimeediaga"))}
    </div>
    <div class="col-md-6 col-xl-4">    
      ${h.checkbox('autostart', model.Sisuplokk.AUTOSTART_MEDIA, checkedif=opts,
      label=_("Eespool oleva multimeedia lõppemisel"))}
    </div>
  </div>
</div>
<div class="row mb-1">
  ${ch.flb(_("Nupud"), 'dnupud')}
  <div class="col-md-9 col-xl-10 row" id="dnupud">
    <div class="col-md-6 col-xl-4">
      ${h.checkbox1('f_pausita', True, checked=c.block.pausita, label=_("Pausi keelamine"))}
    </div>
    <div class="col-md-6 col-xl-4">    
      ${h.checkbox1('auk.max_vastus', 1, checked=kysimus.max_vastus==1, label=_("Uuesti alustamine keelatud"))}
    </div>
    <div class="col-md-6 col-xl-4">
      ${h.checkbox1('auk.peida_start', True, checked=kysimus.peida_start, label=_("Ei kuva alustamise nuppu"))}
    </div>
    <div class="col-md-6 col-xl-4">
      ${h.checkbox1('auk.peida_paus', True, checked=kysimus.peida_paus, label=_("Ei kuva pausi/jätkamise nuppu"))}
    </div>
    <div class="col-md-6 col-xl-4">
      ${h.checkbox1('auk.peida_stop', True, checked=kysimus.peida_stop, label=_("Ei kuva lõpetamise nuppu"))}      
    </div>
    <div class="col-md-6 col-xl-4">
      ${h.checkbox1('auk.naita_play', True, checked=kysimus.naita_play, label=_("Vastuse kuulamise võimalus"))}      
    </div>
  </div>
</div>
<div class="row mb-1">
  <% name = 'f_piiraeg' %>
  ${ch.flb(_("Vastamise piiraeg"), name)}
  <div class="col-md-3 col-xl-2">
      ${h.timedelta_sec('f_piiraeg', c.item.piiraeg,
      onchange="$('.timer-settings input').prop('disabled', $(this).val()=='');", wide=False)}
      % if c.is_edit:
      <script>
        $(function(){
        $('.timer-settings input').prop('disabled', $('#f_piiraeg').val()=='');
        });
      </script>
      % endif
  </div>

  <% name = 'f_hoiatusaeg' %>
  ${ch.flb(_("Hoiatusaeg"), name, colextra='timer-settings')}
  <div class="col-md-3 col-xl-2">
    ${h.posint5('f_hoiatusaeg', c.item.hoiatusaeg)} ${_("sekundit")}
  </div>
</div>
<div class="row mb-1">
  ${ch.flb(_("Kohustuslikkus"),'auk.min_vastus')}
  <div class="col">
    ${h.checkbox1('auk.min_vastus', 1, checked=kysimus.min_vastus, label=_("Vastamine kohustuslik"))}
  </div>
</div>

<div class="d-flex flex-wrap gbox hmtable overflow-auto">
  <div class="bg-gray-50 p-3">
    ${choiceutils.tulemus(kysimus, tulemus, 'am1.', maatriks=False)}
  </div>
  <div class="flex-grow-1 p-3">
    ${choiceutils.naidisvastus(kysimus, tulemus, 'am1.', rows=5, naha=False)}
  </div>
</div>
</%def>

<%def name="block_view()">
<%
  kysimus = c.block.kysimus
  cls = 'asblock'
  if not c.block.read_only:
     cls += ' asblock-audio'
  if c.block.autostart_opt:
     for key in c.block.autostart_opt:
        # autostart-L, autostart-S, autostart-H, autostart-M
        cls += f' autostart-{key}'
  if c.block.pausita:
     cls += ' nopause'
  if kysimus.ridu == 2:
     cls += ' stereo'
%>
<div class="${cls}" id="block_${c.block_prefix}" ${kysimus.min_vastus and f'data-min="{kysimus.min_vastus}"' or ''}>
${h.qcode(kysimus, nl=False)}
% if not c.block.read_only:
   ${h.hidden(kysimus.result, '', class_="audioblob")}
   ${h.hidden(kysimus.result + '_err_', '', class_="audioerror")}
   ${self.block_view_msg()}
% endif
  <div class="d-flex flex-wrap">
% if not c.block.read_only:
   % if not c.read_only and c.block.piiraeg:
   ${self.block_view_timer()}
   % endif
   ${self.block_view_controls()}
   ${self.block_view_analyser()}
% endif
   ${self.block_view_response()}
   </div>
</div>
</%def>

<%def name="block_print()">
<%
  kysimus = c.block.kysimus
  cls = 'asblock'
%>
<div class="${cls}" id="block_${c.block_prefix}">
${h.qcode(kysimus.kood, nl=False)}
  <div class="d-flex flex-wrap">
% if not c.block.read_only:
   % if not c.read_only and c.block.piiraeg:
   ${self.block_view_timer()}
   % endif
   ${self.block_view_controls()}
   ${self.block_view_analyser()}
% endif
   ${self.block_view_response()}
   </div>
</div>
</%def>

<%def name="block_view_msg()">
<% kysimus = c.block.kysimus %>
  <div class="audio-msg">
      <div class="audio-msg-not-started">
        % if not kysimus.peida_start:
        ${_("Praegu ei salvestata, alustamiseks vajuta nupule")}
        % else:
        ${_("Praegu ei salvestata")}
        % endif
      </div>
      <div class="audio-msg-paused" style="display:none">
        % if not kysimus.peida_paus:
        ${_("Praegu ei salvestata, jätkamiseks vajuta nupule")}
        % else:
        ${_("Praegu ei salvestata")}
        % endif
      </div>
      <div class="audio-msg-recording" style="display:none;font-weight:bold;">
        ${_("Salvestamine käib, räägi mikrofoni...")}
      </div>
      <div class="audio-msg-stopped" style="display:none">
        ${_("Vastus on salvestatud")}
      </div>    
      <div class="audio-msg-missed" style="display:none">
        ${_("Jäänud vastamata")}
      </div>    
      <div class="audio-not-supported errormsg" style="display:none">
        ${_("See brauser ei suuda heli salvestada")}
      </div>
    </div>
</%def>

<%def name="block_view_timer()">
    <div class="circle-wrap countdown-audio m-2" limit="${c.block.piiraeg}" warntime="${c.block.hoiatusaeg or ''}">
    </div>
</%def>    

<%def name="block_view_controls()">
  <div class="audio-controls mr-1">
      <%
        kysimus = c.block.kysimus
        %>
      % if not kysimus.peida_start:
      <button type="button" class="audio-recordButton iaudiobtn">
        ${h.mdi_icon('mdi-microphone')}
        <div class="iaudiolabel">
          ${_("Alustan vastamist")}
        </div>
      </button>
      % if kysimus.max_vastus is None or kysimus.max_vastus > 1:
      <button type="button" class="audio-record2Button iaudiobtn" style="display:none;">
        ${h.mdi_icon('mdi-microphone')}
        <div class="iaudiolabel">
            ${_("Alustan vastamist uuesti")}
        </div>
      </button>
      % endif
      % endif
      % if not c.block.pausita and not kysimus.peida_paus:
	  <button type="button" class="audio-pauseButton iaudiobtn" disabled="disabled" style="display:none;">
        <span class="if-pause">
          ${h.mdi_icon('mdi-pause')}
          <div class="iaudiolabel">
            ${_("Paus")}
          </div>
        </span>
        <span class="if-continue" style="display:none">
          ${h.mdi_icon('mdi-play')}
          <div class="iaudiolabel">
            ${_("Jätkan kõne salvestamist")}
          </div>
        </span>
      </button>
      % endif
      % if not kysimus.peida_stop:
	  <button type="button" class="audio-stopButton iaudiobtn" disabled="disabled">
        ${h.mdi_icon('mdi-stop')}
        <div class="iaudiolabel">
          ${_("Lõpetan")}
        </div>
      </button>
      % endif
	  <button type="button" class="audio-uploadButton iaudiobtn" style="display:none;">
        ${h.mdi_icon('mdi-upload')}
        <div class="iaudiolabel">
          ${_("Saada serverisse")}
        </div>
      </button>
    </div>
</%def>

<%def name="block_view_analyser()">
    <div class="audio-analyser mr-2">
	  <canvas class="audio-analyser" width="244" height="60"></canvas>
      <div class="audio-timer"></div>
    </div>
</%def>    

<%def name="block_view_response()">
<%
  kysimus = c.block.kysimus
  noplay = not c.read_only and not kysimus.naita_play
%>
<div class="showresponse ${noplay and 'noplay' or ''}" style="height:72px;" onclick="return false">
    % if c.prepare_response:
      <% 
         kv = c.responses.get(kysimus.kood)
         responded = False
      %>
      % if kv and not noplay:
        % for kvs in kv.kvsisud:
           % if kvs.has_file:
               <%
                 mimetype = kvs.filename and kvs.filename.endswith('.wav') and 'audio/wav' or 'audio/mp3'
                 responded = True
               %>
               ${self.play_audio(kvs.url, mimetype, kvs.id)}
           % endif
        % endfor
      % endif
      % if c.read_only and not responded:
      ${h.alert_notice(_("Kõne salvestamise küsimus on jäänud vastamata"), False)}
      % endif
      % if responded and not c.read_only and kysimus.max_vastus == 1:
       ## vastus on juba salvestatud, ylesanne on uuesti avatud, aga rohkem vastata ei tohi
       <script>$(function(){ $('.asblock#block_${c.block_prefix}').trigger('recorderapp:stop'); });</script>
       % endif
       % if responded and not c.read_only:
       <script>set_sp_finished($('.asblock#block_${c.block_prefix}'), true);</script>
       % endif
   % endif
</div>
<div class="save-status">
  ${h.spinner(_("Salvestan..."), 'audio-spinner', True)}
  ${h.mdi_icon('mdi-check-circle-outline audio-saved mdi-green', size=36, style="display:none")}
  <span class="p-2 error audio-not-saved" style="display:none">${_("Kahjuks ei õnnestunud helifaili serverisse saata")}</span>
</div>
</%def>

<%def name="play_audio(o_url, mimetype, kvs_id)">
<audio controls id="audio_ks_${kvs_id}">
  <source src="${o_url}" type="${mimetype}">
</audio>
## uuesti laadimise nupp juhuks, kui Chrome ei suuda kohe laadida
${h.mdi_icon('mdi-reload', size=12, onclick="$('#audio_ks_%s')[0].load()" % kvs_id)}
</%def>

<%def name="block_entry()">
<div class="td-sis-value2">${_("Heli ei sisestata")}</div>
</%def>
