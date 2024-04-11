% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
${h.form(url=h.url('regamised'), method='get', id="form_list")}
${h.hidden('regteade', '1', class_="regteade")}
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      <th>
        % if c.tasumata or c.regamata:
        ${h.checkbox1('j_all', 1, title=_("Vali kõik"))}
        % endif
      </th>
      ${h.th_sort('kasutaja.perenimi kasutaja.eesnimi', _("Sooritaja"))}
      ${h.th_sort('sooritaja.meeldetuletusaeg', _("Meeldetuletus"))}
      ${h.th_sort('test.nimi sooritaja.kursus_kood', _("Test"))}
      ${h.th_sort('testimiskord.alates', _("Toimumise aeg"))}
      ${h.th(_("Reg aeg"))}
      ${h.th(_("Registreerija"))}
      ${h.th_sort('sooritaja.staatus', _("Olek"))}
      ${h.th_sort('sooritaja.tasutud', _("Tasutud"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% k = rcd.kasutaja %>
    <tr>
      <td>
        % if c.tasumata or c.regamata:
         <%
           cbcls = ''
           if rcd.staatus == const.S_STAATUS_TASUMATA:
              cbcls += ' j-tasumata'
           if rcd.staatus == const.S_STAATUS_REGAMATA:
              cbcls += ' j-regamata'
           if rcd.staatus < const.S_STAATUS_POOLELI:
              cbcls += ' j-tegemata'                      
         %>
         % if cbcls:
           ${h.checkbox('j_id', rcd.id, onclick="toggle_j()", class_='nosave j-id' + cbcls, title=_("Vali rida"))}
         % endif
       % endif
      </td>
      <td>
        ${h.link_to('%s, %s' % (k.nimi, k.isikukood or h.str_from_date(k.synnikpv)), 
                    h.url('regamine', id=rcd.id))}
      </td>
      <td>
        % if rcd.meeldetuletusaeg:
        ${h.str_from_datetime(rcd.meeldetuletusaeg)}
        % else:
        <div style="color:red">${_("Saatmata")}</div>
        % endif
      </td>
      <td>${rcd.testimiskord.test.nimi}
        ${rcd.testimiskord.test_id}-${rcd.testimiskord.tahis}
        % if rcd.kursus_kood:
        (${rcd.kursus_nimi})
        % endif
      </td>
      <td>${rcd.testimiskord.millal}</td>
      <td>${h.str_from_datetime(rcd.reg_aeg)}</td>
      <td>
        % if rcd.regviis_kood == const.REGVIIS_KOOL_EIS:
        <% koht = rcd.esitaja_koht %>
        ${koht and koht.nimi or ''}
        % else:
        ${rcd.regviis_nimi}
        % endif
      </td>
      <td>${rcd.staatus_nimi}</td>
      <td>${h.sbool(rcd.tasutud)}</td>
    </tr>
    % endfor
  </tbody>
</table>

<script>
  function toggle_j()
  {
     $('#b_regamata').toggle($('input.j-regamata:checked').length > 0);
     $('#b_tasumata').toggle($('input.j-tasumata:checked').length > 0);  
  }
  $(function(){
     toggle_j();
     $('input[name="j_all"]').click(function(){
         $('input[name="j_id"]').prop('checked', $(this).prop('checked'));
         toggle_j();
     });
  });
</script>

% endif
