% if c.list_holek:
<%include file="ekspert.holek_list.mako"/>
% else:

${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('sooritus.tahised', _("Testitöö tähis"))}
      ${h.th_sort('sooritus.hindamine_staatus', _("Hindamise olek"))}
      % if c.probleem in ('lahendamata', 'vaided'):
      ${h.th_sort('vaie.staatus', _("Vaide olek"))}
      % endif
      ${h.th_sort('sooritus.pallid', _("Tulemus"))}
    </tr>
  </thead>
  <tbody>
    % for n, (tos, v_staatus) in enumerate(c.items):
    <% 
       url_edit = h.url('hindamine_ekspert_kogum', toimumisaeg_id=c.toimumisaeg.id, id=tos.id)
    %>
    <tr>
      <td>${h.link_to(tos.tahised, url_edit, level=0)}</td>
      <td>${tos.hindamine_staatus_nimi}</td>
      % if c.probleem in ('lahendamata','vaided'):
      <td>${c.opt.V_STAATUS.get(v_staatus)}</td>
      % endif
      <td>${h.fstr(tos.pallid)}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif

% endif
