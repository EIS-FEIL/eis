<%inherit file="baasplokk.mako"/>
<%namespace name="dragimg" file="bmedia.dragimg.mako"/>

<%def name="block_edit()">
${dragimg.edit_images(c.block)}

% if c.is_edit:
${h.checkbox('muudform', 1, label=_("Märgi samanimelised failid (ainult laiend erineb) sama pala erinevate formaatidena"))}
% endif
</%def>

<%def name="block_view()">
% for obj in c.block.samameediaobjektid:
<div class="eis-mediaitem mb-1">
  ${self.play(obj)}
</div>
% endfor
</%def>

<%def name="block_print()">
% for obj in c.block.samameediaobjektid:
<p>
  <i>${_("Multimeedia")}</i>
  ${obj.filename}
  % for obj2 in obj.muudformaadid:
  ${obj2.filename}
  % endfor
</p>
% endfor
</%def>

<%def name="block_preview()">
% for obj in c.block.samameediaobjektid:
<p><i>${_("Multimeedia")}</i>
  ${obj.filename}
  % for obj2 in obj.muudformaadid:
  ${obj2.filename}
  % endfor
</p>
% endfor
</%def>

<%def name="play(obj)">
<%
     tran = obj.tran(c.lang)
     o_url = tran.fileurl or obj.get_url(c.lang, c.url_no_sp)
     MIMETYPES_WAV = ('audio/vnd.wave', 'audio/wav', 'audio/wave', 'audio/x-wav')
     MIMETYPES_AUDIO = ('audio/mpeg','audio/mp3','audio/mp4','audio/wav','audio/x-wav','audio/ogg','audio/webm')
     MIMETYPES_VIDEO = ('video/mpeg','video/mp4','video/ogg','video/webm')
     # kuulamiste loendur
     kpc = obj.get_kysimus(const.OBJSEQ_COUNTER)
     kpc_value = ''
     if kpc and not (c.block.naide or c.block_correct or c.read_only):
        kv = c.responses.get(kpc.kood)
        if kv:
           for ks in kv.kvsisud:
              try:
                  kpc_value = int(ks.sisu)
              except:
                  kpc_value = 0
              break
     # kuulamise järg
     kpp = obj.get_kysimus(const.OBJSEQ_POS)
     kpp_value = 0
     if kpp and not c.read_only:
        kv = c.responses.get(kpp.kood)
        if kv:
           for ks in kv.kvsisud:
              try:
                  kpp_value = int(ks.sisu)
              except:
                  kpp_value = 0
              break
  
  %>
% if kpc:
  ${h.hidden(kpc.result, kpc_value, class_="bmedia-kpc")}
% endif
% if kpp:
  ${h.hidden(kpp.result, kpp_value, class_="bmedia-kpp")}
% endif
  % if obj.is_youtube():
<iframe title="YouTube video player" ${h.width(obj)} ${h.height(obj)}
        src="${o_url}" 
        frameborder="0" allowfullscreen></iframe>
  ${h.origin(tran.tiitel)}

  % elif obj.mimetype in MIMETYPES_AUDIO and obj.is_jplayer:
    ${self.play_mp3(obj, tran, o_url, kpc_value, kpp_value)}
  % elif obj.mimetype in MIMETYPES_VIDEO and obj.is_jplayer:
    ${self.play_mp4(obj, tran, o_url, kpc_value, kpp_value)}
  % elif obj.mimetype in MIMETYPES_AUDIO:
    ${self.play_audio(obj, tran, o_url, kpc_value, kpp_value)}
  % elif obj.mimetype in MIMETYPES_VIDEO:
    ${self.play_video(obj, tran, o_url, kpc_value, kpp_value)}
  % elif obj.mimetype in MIMETYPES_WAV and not h.is_msie():
##    ## IE HTML5 ei toeta .wav
    ${self.play_audio(obj, tran, o_url, kpc_value, kpp_value)}
  % else:
    ${self.play_media(obj, tran, o_url, kpc_value, kpp_value)}
  % endif
</%def>

