% if not c.testsessioon_id:
${h.form_save(c.item.id)}
${h.hidden('sub', 'kord')}
<table class="table" width="100%" >
  <caption>${_("Testsessioon")}</caption>
  <tr>
    <td>
      ${h.select('testsessioon_id', c.testsessioon_id,
       model.Testsessioon.get_opt(testiliik_kood=c.item.testiliik_kood), empty=True,
        onchange='change_sessioon(this)')}
      <script>
        function change_sessioon(field)
        {
           var sessioon_id = $(field).val();
           if(sessioon_id == '') 
           { 
               ## tühi valik
               $('#dlg_contents').html('');
               return;
           }
           var url = "${h.url('admin_edit_kiirvalik', id=c.item.id, sub='kord', partial=True)}";
           url += '&testsessioon_id=' + sessioon_id;
           $.get(url, function(data){ $('#dlg_contents').replaceWith(data); });
        }
      </script>
    </td>
  </tr>
</table>
% endif

<div id="dlg_contents">
<table width="100%" class="multipleselect list" >
  <caption>Testimiskorrad</caption>
  % for rcd in c.items:
     % if rcd in c.item.testimiskorrad:
        <% checked = True %>
  <tr class="selected">
     % else:
        <% checked = False %>
  <tr>
     % endif
    <td>
      ${h.checkbox('kord_id', rcd.id, checked=checked, class_="selectrow")}
    </td>
    <td>
      ${h.link_to('%s %s' % (rcd.test.nimi, rcd.tahis), 
          h.url('test_kord', test_id=rcd.test.id, id=rcd.id), target='_blank')}
    </td>
  </tr>
  % endfor
  % if len(c.items) == 0 and c.testsessioon_id:
  ${_("Valitud testsessioon ei sisalda ühtki testimiskorda")}
  % endif
</table>

% if len(c.items):
${h.submit()}
% endif
</div>

% if not c.testsessioon_id:
${h.end_form()}
% endif
