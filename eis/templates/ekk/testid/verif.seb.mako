## dlgpage.mako mallist ei saa pärida, sest form_dlg_target aknas puudub jquery
<%include file="/common/message.mako"/>
${h.form(h.url_current('update', id=c.item.id), id="form_seb", method="post", multipart=True, target="form_dlg_target")}
${h.hidden('sub', 'seb')}
<div class="row">
  <div class="col-6 pr-3">
    ${h.flb(_("Olemasolev seadistuste fail"))}
    <div class="m-2">
    % if c.item.seb_konf:
      ${h.link_to(_("Laadi alla"), h.url_current('download', format='seb'), target='_blank')}
    % endif
    </div>
    % if c.is_edit:
    ${h.submit(_("Genereeri uus"), id="genereeri")}
    % endif
  </div>
  % if c.is_edit:
  <div class="col-6">
    ${h.flb(_("Laadi üles uus .seb fail"))}
    <div class="m-2">
    ${h.file('seb_konf', value=_("Fail"))}
    </div>
    ${h.submit()}
  </div>
  % endif
</div>
${h.end_form()}

<iframe name="form_dlg_target" width="0" height="0" style="display:none" onload="if(typeof(move_to_dlg)=='function') move_to_dlg(this)" src="">  