<%def name="display_kpc(obj, kpc_value, is_video)">        
## kuulamiste arvu ja max kuulamiste arvu kuvamine
% if obj.max_kordus:
         <div class="kpc-msg">
          % if is_video: 
          ${_("Vaatamiste arv")}:
          % else:
          ${_("Kuulamiste arv")}:
          % endif
          <span class="display-kpc">${kpc_value or 0}</span>/${obj.max_kordus}
          <div class="mediafile-error mx-3 float-right" style="display:none" title="${_("Faili allalaadimise viga")}">
            ${h.mdi_icon('mdi-information text-danger')}
          </div>         
        </div>
% endif
</%def>

<%def name="play_mp3(obj, tran, o_url, kpc_value, kpp_value)">
  <div id="jquery_jplayer_${obj.id}" class="jp-jplayer"></div>
  <div id="jp_container_${obj.id}" class="jp-audio" role="application" aria-label="plmedia player">
    <div class="jp-type-single">
      <div class="jp-gui jp-interface">
        <div class="jp-controls-holder">
          <div class="jp-volume-controls">
            <button class="jp-mute" role="button" tabindex="0">mute</button>
            <button class="jp-volume-max" role="button" tabindex="0">max volume</button>
            <div class="jp-volume-bar">
              <div class="jp-volume-bar-value"></div>
            </div>
          </div>
          <div class="jp-controls">
            <button class="jp-play" role="button" tabindex="0">play</button>
            % if not obj.pausita or c.block_correct:
            <button class="jp-pause" role="button" tabindex="0">pause</button>            
            % endif
            % if obj.max_kordus is None or c.block_correct:
            <button class="jp-stop" role="button" tabindex="0">stop</button>
            % endif            
          </div>

          <div class="jp-progress">
            % if (obj.max_kordus or obj.pausita) and not c.block_correct:
            <div class="jp-play-bar"></div>
            % else:
            <div class="jp-seek-bar">
              <div class="jp-play-bar"></div>
            </div>
            % endif
          </div>

          <div class="jp-current-time" role="timer" aria-label="time">&nbsp;</div>
##          <div class="jp-duration" role="timer" aria-label="duration">&nbsp;</div>
        </div>
      </div>
      <div class="jp-details">
        <div class="jp-title" aria-label="title">&nbsp;</div>
        ${self.display_kpc(obj, kpc_value, False)}
      </div>
      <div class="jp-no-solution">
        ${_("Seda faili ei saa mängida")}
      </div>
    </div>
  </div>
<script>
$(function(){
   var jp = $("#jquery_jplayer_${obj.id}");
   jp.jPlayer({
        ready: function () {
          var au = jp.find('audio');
% if obj.pausita:
          au.attr('nopause', 'yes');
% endif
% if obj.max_kordus is not None and not c.block_correct:
          au.attr('max_play_count', ${obj.max_kordus});
% endif
% if obj.pausita and not c.block_correct:
          ## kui paus keelatud, siis peidame play nupu, et ei arvataks, et see teeb pausi
          var jpc = jp.closest('.eis-spbody').find('.jp-audio');
          jpc.find('button.jp-play').addClass('hide-on-play');
% endif
% if kpp_value:
          ## eelmisel korral jäi pooleli
          au.attr('data-current', ${kpp_value});
          au[0].currentTime = ${kpp_value};
% endif
% if kpc_value:
          ## eelmisel korral juba kuulati
          au.data('play_count', ${kpc_value});
% endif
<%

  mtypes = {'audio/mp3': 'mp3',
            'audio/mp4': 'm4a',
            'audio/mpeg': 'm4a',
            'audio/m4a': 'm4a',
            'audio/webm': 'webma',
            'audio/ogg': 'oga',
            'audio/wav': 'wav',
            'audio/x-wav': 'wav',
            }
  mtype = mtypes.get(obj.mimetype) or 'mp3'
  supplied = [mtype]
  muud = []
  for obj2 in obj.muudformaadid:
      mtype2 = mtypes.get(obj2.mimetype)
      if mtype2:
          muud.append((obj2, mtype2))
          supplied.append(mtype2)
  is_over = obj.max_kordus is not None and kpc_value and \
     (kpp_value and kpc_value > obj.max_kordus or (not kpp_value) and kpc_value == obj.max_kordus) and \
     not c.block_correct and not c.read_only
%>
          $(this).jPlayer("setMedia", {
             ${mtype}: "${o_url}"
% for obj2, mtype2 in muud:
             ,${mtype2}: "${obj2.get_tran_url(c.lang, c.url_no_sp)}"
% endfor
          })
% if obj.autostart and not is_over:
          .jPlayer("play")
% endif
          ;
% if is_over:
          set_media_over(au);
% endif
        },
        preload: "auto",
        solution: "html",
        cssSelectorAncestor: "#jp_container_${obj.id}",
        swfPath: "/jPlayer-2.9.2/jplayer",
        supplied: "${','.join(supplied)}",
        autoBlur: false,
        smoothPlayBar: true,
        keyEnabled: true,
        remainingDuration: false,
        toggleDuration: false
   });
   % if obj.isekorduv:
	  jp.jPlayer("play");
   % endif
   % if (obj.max_kordus is not None or obj.pausita) and not c.block_correct:
    ## kui max kuulamiste arv on antud, siis ei lasta lahendajal kerida
    jp.find('.jp-progress').unbind('click');
   % endif
   resized();
});
</script>
</%def>

