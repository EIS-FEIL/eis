<%namespace name="tab" file='/common/tab.mako'/>
<% 
   c.koht = c.koht or c.item 
   edit = c.is_edit and '_edit' or ''
%>
% if c.koht.id:
${tab.draw('kohad', h.url('admin_koht', id=c.koht.id), _("Üldandmed"))}
${tab.draw('ruumid', h.url('admin_koht_ruumid', koht_id=c.koht.id), _("Ruumid"), c.tab1)}
${tab.draw('kohakasutajad', h.url('admin_koht_kasutajad', koht_id=c.koht.id), _("Isikud"), c.tab1)}

% else:

${tab.draw('kohad', None, _("Üldandmed"))}
${tab.draw('ruumid', None, _("Ruumid"), c.tab1)}
${tab.draw('kohakasutajad', None, _("Isikud"))}

% endif
