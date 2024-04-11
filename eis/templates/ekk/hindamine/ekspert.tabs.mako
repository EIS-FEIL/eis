<%namespace name="tab" file='/common/tab.mako'/>
<% 
   edit = c.is_edit and '_edit' or ''
%>
${tab.subdraw('eksperttood',
h.url('hindamine_eksperttood',toimumisaeg_id=c.toimumisaeg.id), _("Hinnatavad tööd"))}
% if c.user.has_permission('ekspertryhmad', const.BT_SHOW, obj=c.test):
${tab.subdraw('ekspertryhmad',
h.url('hindamine_ekspertryhmad',toimumisaeg_id=c.toimumisaeg.id), _("Ekspertrühm"))}
% endif
% if c.sooritus:
${tab.subdraw('ekspertkogumid',
h.url('hindamine_ekspert_kogum', toimumisaeg_id=c.toimumisaeg.id, id=c.sooritus.id), _("Testitöö"), c.tab2)}
% endif

% if c.sooritus and c.sooritus.sooritaja.vaie_esitatud:
${tab.subdraw('ettepanekud',
h.url('hindamine_edit_ettepanek',toimumisaeg_id=c.toimumisaeg.id, id=c.sooritus.id), _("Ettepanek"))}
% endif