<%def name="play_mp4(obj, tran, o_url, kpc_value, kpp_value)">
  <div id="jp_container_${obj.id}" class="jp-video" role="application" 
       aria-label="media player">
    <div class="jp-type-single d-flex flex-wrap justify-content-center">
      <div id="jquery_jplayer_${obj.id}" class="jp-jplayer"></div>
      <div class="jp-gui flex-grow-1">
        <div class="jp-video-play">
          <button class="jp-video-play-icon" role="button" tabindex="0">play</button>
        </div>
        <div class="jp-interface">
          <div class="jp-progress">
            % if (obj.max_kordus or obj.pausita) and not c.block_correct:
            <div class="jp-play-bar"></div>
            % else:
            <div class="jp-seek-bar">
              <div class="jp-play-bar"></div>
            </div>
            % endif
          </div>
          <div class="jp-current-time" role="timer" aria-label="time">&nbsp;</div>
          <div class="jp-duration" role="timer" aria-label="duration">&nbsp;</div>
          <div class="jp-details">
            <div class="jp-title" aria-label="title">&nbsp;</div>
            ${self.display_kpc(obj, kpc_value, True)}
          </div>
          <div class="jp-controls-holder">
            <div class="jp-volume-controls">
              <button class="jp-mute" role="button" tabindex="0">mute</button>
              <button class="jp-volume-max" role="button" tabindex="0">max volume</button>
              <div class="jp-volume-bar">
                <div class="jp-volume-bar-value"></div>
              </div>
            </div>
            <div class="jp-controls">
              <button class="jp-play" role="button" tabindex="0">play</button>
              % if not obj.pausita or c.block_correct:
              <button class="jp-pause" role="button" tabindex="0">pause</button>
              % endif
              % if obj.max_kordus is None or c.block_correct:
              <button class="jp-stop" role="button" tabindex="0">stop</button>
              % endif              
            </div>
% if False:
            <div class="jp-toggles">
              <button class="jp-repeat" role="button" tabindex="0">repeat</button>
              <button class="jp-full-screen" role="button" tabindex="0">full screen</button>
            </div>
% endif
          </div>
        </div>
      </div>

      <div class="jp-no-solution">
        ${_("Seda faili ei saa mängida")}
      </div>
    </div>
  </div>
