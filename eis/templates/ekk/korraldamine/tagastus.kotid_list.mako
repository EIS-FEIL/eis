${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('turvakott.kotinr', _("Turvakott"))}
      ${h.th_sort('koht.nimi', _("Soorituskoht"))}
      ${h.th_sort('testipakett.lang', _("Keel"))}
      ${h.th_sort('turvakott.staatus', _("Olek"))}
    </tr>
  </thead>
  <tbody>
    % for n, (kott, pk_lang, koht_nimi) in enumerate(c.items):
    <tr>
      <td>
        ${kott.kotinr}</td>
      <td>${koht_nimi}</td>
      <td>${model.Klrida.get_lang_nimi(pk_lang)}</td>
      <td>${kott.staatus_nimi}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
