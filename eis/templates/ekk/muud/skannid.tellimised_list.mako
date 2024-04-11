% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      <th>${_("Välja otsitud")}</th>
      % for item in c.prepare_header():
      % if isinstance(item, tuple) and item[0]:
      ${h.th_sort(item[0], item[1])}
      % else:
      ${h.th(item)}
      % endif
      % endfor
      ${h.th(_("Skannitud testitöö"), width="160")}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       sooritus, sooritaja, k, test, tkord = rcd
       #url_edit = h.url('muud_skannid_edit_tellimine', id=sooritus.id)
       test = sooritaja.test
       item = c.prepare_item(rcd)
    %>
    <tr>
      <td>${h.checkbox('s_id', sooritus.id, checked=sooritus.valjaotsitud)}
        % if sooritus.valjaotsitud:
        ${h.hidden('endine_id', sooritus.id)}
        % endif
      </td>
      % for ind, value in enumerate(item):
      <td>
        % if isinstance(value, list):
        ${', '.join(value)}
##        % elif ind in (5,6):
##        ${h.link_to(value, url_edit)}
        % else:
        ${value}
        % endif
      </td>
      % endfor
      <td class="tdfile">
        % if c.is_edit:
        <div style="display:inline-block">
          <div class="dropzone" href="${h.url('muud_skannid_toolaadimine', id=sooritus.id)}"></div>
        </div>
        % endif
        <a href="${h.url('muud_skannid_tellimine', id='%d.%s' % (sooritus.id, 'pdf'))}" class="download"
           style="${not sooritus.skannfail and 'display:none' or ''}">
          <i class="mdi mdi-file-pdf mr-2"></i>
        </a>
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

<script>
$(function(){
  $('div.dropzone').each(function(){
  $(this).dropzone({url: $(this).attr('href'),
     dictDefaultMessage: "${_("Laadi fail")}",
     parallelUploads: 1,
     previewTemplate: $('.fz-template')[0].innerHTML,  
     acceptedFiles: ".pdf",
     init: function(){
           this.on('addedfile', function(file){
              ## eemaldame senise faili
              var el = $(file.previewElement);
              el.closest('.dropzone').children().filter(':not(:last)').remove();
           });
        },
     error: function(file, err){
          var el = $(file.previewElement);
          el.find('.progress').hide();
          el.find('.error').text('${_("Viga laadimisel")}'); 
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
             if(response.filename)
                el.closest('.tdfile').find('a.download').show();
             if(response.msg)
                el.find('.msg').text(response.msg);               
          }
        }
  });
  });
});
</script>

<div style="display:none" class="fz-template">
  <div>
      <span class="size" style="padding-left:10px" data-dz-size></span>
      <strong class="error text-danger" data-dz-errormessage></strong>
      <div class="progress progress-striped active" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">
        <div class="progress-bar progress-bar-success" style="width:0%;" data-dz-uploadprogress></div>
      </div>
      <div class="msg"></div>
  </div>
</div>