<script>
$(function(){
   var jp = $("#jquery_jplayer_${obj.id}");
   jp.jPlayer({
        ready: function () {
          var au = jp.find('video');
% if obj.pausita:
          au.attr('nopause', 'yes');
% endif
% if obj.max_kordus is not None and not c.block_correct and not c.read_only:
          au.attr('max_play_count', ${obj.max_kordus});
% endif
% if obj.pausita and not c.block_correct:
          ## kui paus keelatud, siis peidame play nupu, et ei arvataks, et see teeb pausi
          var jpc = jp.closest('.eis-spbody').find('.jp-video');
          jpc.find('button.jp-play').addClass('hide-on-play');
% endif
  % if kpp_value:
          ## eelmisel korral jäi pooleli
          au.attr('data-current', ${kpp_value});
          au[0].currentTime = ${kpp_value};
  % endif
  % if kpc_value:
          ## eelmisel korral juba kuulati
          au.data('play_count', ${kpc_value});
  % endif


<%
  mtypes = {'video/mp4': 'm4v',
            'video/mpeg': 'm4v',
            'video/m4v': 'm4v',
            'video/webm': 'webmv',
            'video/ogg': 'ogv',
            }
  mtype = mtypes.get(obj.mimetype) or 'm4v'
  supplied = [mtype]
  muud = []
  for obj2 in obj.muudformaadid:
     mtype2 = mtypes.get(obj2.mimetype)
     if mtype2:
        muud.append((obj2, mtype2))
        supplied.append(mtype2)
  is_over = obj.max_kordus is not None and kpc_value and \
     (kpp_value and kpc_value > obj.max_kordus or (not kpp_value) and kpc_value == obj.max_kordus) and \
     not c.block_correct and not c.read_only
%>
          $(this).jPlayer("setMedia", {
            ${mtype}: "${o_url}"
% for obj2, mtype2 in muud:
            ,${mtype2}: "${obj2.get_tran_url(c.lang, c.url_no_sp)}"
% endfor
          })
  % if obj.autostart and not is_over:
          .jPlayer("play")
  % endif
          ;
% if is_over:
          set_media_over(jp);
% endif
        },
        preload: "auto",
        solution: "html",
        cssSelectorAncestor: "#jp_container_${obj.id}",
        swfPath: "/jPlayer-2.9.2/jplayer",
        supplied: "${','.join(supplied)}",
        autoBlur: false,
        smoothPlayBar: true,
        keyEnabled: true,
<%
  # vaikimisi suurus on 480x270
  # jPlayeri nupuriba laius on alati 480
  dims = []
  if obj.laius:
     dims.append('width:%s' % obj.laius)
  if obj.korgus:
     dims.append('height:%s' % obj.korgus)
%>
% if dims:
        size: {${','.join(dims)}},
% endif
        remainingDuration: true,
        toggleDuration: true
      });
   % if obj.laius and obj.laius > 480:
      ## teeme nupurea sama laiaks kui video
      $('#jp_container_${obj.id}.jp-video').width(${obj.laius});
   % endif
   % if obj.isekorduv:
	  jp.jPlayer("play");
   % endif

   % if (obj.max_kordus is not None or obj.pausita) and not c.block_correct and not c.read_only:
    ## kui max kuulamiste arv on antud, siis ei lasta lahendajal kerida
    jp.unbind('click');
    jp.find('video')
      .on('contextmenu', function(){return false;})
      .on('selectstart', function(){return false;})
      .on('dragstart', function(){return false;});
   % endif
   resized();
});
</script>
</%def>

<%def name="play_video(obj, tran, o_url, kpc_value, kpp_value)">
<div style="{h.width(obj, True)}">
  <video ${h.width(obj)} ${h.height(obj)} title="${tran.tiitel}" id="bmvideo${obj.id}"
% if obj.autostart:
       autoplay
% endif
% if obj.isekorduv:
       loop
% endif
% if not c.block_correct and not c.read_only:
       ${obj.pausita and 'nopause="yes"' or ''}
       ${obj.max_kordus and 'max_play_count="%d"' % obj.max_kordus or ''}
% endif
       oncontextmenu="return false" onselectstart="return false" ondragstart="return false" controls controlsList="nodownload">
    <source src="${o_url}" type="${obj.mimetype}">
    % for obj2 in obj.muudformaadid:
    <source src="${obj2.get_tran_url(c.lang, c.url_no_sp)}" type="${obj2.mimetype}">
    % endfor
    
  </video>
  ${self.display_kpc(obj, kpc_value, True)}
<%
  is_over = obj.max_kordus is not None and kpc_value and \
     (kpp_value and kpc_value > obj.max_kordus or (not kpp_value) and kpc_value == obj.max_kordus) and \
     not c.block_correct and not c.read_only
%>
  % if is_over:
  <script>
    set_media_over($('video#bmvideo${obj.id}'));
  </script>
  % elif kpp_value or kpc_value:
    ## eelmisel korral jäi pooleli
  <script>
    $(function(){
    var au = $('video#bmvideo${obj.id}');
    % if kpp_value:
    au.attr('data-current', ${kpp_value});
    au[0].currentTime = ${kpp_value};
    % endif
    % if kpc_value:
    au.data('play_count', ${kpc_value});
    % endif
    });
  </script>
  % endif
