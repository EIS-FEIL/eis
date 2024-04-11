## Ühe aadressi valimine ADSi komponentidest
## enne include peab olema seatud c.piirkond_id ja c.piirkond_field ja c.aadress_obj
## võib olla seatud c.piirkond_on_change ja c.piirkond_filtered

% if not c.is_edit or c.aadress_is_not_edit:
  % if c.aadress_obj:
  ${c.aadress_obj.tais_aadress}
  % endif
% else:
<%
  c.aadressivalik_id = 'aadressivalik_%s' % h.rnd()
  if c.aadress and c.aadress.id:
      #opt_adr = [{'id': c.aadress.id, 'text': c.aadress.tais_aadress}]
      opt_adr = [(c.aadress.id, c.aadress.tais_aadress)]
  else:
      opt_adr = []
%>
<script>
function on_select2_${c.aadressivalik_id}()
{
  $('#${c.aadressivalik_id} input[name="a_normimata"]').val('');
}
</script>
<div id="${c.aadressivalik_id}" class="aadressivalik">
  ${h.select2('a_adr_id', c.aadress and c.aadress.id, opt_adr,
  url=h.url('pub_formatted_valikud', kood='AADRESS'),
  on_select='on_select2_%s' % c.aadressivalik_id, allowClear=True)}
  <label for="a_normimata">${_("või muu aadress")}:</label>
  ${h.text('a_normimata', c.aadress_obj and c.aadress_obj.normimata or '')}
</div>
% endif
