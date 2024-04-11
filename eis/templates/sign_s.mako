% if error:
${h.alert_error(error)}
% else:
<div class="alert alert-secondary">
<p>
${_("Allkirjastamissõnum on saadetud telefoni.")}
  <br/>
  ${h.spinner()}
  ${_("Palun veendu, et telefonis on kontrollkood")}
  <span style="font-size:200%;">${challengeID}</span>
</p>
<script>
$(function(){
  var data = {'container_id':'${container_id}', 'signature_id': '${signature_id}', 'dformat':'${dformat}', 'sub':'finalize_signature', 'op':'smartid'};
  dialog_load("/${request.url.split('/',3)[-1]}", data, 'POST', $('div#ddoc_status'));
});
</script>
</div>
% endif
