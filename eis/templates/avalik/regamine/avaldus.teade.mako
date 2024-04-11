<% c.kinnitamata = list(c.kasutaja.get_reg_sooritajad(c.testiliik, peitmata=True, regamine=True, kinnitamata=True)) %>
% if c.kinnitamata:
<div class="alert alert-secondary fade show my-2">
  ${_("Registreerimine on veel kinnitamata.")}
  ${_("Registreerimise taotlust ei arvestata, kui seda pole kinnitatud.")}
  ${_("Kinnitamiseks on vajalik läbida kõik registreerimise sammud.")}
</div>
% endif
