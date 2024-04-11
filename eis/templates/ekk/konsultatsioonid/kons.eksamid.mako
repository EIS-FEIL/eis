${h.form_save(c.item.id)}
${h.hidden('sub', 'eksam')}
<table class="table" >
  <col width="40"/>
  <col width="100"/>
  <col/>
  % for rcd in c.items:
  <% tkord_id, test_id, tk_tahis, test_nimi = rcd %>
  <tr>
    <td>${h.checkbox('kord_id', tkord_id, checked=tkord_id in c.eksamid_id)}</td>
    <td>${test_id}-${tk_tahis}</td>
    <td>
      % if c.on_kons:
      ${h.link_to(test_nimi, h.url('test_edit_kord', test_id=test_id, id=tkord_id))}
      % else:
      ${h.link_to(test_nimi, h.url('konsultatsioon_edit_kord', test_id=test_id, id=tkord_id))}
      % endif
    </td>
  </tr>
  % endfor
  % if not len(c.items):
  <td colspan="3">
    % if c.on_kons:
    ${_("Konsultatsiooniga samal testsessioonil, samas õppeaines ja samal keeleoskuse tasmeel ei ole ühtki testi.")}
    % else:
    ${_("Testiga samal testsessioonil, samas õppeaines ja samal keeleoskuse tasemel ei ole ühtki konsultatsiooni.")}
    % endif
  </td>
  % endif
</table>
<div class="text-right mt-2">
  ${h.submit_dlg()}
</div>
${h.end_form()}
