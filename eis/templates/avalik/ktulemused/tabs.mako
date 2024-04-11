<%namespace name="tab" file='/common/tab.mako'/>
% if c.FeedbackReport.init_kirjeldus(handler, c.test, None, c.kursus, check=True):
${tab.draw('kirjeldus', h.url('ktulemused_kirjeldus', test_id=c.test.id, testimiskord_id=c.testimiskord.id, kursus=c.kursus or ''), _("Testi kirjeldus"), c.tab1)}
% endif
${tab.draw('osalejad', h.url('ktulemused_osalejad', test_id=c.test.id, testimiskord_id=c.testimiskord.id, kursus=c.kursus or ''), _("Osalejad"), c.tab1)}
% if c.FeedbackReport.init_gruppidetulemused(handler, c.test, None, c.kursus, check=True):
${tab.draw('gruppidetulemused', h.url('ktulemused_gruppidetulemused', test_id=c.test.id, testimiskord_id=c.testimiskord.id, kursus=c.kursus or ''), _("Gruppide tulemused"), c.tab1)}
% endif
% if c.FeedbackReport.init_osalejatetulemused(handler, c.test, None, c.kursus, check=True):
${tab.draw('osalejatetulemused', h.url('ktulemused_osalejatetulemused', test_id=c.test.id, testimiskord_id=c.testimiskord.id, kursus=c.kursus or ''), _("Osalejate tulemused"), c.tab1)}
% endif
% if c.on_valim and c.FeedbackReport.init_valim(handler, c.test, None, c.kursus, check=True):
${tab.draw('valimitulemused', h.url('ktulemused_valimitulemused', test_id=c.test.id, testimiskord_id=c.testimiskord.id, kursus=c.kursus or ''), _("Valimi koondtulemus"), c.tab1)}
% endif
% if c.sooritaja:
${tab.draw('opetajatulemus', h.url('ktulemused_opetajatulemus', test_id=c.test.id, testimiskord_id=c.testimiskord.id, id=c.sooritaja.id, kursus=c.kursus or ''), c.sooritaja.nimi, c.tab1)}
% endif
