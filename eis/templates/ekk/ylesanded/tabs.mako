<%namespace name="tab" file='/common/tab.mako'/>
<% 
   c.ylesanne = c.ylesanne or c.item 
## kui kasutaja on muutmisresiimis ja tal on õigus muuta, siis lingid on ka muutmisresiimis
   edit = c.is_edit and c.user.has_permission('ylesanded', const.BT_UPDATE,c.ylesanne) and '_edit' or ''
%>
% if c.ylesanne.id:
${tab.draw('ylesanded', h.url('ylesanne', id=c.ylesanne.id), _("Üldandmed"))}

% if c.ylesanne.ptest and not c.ylesanne.etest:
${tab.draw('sisu', h.url('ylesanne%s_psisu' % edit, id=c.ylesanne.id, lang=c.lang), _("Ülesande sisu"), c.tab1)}
% else:
${tab.draw('sisu', h.url('ylesanded%s_sisu' % edit, id=c.ylesanne.id, lang=c.lang), _("Ülesande sisu"), c.tab1)}
% endif

% if c.ylesanne.on_tagasiside:
${tab.draw('tagasisided', h.url('ylesanded_tagasiside', ylesanne_id=c.ylesanne.id), _("Tagasiside"))}
% endif
${tab.draw('juhised', h.url('ylesanded_juhised', id=c.ylesanne.id), _("Aspektid"))}
${tab.draw('koostamine', h.url('ylesanded_koostamine', id=c.ylesanne.id), _("Koostamine"))}
${tab.draw('versioonid', h.url('ylesanded_versioonid', ylesanne_id=c.ylesanne.id), _("Tekstide versioonid"))}
${tab.draw('muutjad', h.url('ylesanded_muutjad', id=c.ylesanne.id), _("Koostamise ajalugu"))}
${tab.draw('testid', h.url('ylesanded_testid', ylesanne_id=c.ylesanne.id), _("Kasutamise ajalugu"))}
% else:
${tab.draw('ylesanded', None, _("Üldandmed"))}
${tab.draw('sisu', None, _("Ülesande sisu"), disabled=True)}
${tab.draw('juhised', None, _("Aspektid"), disabled=True)}
${tab.draw('koostamine', None, _("Koostamine"), disabled=True)}
${tab.draw('versioonid', None, _("Tekstide versioonid"), disabled=True)}
${tab.draw('muutjad', None, _("Koostamise ajalugu"), disabled=True)}
${tab.draw('testid', None, _("Kasutamise ajalugu"), disabled=True)}
% endif

