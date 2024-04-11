<%def name="edit_images(item)">
<div style="float:left;width:100%">
  <%
    c.THUMB_HEIGHT = 120
    meediaobjektid = c.block.samameediaobjektid
  %>
  % if c.is_edit:
  <div class="dropzone dropzone-add"> </div>
  ${self.lisaurl()}
  % endif
  <div class="previews table" counter="${len(meediaobjektid)}">
    <% obj_ind = -1 %>
    % for obj in meediaobjektid:
    <%
      obj_ind += 1
      prefix = 'mot-%d' % obj_ind
      tr_obj = c.lang and obj.tran(c.lang) or obj
      %>
    <div class="table-row-group" id="replace_${obj.id}">
      <div class="sameobj bg-gray-50 m-2 p-2">
      ${self.file_row(obj, tr_obj, prefix)}

      % for obj2 in obj.muudformaadid:
      <div class="table-row-group" id="replace_${obj2.id}">    
      <%
        obj_ind += 1
        prefix2 = 'mot-%d' % obj_ind
        tr_obj2 = c.lang and obj2.tran(c.lang) or obj2
      %>
      ${self.file_row(obj2, tr_obj2, prefix2)}
      </div>
      % endfor
      ${self.file_row_imgdata(obj, tr_obj, prefix)}
      </div>
    </div>
    % endfor
  </div>
</div>

% if c.is_edit or c.is_tr:
<div class="file-template" style="display:none">
  ${self.fz_template_edit()}
</div>
<script>
  ${self.js_dropzone()}
</script>
% endif
</%def>

<%def name="lisaurl()">
  ${h.button(_("Lisa URLi viide"), id="b_lisaurl", level=2)}
  <div id="d_lisaurl" style="display:none">
  <div class="m-2 d-flex flex-wrap">
    <label class="mr-3">${_("URL")}:</label>
    <div class="flex-grow-1 mr-3">${h.text('url', '')}</div>
    ${h.button(_("Lisa"), id="f_lisaurl")}
  </div>
  <div id="e_lisaurl" class="error" style="display:none"></div>
  </div>
</%def>

<%def name="fz_template_edit()">
## uue faili rea mall
<div class="file-row bg-gray-50 m-2">
    <div class="p-2">
          <div style="margin:4px 0 4px 2px">
            <span class="name" data-dz-name></span>
            <span class="size" style="padding-left:10px" data-dz-size>
            </span>
            <span style="padding-left:10px;display:none;" class="dimens">
              <span class="width"></span> &times; <span class="height"></span>
            </span>
            <div style="float:right;padding:0 4px 0 4px">${h.grid_s_remove('.file-row')}</div>
          </div>
          <div class="mediainfo" style="display:none">
            <div class="d-flex flex-wrap mr-1">
              <div class="item mr-4 py-1">
                ${h.flb(_("Formaat"))}
                <div class="mi-format"></div>
              </div>
              <div class="item mr-4 py-1">
                ${h.flb(_("Kestus"))}
                <div class="mi-duration"></div>
              </div>
              <div class="item mr-4 py-1">
                ${h.flb(_("Bitikiirus"))}
                <div class="mi-bitrate"></div>
              </div>
              <div class="item mr-4 py-1">
                ${h.flb(_("Bitisügavus"))}
                <div class="mi-bitdepth"></div>
              </div>
            </div>
          </div>

          <strong class="error text-danger" data-dz-errormessage></strong>
          
          
          <div class="progress progress-striped active" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">
            <div class="progress-bar progress-bar-success" style="width:0%;" data-dz-uploadprogress></div>
          </div>
    </div>
   <%
     prefix = 'xmot-new'
     ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') 
     obj = tr_obj = c.new_item()
    %>
    <div class="row fz-fileurl invisible">
        ${ch.flb(_("URL"))}
        <div class="col-md-9 col-xl-10">
          ${h.text(prefix + '.fileurl', '', class_="fileurl", maxlength=200)}
        </div>
    </div>
    ${h.hidden(prefix + '.id', obj.id, class_="obj-id")}
    ${self.file_row_imgdata(obj, tr_obj, prefix)}          
</div>
</%def>

<%def name="file_row(obj, tr_obj, prefix)">      
## andmebaasis olemas oleva faili kuvamine
<%
  ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') 
