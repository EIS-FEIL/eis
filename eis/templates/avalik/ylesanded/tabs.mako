## -*- coding: utf-8 -*- 
<%namespace name="tab" file='/common/tab.mako'/>
<% 
   c.ylesanne = c.ylesanne or c.item 
%>
% if not c.ylesanne.id:
${tab.draw('ylesanded', None, _("Üldandmed"))}
${tab.draw('sisu', None, _("Ülesande sisu"), disabled=True)}
${tab.draw('testid', None, _("Kasutamise ajalugu"), disabled=True)}
% elif c.user.has_permission('avylesanded', const.BT_SHOW, c.ylesanne):
${tab.draw('ylesanded', h.url('edit_ylesanne', id=c.ylesanne.id), _("Üldandmed"))}
${tab.draw('sisu', h.url('ylesanded_edit_sisu', id=c.ylesanne.id, lang=c.lang), _("Ülesande sisu"), c.tab1)}
${tab.draw('testid', h.url('ylesanded_testid', ylesanne_id=c.ylesanne.id), _("Kasutamise ajalugu"))}
% else:
${tab.draw('lahendamine', h.url('ylesanded_edit_lahendamine', id=c.ylesanne.id), c.item.nimi, True)}
% endif

