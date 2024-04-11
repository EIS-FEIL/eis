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
<%def name="requirenw()">
<% c.pagenw = True %>
</%def>

${h.form_search(h.url_current('new'))}

${h.rqexp(None, _("Sisesta isikukood või kui isikukood pole teada, siis sünniaeg ja nimi"))}
<div class="gray-legend p-3">
  <div class="row filter">
      <div class="col-lg-3 col-md-6" >
        ${h.flb(_("Isikukood"),'isikukood')}
        <%
          value = c.isikukood
        %>
        ${h.text('isikukood', value)}
      </div>
      <% if c.kasutaja: c.is_edit = False %>
      <div class="col-lg-3 col-md-6">
        ${h.flb(_("Sünniaeg"), 'synnikpv')}
        ${h.date_field('synnikpv', c.synnikpv)}
      </div>
      <div class="col-lg-3 col-md-6">
        ${h.flb(_("Eesnimi"), 'eesnimi')}
        ${h.text('eesnimi', c.eesnimi)}
      </div>
      <div class="col-lg-3 col-md-6">
        ${h.flb(_("Perekonnanimi"), 'perenimi')}
        ${h.text('perenimi', c.perenimi)}
      </div>
  </div>
</div>

<script>
$(function(){
## kui isikukood on sisestatud, siis synnikpv ja nime väljad olgu disabled
  $('#isikukood').keyup(function(){
    var f=$('#synnikpv,#eesnimi,#perenimi');
    f.prop('disabled', ($('#isikukood').val()!=''));
  });
});
</script>

<div class="text-right">
${h.submit(_("Otsi"), id='otsi')}
</div>

% if c.items:
<% cnt = len(c.items) %>
% if cnt==1:
${_("Andmebaasist leiti 1 sama sünniaja ja nimega isik")}
% else:
${_("Andmebaasist leiti {n} sama sünniaja ja nimega isikut").format(n='<span class="brown">%s</span>' % cnt)}
% endif

<table  class="table table-borderless table-striped" width="100%">
  <thead>
    <th></th>
    <th>${_("Isikukood")}</th>
    <th>${_("Sünniaeg")}</th>
    <th>${_("Nimi")}</th>
    <th>${_("Aadress")}</th>
    <th>${_("E-posti aadress")}</th>
    <th>${_("Telefon")}</th>
  </thead>
  <tbody>
    % for item in c.items:
    <tr>
      <td>
        ${h.btn_to(_("See on sama isik"), h.url_current('new', kasutaja_id=item.id))}
      </td>
      <td>${item.isikukood}</td>
      <td>${h.str_from_date(item.synnikpv)}</td>
      <td>${h.link_to(item.nimi, h.url('admin_eksaminand', id=item.id), target='_blank')}</td>
      <td>
        ${item.tais_aadress}
      </td>
      <td>${item.epost}</td>
      <td>${item.telefon}</td>
    </tr>
    % endfor
  </tbody>
</table>
<br/>
% endif
${h.end_form()}