%>
<div class="file-row bg-gray-50 m-2">
  <div class="d-flex">
      <div style="width:200px;text-align:center;">
          % if c.lang:
          ${h.lang_tag(c.lang)}
          % endif
          % if (c.is_edit or c.is_tr) and not obj.fileurl:
          <div class="dropzone dropzone-upd" 
               action="${h.url('ylesanne_update_piltobjekt', ylesanne_id=c.ylesanne.id, sisuplokk_id=c.block.id, id=obj.id, lang=c.lang, is_tr=c.is_tr)}"
               previews="#replace_${obj.id}">
          </div>
          % else:
          <div></div>
          % endif
      </div>

      <div class="flex-grow-1">
        <div class="m-2">
          % if obj.has_file:
          <a href="${obj.get_url(c.lang, c.url_no_sp)}">images/<span class="name">${obj.filename}</span></a>             
          
          <span class="size" style="padding-left:10px">${h.filesize(tr_obj.filesize)}</span>
          % if tr_obj.laius_orig and tr_obj.korgus_orig:
          <span style="padding-left:10px">
            ${tr_obj.laius_orig} &times; ${tr_obj.korgus_orig}
          </span>
          % endif
          % endif

          % if c.is_edit:
          <div style="float:right;padding:0 4px 0 4px">
            ${h.grid_s_remove('.table-row-group')}
          </div>
          % endif
          <% info = obj.get_mediainfo() %>
          % if info:
          <div class="mediainfo">
            <div class="d-flex flex-wrap mr-1">          
              <div class="item mr-4 py-1">
                ${h.flb(_("Formaat"))}
                <div class="mi-format">${info.get('format')}</div>
              </div>
              <div class="item mr-4 py-1">
                ${h.flb(_("Kestus"))}
                <div class="mi-duration">${info.get('duration')}</div>
              </div>
              <div class="item mr-4 py-1">
                ${h.flb(_("Bitikiirus"))}
                <div class="mi-bitrate">${info.get('bit_rate')}</div>
              </div>
              <div class="item mr-4 py-1">
                ${h.flb(_("Bitisügavus"))}
                <div class="mi-bitdepth">${info.get('bit_depth')}</div>
              </div>
            </div>
          </div>
          % endif
        </div>
      </div>

  </div>
  <div>    
    % if obj.has_file:
    <div class="mb-1">
        <% name = prefix + '.filedata' %>
        <label class="font-weight-bold px-2">${_("Fail")}</label>
        <div class="d-inline-block">
    <%
         files = []
         url = h.url('ylesanne_sisufail', id='%s.%s' % (obj.id, obj.fileext))
         files.append((url, obj.filename, obj.filesize))
         if c.lang and tr_obj and tr_obj.has_file:
            url = h.url('ylesanne_sisufail', id='%s.%s' % (obj.id, tr_obj.fileext),lang=c.lang)
            files.append((url, c.lang, tr_obj.filesize))      
    %>
         ${h.file(name, value=_("Fail"), files=files)}
        </div>
    </div>
    % else:
    <div class="mb-1">
        <% name = prefix + '.fileurl' %>
        <label class="font-weight-bold px-2">${_("URL")}</label>
        <div class="d-inline-block">
          % if c.lang:
          ${h.lang_orig(obj.fileurl)}<br/>
          ${h.lang_tag()}
          ${h.text(name, tr_obj.fileurl, maxlength=200, ronly=not c.is_tr)}
          % else:
          ${h.text(name, tr_obj.fileurl, maxlength=200, ronly=not c.is_tr and not c.is_edit)}
          % endif
        </div>
    </div>
    % endif
  </div>
    ${h.hidden(prefix + '.id', obj.id, class_="obj-id")}
</div>
</%def>

