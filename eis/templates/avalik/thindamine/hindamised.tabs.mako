## -*- coding: utf-8 -*- 
<%namespace name="tab" file='/common/tab.mako'/>
${tab.subdraw('ylesandehindamised', h.url('test_ylesandehindamised', test_id=c.test_id, testiruum_id=c.testiruum_id), _('Ülesannete kaupa hindamine'), c.tab2)}
${tab.subdraw('toohindamised', h.url('test_toohindamised', test_id=c.test_id, testiruum_id=c.testiruum_id), _('Tööde kaupa hindamine'), c.tab2)}
