<%inherit file="/common/dlgpage.mako"/>
${h.form(h.url_current())}

<% ch = h.colHelper('col-md-4', 'col-md-8') %>
<div id="transformer">
   <div class="form-group row">
      ${ch.flb(_("Erista tekstiosadena"), 'divunit')}
      <div class="col-md-8" id="divunit">
        <% c.unit = 'W' %>
        ${h.checkbox1('unitc', 'C', checked=c.unitc, label=_("Tähed"), class_="unitc")}
        <br/>
        ${h.checkbox1('unitn', 'N', checked=c.unitn, label=_("Numbrid"), class_="unitc")}
        <br/>
        <div class="d-flex">
        ${h.checkbox1('unity', 'Y', checked=c.unity, label=_("Erisümbolid"), class_="unitc")}
        ${h.text('splitby', c.cplitby, size=8)}
        </div>
        ${h.radio('unit', 'W', label=_("Sõnad"), checkedif=c.unit)}
        <br/>
        ${h.radio('unit', 'S', label=_("Laused"), checkedif=c.unit)}
      </div>
    </div>
    <div class="form-group row">
      ${ch.flb(_("Küsimuse ID"), 'nkood')}
      <div class="col-md-8">
        ${h.text('nkood', c.nkood, class_="identifier", size=10)}
      </div>
    </div>
    <div class="form-group row">
      ${h.checkbox1('vuitype', 1, label=_("Lahendajale kuvatakse märkeruut või raadionupp"))}
    </div>
</div>
  <p>
    ${h.button(_("Salvesta"), id="runtransform")}
    ${h.button(_("Katkesta"), onclick="close_dialog('transformer')")}
  </p>
${h.end_form()}
  
<script>
  $('input.unitc').click(function(){
    $('input[name="unit"]').prop('checked', false);
  });
  $('input[name="unit"]').click(function(){
    $('input.unitc').prop('checked', false);
  });
   $('#runtransform').click(function(){
           $('#transformer_parent').html($('#transformer').clone());
           $('input#transform').val('1');
           set_spinner($('.ui-dialog-title'));
           $('form#form_save').submit();
   });
</script>
