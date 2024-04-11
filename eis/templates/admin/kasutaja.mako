<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Kasutajad")} | ${c.item.nimi or _("Uus kasutaja")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Kasutajad"), h.url('admin_kasutajad'))} 
${h.crumb(c.item.nimi or _("Uus kasutaja"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<%def name="draw_tabs()">
<%include file="kasutaja.tabs.mako"/>
</%def>
<%
 c.profiil = c.item.give_profiil()
%>

${h.form_save(c.item.id)}
% if c.item.id and c.user.has_permission('ametnikud', const.BT_SHOW):
<div align="right">${h.link_to(_("Eksamikeskuse kasutaja andmed"),
  h.url('admin_ametnik', id=c.item.id))}</div>
% endif

${h.rqexp()}
<div class="form-wrapper mb-1">
  ## isikukood, nimi, synniaeg, sugu, kasutajatunnus, parool
  <%include file="kasutaja.isikukood.mako"/>
  
  <div class="form-group row">
    <div class="col-md-9">
      ${h.checkbox('k_on_labiviija', True,
      checked=c.item.on_labiviija, label=_(" Testide läbiviimisega seotud isik"))}
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
  <div class="form-group row">
    ${h.flb3(_("Arveldusarve"))}
    <div class="col-md-9">
      ${h.text('p_arveldusarve', c.profiil.arveldusarve, maxlength=20)}
    </div>
  </div>
  <div class="form-group row">
    <div class="col">
      ${h.checkbox1('p_on_psammas', 1, checked=c.profiil.on_psammas, 
      label=_("On liitunud pensionikindlustuse II sambaga"))}
      <span id="psammas">
        ${h.radio('p_psammas_protsent', 2, checkedif=c.profiil.psammas_protsent, label='2%')}
        ${h.radio('p_psammas_protsent', 3, checkedif=c.profiil.psammas_protsent, label='3%')}        
      </span>
      <script>
        $(function(){
          $('input#p_on_psammas').change(function(){
             $('span#psammas').toggle($('input#p_on_psammas:checked').length > 0);
          });
          $('span#psammas').toggle($('input#p_on_psammas:checked').length > 0);
        });
      </script>
    </div>
  </div>
  <div class="form-group row">
    <div class="col">
      ${h.checkbox('p_on_pensionar', 1, checked=c.profiil.on_pensionar, 
      label=_("On vanaduspensionär"))}
    </div>
  </div>
  <div class="form-group row">
    <div class="col">  
      ${h.checkbox('p_on_ravikindlustus', 1, checked=c.profiil.on_ravikindlustus, 
      label=_("Kehtiv ravikindlustusleping"))}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Märkused"))}
    <div class="col-md-9">
      ${h.textarea('k_markus', c.item.markus)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Läbiviija märkused"))}
    <div class="col-md-9">
      ${h.textarea('p_oma_markus', c.profiil.oma_markus)}
    </div>
  </div>

% if c.item.id:
  <div class="form-group row">
    ${h.flb3(_("Ametikohtade andmed"))}
    <div class="col-md-5" id="ametikohad">
      <% c.kasutaja = c.item %>
      <%include file="kasutaja.ametikohad.mako"/>
    </div>
    <div class="col-md-4">
      % if request.is_ext():
      ${h.button(_("Kontrolli EHISest"),
      onclick="ajax_url('%s','get','#ametikohad')" % h.url_current('show',
      id=c.item.id, sub='ehis'), level=2)}
      % endif
      % if c.user.has_permission('kasutajad', const.BT_UPDATE):
      ${h.btn_to_dlg(_("Lisa ametikoht käsitsi"), 
      h.url('admin_kasutaja_new_amet', kasutaja_id=c.kasutaja.id), 
      title=_("Uus ametikoht"), width=600, level=2)}
      % endif
    </div>
  </div>
% endif
</div>

% if len(c.kasutaja.labiviijalepingud):
<table  class="table table-borderless table-striped">
  <thead>
    <tr>
      ${h.th(_("Testsessioon"))}
      ${h.th(_("Õppeaasta"))}
      ${h.th(_("Testiliik"))}
      ${h.th(_("Leping"))}
      ${h.th(_("Tingimustega nõustumise kuupäev"))}
    </tr>
  </thead>
  <tbody>
    % for lleping in c.kasutaja.labiviijalepingud:
    <%
       sessioon = lleping.testsessioon
       leping = lleping.leping
    %>
    <tr>
      % if sessioon:
      <td>${sessioon.nimi}</td>
      <td>${sessioon.oppeaasta}</td>
      <td>${sessioon.testiliik_nimi}</td>
      % else:
      <td colspan="3">${_("Üldtingimused")}</td>
      % endif
      <td>
        ${h.link_to(leping.nimetus, leping.url)}
      </td>
      <td>
        ${h.str_from_date(lleping.noustunud)}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.btn_back(url=h.url('admin_kasutajad'))}

    % if c.is_edit and c.item.id:
    ${h.btn_to(_("Vaata"), h.url('admin_kasutaja', id=c.item.id), method='get', level=2)}
    % endif
  </div>
  <div>
    % if c.is_edit:
    ${h.submit()}
    % elif c.user.has_permission('kasutajad', const.BT_UPDATE):
    ${h.btn_to(_("Muuda"), h.url('admin_edit_kasutaja', id=c.item.id), method='get')}
    % endif
  </div>
</div>


${h.end_form()}
