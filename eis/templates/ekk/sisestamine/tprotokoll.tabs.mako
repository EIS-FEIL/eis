<%namespace name="tab" file='/common/tab.mako'/>
${tab.draw('protokollilosalejad', h.url('sisestamine_protokoll_osalejad', toimumisprotokoll_id=c.toimumisprotokoll.id),
_("Testil osalejad"))}
% if request.is_ext() and c.toimumisprotokoll.leidub_suulist:
${tab.draw('helifailid', h.url('sisestamine_protokoll_helifailid',
toimumisprotokoll_id=c.toimumisprotokoll.id), u'Helifailid')}
% endif
