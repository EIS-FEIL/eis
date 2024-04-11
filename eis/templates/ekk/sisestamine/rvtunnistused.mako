<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Rahvusvahelise eksami tunnistuse sisestamine")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sisestamine' %>
</%def>

<h1>${_("Rahvusvahelise eksami tunnistuse sisestamine")}</h1>
${h.form_search(url=h.url('sisestamine_rvtunnistused'))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-6">
      <div class="form-group">
        ${h.flb(_("Rahvusvaheline eksam"),'rveksam_id')}
        ${h.select('rveksam_id', c.rveksam_id, c.opt.rveksamid())}
      </div>
    </div>
    <div class="col-12 col-md-6">
      <div class="form-group mt-4">
        ${h.submit(_('Sisesta failiga'), id='failiga')}
      </div>
    </div>
  </div>
  <div class="row filter">
    <div class="col-12 col-md-6">
      <div class="form-group">
        ${h.flb(_("Isikukood"),'isikukood')}
        ${h.text('isikukood', c.isikukood, maxlength=50, size=15)}
        ${h.btn_search(_('Sisesta'))}
      </div>
    </div>
    <div class="col-12 col-md-6 nimesisestus">
        ${_("Sünniaeg ja nimi sisesta juhul, kui isikukood pole teada")}
        <div class="form-group row">
          ${h.flb3(_("Sünniaeg"),'synnikpv')}
          <div class="col-md-9">
            ${h.date_field('synnikpv', c.kasutaja and c.kasutaja.synnikpv or c.synnikpv)}
          </div>
        </div>
        <div class="form-group row">
          ${h.flb3(_("Eesnimi"),'eesnimi')}
          <div class="col-md-9">
            ${h.text('eesnimi', c.kasutaja and c.kasutaja.eesnimi or c.eesnimi, maxlength=30)}
          </div>
        </div>
        <div class="form-group row">
          ${h.flb3(_("Perekonnanimi"),'perenimi')}
          <div class="col-md-9">
            ${h.text('perenimi', c.kasutaja and c.kasutaja.perenimi or c.perenimi, maxlength=30)}
          </div>
        </div>
        ${h.submit(_('Otsi'), id='otsinimi')}
    </div>
  </div>
</div>
<script>
$(function(){
## kui isikukood on sisestatud, siis synnikpv ja nime väljad olgu disabled
  $('#isikukood').keyup(function(){
    var f=$('#synnikpv,#eesnimi,#perenimi,table.nimesisestus input');
    if($(this).val()=='') f.removeAttr('disabled'); else f.prop('disabled',true);
  });
});
</script>

<%include file="rvtunnistused.isikuvalik.mako"/>

${h.end_form()}
