<%namespace name="tab" file='/common/tab.mako'/>
<% 
c.ylesanne = c.ylesanne or c.item
exists = False 
edit = c.is_edit and c.user.has_permission('ylesanded', const.BT_UPDATE,c.ylesanne) and '_edit' or ''
%>
% if not c.ylesanne.is_encrypted:

% for rcd in c.ylesanne.sisuplokid:
  % if rcd.id: 
     <%
      exists = True
      if c.tab2 == rcd.id and c.is_edit and not c.is_tr:
         ## jooksev sisuplokk
         tab_url = None
      elif c.is_tr or (c.is_edit and c.user.has_permission('ylesanded', const.BT_UPDATE,c.ylesanne)):
         tab_url = h.url('ylesanne_edit_sisuplokk', id=rcd.id, ylesanne_id=c.ylesanne.id, lang=c.lang, is_tr=c.is_tr)
      else:
         tab_url = h.url('ylesanne_sisuplokk', id=rcd.id, ylesanne_id=c.ylesanne.id, lang=c.lang)

     %>
  ${tab.subdraw(rcd.id, tab_url, rcd.tahis or rcd.seq, c.tab2)}

  % else:
  ${tab.subdraw('NEW', None, _("Uus"), 'NEW')}
  % endif
% endfor
% endif

% if exists:
  ${tab.subdraw('lahendamine', h.url('ylesanded_edit_lahendamine', id=c.ylesanne.id, lang=c.lang), _("Lahendamine"), c.tab2)}

% if c.ylesanne.ptest and not c.ylesanne.etest:
${tab.subdraw('psisu', h.url('ylesanne%s_psisu' % edit, id=c.ylesanne.id, lang=c.lang), _("P-testi lihtsustatud sisu"), c.tab2)}
% endif

% endif
