${_("Sooritajad, kelle tulemus erineb hilisemast vähemalt {p} palli").format(p='<span class="brown">%s</span>' % c.erinevus)}

${h.pager(c.items)}
% if c.items:

<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('kasutaja.isikukood', _("Isikukood"))}
      ${h.th_sort('sooritaja.algus', _("Kuupäev"))}
      ${h.th_sort('sooritaja.pallid', u'T')}
      ${h.th_sort('sooritaja.tulemus_protsent', u'%')}
      % for descr in c.headers1:
      ${h.th(descr)}
      % endfor
      ${h.th_sort('sooritaja2.algus', _("Kuupäev"))}
      ${h.th_sort('sooritaja2.pallid', u'T')}
      ${h.th_sort('sooritaja2.tulemus_protsent', u'%')}
      % for descr in c.headers2:
      ${h.th(descr)}
      % endfor      
      % if c.test.keeletase_kood:
      ${h.th(_("Tase"))}
      % endif
      ${h.th_sort('abs(sooritaja.pallid-sooritaja2.pallid)', _("Vahe"))}
      ${h.th_sort('testimiskord2.aasta', _("Aasta"))}
    </tr>
  </thead>
  <tbody>
    % for rcd in c.items:
    <% 
       ik, synnikpv, sooritaja_id, algus, pallid, tulemus_protsent,\
                     sooritaja2_id, algus2, pallid2, tulemus_protsent2,\
                     test2_id, keeletase2, aasta2, vahe = rcd
       row1 = c.get_alatulemused(sooritaja_id, c.alaosaindeks1)
       row2 = c.get_alatulemused(sooritaja2_id, c.alaosaindeks2)
    %>
    <tr>
      <td>${ik}</td>
      <td>${h.str_from_date(algus)}</td>
      <td>${h.fstr(pallid)}</td>
      <td>${h.fstr(tulemus_protsent)}%</td>
      % for r in range(len(c.headers1)):
      <td>${row1.get(r)}</td>
      % endfor

      <td style="border-left: 3px #e4882a solid;">${h.str_from_date(algus2)}</td>
      <td>${h.fstr(pallid2)}</td>
      <td>${h.fstr(tulemus_protsent2)}%</td>      
      % for r in range(len(c.headers2)):
      <td>${row2.get(r)}</td>
      % endfor
      % if c.test.keeletase_kood:
      <td>${model.Klrida.get_str('KEELETASE', keeletase2, ylem_kood=c.test.aine_kood)}</td>
      % endif
      <td style="border-left: 3px #e4882a solid;">${h.fstr(vahe)}</td>
      <td>${aasta2}</td>
    </tr>
    % endfor
  </tbody>
</table>

% endif
