<%namespace name="tab" file='/common/tab.mako'/>
<% 
   c.kasutaja = c.kasutaja or c.item 
   edit = c.is_edit and '_edit' or ''
%>
% if c.kasutaja.id:
${tab.draw('kasutajad', h.url('admin_kasutaja', id=c.kasutaja.id), _("Üldandmed"))}
% else:
${tab.draw('kasutajad', None, _("Üldandmed"))}
% endif

% if c.kasutaja.id and c.kasutaja.on_labiviija:
${tab.draw('profiil', h.url('admin_kasutaja_profiil', id=c.kasutaja.id),_("Läbiviija profiil"), c.tab1)}
${tab.draw('nousolekud', h.url('admin_kasutaja_nousolekud', kasutaja_id=c.kasutaja.id), _("Nõusolekud"), c.tab1)}
% else:
${tab.draw('profiil', None, _("Läbiviija profiil"), c.tab1, disabled=True)}
${tab.draw('nousolekud', None, _("Nõusolekud"), disabled=True)}
% endif

% if c.kasutaja.id:
${tab.draw('ajalugu', h.url('admin_kasutaja_ajalugu', kasutaja_id=c.kasutaja.id),_("Läbiviija ajalugu"), c.tab1)}
${tab.draw('kasutajakohad', h.url('admin_kasutaja_kohad', kasutaja_id=c.kasutaja.id), _("Soorituskohad"), c.tab1)}
% else:
${tab.draw('ajalugu', None, _("Läbiviija ajalugu"), disabled=True)}
${tab.draw('kasutajakohad', None, _("Soorituskohad"), disabled=True)}
% endif
