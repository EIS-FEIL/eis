<%namespace name="tab" file='/common/tab.mako'/>
${tab.draw('isikuandmed', h.url('nousolekud_isikuandmed'), _('Isikuandmed'), c.tab1)}
${tab.draw('nousolekud', h.url('nousolekud'), _('Nõusolekud'), c.tab1)}
${tab.draw('maaramised', h.url('nousolekud_maaramised'), _('Määramised'), c.tab1)}
${tab.draw('profiil', h.url('nousolekud_profiil'), _('Profiil'), c.tab1)}
