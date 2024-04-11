## -*- coding: utf-8 -*- 
## $Id: tabs.mako 9 2015-06-30 06:34:46Z ahti $         
<%namespace name="tab" file='/common/tab.mako'/>
<% 
   c.test = c.test or c.item 
   edit = c.is_edit and '_edit' or ''
%>
% if not c.test.id:
## uus kirje
${tab.draw('konsultatsioonid', None, _('Üldandmed'))}
${tab.draw('korraldus', None, _('Korraldus'))}

% else:

${tab.draw('konsultatsioonid', h.url('konsultatsioon', id=c.test.id), _('Üldandmed'))}
${tab.draw('korraldus', h.url('konsultatsioon_korrad', test_id=c.test.id), _('Korraldus'), c.tab1)}
% endif
