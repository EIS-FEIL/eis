${h.pager(c.items)}
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('testimiskord.test_id', _("Testi ID"))}
      ${h.th_sort('test.nimi', _("Testi nimetus"))}
      ${h.th_sort('toimumisaeg.tahised', _("Tähis"))}
      ${h.th_sort('toimumisaeg.alates', _("Toimumisaeg"))}
      ${h.th_sort('vastvorm_kood', _("Vastamise vorm"))}
      ${h.th(_("Ülesanded"))}
      ${h.th(_("Sisestamisel"))}
      ${h.th(_("Kinnitatud"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
      test = rcd.testimiskord.test
      if c.user.has_permission('ekk-hindamine', const.BT_SHOW, obj=test):
         url_edit = h.url('hindamine_arvutused', toimumisaeg_id=rcd.id)
      elif c.user.has_permission('vastusteanalyys', const.BT_SHOW, obj=test):
         url_edit = h.url('hindamine_analyys_vastused', toimumisaeg_id=rcd.id)
      else:
         url_edit = None
    %>
    <tr>
      <td>${test.id}</td>
      <td>
        % if url_edit:
        ${h.link_to(test.nimi, url_edit)}
        % else:
        ${test.nimi}
        % endif
      </td>
      <td>${rcd.tahised}</td>
      <td>${rcd.millal}</td>
      <td>${rcd.testiosa.vastvorm_nimi}</td>
      <td>
        <%
         vastamata = model.Hindamiskysimus.query.\
           join((model.Valitudylesanne, model.Valitudylesanne.ylesanne_id==model.Hindamiskysimus.ylesanne_id)).\
           join(model.Valitudylesanne.komplekt).\
           join(model.Komplekt.toimumisajad).\
           filter(model.Toimumisaeg.id==rcd.id).\
           filter(model.Hindamiskysimus.vastus==None).count()
        %>
        % if vastamata:
        <span style="font-color:red">${vastamata}</span>
        % endif
      </td>
      <td>${h.sbool(rcd.hinnete_sisestus)}</td>
      ##<td></td>
      <td>${h.sbool(rcd.tulemus_kinnitatud)}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
