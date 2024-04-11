## pooleli avalduselt lahkumisel antakse hoiatus
% if c.testiliik and c.kasutaja.get_reg_sooritajad(c.testiliik, kinnitamata=True):
## kui on pooleli registreeringuid
<script>
  being_clicked_args = {message: "${_('Avaldus on kinnitamata, kas soovid registreerimise katkestada?')}",
  % if c.continue_url:
                        continue_text: "${_("Kinnita avaldus")}",
                        continue_url: "${c.continue_url}",
  % else:
                        continue_text: "${_("Jätka sisestamist")}",
  % endif
                        cancel_text: "${_("Tühista registreerimine")}",
                        cancel_url: "${h.url('regamine_avaldus_delete_kinnitamine', testiliik=c.testiliik)}",
  };
</script>
% endif               
