<%include file="/common/message.mako"/>
${h.form_save(None, h.url('korraldamine_sooritajad',testikoht_id=c.testikoht.id))}
${h.hidden('sub','ruumid')}
<% 
   ruumid_id = [r.ruum_id or 0 for r in c.testikoht.testiruumid] 
   c.koht = c.testikoht.koht
%>
<%include file="/ekk/korraldamine/koht.ruumid.mako"/>

% if c.is_edit:
${h.submit_dlg(clicked=True)}
% endif
${h.end_form()}

