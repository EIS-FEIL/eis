## -*- coding: utf-8 -*- 
## Pildiobjektide haldus
<%namespace name="graphutils" file="graphutils.mako"/>
<%def name="edit_drag_images(item, bkysimus2)">
<div class="border p-3 m-2">
  <%
    c.THUMB_HEIGHT = 120    
    piltobjektid = list(item.piltobjektid)
    piltvalikud = {v.kood: v for v in bkysimus2.valikud}
  %>
  <h3>${_("Lohistatavad pildid")}</h3>
  % if c.is_edit:
  <div class="dropzone dropzone-add">  </div>
  % endif
  <div class="previews" counter="${len(piltobjektid)}">
    % for obj_ind, obj in enumerate(piltobjektid):
    <%
      prefix = 'mod-%d' % obj_ind
      valik = obj.kood and piltvalikud.get(obj.kood) or None
    %>
    <div style="display:inline-block" class="file-row-group" id="replace_${obj.id}">
      ${self.file_row(obj, prefix, valik)}
    </div>
    % endfor
  </div>
  ${graphutils.edit_drag_images_pos(item)}
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
<%
  prefix = 'xmod-new'
  obj = c.new_item(max_vastus=1)
%>
${self.file_row(obj, prefix, None)}
</%def>

<%def name="file_row(obj, prefix, valik)">
<%
  tr_obj = c.lang and obj.tran(c.lang) or obj
%>
<div style="display:inline-block" class="file-row form">
  <div class="float-left bg-gray-50">
    <div class="table form" style="padding:10px">
      <div class="table-row row">
        <div style="width:70px">${_("Jrk")}</div>
        <div>
          ${h.posint5('%s.seq' % (prefix), obj.seq, class_="obj-seq")}
          ${h.hidden(prefix + '.id', obj.id, class_="obj-id")}
        </div>
      </div>
      <div class="table-row row">
        <div>ID</div>
        <div>${h.text('%s.kood' % (prefix), obj.kood, class_="obj-kood", size=5)}</div>
      </div>
      <div class="table-row row">
        <div>${_("Arv")}</div>
        <div>
          ${h.int5('%s.max_vastus' % (prefix), obj.max_vastus)}
          <br/>
          ${h.checkbox('%s.eraldi' % (prefix), 1, checked=obj.eraldi, label=_("Kuva eraldi"))}
        </div>
      </div>
      <div class="table-row row">
        <div>${_("Laius")}</div>
        <div>${h.posint5(prefix + '.laius', tr_obj.laius, class_="width",
          ronly=not c.is_edit and not c.is_tr)}</div>
      </div>
      <div class="table-row row">
        <div>${_("Kõrgus")}</div>
        <div>${h.posint5(prefix + '.korgus', tr_obj.korgus, class_="height",
          ronly=not c.is_edit and not c.is_tr)}
        </div>
      </div>
      <div class="table-row row">
        <div>${_("Selgitus")}</div>
        <div>
           ${h.text(prefix + '.selgitus', valik and valik.selgitus, maxlength=90, class_="desc",
          ronly=not c.is_edit)}
        </div>
      </div>
    </div>
    % if tr_obj.fileext.lower() != 'svg':
    % if tr_obj.laius and tr_obj.laius_orig and tr_obj.laius_orig > 4 * tr_obj.laius or \
    tr_obj.korgus and tr_obj.korgus_orig and tr_obj.korgus_orig > 4 * tr_obj.korgus:
    <div class="error" style="width:200px;margin:5px;">
      ${_("Pildi tegelik mõõt on väga palju suurem kuvamise mõõdust. Soovitatav on pildifail teisendada väiksemasse mõõtu ning laadida väiksema mahuga pildifail.")}
    </div>
    % endif
    % endif
  </div>
  <div style="float:left" class="nocopy">
      % if obj.id:
      ${self.file_row_img(obj, tr_obj)}
      % else:
      ${self.template_row_img()}
      % endif
  </div>
</div>
</%def>

<%def name="file_row_img(obj, tr_obj)">
    <div>
      % if c.is_edit:
      <div style="float:right;padding:2px 6px 2px 2px">
        ${h.grid_s_remove('.file-row')}
      </div>
      % endif

      % if c.lang:
      ${h.lang_tag(c.lang)}
      % endif

      % if c.is_edit or c.is_tr:
      <div class="dropzone dropzone-upd" 
           action="${h.url('ylesanne_update_piltobjekt', ylesanne_id=c.ylesanne.id, sisuplokk_id=c.block.id, id=obj.id, lang=c.lang, is_tr=c.is_tr)}"
           style="padding:3px 20px 3px 20px"
           previews="#replace_${obj.id}">
      % else:
      <div>
      % endif
      <% img_attr = {'data-width': tr_obj.laius, 'data-height': tr_obj.korgus} %>  
      ${h.image(obj.get_url(c.lang, c.url_no_sp), _("Pilt"),
      height=min(c.THUMB_HEIGHT, tr_obj.korgus or obj.korgus),
      title=obj.kood, class_="file-img fancybox", **img_attr)}
      <br/>
      <a href="${obj.get_url(c.lang, c.url_no_sp)}">${obj.filename}</a>
      <br/>
      <span class="size" style="padding-left:10px">${h.filesize(tr_obj.filesize)}</span>
      % if tr_obj.laius_orig and tr_obj.korgus_orig:
      <br/>
      <span style="padding-left:10px">
        <span class="o-width">${tr_obj.laius_orig}</span> &times; <span class="o-height">${tr_obj.korgus_orig}</span>
      </span>
      % endif
     </div>
    </div>
