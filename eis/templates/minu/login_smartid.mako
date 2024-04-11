<div>
% if err:
${h.alert_error(err.replace('\n', '<br/>'))}
<script>
  $('div.sisene_smartid').show();
</script>
% else:
  ${h.spinner()}
  <div class="alert alert-secondary">
    ${_("Sõnum on saadetud kontrollkoodiga:")}
  <span style="font-size:200%;">${challengeID}</span>
  </div>
  <script>
      $('div.sisene_smartid').hide();
      var data = {'session_id':'${session_id}', 'request_url':'${c.request_url}'};
      dialog_load("${h.url('login', action='signin_smartid2')}", data, 'POST', $('#smartidstatus'));
  </script>
% endif
</div>
