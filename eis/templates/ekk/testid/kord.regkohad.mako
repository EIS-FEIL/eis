${h.form_save(c.item.id, form_name='form_dlg_save', multipart=True, target="form_dlg_target")}
${h.hidden('sub', c.sub)}

<table width="100%" class="table" >
  <col width="120"/>
  <col/>
  <tr>
    <td class="fh">${_("Piirkond")}</td>
    <td colspan="4">
            <%
               c.piirkond_id = c.piirkond_id
               c.piirkond_field = 'piirkond_id'
            %>
            <%include file="/admin/piirkonnavalik.mako"/>
    </td>
  </tr>
  <tr>
    <td class="fh">${_("Maakond")}</td>
    <td>
      ${h.select('maakond_kood', c.maakond_kood, model.Aadresskomponent.get_opt(None),
      empty=True, wide=False)}
    </td>
  </tr>
  <tr>
    <td class="fh" valign="top">${_("Õppeasutused")}</td>
    <td>
      <%
        kohad = c.item.regkohad
        koht_opt = [(r.id, r.nimi) for r in kohad]
        selected_id = [r[0] for r in koht_opt]
      %>
      ${h.select('koht_id', selected_id, koht_opt, multiple=True)}
    </td>
  </tr>
  <tr>
    <td class="fh">${_("Fail")}</td>
    <td>
      ${h.file('fkoolid')}
    </td>
  </tr>
</table>
${h.button(_("Salvesta"), onclick="$('form#form_dlg_save').submit();")}
${h.end_form()}
<script>
function cp_result(){
  var res = $('div.result');
  if(res.length) {
    ## kui on tulemuste div, siis kopeerime sisu suurde aknasse ja suleme dialoogi
    res.removeClass('result');
    $('.regkohad-list').html(res);
    close_dialog();
  }
}
$(function(){
  $('select#koht_id').select2({
  ajax: {
    url: '${h.url('pub_formatted_valikud', kood='SOORITUSKOHT', format='json')}',
    dataType: 'json',
    data: function(params){
      var query = {
         term: params.term,
         piirkond_id: $('input#piirkond_id').val(),
         tasekood: $('select#maakond_kood').val()
      }
      return query;
    },
    processResults: function(data){
      var results = $.map(data, function(obj){
        obj.text = obj.value;
        return obj;
      });
      return {results: results};
    }
  },
  width: '100%',
  multiple: true,
  language: '${request.localizer.locale_name}'
});
});
</script>
<iframe name="form_dlg_target" width="0" height="0" style="display:none" onload="if(typeof(move_to_dlg)=='function'){move_to_dlg(this);if(typeof(cp_result)=='function') cp_result();}"></iframe>


