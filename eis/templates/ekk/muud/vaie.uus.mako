<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Uue vaide lisamine")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Vaided"), h.url('muud_vaided'))}
${h.crumb(_("Lisa uus"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'muud' %>
</%def>
<h2>${_("Uue vaide lisamine")}</h2>
${h.form_save(None, multipart=True)}
${h.hidden('kasutaja_id', c.kasutaja.id)}

${h.rqexp()}
<div class="form-wrapper mb-2">
  % if c.kasutaja.isikukood:
  <div class="form-group row">
    ${h.flb3(_("Vaidlustaja isikukood"))}
    <div class="col">${c.kasutaja.isikukood}</div>
  </div>
  % endif
  <div class="form-group row">    
    ${h.flb3(_("Vaidlustaja nimi"))}
    <div class="col">${c.kasutaja.nimi}</div>
  </div>
  <div class="form-group row">    
    ${h.flb3(_("Vaidlustaja sünnikuupäev"))}
    <div class="col">
      ${h.str_from_date(c.kasutaja.synnikpv)}
    </div>
  </div>

  % if len(c.opt_sooritaja):
  <div class="form-group row">
    ${h.flb3(_("Testisooritus"), rq=True)}
    <div class="col">
      ${h.select('sooritaja_id', c.sooritaja_id, c.opt_sooritaja)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Aadress"))}
    <div class="col">
      <%
         c.aadress = c.kasutaja.aadress
         c.aadress_obj = c.kasutaja
      %>
      <%include file="/admin/aadressivalik.mako"/>
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Postiindeks"))}
    <div class="col-md-3">${h.posint('k_postiindeks', c.kasutaja.postiindeks)}</div>
    ${h.flb3(_("Telefon"),'k_telefon', 'text-md-right')}
    <div class="col-md-3">${h.text('k_telefon', c.kasutaja.telefon)}</div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("E-post"))}
    <div class="col err-parent">
      <div class="d-flex flex-wrap">
        <div class="flex-grow-1 pr-5">
          ${h.text('k_epost', c.kasutaja.epost)}
        </div>
        ${h.checkbox1('otsus_epostiga', 1, checked=True, label=_("Otsus saadetakse e-postiga"))}
      </div>
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Vaide esitamise kuupäev"))}
    <div class="col">${h.date_field('esitamisaeg', c.esitamisaeg, wide=False)}</div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Põhjendus"), rq=True)}
    <div class="col">
      ${h.textarea('markus', c.markus, rows=5)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Lisafail"))}
    <div class="col">
      ${h.file('vfail')}
    </div>
  </div>
  % else:
  <div class="form-group row">
    <div class="col">
      ${_("Ei ole testisooritusi, mida saaks vaidlustada")}
    </div>
  </div>
  % endif
</div>
    
<div class="d-flex">
${h.btn_to(_("Otsi teine isik"), h.url_current('new'))}
<div class="flex-grow-1 text-right">
  % if len(c.opt_sooritaja):
  ${h.submit()}
  % endif
</div>
</div>
