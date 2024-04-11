<%inherit file="/common/page.mako"/>

<%def name="page_title()">
${_("Ühine fail")} ${c.item.filename}
</%def>      

<%def name="breadcrumbs()">
${h.crumb(_("Ülesanded"), h.url('ylesanded'))} 
${h.crumb(_("Ühised failid"), h.url('ylesanne_yhisfailid'))} 
${h.crumb(c.item.filename or _("Fail"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'ylesanded' %>
</%def>
<h3>${_("Ühiselt kasutatav fail")}</h3>
${h.rqexp()}
${h.form_save(c.item.id, multipart=True)}
<div class="form-wrapper mb-2">
  <div class="form-group row">
    ${h.flb3(_("Fail"), 'f_filedata', rq=True)}
    <div class="col">
      ${h.file('f_filedata', value=_("Fail"))}
      ${h.hidden('f_id', c.item.id)}
      % if c.item.filename:
      <a href="${h.url('shared', filename=c.item.filename)}">${c.item.filename}</a>
      % endif
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Teema"),'f_teema')}
    <div class="col">
      ${h.text('f_teema', c.item.teema, maxlength=256)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Liik"), 'f_yhisfail_kood')}
    <div class="col">
      ${h.select('f_yhisfail_kood', c.item.yhisfail_kood,
      c.opt.klread_kood('YHISFAIL', empty=True, vaikimisi=c.item.yhisfail_kood))}
    </div>
  </div>
  % if c.item.id:
  <div class="form-group row">
    ${h.flb3(_("Failinimi"), 'f_filename', rq=True)}
    <div class="col">
      ${h.text('f_filename', c.item.filename)}
    </div>
  </div>
  <div class="form-group row">
    <div class="col">
      <% 
         o_url = 'shared/%s' % h.literal(c.item.filename) 
         mimetype = c.item.mimetype
      %>
    % if c.item.is_image:
      ${h.image(o_url, 'Pilt')}

    % elif c.item.is_video:

      <object>
        <param name="movie" value="${o_url}"></param>
        <param name="allowFullScreen" value="true"></param>
        <embed src="${o_url}" type="${mimetype}">
        </embed>
      </object>

    % endif
    </div>
  </div>
  % endif
</div>
<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.btn_to(_("Tagasi"), h.url('ylesanne_yhisfailid'), level=2)}

    % if c.is_edit and c.item.id:
    ${h.btn_to(_("Vaata"), h.url('ylesanne_yhisfail', id=c.item.id), method='get')}
    % elif not c.is_edit and c.user.has_permission('yhisfailid', const.BT_UPDATE):
    ${h.btn_to(_("Muuda"), h.url('ylesanne_edit_yhisfail', id=c.item.id), method='get')}
    % endif
  </div>
  <div>
    % if c.item.id and c.user.has_permission('yhisfailid', const.BT_UPDATE):
    ${h.btn_to(_("Kustuta"), h.url('ylesanne_delete_yhisfail', id=c.item.id), method='delete', level=2)}
    % endif
    % if c.is_edit:
    ${h.submit()}
    % endif
  </div>
</div>
${h.end_form()}
