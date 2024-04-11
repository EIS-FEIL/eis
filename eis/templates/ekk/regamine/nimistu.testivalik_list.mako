## -*- coding: utf-8 -*- 
% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
${h.form(h.url('regamine_nimistu_testivalik'), method='post')}
${h.hidden('testiliik', c.testiliik)}
<table  class="table table-borderless table-striped" width="100%">
  <col width="70px"/>
  <thead>
    <tr>
      <th></th>
      ${h.th(_("Test"))}
      ${h.th(_("Toimumisaeg"))}
      ${h.th(_("Aeg"))}
      ${h.th(_("Testi liik"))}
    </tr>
  </thead>
  <tbody>
    % for rcd in c.items:
    <tr>
      <td>
        ${h.checkbox('kord_id', rcd.id, onclick='toggle_saada()', class_="kord_id", checkedif=c.korrad_id)}
      </td>
      <td>${rcd.test.nimi}</td>
      <td>${rcd.tahised}</td>
      <td>${rcd.millal}</td>
      <td>${rcd.test.testiliik_nimi}</td>
    </tr>
    % endfor
  </tbody>
</table>

<script>
  function toggle_saada()
  {
  var visible = ($('input:checked.kord_id').length > 0);
  $('div#add').toggleClass('d-none', !visible);
  }
  $(function(){
     toggle_saada();
  });
</script>
<div id="add" class="d-none text-right">
${h.submit(_("Jätka"), id='lisavalikutele', mdicls2='mdi-arrow-right-circle')}
</div>
${h.end_form()}

% endif
