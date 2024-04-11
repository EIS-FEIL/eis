${h.form_search()}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Isikukood"),'isikukood')}
        ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Sünniaeg"), 'synnikpv')}
        ${h.date_field('synnikpv', c.synnikpv)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Eesnimi"),'eesnimi')}
        ${h.text('eesnimi', c.eesnimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Perekonnanimi"),'perenimi')}
        ${h.text('perenimi', c.perenimi)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.submit_dlg(_("Otsi"))}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<%include file="/common/message.mako"/>
% if c.items != '' and not c.items:
${_("Otsingu tingimustele vastavaid isikuid ei leitud")}
% elif c.items:

<%
  hcls = 'd-none d-lg-table-cell'
  hcls2 = 'd-lg-none'
%>
<table  class="table table-borderless table-striped" width="100%">
  <thead>
    <th></th>
    <th class="${hcls2}">${_("Isik")}</th>
    <th class="${hcls}">${_("Isikukood")}</th>
    <th class="${hcls}">${_("Sünniaeg")}</th>
    <th class="${hcls}">${_("Nimi")}</th>
    <th class="${hcls}">${_("Aadress")}</th>
    <th class="${hcls}">${_("E-posti aadress")}</th>
    <th class="${hcls}">${_("Telefon")}</th>
  </thead>
  <tbody>
    % for item in c.items:
    <tr>
      <td>
        ${h.button(_("Ühenda"), 
        onclick="dialog_load('%s', null, 'post')" % h.url_current('update', id=item.id), level=2)}
      </td>
      <td class="${hcls2}">
        ${item.isikukood} ${h.str_from_date(item.synnikpv)}
        ${h.link_to(item.nimi, h.url('admin_eksaminand', id=item.id), target='_blank')}
        <% tais_aadress = item.tais_aadress %>
        % if tais_aadress:
        <div>${item.tais_aadress}</div>
        % endif
        <div>${item.epost}  ${item.telefon}</div>
      </td>
      <td class="${hcls}">${item.isikukood}</td>
      <td class="${hcls}">${h.str_from_date(item.synnikpv)}</td>
      <td class="${hcls}">${h.link_to(item.nimi, h.url('admin_eksaminand', id=item.id), target='_blank')}</td>
      <td class="${hcls}">
        ${item.tais_aadress}
      </td>
      <td class="${hcls}">${item.epost}</td>
      <td class="${hcls}">${item.telefon}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

