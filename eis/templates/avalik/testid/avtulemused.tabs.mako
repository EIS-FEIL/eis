<%namespace name="tab" file='/common/tab.mako'/>
% if c.test.on_jagatudtoo:
${tab.subdraw('avylesanded', h.url('test_tootulemused', test_id=c.test_id, testiruum_id=c.testiruum_id), _('Tulemused ülesannete kaupa'), c.tab2)}
% else:
${tab.subdraw('avtulemused', h.url('test_avtulemused', test_id=c.test_id, testiruum_id=c.testiruum_id), _('Testi tulemus', c.tab2))}
% if not c.test.pallideta:
${tab.subdraw('avylesanded', h.url('test_avylesanded', test_id=c.test_id, testiruum_id=c.testiruum_id), _('Tulemused ülesannete kaupa'), c.tab2)}
% endif
% endif

% if not c.test.pallideta and not c.test.opetajale_peidus:
${tab.subdraw('avanalyys', h.url('test_avanalyys', test_id=c.test_id, testiruum_id=c.testiruum_id), _('Vastuste analüüs'), c.tab2)}
% endif
