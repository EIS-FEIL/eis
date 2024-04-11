## -*- coding: utf-8 -*- 
<%inherit file="baasplokk.mako"/>

<%def name="block_edit()">
<p>
${h.checkbox('f_reanr', 1, checked=c.block.reanr, label=_("Nummerda read (1,6,11,...)"))}
${h.checkbox('f_kopikeeld', 1, checked=c.block.kopikeeld, label=_("Takista teksti kopeerimist"))}
${h.checkbox('f_kommenteeritav', 1, checked=c.block.kommenteeritav, label=_("Kommenteeritav tekst"))}
${h.checkbox('f_nahtavuslogi', 1, checked=c.block.nahtavuslogi, label=_("Salvesta sisuploki kuvamised ja peitmised"))}
${h.checkbox('f_wirismath', 1, checked=c.block.wirismath, label=_("WIRIS"))}
</p>

  % if c.lang:
    ${h.literal(c.block.sisu)}
    <div class="linebreak"></div>
    ${h.lang_tag(c.lang)}
  % endif
    <%
      baseHref = c.lang and 'lang/%s/' % c.lang or None

      icons = ['MetaBlock','ToggleButton',
         'NewPage',
         'Cut','Copy',
         'Undo','Redo','Find','Replace','SelectAll','RemoveFormat',
         'Bold', 'Italic', 'Underline','mathck','Subscript','Superscript','SupSub',
         'NumberedList','BulletedList','Outdent','Indent','Blockquote','CreateDiv',
         'JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock',
         'Image','Html5audio','Table','SpecialChar','Link','Iframe',
         'Styles','Format','Font','FontSize','lineheight','TextColor','BGColor',
         'gg',
         'Maximize', 'ShowBlocks']
      if c.block.wirismath:
         icons.extend(['ckeditor_wiris_formulaEditor','ckeditor_wiris_formulaEditorChemistry'])
      if c.user.has_permission('srcedit', const.BT_UPDATE):
         icons.append('Source')
    %>
    ${h.ckeditor('f_sisu', c.block.tran(c.lang).sisu, 'meta', icons=icons, ronly=not c.is_tr and not c.is_edit, baseHref=baseHref, disain_ver=c.ylesanne.disain_ver)}
  % if not c.lang:
    <script>
      $(function(){
      $('#f_kopikeeld').change(function(){
        var keeld = $('#f_kopikeeld').prop('checked');
        if(keeld) $('#f_kommenteeritav').prop('checked',false);
        $('#f_kommenteeritav').prop('disabled', keeld);
      });
      var keeld = $('#f_kopikeeld').prop('checked');
      if(keeld) $('#f_kommenteeritav').prop('checked',false);
      $('#f_kommenteeritav').prop('disabled', keeld);
      });
    </script>
  % endif
</%def>

<%def name="block_view()">
<%
   sisu = c.block.tran(c.lang).sisuvaade or c.block.tran(c.lang).sisu
   if sisu:
      sisu = sisu.replace('{firstname}', c.sooritaja_eesnimi or '')
   cls = ""
   if c.block.kommenteeritav:
      cls += " rcommentable"
      kysimus = c.block.get_kysimus()
      # loeme alusteksti koos sooritaja varem salvestatud kommentaaridega
      if kysimus and not c.read_only:
          # kommenteeritud teksti kasutame ainult sooritamise ajal
          kv = c.responses.get(kysimus.kood)
          if kv:
             for kvs in kv.kvsisud: 
                sisu = kvs.sisu or sisu
                break
   elif c.block.kopikeeld:
      cls += " unselectable"
%>
  % if sisu:
  <div class="contents${cls} contents-${c.block.get_prefix()} speech" ${c.block.kopikeeld and 'oncopy="return false;"' or ''} lang="${c.lang}">
  ${h.literal(c.block.replace_img_url(sisu or '', lang=c.lang))}
  </div>
  % endif
  % if c.block.kommenteeritav:
    ${h.hidden(c.block_result, '')}  
  % endif
</%def>