<%def name="file_row_imgdata(obj, tr_obj, prefix)">        
<% ch = h.colHelper('col-md-3 col-xl-2 text-md-right', 'col-md-3 col-xl-4') %>
<div style="${not c.item.staatus and 'display:none' or ''}" class="imgdata mt-2">
  <div class="mx-2">${_("Seaded sisuplokina kuvamisel")}</div>
  <div class="row">
    <% name = prefix + '.tiitel' %>
    ${ch.flb(_("Soovituslik pealkiri"), name)}
    <div class="col-md-9 col-xl-10">
      ${h.text(name, obj.tiitel)}
    </div>
  </div>
  <div class="row mb-1">
    <% name = prefix + '.mimetype' %>
    ${ch.flb(_("Liik"), name)}
    <div class="col-md-3 col-xl-2">
      ${h.select(name, obj.mimetype,  c.opt.mimetype_media_empty)}
    </div>
    
    <% name = prefix + '.player' %>
    ${ch.flb(_("Mängija"), name)}
    <div class="col-md-3 col-xl-2">
      ${h.radio(name, model.Meediaobjekt.PLAYER_JPLAYER, checked=not obj.player, label='jPlayer')}
      ${h.radio(name, model.Meediaobjekt.PLAYER_HTML5, checked=obj.player, label=_("brauser"))}
    </div>
    
    <% playercls = 'player jplayer-audio jplayer-video video audio plmedia' %>
    <% name = prefix + '.autostart' %>
    ${ch.flb(_("Autostart"), name, colextra=playercls)}
    <div class="col-md-3 col-xl-2 ${playercls}">
      ${h.checkbox(name, True, checked=obj.autostart)}
    </div>
    
    <% playercls = 'player youtube jplayer-video video plmedia' %>
    <% name = prefix + '.laius' %>
    ${ch.flb(_("Laius"), name, colextra=playercls)}
    <div class="col-md-3 col-xl-2 ${playercls}">
      ${h.posint5(name, obj.laius, maxvalue=900)}
    </div>
    <% name = prefix + '.korgus' %>
    ${ch.flb(_("Kõrgus"), name, colextra=playercls)}
    <div class="col-md-3 col-xl-2 ${playercls}">
      ${h.posint5(name, obj.korgus)}
    </div>
    
    <% playercls = 'player jplayer-video video audio plmedia' %>
    <% name = prefix + '.isekorduv' %>
    ${ch.flb(_("Tsükkel"), name, colextra=playercls)}
    <div class="col-md-3 col-xl-2 ${playercls}">
      ${h.checkbox(name + '.isekorduv', True, checked=obj.isekorduv)}
    </div>
    
    <% playercls = 'player audio' %>
    <% name = prefix + '.nocontrols' %>
    ${ch.flb(_("Ainult mängimise nupp"), name, colextra=playercls)}
    <div class="col-md-3 col-xl-2 ${playercls}">
      ${h.checkbox(name, True, checked=obj.nocontrols)}
    </div>
    
    <% playercls = 'player plmedia audio jplayer-audio jplayer-video' %>
    <% name = prefix + '.max_kordus' %>
    ${ch.flb(_("Max kuulamiste arv"), name, colextra=playercls)}
    <div class="col-md-3 col-xl-2 ${playercls}">
      ${h.int5(name, obj.max_kordus)}
    </div>

    <% playercls = 'player plmedia audio jplayer-audio jplayer-video' %>
    <% name = prefix + '.pausita' %>
    ${ch.flb(_("Pausi keelamine"), name, colextra=playercls)}
    <div class="col-md-3 col-xl-2 ${playercls}">
      ${h.checkbox(name, True, checked=obj.pausita)}
    </div>

    <% playercls = 'player plmedia audio jplayer-audio jplayer-video' %>
    <% name = prefix + '.kpc_kood' %>
    <% kpc = obj.id and obj.get_kysimus(const.OBJSEQ_COUNTER) %>
    ${ch.flb(_("Kuulamiste arvu loendur"), name, colextra=playercls)}
    <div class="col-md-3 col-xl-2 ${playercls}">
      ${h.text(name, kpc and kpc.kood or '', size=10, class_="identifier")}
    </div>
  </div>
  
</div>
</%def>