</%def>

<%def name="template_row_img()">
    <div style="padding-left:10px;text-align:center;">
      % if c.is_edit:
      <div style="float:right;padding:2px 6px 2px 2px">
        ${h.grid_s_remove('.file-row')}
      </div>
      % endif
      <div style="float:left">
      % if c.lang:
      ${h.lang_tag(c.lang)}
      % endif
      <div class="preview"><img data-dz-thumbnail class="file-img fancybox"/></div>
      <span class="name" data-dz-name></span>
      <div class="size" style="padding-left:10px" data-dz-size>  </div>
      <div style="padding-left:10px;display:none;" class="dimens">
        <span class="width o-width"></span> &times; <span class="height o-height"></span>
      </div>
      <div><strong class="error text-danger" data-dz-errormessage></strong></div>
      <div class="progress progress-striped active" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">
        <div class="progress-bar progress-bar-success" style="width:0%;" data-dz-uploadprogress></div>
      </div>
      </div>
    </div>
</%def>

<%def name="js_dropzone()">
$(function(){
% if c.is_edit:
## uute piltide lisamine
   $('div.dropzone-add').dropzone(
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
              el.find(':input[name^="xmod-new"]').each(function(){
                 var name = $(this).attr('name');
                 $(this).attr('name', name.replace('xmod-new', 'mod-'+cnt));
              });
              ##preview_img_size(file.previewElement);
           });
        },
        success: function(file, response){
          ## peale edukat salvestamist
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
              el.find('.obj-seq').val(response.seq);
              el.find('span.name').text(response.filename);
              el.find('.obj-kood').val(response.kood);
              if(el.find('.desc').val()=='')
              {
                 el.find('.desc').val(response.selgitus);
              }
              if(response.width && response.height)
              {
                 ## kuvame mõõdud
                 el.find('.dimens span.width').text(response.width);
                 el.find('.dimens span.height').text(response.height);
                 el.find('.dimens').show();
                 el.find('input.width').val(response.width);
                 el.find('input.height').val(response.height);
              }
              var fba = wrap_fancybox(el.find('img.fancybox'), response.href);
              init_fancybox_wrapper(fba);
          }
       }
   });
% endif

% if c.is_edit or c.is_tr:
### olemasolevate piltide asendamine või tõlkimine

 $('div.dropzone.dropzone-upd').each(function(){
   var action = $(this).attr('action');
   var previews = $(this).attr('previews');
   var oldimg = $(this).find('img');
   $(this).dropzone(
       {url: action,
        dictDefaultMessage: "",
        thumbnailHeight: ${c.THUMB_HEIGHT},
        thumbnailWidth: null,
        ##thumbnailHeight: oldimg.attr('height') || null,
        ##thumbnailWidth:oldimg.attr('width') || null,
        ##maxFiles: 1,
        acceptedFiles: ".png,.jpg,.gif,.jpeg,.svg",
        previewsContainer: previews,
        previewTemplate: $('.file-template')[0].innerHTML,
        init: function(){
           this.on('addedfile', function(file){
              ## eemaldame senise faili
              var el = $(file.previewElement);
              var rm = el.closest('.file-row-group').children().filter(':not(:last)');
              var rmlast = rm.last();
              if(rmlast)
              {
                  ## vanad väärtused jätame meelde
                  var lastch = rmlast.children(':not(.nocopy)');
                  var elch = el.children(':not(.nocopy)');
                  for(var i=0; i<lastch.length; i++)
                  {
                     elch.eq(i).replaceWith(lastch.eq(i));
                  }
                  rm.remove();
              }
              ##preview_img_size(file.previewElement);
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
              var img = el.find('img.fancybox');
              img.attr('data-width', el.find('input.width').val());
              img.attr('data-height', el.find('input.height').val());
              var fba = wrap_fancybox(img, response.href);
              init_fancybox_wrapper(fba);
           }
     }
 });
 });
% endif
$('body').on('change', 'input.width,input.height', function(){
   var fld = this;
   var p = $(fld);                                               
   if(!p.hasClass('file-row')) p = $(fld).closest('.file-row');
   ## pildi tegelik mõõt
   var o_width = parseFloat(p.find('.o-width').text());
   var o_height = parseFloat(p.find('.o-height').text());
   ## sisestatud mõõt
   var height = parseFloat(p.find('input.height').val());
   var width = parseFloat(p.find('input.width').val());
   if($(fld).hasClass('width') && !isNaN(width))
   {
      ## muudeti laiust
      height = Math.round(o_height * width / o_width);
      p.find('input.height').val(height);
   }
   else if($(fld).hasClass('height') && !isNaN(height))
   {
      ## muudeti kõrgust
      width = Math.round(o_width * height / o_height);
      p.find('input.width').val(width);
   }
   var img = p.find('img.file-img');
   img.attr('data-width', width);
   img.attr('data-height', height);
});
});
</%def>
