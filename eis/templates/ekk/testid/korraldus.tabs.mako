<%namespace name="tab" file='/common/tab.mako'/>
${tab.subdraw('kogumid', h.url('test_kogumid', test_id=c.test.id), _("Ülesannete kogumid"), c.tab2)}
${tab.subdraw('korrad', h.url('test_korrad', test_id=c.test.id), _("Testimiskorrad ja parameetrid"), c.tab2)}

