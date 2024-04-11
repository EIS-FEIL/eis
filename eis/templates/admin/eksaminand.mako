<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Sooritaja")} ${c.item.nimi}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Sooritajad"), h.url('admin_eksaminandid'))} 
${h.crumb(c.item.nimi or _("Uus kasutaja"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>

${h.form_save(c.item.id)}

<div align="right">
% if c.item.on_labiviija and c.user.has_permission('kasutajad', const.BT_SHOW):
<span class="pl-3">
  ${h.link_to(_("Testide läbiviimisega seotud isiku andmed"), h.url('admin_kasutaja', id=c.item.id))}
</span>
% endif

% if c.item.on_kehtiv_ametnik and c.user.has_permission('ametnikud', const.BT_SHOW):
<span class="pl-3">
${h.link_to(_("Eksamikeskuse kasutaja andmed"), h.url('admin_ametnik', id=c.item.id))}
</span>
% endif
</div>

<% c.kasutaja = c.item %>
<h3>${_("Isikuandmed")}</h3>
${h.rqexp()}
<div class="form-wrapper pb-1 mb-3">
  ## isikukood, nimi, synniaeg, sugu, kasutajatunnus, parool
  <% c.is_eksaminand = True %>
  <%include file="kasutaja.isikukood.mako"/>

  <div class="form-group row">
    ${h.flb3(_("Aadress"))}
    <div class="col-md-9">
      <%
         c.aadress = c.item.aadress or c.item.aadress_id and model.Aadress.get(c.item.aadress_id)        
         c.aadress_obj = c.kasutaja
      %>
      <%include file="/admin/aadressivalik.mako"/>
    </div>
  </div>
  <div class="form-group row d-none" id="tr_rr_aadress">
    ${h.flb3(_("Aadress Rahvastikuregistris"),'rr_taisaadress')}
    <div class="col-md-9">
      <span id="rr_taisaadress"></span>
      ${h.button(_("Võta kasutusele Rahvastikuregistri aadress"), id='rraa', onclick='use_rr_aadress()', level=2)}
    </div>
  </div>

  <div class="form-group row">
    ${h.flb3(_("Postiindeks"),'k_postiindeks')}
    <div class="col-md-3">
      ${h.posint('k_postiindeks', c.kasutaja.postiindeks, maxlength=5)}
    </div>
    ${h.flb3(_("Telefon"),'k_telefon', 'text-md-right')}
    <div class="col-md-3">
      ${h.text('k_telefon', c.kasutaja.telefon)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("E-post"),'k_epost')}
    <div class="col-md-3 err-parent">
      ${h.text('k_epost', c.kasutaja.epost)}
    </div>
  </div>
</div>

<h3>${_("Õppimisandmed")}</h3>
<% c.lopetanud_tingimused = True %>
<%include file="/ekk/regamine/haridusandmed.mako"/>

<div class="form-wrapper pb-1">
  <div class="form-group row">
    ${h.flb3(_("Märkused"))}
    <div class="col-md-9">
      ${h.textarea('k_markus', c.item.markus)}
    </div>
  </div>

  <div class="form-group row">
    ${h.flb3(_("Kodakondsus"), 'dkodakond')}
    <div class="col-md-9" id="dkodakond">
      % if c.item.isikukood_ee:
      ${c.kasutaja.kodakond_nimi}
      % else:
      ${h.select('k_kodakond_kood', c.kasutaja.kodakond_kood, 
      c.opt.klread_kood('KODAKOND', vaikimisi=c.kasutaja.kodakond_kood), 
      empty=True, wide=False)}
      % endif
    </div>
  </div>

  % if c.item.synnikoht:
  ## sisestatakse rv eksamile registreerimisel
  <div class="form-group row">
    ${h.flb3(_("Sünnikoht"), 'dsynnikoht')}
    <div class="col-md-9" id="dsynnikoht">
      ${c.item.synnikoht}
    </div>
  </div>
  % endif
  
  <div class="form-group row">
    <div class="col-md-3">
      ${h.checkbox('on_lisatingimused', 1, checked=bool(c.kasutaja.lisatingimused),
      onchange="$('#k_lisatingimused').toggleClass('d-none', !this.checked);", label=_("Lisatingimused"))}
    </div>
    <div class="col-md-9">
      ${h.textarea('k_lisatingimused', c.kasutaja.lisatingimused, rows=4,
      class_=not c.kasutaja.lisatingimused and 'd-none' or None)}
    </div>
  </div>

  % if c.item.id and request.is_ext():
  <div id="oppurid" class="pb-1">
    <% c.kasutaja = c.item %>
    <%include file="eksaminand.oppurid.mako"/>
  </div>
  % endif
</div>

<div class="d-flex flex-wrap mt-2 mb-6">
  <div class="flex-grow-1">
  ${h.btn_back(url=h.url('admin_eksaminandid'))}      
  % if c.is_edit and c.item.id:
  ${h.btn_to(_("Vaata"), h.url('admin_eksaminand', id=c.item.id), method='get', level=2)}
  % endif
  </div>
  <div>
  % if c.item.id and not c.item.isikukood_ee and c.user.has_permission('eksaminandid', const.BT_UPDATE):
    ${h.btn_to_dlg(_("Isikukirjete ühendamine"), 
h.url('admin_eksaminand_yhendamised', yhendatav_id=c.kasutaja.id, default=True), 
title=_("Sama isiku mitme kirje ühendamine"), width=900, size='lg', level=2)}
  % endif

    % if c.is_edit:
    ${h.submit()}
    % elif c.user.has_permission('eksaminandid', const.BT_UPDATE):
    ${h.btn_to(_("Muuda"), h.url('admin_edit_eksaminand', id=c.item.id), method='get')}
    % endif
  </div>
</div>

% if c.yhendaja_ik:
  ## prooviti isikukood muuta selliseks, mis on juba kasutusel
  <%
        s_attrs = "title: '%s'" % _("Sama isiku mitme kirje ühendamine")
        s_attrs += ", url: '%s'" % h.url('admin_eksaminand_yhendamised', yhendatav_id=c.kasutaja.id, yhendaja_ik=c.yhendaja_ik, default=True)
        s_attrs += ", size: 'lg'" 
  %>
  <script>open_dialog({${s_attrs}});</script>
% endif

${h.end_form()}

% if c.sooritajad:
<div id="sooritajad">
  <%include file="eksaminand.sooritajad.mako"/>
</div>
% endif

% if c.rvsooritajad:
<div id="rvsooritajad">
  <%include file="eksaminand.rvsooritajad.mako"/>
</div>
% endif

<div class="mt-3">
% if c.item.isikukood:
${h.link_to(_("Saadetud teated"), h.url('otsing_teated', isikukood=c.item.isikukood))}
% else:
${h.link_to(_("Saadetud teated"), h.url('otsing_teated', eesnimi=c.item.eesnimi,
perenimi=c.item.perenimi))}
% endif
</div>
