<%namespace name="tab" file='/common/tab.mako'/>
${tab.draw('valjastamine', h.url('muud_tunnistused_valjastamised'), _("Väljastamine"))}
${tab.draw('salvestamine', h.url('muud_tunnistused_salvestamised'), _("Salvestamine"))}
${tab.draw('avaldamine', h.url('muud_tunnistused_avaldamised'), _("Avaldamine"))}
${tab.draw('tyhistamine', h.url('muud_tunnistused_tyhistamised'), _("Tühistamine"))}
