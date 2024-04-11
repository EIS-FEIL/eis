<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Logopeedid")} | ${c.item.nimi or "Uus logopeed"}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Logopeedid"), h.url('logopeedid'))} 
${h.crumb(c.item.nimi or _("Uus logopeed"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'logopeedid' %>
</%def>
% if not c.item.id:
<h1>${_("Uus logopeed")}</h1>
% else:
<h1>${c.item.nimi}</h1>
% endif

% if not c.item.id:
${h.form_search(url=h.url('new_logopeed'))}
${h.hidden('isikukood','')}
${h.end_form()}
<script>
function search_by_ik(){
  var ik=$('form#form_save input[name="isikukood"]').val();
  $('form#form_search input#isikukood').val(ik);
  $('form#form_search').submit();
}
</script>
% endif

${h.form_save(c.item.id)}
<% c.kasutaja = c.item %>
${h.rqexp()}
<div class="form-wrapper mb-1">
  <%include file="/admin/kasutaja.isikukood.mako"/>

  <div class="form-group row">
    <div class="col-md-9">
      ${h.checkbox('on_roll', True,
      checked=c.item.on_kehtiv_roll(const.GRUPP_A_LOGOPEED), label=_("Isik on logopeed"))}
    </div>
  </div>
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

<div class="d-flex flex-wrap">
${h.btn_back(url=h.url('logopeedid'))}

<div class="flex-grow-1 text-right">
% if c.is_edit:
%   if c.item.id:
${h.btn_to(_("Vaata"), h.url('logopeed', id=c.item.id), method='get', level=2)}
%   endif
${h.submit()}
% elif c.user.has_permission('lglitsentsid', const.BT_UPDATE):
${h.btn_to(_("Muuda"), h.url('edit_logopeed', id=c.item.id), method='get')}
% endif
</div>
</div>

${h.end_form()}
