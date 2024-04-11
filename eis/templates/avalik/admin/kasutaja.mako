<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Kasutajad")} | ${c.item.nimi}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Kasutajad"), h.url('admin_kasutajad'))} 
${h.crumb(c.item.nimi, h.url('admin_kasutaja', id=c.item.id))}
</%def>

<% 
   c.kasutaja = c.item 
   c.profiil = c.item.give_profiil()
   #if c.user.has_permission('avalikadmin', const.BT_UPDATE):
   c.is_edit = True
   c.can_update_profiil = True
%>

${h.form_save(c.item.id)}
<div class="form-wrapper-lineborder mb-2">
  <div class="form-group row">
    ${h.flb3(_("Isikukood"))}
    <div class="col">${c.item.isikukood}</div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Eesnimi"))}
    <div class="col">${c.item.eesnimi}</div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Perekonnanimi"))}
    <div class="col">${c.item.perenimi}</div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("E-post"))}
    <div class="col">
      % if c.item.epost:
      ${c.item.epost}
      % else:
      ${h.text('k_epost', c.item.epost, size=40)}
      % endif
    </div>
  </div>
  % if c.profiil.markus:
  <div class="form-group row">
    ${h.flb3(_("Märkus"))}
    <div class="col">${c.profiil.markus}</div>
  </div>
  % endif
</div>

<%include file="/admin/kasutaja.profiilisisu.mako"/>

<div class="d-flex">
${h.btn_back(url=h.url('admin_kasutajad'))}
<div class="flex-grow-1 text-right">
% if c.is_edit:
${h.submit()}
% endif
</div>
</div>

${h.end_form()}
