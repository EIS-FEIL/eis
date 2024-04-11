<%namespace name="tab" file='/common/tab.mako'/>
<% 
   c.test = c.test or c.item 
   edit = c.is_edit and '_edit' or ''
   on_diag2 = c.test.testiliik_kood == const.TESTILIIK_DIAG2
   testiosad = list(c.test.testiosad)
   on_testiosi = len(testiosad) > 0
%>
% if c.test.id:
${tab.draw('testid', h.url('test', id=c.test.id), _("Üldandmed"))}
% if c.test.diagnoosiv:
${tab.draw('struktuur', h.url('test_struktuur', test_id=c.test.id), _("Struktuur ja ülesanded"), c.tab1)}
% else:
${tab.draw('struktuur', h.url('test_struktuur', test_id=c.test.id), _("Struktuur"), c.tab1)}
% endif
% if on_testiosi:
${tab.draw('tagasisideviis', h.url('test_tagasiside_viis', test_id=c.test.id, testiosa_id=0), _("Tagasiside"), c.tab1)}
% else: 
${tab.draw('tagasisideviis', None, _("Tagasiside"))}
% endif

% if c.test.diagnoosiv:
% if len(testiosad) > 0:
${tab.draw('eelvaade', h.url('test_new_eelvaade', test_id=c.test.id, e_komplekt_id='', testiosa_id=testiosad[0].id, alatest_id='', lang=c.lang), _("Eelvaade"))}
% endif
% else:
  % if on_testiosi:
${tab.draw('valitudylesanded', h.url('test_valitudylesanded', test_id=c.test.id), _("Ülesanded"), c.tab1)}
  % else:
${tab.draw('valitudylesanded', None, _("Ülesanded"))}
  % endif
% endif
% if not on_diag2 and c.user.has_permission('testimiskorrad', const.BT_SHOW, test_id=c.test.id):
${tab.draw('korraldus', h.url('test_korrad', test_id=c.test.id), _("Korraldus"), c.tab1)}
% endif

${tab.draw('koostamine', h.url('test_koostamine', id=c.test.id),_("Koostamine"))}
% if c.test.eeltest_id is None and c.test.testityyp == const.TESTITYYP_EKK:
${tab.draw('eeltestid', h.url('test_eeltestid', test_id=c.test.id), _("Eeltestimine"))}
% endif
% if on_diag2 or c.test.avaldamistase in (const.AVALIK_LITSENTS, const.AVALIK_SOORITAJAD, const.AVALIK_OPETAJAD, const.AVALIK_MAARATUD):
${tab.draw('analyys', h.url('test_analyys', test_id=c.test.id), _("Vastuste analüüs"), c.tab1)}
% endif

${tab.draw('muutjad', h.url('test_muutjad', id=c.test.id), _("Koostamise ajalugu"))}

% else:

${tab.draw('testid', None, _("Üldandmed"))}
${tab.draw('struktuur', None, _("Struktuur"), c.tab1, disabled=True)}
${tab.draw('valitudylesanded', None, _("Ülesanded"), disabled=True)}
${tab.draw('korraldus', None, _("Korraldus"), disabled=True)}
${tab.draw('koostamine', None, _("Koostamine"), disabled=True)}
${tab.draw('eeltestid', None, _("Eeltestimine"), disabled=True)}
${tab.draw('muutjad', None, _("Koostamise ajalugu"), disabled=True)}

% endif
