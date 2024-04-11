% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
    % if c.naita == 'epost':
    ${_("Sooritajad, kellele saadetakse teavitus e-postiga")}
    % elif c.naita == 'tpost':
    ${_("Sooritajad, kellele saadetakse teavitus tavapostiga")}    
    % elif c.naita == 'puudu':
    ${_("Sooritajad, kelle aadress pole teada")}
    % endif
  <thead>
    <tr>
      ${h.th_sort('kasutaja.isikukood kasutaja.synnikpv', _("Isikukood või sünniaeg"))}
      ${h.th_sort('kasutaja.perenimi kasutaja.eesnimi', _("Nimi"))}
      ${h.th_sort('kasutaja.epost', _("E-posti aadress"))}
      % if c.on_tseis:
      ${h.th_sort('sooritaja.algus', _("Kuupäev"))}
      ${h.th_sort('test.nimi', _("Test"))}
      ${h.th_sort('testimiskord.test_id testimiskord.tahis', _("Testimiskord"))}
      % if c.testiliik == const.TESTILIIK_TASE:
      ${h.th_sort('sooritaja.keeletase_kood', _("Keeleoskuse tase"))}
      % endif
      ${h.th_sort('sooritaja.tulemus_protsent', _("Tulemus"))}
      % endif
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <tr>
      <% k_id, k_ik, k_synnikpv, k_nimi, k_epost = rcd[:5] %>
      <td>${k_ik or h.str_from_date(k_synnikpv)}</td>
      <td>${k_nimi}</td>
      <td>${k_epost}</td>
      % if c.on_tseis:
      <% 
         aeg, test_nimi, test_id, tk_tahis, pallid, tulemus_protsent = rcd[6:12] 
      %>
      <td>${h.str_from_date(aeg)}</td>
      <td>${test_nimi}</td>
      <td>${test_id}-${tk_tahis}</td>
      % if c.testiliik == const.TESTILIIK_TASE:
      <td>${model.Klrida.get_str('KEELETASE', rcd[12], ylem_kood=const.AINE_RK)}</td>
      % endif
      <td>${h.fstr(pallid)} p</td>
      % endif
    </tr>
    % endfor
  </tbody>
</table>
% endif
