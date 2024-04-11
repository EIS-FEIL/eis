<%namespace name="tab" file='/common/tab.mako'/>
<% 
   edit = c.is_edit and '_edit' or ''
%>
${tab.subdraw('tagastuskotid', h.url('korraldamine_tagastuskotid',
toimumisaeg_id=c.toimumisaeg.id), _("Tagastamata kotid"))}
${tab.subdraw('tagastusymbrikud', h.url('korraldamine_tagastusymbrikud',
toimumisaeg_id=c.toimumisaeg.id), _("Tagastusümbrikud"))}
${tab.subdraw('tagastustoimumised', h.url('korraldamine_tagastustoimumised',
toimumisaeg_id=c.toimumisaeg.id), _("Protokollimata toimumised"))}
