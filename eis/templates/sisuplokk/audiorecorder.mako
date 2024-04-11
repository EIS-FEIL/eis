## Kõne salvestamine

<%def name="recorder(name, id, extracls='')">
<div class="asblock asblock-audio">
  ${h.hidden(name, '', id=id, class_="audioblob")}
  ${self.block_view_msg()}
  <div class="d-flex flex-wrap">
    ${self.block_view_controls()}
    ${self.block_view_analyser()}
  </div>
</div>
</%def>

<%def name="block_view_msg()">
  <div class="audio-msg">
      <div class="audio-msg-not-started">
        ${_("Praegu ei salvestata, alustamiseks vajuta nupule")}
      </div>
      <div class="audio-msg-paused" style="display:none">
        ${_("Praegu ei salvestata, jätkamiseks vajuta nupule")}
      </div>
      <div class="audio-msg-recording" style="display:none;">
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

<%def name="block_view_controls()">
  <div class="audio-controls">
      <button type="button" class="audio-recordButton iaudiobtn">
        ${h.mdi_icon('mdi-microphone')}
        <div class="iaudiolabel">
          ${_("Alustan salvestamist")}
        </div>
      </button>
      <button type="button" class="audio-record2Button iaudiobtn" style="display:none;">
        ${h.mdi_icon('mdi-microphone')}
        <div class="iaudiolabel">
            ${_("Alustan salvestamist uuesti")}
        </div>
      </button>
	  <button type="button" class="audio-pauseButton iaudiobtn" disabled="disabled" style="display:none;">
        <span class="if-pause">
          ${h.mdi_icon('mdi-pause')}
          <div class="iaudiolabel">
            ${_("Paus")}
          </div>
        </span>
        <span class="if-continue" style="display:none;">
          ${h.mdi_icon('mdi-play')}
          <div class="iaudiolabel">
            ${_("Jätkan kõne salvestamist")}
          </div>
        </span>
      </button>
	  <button type="button" class="audio-stopButton iaudiobtn" disabled="disabled" style="display:none;">
        ${h.mdi_icon('mdi-stop')}
        <div class="iaudiolabel">
          ${_("Lõpetan")}
        </div>
      </button>
	  <button type="button" class="audio-uploadButton iaudiobtn" style="display:none;">
        ${h.mdi_icon('mdi-upload')}
        <div class="iaudiolabel">
          ${_("Saada serverisse")}
        </div>
      </button>
    </div>
</%def>

<%def name="block_view_analyser()">
      <div class="audio-analyser">
	    <canvas class="audio-analyser" width="244" height="60"></canvas>
        <div class="audio-timer"></div>
    </div>
    <div class="save-status p-1 mx-1">
      ${h.spinner(_("Salvestan..."), 'audio-spinner', True)}
      ${h.mdi_icon('mdi-check-circle-outline audio-saved mdi-green', size=36, style="display:none")}
      <span class="p-2 error audio-not-saved" style="display:none">${_("Kahjuks ei õnnestunud helifaili serverisse saata")}</span>
    </div>      
    </div>
</%def>    

<%def name="play_audio(o_url, mimetype, height=None)">
% if not h.is_msie():
## IE HTML5 ei toeta WAV formaati
<audio controls ${height and f'style="height:{height};"' or ''}>
  <source src="${o_url}" type="${mimetype}">
</audio>
% else:
<object type="${mimetype}" data="${o_url}" width="300" height="50">
    <param name="autoplay" value="false">
    <param name="autostart" value="false">
    <embed src="${o_url}" type="${mimetype}" autostart="false" loop="false" height="50"></embed>
</object>
% endif
</%def>
