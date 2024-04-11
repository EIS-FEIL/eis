% if c.items != '':
<br/>
<% cnt = len(c.items) %>
% if cnt == 0:
${_("Andmebaasist ei leitud sellise nime ja sünniajaga isikuid")}
% elif cnt==1:
${_("Andmebaasist leiti 1 sama sünniaja ja nimega isik")}
% else:
${_("Andmebaasist leiti {n} sama sünniaja ja nimega isikut").format(n='<span class="brown">%s</span>' % cnt)}
% endif

% if cnt:
<table class="table table-borderless table-striped" width="100%">
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
        ${h.btn_to(_("See on sama isik"), h.url('sisestamine_rvtunnistused', rveksam_id=c.rveksam_id, kasutaja_id=item.id))}
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
% endif
<br/>
${h.submit(_("Salvesta uue isikuna"), id='uus')}
% endif
