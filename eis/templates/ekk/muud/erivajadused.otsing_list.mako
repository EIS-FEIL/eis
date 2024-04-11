% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('kasutaja.isikukood', _("Isikukood"))}
      ${h.th_sort('sooritaja.eesnimi', _("Eesnimi"))}
      ${h.th_sort('sooritaja.perenimi', _("Perekonnanimi"))}
      ${h.th_sort('sooritus.tahised', _("Soorituse tähis"))}
      ${h.th_sort('sooritaja.lang_LS', _("Soorituskeel"))}
      ${h.th_sort('test.aine_KL', _("Aine"))}
      ${h.th_sort('test.nimi', _("Test"))}
      ${h.th_sort('toimumisaeg.tahised', _("Toimumisaeg"))}
      ${h.th_sort('koht.nimi', _("Soorituskoht"))}
      ${h.th_sort('ruum.tahis', _("Ruum"))}
      ${h.th_sort('kool_koht.nimi', _("Õppimiskoht"))}
      ${h.th(_("Eritingimused"))}
      ${h.th(_("Kinnitatud"))}
      % if not c.hide_reviewed:
      ${h.th(_("Üle vaadatud"))}
      % endif
      ${h.th(_("Ül komplekt"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       tos, lang, isikukood, synnikpv, eesnimi, perenimi, test_nimi, aine_kood, testiosa_nimi, koht_nimi, ruum_tahis, kool_koht_nimi, komplekt_tahis = rcd
       url_edit = h.url('muud_edit_erivajadus', id=tos.id)
    %>
    <tr>
      <td>${isikukood or h.str_from_date(synnikpv)}</td>
      <td>${eesnimi}</td>
      <td>${perenimi}</td>
      <td>${tos.tahised}</td>
      <td>${model.Klrida.get_lang_nimi(lang)}</td>
      <td>${model.Klrida.get_str('AINE', aine_kood)}</td>
      <td>${test_nimi}</td>
      <td>
        % if tos.toimumisaeg:
        ${tos.toimumisaeg.tahised}
        % endif
      </td>
      <td>${koht_nimi}</td>
      <td>${ruum_tahis}</td>
      <td>${kool_koht_nimi}</td>
      <td>
        ${h.link_to(h.literal(tos.get_str_erivajadused('<br/>', kasutamata=True, markused=False) or _("Märkimata")), url_edit)}
      </td>
      <td>${h.sbool(tos.on_erivajadused_kinnitatud)}</td>
      % if not c.hide_reviewed:
      <td>${h.sbool(tos.on_erivajadused_vaadatud)}</td>
      % endif
      <td>${komplekt_tahis}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
