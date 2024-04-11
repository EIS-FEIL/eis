<%namespace name="tab" file='/common/tab.mako'/>
<% 
   edit = c.is_edit and '_edit' or ''
%>
% if c.toimumisaeg.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_KP, const.VASTVORM_I, const.VASTVORM_SH):
${tab.subdraw('hindajad',h.url('hindamine_hindajad',toimumisaeg_id=c.toimumisaeg.id),
_("Esmane (I ja II) hindamine"), c.tab2)}
% endif
${tab.subdraw('hindajad3',
h.url('hindamine_hindajad3',toimumisaeg_id=c.toimumisaeg.id), 
_("Kolmas hindamine"), c.tab2)}
${tab.subdraw('suunamised',
h.url('hindamine_suunamised',toimumisaeg_id=c.toimumisaeg.id),
_("Ümbersuunamine"), c.tab2)}
${tab.subdraw('ymbrikud',
h.url('hindamine_analyys_ymbrikud',toimumisaeg_id=c.toimumisaeg.id), _("Testitööde ümbrikud"))}
% if c.hindaja:
${tab.subdraw('vastajad',
h.url('hindamine_hindajavaade_vastajad',toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.hindaja.id), _("Hindaja eelvaade"), c.tab2)}
% elif c.labiviija:
## SH hindaja
${tab.subdraw('vastajad',
h.url('hindamine_hindajavaade_vastajad',toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.labiviija.id), _("Hindaja eelvaade"), c.tab2)}
% endif
