## -*- coding: utf-8 -*- 
## $Id: otsing_list.mako 857 2016-09-14 17:31:06Z ahti $         
${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('test.nimi', _("Test"))}
      ${h.th_sort('koht.nimi', _("Testikoht"))}
      ${h.th_sort('testikoht.tahised', _("Tähis"))}
      ${h.th_sort('toimumisprotokoll.lang', _("Keel"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       toimumisprotokoll, test_nimi, koht_nimi, tk_tahised, r_tahis = rcd
       url_edit = h.url('protokoll_osalejad', toimumisprotokoll_id=toimumisprotokoll.id)
    %>
    <tr>
      <td>${h.link_to(test_nimi, url_edit)}</td>
      <td>${koht_nimi} 
        % if r_tahis:
        ${_("ruum")} ${r_tahis}
        % endif
      </td>
      <td>${toimumisprotokoll.tahistus}</td>
      <td>
        % if toimumisprotokoll.lang:
        ${model.Klrida.get_lang_nimi(toimumisprotokoll.lang)}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
