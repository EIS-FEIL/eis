## -*- coding: utf-8 -*- 
${h.pager(c.items,msg_not_found=_("Toimumisaegu ei leitud"),
          msg_found_one=_("Leiti 1 läbiviimine"),
          msg_found_many=_("Leiti {n} läbiviimist"))}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('toimumisaeg.tahised', _("Toimumisaja tähis"))}
      ${h.th_sort('test.nimi', _("Test"))}
      ${h.th_sort('testiosa.tahis', _("Testiosa"))}
      ${h.th_sort('ruum.tahis', _("Soorituskoht ja -ruum"))}
      ${h.th_sort('testiruum.algus', _("Aeg"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       testiruum_id, tk_tahis, tr_tahis, k_nimi, r_tahis, osa_tahis, ta_tahised, t_nimi, tr_algus = rcd
       url_edit = h.url('klabiviimine_edit_toimumisaeg', id=testiruum_id)
       koht_nimi = '%s %s (%s-%s)' % (k_nimi, r_tahis or '', tk_tahis, tr_tahis)
    %>
    <tr>
      <td width="130px">${ta_tahised}</td>
      <td>
        ${h.link_to(t_nimi, url_edit)}
      </td>
      <td>
        ${osa_tahis}
      </td>
      <td>
        ${h.link_to(koht_nimi, url_edit)}
      </td>
      <td>${h.str_from_datetime(tr_algus)}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
