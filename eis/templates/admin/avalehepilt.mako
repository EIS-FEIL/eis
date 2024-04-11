<%inherit file="/common/dlgpage.mako"/>
<%include file="/common/message.mako"/>

${h.flb(_("Vali pilt"))}
<div class="row">
  % for rcd in c.items:
  <div class="col-3 p-3 text-center">
    % if rcd == c.item:
    <div class="dropzone" action="${h.url_current('update', sub='file', id=rcd.id)}">
      <button type="button" class="btn btn-link rundz">${_("Vaheta pilt")}</button>
      % if rcd.filename:
      <div class="onlyimg">
        <div class="dz-image">
          <img data-dz-thumbnail="" alt="${rcd.filename}" src="${h.url('avalehepilt', format=rcd.fileext, id=rcd.id, v=rcd.fileversion)}" width="100%">
        </div>
        <div class="dz-details">
          <div class="dz-size">
            <span data-dz-size="">${h.filesize(rcd.filesize)}</span>
          </div>
          <div class="dz-filename">
            <span data-dz-name="">${rcd.filename}</span></div>
        </div>
        <div class="dz-error-message"><span data-dz-errormessage=""></span></div>
      </div>
      % endif
    </div>
    % else:
    <div class="pickimg" action="${h.url_current('edit', id=rcd.id)}">
      <button type="button" class="btn btn-link chimgb">${_("Vali pilt")}</button>
      % if rcd.filename:
      <div class="small">
        % if rcd.alates and rcd.kuni and rcd.id != model.Avalehepilt.DEFAULT_ID:
        ${h.str_from_date(rcd.alates)} - ${h.str_from_date(rcd.kuni_ui)}
        % endif
      </div>
      ${h.image(h.url('avalehepilt', format=rcd.fileext, id=rcd.id, v=rcd.fileversion), width="100%")}
      % endif
    </div>
    % endif
  </div>
  % endfor
</div>

% if c.item:
${h.form_save(c.item.id)}
<div class="p-3">
  ${h.flb(_("Kuvamise ajavahemik"))}
  <div class="row">
    % if c.item.id == model.Avalehepilt.DEFAULT_ID:
    <div class="col">
      ${_("siis, kui muud pilti pole määratud")}
      ${h.hidden('f_alates', h.str_from_date(c.item.alates))}
      ${h.hidden('f_kuni','')}
      ${h.hidden('kuni_vaja','')}
    </div>
    % else:
    <div class="col-sm-6">
      ${h.flb(_("Algus"), 'f_alates')}
      ${h.date_field('f_alates', c.item.alates)}
    </div>
    <div class="col-sm-6">
      ${h.flb(_("Lõpp"), 'f_kuni')}
      ${h.date_field('f_kuni', c.item.kuni_ui)}
      <div>${h.hidden('kuni_vaja','1')}</div>
    </div>
    % endif
  </div>
</div>
<div class="p-3">
  ${h.flb(_("Viitamine"))}
  <div class="row">
    <div class="col-sm-6">
      ${h.flb(_("Autori nimi"), 'f_autor')}
      ${h.text('f_autor', c.item.autor)}
    </div>
    <div class="col-sm-6">
      ${h.flb(_("Allikas"), 'f_allikas')}
      ${h.text('f_allikas', c.item.allikas)}
    </div>
  </div>
</div>

<div class="d-flex">
  <div class="flex-grow-1"></div>
  ${h.submit_dlg()}
</div>
${h.end_form()}
% endif

<script>
## pildi kirje valimine
$('div.pickimg').click(function(){
  dialog_load($(this).attr('action'), '', 'GET');
});
## pildi faili laadimine
$('div.dropzone').each(function(){
   var action = $(this).attr('action');
   $(this).dropzone(
        {url: action,
        dictDefaultMessage: "",
        thumbnailWidth:"100%",
        maxFiles: 1,
        acceptedFiles: ".svg",
        success: function(file, response){
          var el = $(file.previewElement);
          el.find('.progress').hide();
          if(response.error)
          {
              el.find('.dz-error-message').text(response.error); 
          }
          else
          {
              ## eemaldame vana pildi
              el.parent().find('.onlyimg').remove();
              el.addClass('onlyimg');
              ## märgime pildi URLi (dz ise lisab vigase data-urli)
              el.find('.dz-image img').prop('src', response.href).prop('width',el.parent().width());
              ## eemaldame mallis olnud ikoonid
              el.find('.dz-success-mark,.dz-error-mark').remove();
              ## kui sama pilt on põhiaknas, siis muudame seal ka
              $('img.avimg-${c.item.id}').prop('src', response.href);
          }
        }

  });
  $('button.rundz').click(function(){
    $('.dropzone').get(0).dropzone.hiddenFileInput.click();
  });
});
</script>
