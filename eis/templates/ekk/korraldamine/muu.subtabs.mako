<%namespace name="tab" file='/common/tab.mako'/>
<% 
   edit = c.is_edit and '_edit' or ''
%>
${tab.subdraw('eksamilogi', h.url('korraldamine_eksamilogi',
toimumisaeg_id=c.toimumisaeg.id), _("Eksamilogi"))}
${tab.subdraw('markused', h.url('korraldamine_markused',
toimumisaeg_id=c.toimumisaeg.id), _("Märkused"))}
${tab.subdraw('aadressid', h.url('korraldamine_aadressid',
toimumisaeg_id=c.toimumisaeg.id), _("Sooritajate aadressid"))}
${tab.subdraw('eritingimused', h.url('korraldamine_eritingimused',
toimumisaeg_id=c.toimumisaeg.id), _("Eritingimused"))}
% if c.testiosa.vastvorm_kood in (const.VASTVORM_SP, const.VASTVORM_SH):
${tab.subdraw('helifailid', h.url('korraldamine_helifailid',
toimumisaeg_id=c.toimumisaeg.id), _("Helifailid"))}
% endif
% if c.test.testiliik_kood == const.TESTILIIK_SISSE:
${tab.subdraw('kandideerimine', h.url('korraldamine_kandideerimine',
toimumisaeg_id=c.toimumisaeg.id), _("Kandideerimine"))}
% endif
