<%inherit file="/common/simplepage.mako"/>
<script>
        function returnFileUrl(fileUrl) {
          top.opener.$('.cke_dialog_image_url input.cke_dialog_ui_input_text').val(fileUrl);
          window.close();
        }
</script>

% if not c.items:
${h.alert_notice(_("Sellel testil ei ole ühtki tagasisidefaili"), False)}
% else:
<div>
  % for r in c.items:
  <div class="browseimg rounded border m-2 p-2" style="float:left;text-align:center;">
    <% url = f'testimages/{r.filename}' %>
    <div>${r.filename}</div>
    <div><i>${h.filesize(r.filesize)}</i></div>
    <div class="m-2">
      <img src="testimages/${r.filename}" width="120px"/>
    </div>
    ${h.button(_("Vali"), onclick="returnFileUrl('%s')" % url)}
    ${h.btn_remove(h.url_current('delete', id=r.id))}
  </div>
  % endfor
</div>
% endif
