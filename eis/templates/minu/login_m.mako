<div>
% if err:
${h.alert_error(err.replace('\n', '<br/>'))}

<script>
  $('div.sisene_m').show();
</script>
% else:
${h.spinner()}
<div class="alert alert-secondary">
  ${_("Sõnum on saadetud kontrollkoodiga:")}
  <span style="font-size:200%;">${challengeID}</span>
</div>
  <script>
    $('div.sisene_m').hide();
    var data = {'sesscode':'${sesscode}', 'request_url':'${c.request_url}'};
    dialog_load("${h.url('login', action='signin_m2')}", data, 'POST', $('#mobstatus'));
  </script>
% endif
</div>
