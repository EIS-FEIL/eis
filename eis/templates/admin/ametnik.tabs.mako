<%namespace name="tab" file='/common/tab.mako'/>
<% 
   c.kasutaja = c.kasutaja or c.item 
   edit = c.is_edit and '_edit' or ''
   k_id = c.kasutaja.id
%>
${tab.draw('ametnikud', k_id and h.url('admin_ametnik', id=k_id) or None, _("Üldandmed"))}
${tab.draw('ametnikurollid', k_id and h.url('admin_ametnik_rollid', kasutaja_id=k_id) or None,_("Rollid"), c.tab1)}
${tab.draw('ametnikuylesanded', k_id and h.url('admin_ametnik_ylesanded', kasutaja_id=k_id) or None, _("Ülesanded"), c.tab1)}
${tab.draw('ametnikutestid', k_id and h.url('admin_ametnik_testid', kasutaja_id=k_id) or None, _("Testid"), c.tab1)}
