<%namespace name="tab" file='/common/tab.mako'/>
${tab.subdraw('tagasisideviis', h.url('test_tagasiside_viis', test_id=c.test.id, testiosa_id=c.testiosa and c.testiosa.id or 0), _("Tulemuste kuvamine"))}

##<% disabled = c.test.tagasiside_mall is None %>
<% disabled = False %>
${tab.subdraw('tagasisidetunnused', h.url('test_tagasiside_tunnused', test_id=c.test.id, testiosa_id=c.testiosa and c.testiosa.id or 0), _("Tunnused"), disabled=disabled)}
${tab.subdraw('tagasisideatgrupid', h.url('test_tagasiside_atgrupid', test_id=c.test.id, testiosa_id=c.testiosa and c.testiosa.id or 0), _("Tunnuste grupid"), c.tab2, disabled=disabled)}
% if c.test.tagasiside_mall == const.TSMALL_DIAG:
${tab.subdraw('tagasisidensgrupid', h.url('test_tagasiside_nsgrupid', test_id=c.test.id, testiosa_id=c.testiosa and c.testiosa.id or 0), _("Tagasiside grupid"), c.tab2, disabled=disabled)}
% endif
${tab.subdraw('tagasisideylgrupid', h.url('test_tagasiside_ylgrupid', test_id=c.test.id, testiosa_id=c.testiosa and c.testiosa.id or 0), _("Ülesandegrupid"), c.tab2, disabled=disabled)}
% if c.tvorm_id:
${tab.subdraw('tagasisidevormid', h.url('test_tagasiside_edit_vorm', test_id=c.test.id, testiosa_id=c.testiosa and c.testiosa.id or 0, id=c.tvorm_id), _("Tagasisidevorm"), c.tab2, disabled=disabled)}
% else:
${tab.subdraw('tagasisidevormid', h.url('test_tagasiside_vormid', test_id=c.test.id, testiosa_id=c.testiosa and c.testiosa.id or 0), _("Tagasisidevorm"), c.tab2, disabled=disabled)}
% endif

% if c.tvorm_id:
${tab.subdraw('tagasisideeelvaade', h.url('test_tagasiside_eelvaade1', test_id=c.test.id, testiosa_id=c.testiosa and c.testiosa.id or 0, id=c.tvorm_id), _("Eelvaade"), c.tab2, disabled=disabled)}
% else:
${tab.subdraw('tagasisideeelvaade', h.url('test_tagasiside_eelvaade', test_id=c.test.id, testiosa_id=c.testiosa and c.testiosa.id or 0), _("Eelvaade"), c.tab2, disabled=disabled)}
% endif

