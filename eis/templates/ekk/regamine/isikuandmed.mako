<div class="form-wrapper">
  <div class="form-group row">
    ${h.flb3(_("Sooritaja"),'k_nimi')}
    <div class="col-md-9">
      <span id="k_nimi">
        % if c.sooritaja:
        ${c.sooritaja.eesnimi}
        ${c.sooritaja.perenimi}
        % else:
        ${c.kasutaja.eesnimi}
        ${c.kasutaja.perenimi}
        % endif
      </span>

      % if c.kasutaja.isikukood:
      ${c.kasutaja.isikukood}
      % else:
      ${h.str_from_date(c.kasutaja.synnikpv)}
      % endif

    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Aadress"))}
    <div class="col-md-9">
      <%
         c.aadress = c.kasutaja.aadress
         c.aadress_obj = c.kasutaja
      %>
      <%include file="/admin/aadressivalik.mako"/>
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Aadress Rahvastikuregistris"), 'aadressrr')}
    <div class="col-md-9" id="aadressrr">
      <% c.rr_query_url = h.url_current('edit', sub='rr') %>
      <%include file="/admin/rahvastikuregister_js.mako"/>
      <span id="rr_taisaadress">
      ${h.button(_("Päri andmed Rahvastikuregistrist"), onclick='query_rr(%s)' % c.kasutaja.id, level=2)}
      </span>
      ${h.button(_("Võta kasutusele Rahvastikuregistri aadress"), id='rraa',
      class_="invisible", onclick='use_rr_aadress()', level=2)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Postiindeks"),'k_postiindeks')}
    <div class="col-md-9">
      ${h.int5('k_postiindeks', c.kasutaja.postiindeks)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Telefon"),'k_telefon')}
    <div class="col-md-9">
      ${h.text('k_telefon', c.kasutaja.telefon, size=20)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("E-post"),'k_epost')}
    <div class="col-md-9 err-parent">
      ${h.text('k_epost', c.kasutaja.epost, size=40)}
    </div>
  </div>
</div>

<%include file="haridusandmed.mako"/>

