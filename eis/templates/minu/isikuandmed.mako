<div class="form-wrapper mb-3">
  <div class="form-group row">
    ${h.flb3(_("Isikukood ja nimi"))}
    <div class="col-md-9">
      <div class="d-flex flex-wrap">
        <div class="flex-grow-1">
          ${c.kasutaja.isikukood}
          ${c.kasutaja.eesnimi}
          ${c.kasutaja.perenimi}
        </div>
        % if c.kasutaja.isikukood and request.is_ext() and c.submit_rr:
        ${h.submit(_('Päri andmed Rahvastikuregistrist'), id='rr', level=2)}
        % endif
      </div>
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("Aadress"),'aadress_id', rq=True)}
    <div class="col-md-9">
      <%
         c.aadress = c.kasutaja.aadress
         c.aadress_obj = c.kasutaja
      %>
      <%include file="/admin/aadressivalik.mako"/>
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("Postiindeks"),'k_postiindeks')}
    <div class="col-md-9">
      ${h.posint('k_postiindeks', c.kasutaja.postiindeks)}
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("Telefon"),'k_telefon')}
    <div class="col-md-9">
      ${h.text('k_telefon', c.kasutaja.telefon)}
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("E-post"),'k_epost', rq=True)}
    <div class="col-md-9">
      ${h.text('k_epost', c.kasutaja.epost)}
    </div>
  </div>
  <div class="form-group row">  
    ${h.flb3(_("Korda e-posti aadressi"),'epost2', rq=True)}
    <div class="col-md-9">
      ${h.text('epost2', c.kasutaja.epost)}
    </div>
  </div>
</div>