</div>
<br/>
</%def>

<%def name="play_audio(obj, tran, o_url, kpc_value, kpp_value)">
% if obj.nocontrols:
<div class="audio-nocontrols">
% endif
<audio ${h.width(obj)} ${h.height(obj)} id="audio_${obj.id}" controlslist="nodownload noplaybackrate"
       ${tran.tiitel and 'title="%s"' % tran.tiitel or ''}
       % if not c.block_correct and not c.read_only:
       ${obj.pausita and 'nopause="yes"' or ''}
       ${obj.max_kordus and 'max_play_count="%d"' % obj.max_kordus or ''}
       % endif
       ${obj.autostart and 'autoplay' or ''} ${obj.isekorduv and 'loop' or ''} ${not obj.nocontrols and 'controls' or ''}>
  <source src="${o_url}" type="${obj.mimetype}">
  % for obj2 in obj.muudformaadid:
  <source src="${obj2.get_tran_url(c.lang, c.url_no_sp)}" type="${obj2.mimetype}">
  % endfor  
</audio>
${self.display_kpc(obj, kpc_value, False)}
% if obj.nocontrols:
</div>
% endif
<%
  is_over = obj.max_kordus is not None and kpc_value and \
     (kpp_value and kpc_value > obj.max_kordus or (not kpp_value) and kpc_value == obj.max_kordus) and \
     not c.block_correct and not c.read_only
%>
  % if is_over:
    ## lubatud kuulamiste arv on juba ära kuulatud
  <script>
    set_media_over($('audio#bmaudio${obj.id}'));
  </script>
  % elif kpp_value or kpc_value:
    ## eelmisel korral jäi pooleli
  <script>
    $(function(){
    var au = $('audio#audio_${obj.id}');
    % if kpp_value:
    au.attr('data-current', ${kpp_value});
    au[0].currentTime = ${kpp_value};
    % endif
    % if kpc_value:
    au.data('play_count', ${kpc_value});
    % endif
    });
  </script>
  % endif
</%def>

<%def name="play_media_swf(obj, tran, o_url, kpc_value, kpp_value)">
<object ${h.width(obj)} ${h.height(obj)} title="${tran.tiitel}" type="application/x-shockwave-flash">
  <param name="allowfullscreen" value="false"></param>
  <param name="allowscriptaccess" value="never"></param>
  <param name="flashvars" value="file=${o_url}"></param>
  <param name="allowFullScreen" value="true"></param>
  <p>Sorry but your browser doesn't support HTML5 video.</p>    
</object>
${self.display_kpc(obj, kpc_value, True)}
</%def>

<%def name="play_media(obj, tran, o_url, kpc_value, kpp_value)">
% if h.is_msie():
## IE
<object ${h.width(obj)} ${h.height(obj)} title="${tran.tiitel}">
  <param name="movie" value="${o_url}"></param>
  <param name="allowFullScreen" value="true"></param>
  <embed src="${o_url}"
     type="${obj.mimetype}" 
     autostart="${obj.autostart and 'true' or 'false'}"
     loop="${obj.isekorduv and 'true' or 'false'}"
  % if obj.nahtamatu:
     hidden="true"
 % endif
     allowscriptaccess="never" 
     allowfullscreen="true" 
     ${h.width(obj)} ${h.height(obj)}>
  </embed>
</object>

    % else:
## mozilla

<object ${h.width(obj)} ${h.height(obj)} data="${o_url}" title="${tran.tiitel}">
  <param name="url" value="${o_url}"></param>
  <param name="movie" value="${o_url}"></param>
  <param name="allowFullScreen" value="true"></param>
  <embed src="${o_url}"
     type="${obj.mimetype}" 
     autostart="${obj.autostart and 'true' or 'false'}"
     loop="${obj.isekorduv and 'true' or 'false'}"
 % if obj.nahtamatu:
     hidden="true"
 % endif
     allowscriptaccess="never" 
     allowfullscreen="true" 
     ${h.width(obj)} ${h.height(obj)}>
  </embed>
</object>
   % endif

${self.display_kpc(obj, kpc_value, True)}
</%def>

