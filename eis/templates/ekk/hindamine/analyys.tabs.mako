<%namespace name="tab" file='/common/tab.mako'/>
<% 
   edit = c.is_edit and '_edit' or ''
%>
% if c.user.has_permission('hindamisanalyys', const.BT_SHOW, obj=c.test):
${tab.subdraw('protokollid',
h.url('hindamine_analyys_protokollid',toimumisaeg_id=c.toimumisaeg.id), _("Hindamise protokollid"))}
${tab.subdraw('probleemid',
h.url('hindamine_analyys_probleemid',toimumisaeg_id=c.toimumisaeg.id), _("Hindamisprobleemid"))}
${tab.subdraw('hindamised3',
h.url('hindamine_analyys_hindamised3',toimumisaeg_id=c.toimumisaeg.id), _("Kolmas hindamine"))}
${tab.subdraw('analyyshindajad',
h.url('hindamine_analyys_hindajad',toimumisaeg_id=c.toimumisaeg.id), _("Läbiviijate analüüs"))}
% endif
${tab.subdraw('analyysvastused',
h.url('hindamine_analyys_vastused',toimumisaeg_id=c.toimumisaeg.id), _("Vastuste analüüs"))}
% if c.user.has_permission('hindamisanalyys', const.BT_SHOW, obj=c.test):
${tab.subdraw('analyyskoolid',
h.url('hindamine_analyys_koolid',toimumisaeg_id=c.toimumisaeg.id), _("Koolide analüüs"))}

${tab.subdraw('sarnasedvastused',
h.url('hindamine_analyys_sarnasedvastused',toimumisaeg_id=c.toimumisaeg.id),
_("Sarnased vastused"))}

% if c.test.on_tseis:
${tab.subdraw('mootmisvead',
h.url('hindamine_analyys_mootmisvead',toimumisaeg_id=c.toimumisaeg.id), _("Mõõtmisvea kontroll"))}
% endif

% if c.sooritus:
${tab.subdraw('testitood',
h.url('hindamine_analyys_testitoo', toimumisaeg_id=c.toimumisaeg.id, id=c.sooritus.id), c.sooritus.tahised)}
% endif
% endif
