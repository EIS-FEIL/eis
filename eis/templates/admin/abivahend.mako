<%inherit file="/common/dlgpage.mako"/>
<%include file="/common/message.mako"/>
${h.form_save(c.item.id)}
${h.hidden('lang', c.lang)}
<h3>${_("Abivahend")}</h3>
<% is_tr = c.lang and c.lang != const.LANG_XX %>
${h.rqexp()}
<div class="form-wrapper pb-1 mb-3">
  <div class="form-group row">
    ${h.flb3(_("Kood"), rq=True)}
    <div class="col-md-9">
      ${h.text('f_kood', c.item.kood, size=10, ronly=is_tr)}      
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Nimetus"), rq=True)}
    <div class="col-md-9">
      % if not is_tr:
      ${h.text('f_nimi', c.item.nimi)}
      % else:
        ${c.item.nimi}
        <br/>
        <% tran = c.item.tran(c.lang, False) %>
        ${h.text('f_nimi', tran and tran.nimi or '')}
      % endif
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Järjekord"))}
    <div class="col-md-9">
      ${h.posint5('f_jrk', value=c.item.jrk, ronly=is_tr)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Kirjeldus"))}
    <div>
      % if not is_tr:
      ${h.ckeditor('f_kirjeldus', c.item.kirjeldus)}
      % else:
      ${h.literal(c.item.kirjeldus)}      
      <br/>
      <% tran = c.item.tran(c.lang, False) %>
      ${h.ckeditor('f_kirjeldus', tran and tran.kirjeldus or '')}          
      % endif
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("HTML päis"))}
    % if not is_tr:    
    ${h.textarea('f_pais', c.item.pais, rows=5)}
    % else:
    ${c.item.pais}
    <br/>
    ${h.textarea('f_pais', tran and tran.pais or '', rows=5)}
    % endif
  </div>
  <div class="form-group row">
    ${h.flb3(_("Ikooni URL"))}
    <div class="col-md-9">
      ${h.text('f_ikoon_url', c.item.ikoon_url, maxlength=100, ronly=is_tr)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Akna laius"))}
    <div class="col-md-9">
      ${h.posint5('f_laius', c.item.laius, ronly=is_tr)}      
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Akna kõrgus"))}
    <div class="col-md-9">
      ${h.posint5('f_korgus', c.item.korgus, ronly=is_tr)}      
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Olek"), rq=True)}
    <div class="col-md-9">
      % if is_tr:
        % if c.item.kehtib:
        ${h.badge_success(_("Kasutusel"))}
        % else:
        ${h.badge_secondary(_("Pole kasutusel"))}
        % endif
      % else:
      ${h.radio('f_kehtib', const.B_STAATUS_KEHTIV,
      checked=c.item.kehtib, label=_("Kasutusel"))}
      ${h.radio('f_kehtib', '',
      checked=not c.item.kehtib, label=_("Pole kasutusel"))}
      % endif
    </div>
  </div>
</div>

% if c.is_edit and c.user.has_permission('klassifikaatorid', const.BT_UPDATE):
<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
  % if c.item.id:
  ${h.btn_remove(id=c.item.id, confirm=_("Kas oled kindel, et soovid kustutada?"))}
  % endif
  </div>
  <div>
    ${h.submit_dlg(clicked=True)}
  </div>
</div>
% endif
${h.end_form()}
