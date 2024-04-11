## -*- coding: utf-8 -*- 
<%def name="edit_images(item)">
<div style="float:left;width:100%">
  <%
    c.THUMB_HEIGHT = 120
    piltobjektid = list(c.block.piltobjektid)
  %>
  % if c.is_edit:
  <div class="dropzone dropzone-add"> </div>
  % endif
  <div class="previews table" counter="${len(piltobjektid)}">
    % for obj_ind, obj in enumerate(piltobjektid):
    <%
      prefix = 'moi-%d' % obj_ind
    %> 
    <div class="table-row-group" id="replace_${obj.id}">
      ${self.file_row(obj, prefix)}
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

<%def name="fz_template_edit()">
## uue faili rea mall
    <div class="file-row table-row bg-gray-50 m-2">
        <div style="width:200px;text-align:center;">
          % if c.lang:
          ${h.lang_tag()}
          % endif
          <span class="preview"><img data-dz-thumbnail /></span>
        </div>
        <div>
          <div style="margin:4px 0 4px 2px">
            images/<span class="name" data-dz-name></span>
            <span class="size" style="padding-left:10px" data-dz-size>
            </span>

            <span style="padding-left:10px;display:none;" class="dimens">
              <span class="width"></span> &times; <span class="height"></span>
            </span>
            <div style="float:right;padding:0 4px 0 4px">${h.grid_s_remove('.file-row')}</div>
          </div>
          <strong class="error text-danger" data-dz-errormessage></strong>
          
          
          <div class="progress progress-striped active" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">
            <div class="progress-bar progress-bar-success" style="width:0%;" data-dz-uploadprogress></div>
          </div>
          <%
            prefix = 'xmoi-new'
            obj = tr_obj = c.new_item()
          %>
          ${self.file_row_imgdata(obj, tr_obj, prefix)}          
        </div>   
    </div>
</%def>

<%def name="file_row(obj, prefix)">      
## andmebaasis olemas oleva faili kuvamine
<%
  tr_obj = c.lang and obj.tran(c.lang) or obj
  ##tolkimata = c.lang and tr_obj == obj
%>
  <div class="file-row table-row bg-gray-50 m-2">
      <div style="width:200px;text-align:center;">
          % if c.lang:
          ${h.lang_tag(c.lang)}
          % endif
          % if c.is_edit or c.is_tr:
          <div class="dropzone dropzone-upd" 
               action="${h.url('ylesanne_update_piltobjekt', ylesanne_id=c.ylesanne.id, sisuplokk_id=c.block.id, id=obj.id, lang=c.lang, is_tr=c.is_tr)}"
               previews="#replace_${obj.id}">
          % else:
          <div>
          % endif
          ${h.image(obj.get_url(c.lang, c.url_no_sp),
          ##_("Pilt"),  width=tr_obj.laius or None,  height=tr_obj.korgus or None,
          _("Pilt"),  height=min(c.THUMB_HEIGHT, tr_obj.korgus or obj.korgus),
          title=tr_obj.tiitel)}
          </div>
      </div>
      <div>
        <div class="m-2">
          <a href="${obj.get_url(c.lang, c.url_no_sp)}">images/<span class="name">${obj.filename}</span></a>             
          
          <span class="size" style="padding-left:10px">${h.filesize(tr_obj.filesize)}</span>
          % if tr_obj.laius_orig and tr_obj.korgus_orig:
          <span style="padding-left:10px">
            ${tr_obj.laius_orig} &times; ${tr_obj.korgus_orig}
          </span>
          % endif
          % if c.is_edit:
          <div style="float:right;padding:0 4px 0 4px">
            ${h.grid_s_remove('.file-row')}
          </div>
          % endif
        </div>
        ${self.file_row_imgdata(obj, tr_obj, prefix)}
      </div>
   </div>
</%def>

<%def name="file_row_imgdata(obj, tr_obj, prefix)">        
        <table style="margin:1px;${not c.item.staatus and 'display:none' or ''}" width="100%" class="imgdata">
          <tr>
            <td colspan="2">
              ${_("Seaded sisuplokina kuvamisel")}
            </td>
          </tr>
          <col width="120"/>
          <tr>
            <td>${_("Laius")}</td>
            <td>${h.posint5(prefix + '.laius', tr_obj.laius,
              ronly=not c.is_edit and not c.is_tr)}</td>
          </tr>
          <tr>
            <td>${_("Kõrgus")}</td>
            <td>${h.posint5(prefix + '.korgus', tr_obj.korgus,
              ronly=not c.is_edit and not c.is_tr)}</td>
          </tr>
          <tr>
            <td>${_("Soovituslik pealkiri")}</td>
            <td>
              % if c.lang:
              ${h.lang_orig(obj.tiitel)}
              <div class="linebreak"></div>
              ${h.lang_tag()}
              ${h.text(prefix + '.tiitel', tr_obj.tiitel, ronly=not c.is_tr)}              
              % else:
              ${h.text(prefix + '.tiitel', tr_obj.tiitel, ronly=not c.is_edit and not c.is_tr)}
              % endif
            </td>
          </tr>
        </table>
        ${h.hidden(prefix + '.id', obj.id, class_="obj-id")}
</%def>

<%def name="js_dropzone()">
$(function(){
% if c.is_edit:
## uute piltide lisamine
   $('div.dropzone.dropzone-add').dropzone(
        {url: "${h.url('ylesanne_create_piltobjektid', ylesanne_id=c.ylesanne.id, sisuplokk_id=c.block.id)}",
        dictDefaultMessage: "${_("Failide lisamiseks lohista need siia või kliki siin")}",
        thumbnailHeight: ${c.THUMB_HEIGHT},
        thumbnailWidth:null,
        parallelUploads: 1,
        acceptedFiles: ".png,.jpg,.gif,.jpeg,.svg",
        previewsContainer: ".previews",
        previewTemplate: $('.file-template')[0].innerHTML,
        fallback: function(){
          $(this.element).removeClass('dropzone').siblings('span.filebtn').show();
          var t = $('<span>See brauser ei võimalda lohistatud faile vastu võtta, soovitame kasutada paremat brauserit!</span>');
          return this.element.appendChild(t[0]);
        },
        init: function(){
           this.on('addedfile', function(file){
              var el = $(file.previewElement);
              ## asendame prefiksid
              var previews = el.closest('.previews');
              var cnt = previews.attr('counter');
              previews.attr('counter', cnt+1);
              el.find(':input[name^="xmoi-new"]').each(function(){
                 var name = $(this).attr('name');
                 $(this).attr('name', name.replace('xmoi-new', 'moi-'+cnt));
              });
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
              ## jätame meelde lisatud kirje ID
              el.find('.obj-id').val(response.obj_id);
              el.find('span.name').text(response.filename);
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
          }
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
        ##maxFiles: 1,
        acceptedFiles: ".png,.jpg,.gif,.jpeg,.svg",
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
                 ##el.find('input.width').val(response.width);
                 ##el.find('input.height').val(response.height);
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
