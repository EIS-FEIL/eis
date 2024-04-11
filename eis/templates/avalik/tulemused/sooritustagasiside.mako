<% c.test = c.sooritus.sooritaja.test %>
% if c.test.diagnoosiv:
<h3>${_("Tagasiside")}</h3>
<div class="alert alert-secondary">
  <%
    tts = c.test.testitagasiside
  %>
  % if tts:
  <div>${tts.sissejuhatus_opilasele}</div>
  % endif

  % for npv in c.sooritus.npvastused:
  <div>${npv.id} ${npv.nvaartus}</div>
  % endfor

  % if tts:
  <div>${tts.kokkuvote_opilasele}</div>
  % endif
</div>
% endif
