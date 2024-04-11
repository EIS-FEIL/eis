<%namespace name="tab" file='/common/tab.mako'/>
${tab.draw('osalejad', h.url('protokoll_osalejad', toimumisprotokoll_id=c.toimumisprotokoll.id),
_("Testil osalejad"))}

% if request.is_ext() and not c.ainult_opetaja_id:
% if c.toimumisprotokoll.leidub_suulist:
${tab.draw('helifailid', h.url('protokoll_helifailid',
toimumisprotokoll_id=c.toimumisprotokoll.id), _("Helifailid"))}
% endif
% if c.toimumisprotokoll.testimiskord.on_turvakotid:
${tab.draw('turvakotid', h.url('protokoll_turvakotid', toimumisprotokoll_id=c.toimumisprotokoll.id),
_("Turvakotid"))}
% endif
${tab.draw('ruumifailid', h.url('protokoll_ruumifailid', toimumisprotokoll_id=c.toimumisprotokoll.id),
_("Ruumide failid"))}
% if not c.toimumisaeg1.prot_eikinnitata:
% if c.user.has_permission('toimumisprotokoll', const.BT_UPDATE, c.toimumisprotokoll) or c.user.has_permission('tprotadmin', const.BT_UPDATE, c.toimumisprotokoll):
${tab.draw('kinnitamine', h.url('protokoll_kinnitamine', toimumisprotokoll_id=c.toimumisprotokoll.id),_("Kinnitamine"))}
% endif
% endif
% endif
