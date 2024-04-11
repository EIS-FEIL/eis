<%namespace name="tab" file='/common/tab.mako'/>
${tab.draw('taotlemine', h.url('muud_skannid_taotlemised'), _("Taotluse esitamine"))}
${tab.draw('tellimised', h.url('muud_skannid_tellimised'), _("Tellitud eksamitööd"))}
${tab.draw('laadimine', h.url('muud_skannid_laadimised'), _("Üles laadimine"))}
