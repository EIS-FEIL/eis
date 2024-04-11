<%include file="/common/message.mako"/>

${h.form_search(h.url_current('index'), 'form_search_oh')}
<div class="gray-legend p-3">
  <div class="row form-group">
    ${h.flb3(_("Õpetaja"), 'opetaja_id')}
    <div class="col">
      <% opt_opetaja = [('','')] + c.opt_opetaja %>
      ${h.select2('opetaja_id', c.opetaja_id, opt_opetaja)}      
    </div>
  </div>
</div>
${h.end_form()}

% if c.pedagoog_id:
${h.form(h.url_current('create'), method='post')}
${h.hidden('pedagoog_id', c.pedagoog_id)}

<div class="p-3">
  <div class="row form-group">
    ${h.flb3(_("Planeeritud tööde arv"), 'planeeritud_toode_arv')}
    <div class="col">
      ${h.posint5('planeeritud_toode_arv', c.planeeritud_toode_arv)}
    </div>
  </div>
  
  <%
    tyy = [ty for ty in c.testiosa.testiylesanded if not ty.arvutihinnatav]
  %>
  % if len(tyy) > 1:
  <div class="row form-group">
    ${h.flb3(_("Ülesanded"), 'ylesanded')}
    <div class="col" id="ylesanded">
      % for ty in tyy:
      <% checked = not c.tyy_id or ty.id in c.tyy_id %>
      ${h.checkbox('ty_id', ty.id, checked=checked, label=ty.tahis)}
      % endfor
    </div>
  </div>
  % endif
</div>

${h.submit_dlg('Salvesta', id='add_isik')}
${h.end_form()}
% endif


<script>
  $('#opetaja_id').change(function(){
    if($(this).val() != '')
       submit_dlg(this, null, 'get', false, null);
  });
</script>
