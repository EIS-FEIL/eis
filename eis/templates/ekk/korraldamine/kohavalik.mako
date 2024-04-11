${h.form_save(None, form_name='form_dlg_save', multipart=True)}
${h.rqexp(True, _("Vali õppeasutus õppeasutuse väljal (valikut saab filtreerida piirkonna või maakonna järgi) või laadi failist"))}
<div class="form-wrapper-lineborder mb-2">
  <div class="form-group row">
    ${h.flb3(_("Piirkond"))}
    <div class="col">
            <%
               c.piirkond_id = c.piirkond_id
               c.piirkond_field = 'piirkond_id'
            %>
            <%include file="/admin/piirkonnavalik.mako"/>
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Maakond"))}
    <div class="col">
      ${h.select('maakond_kood', c.maakond_kood, model.Aadresskomponent.get_opt(None),
      empty=True)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Õppeasutused"))}
    <div class="col">
      ${h.select('koht_id', '', [], multiple=True)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Fail"))}
    <div class="col">
      ${h.file('fkoolid')}
    </div>
  </div>
</div>
<div class="text-right">
  ${h.button(_("Salvesta"), onclick="$('form#form_dlg_save').submit();")}
</div>
${h.end_form()}
<script>
$(function(){
  $('select#koht_id').select2({
  ajax: {
    url: '${h.url('pub_formatted_valikud', kood='SOORITUSKOHT', format='json')}',
    dataType: 'json',
    data: function(params){
      var query = {
         term: params.term,
         piirkond_id: $('#form_dlg_save input#piirkond_id').val(),
         tasekood: $('#form_dlg_save select#maakond_kood').val()
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