<%def name="js_dropzone()">
$(function(){
% if c.is_edit:
   var action = "${h.url('ylesanne_create_piltobjektid', ylesanne_id=c.ylesanne.id, sisuplokk_id=c.block.id)}",
       previewTemplate = $('.file-template')[0].innerHTML,
## uute piltide lisamine
       onaddedfile = function(el){
              ## asendame prefiksid
              var previews = el.closest('.previews');
              var cnt = previews.attr('counter');
              previews.attr('counter', cnt+1);
              el.find(':input[name^="xmot-new"]').each(function(){
                 var name = $(this).attr('name');
                 $(this).attr('name', name.replace('xmot-new', 'mot-'+cnt));
              });
              ## "Seaded sisuplokina kuvamisel" kuvada ainult siis, kui on märge "Pilt kuvatakse"
              el.find('.imgdata').toggle($('input#staatus').prop('checked'));

       },
       onsuccess = function(el, response) {
          el.find('.progress').hide();
          if(response.error)
          {
              el.find('.error').text(response.error); 
          }
          else
          {
              ## jätame meelde lisatud kirje ID
              el.find('.obj-id').val(response.obj_id);
              el.find('span.name').text(response.filename);
              if(response.fileurl)
              {
                 el.find('input.fileurl').val(response.fileurl);
                 el.find('.fz-fileurl').removeClass('invisible');
              }
              el.find('.obj-kood').val(response.kood);
              if(response.width && response.height)
              {
                 ## kuvame mõõdud
                 el.find('.dimens span.width').text(response.width);
                 el.find('.dimens span.height').text(response.height);
                 el.find('.dimens').show();
                 el.find('input.width').val(response.width);
                 el.find('input.height').val(response.height);
              }
              if(response.mediainfo)
              {
                 var info = response.mediainfo;
                 el.find('.mediainfo').show();
                 el.find('.mediainfo .mi-format').text(info.format);
                 el.find('.mediainfo .mi-duration').text(info.duration);
                 el.find('.mediainfo .mi-bitrate').text(info.bit_rate);
                 el.find('.mediainfo .mi-bitdepth').text(info.bit_depth);
              }
           }
       };

  ## kuvada URLi sisestamise väli uue elemendi lisamiseks URLiga
  $('#b_lisaurl').click(function(){
         $('#d_lisaurl').show();
         $('#b_lisaurl').hide();
  });
  ## lisada uus elementi URLiga andmebaasi
  $('#f_lisaurl').click(function(){
         var url = $('#url').val();
         $.ajax({type:'post',
              url: action,
              data: {url: url},
              success:function(data){
              if(data.error) {
                   $('#e_lisaurl').text(data.error).show();
              } else {

                   var el = $(previewTemplate);
                   $('.previews').append(el);
                   console.log('previews='+$('.previews').length);
                   onaddedfile(el);
                   onsuccess(el, data);
                   $('#e_lisaurl').hide();
              }
              }});
   });

$('div.dropzone.dropzone-add').dropzone(
        {url: action,
        dictDefaultMessage: "${_("Failide lisamiseks lohista need siia või kliki siin")}",
        thumbnailHeight: ${c.THUMB_HEIGHT},
        thumbnailWidth:null,
        parallelUploads: 1,
        acceptedFiles: ".mp3,.mp4,.mpeg,.webm",
        previewsContainer: ".previews",
        previewTemplate: previewTemplate,
        fallback: function(){
          $(this.element).removeClass('dropzone').siblings('span.filebtn').show();
          var t = $('<span>See brauser ei võimalda lohistatud faile vastu võtta, soovitame kasutada paremat brauserit!</span>');
          return this.element.appendChild(t[0]);
        },
        init: function(){
           this.on('addedfile', function(file){
              var el = $(file.previewElement);
              onaddedfile(el);
           });
        },
        success: function(file, response){
          var el = $(file.previewElement);
          onsuccess(el, response);
        }
   });
% endif

% if c.is_edit or c.is_tr:
### olemasolevate piltide asendamine või tõlkimine
 $('div.dropzone.dropzone-upd').each(function(){
   var action = $(this).attr('action');
   var previews = $(this).attr('previews');
   $(this).dropzone(
        {url: action,
        dictDefaultMessage: "",
        thumbnailHeight: ${c.THUMB_HEIGHT},
        thumbnailWidth:null,
        acceptedFiles: ".mp3,.mp4,.mpeg,.webm",
        previewsContainer: previews,
        previewTemplate: $('.file-template')[0].innerHTML,
        init: function(){
           this.on('addedfile', function(file){
              ## eemaldame senise faili
              var el = $(file.previewElement);
              var rm = el.closest('.table-row-group').children().filter(':not(:last)');
              var rmlast = rm.last();
              if(rmlast)
              {
                  ## vanad väärtused jätame meelde
                  el.find('table.imgdata').replaceWith(rmlast.find('table.imgdata'));
                  el.find('input.obj-id').replaceWith(rmlast.find('input.obj-id'));
                  ## pildi muutmisel ei muutu pildi nimi
                  el.find('span.name').text(rmlast.find('span.name').text());
                  rm.remove();
              }
              ## "Seaded sisuplokina kuvamisel" kuvada ainult siis, kui on märge "Pilt kuvatakse"
              el.find('.imgdata').toggle($('input#staatus').prop('checked'));
           });
        },
        success: function(file, response){
          var el = $(file.previewElement);
          el.find('.progress').hide();
          if(response.error)
          {
              el.find('.error').text(response.error); 
          }
          else
          {
              if(response.width && response.height)
              {
                 ## kuvame mõõdud
                 el.find('.dimens span.width').text(response.width);
                 el.find('.dimens span.height').text(response.height);
                 el.find('.dimens').show();
              }
          }
        }
 });
 });
% endif

## "Seaded sisuplokina kuvamisel" kuvada ainult siis, kui on märge "Pilt kuvatakse"
$('input#staatus').change(function(){
  $('.imgdata').toggle($('input#staatus').prop('checked'));
});
});
</%def>
