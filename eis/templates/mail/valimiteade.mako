Subject: Teade valimisse kuulumise kohta
<p>
  Lugupeetud ${kool_nimi}
</p>
<p>
  Anname teada, et Teie kooli ${klassid} klassi ${opilastearv} õpilast kuuluvad ${test_nimi} valimisse.
  % if millal and on_testiliik_t:
  Tasemetöö toimub ${millal}.
  % elif millal:
  Test toimub ${millal}.
  % endif
  % if millalvalim:
  Valimisse kuuluvad õpilased sooritavad testi ${millalvalim}.
  % endif
</p>
<p>
  Valimisse kuuluvate õpilaste nimekirja näete <a href="${url}">EISis</a>.
  % if reg_kuni:
  Soovi korral saate õpilasi juurde registreerida ${reg_alates or ''} kuni ${reg_kuni}.
  % endif
</p>
<p>
  ${user_nimi}
</p>
