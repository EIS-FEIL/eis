Subject: Hindajaks määramise teade
<p>
  Lugupeetud ${isik_nimi}
</p>
<p>
  Olete määratud ${test_nimi}
  % if koht_nimi:
  (${koht_nimi}, toimumise aeg ${millal})
  % else:
  (toimumise aeg ${millal})
  % endif
  % if hk_tahised:
  hindamiskogumite ${hk_tahised}
  % elif hk_tahis:
  hindamiskogumi ${hk_tahis}
  % endif
  hindajaks.
  % if algus:
  Hindamise algusaeg on ${algus}.
  % endif
  % if tahtaeg:
  Hindamise tähtaeg on ${tahtaeg}.
  % endif
</p>
<p>
  Eksamite infosüsteem
</p>
