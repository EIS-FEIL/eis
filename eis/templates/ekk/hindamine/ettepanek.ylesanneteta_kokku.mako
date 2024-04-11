<%
c.submit_url = h.url('hindamine_ettepanek_hindamine',
        hindamiskogum_id=0,
        toimumisaeg_id=c.toimumisaeg.id, sooritus_id=c.sooritus.id, id=0)
%>
<%include file="/common/message.mako"/>
${h.form(c.submit_url, method='post')}
<p>
  ${_("Punktid")}
  ${h.float5('kokku_pallid', c.sooritus.pallid_peale_vaiet)}
</p>
${h.hidden('sub', 'kokku')}
${h.submit_dlg()}
${h.end_form()}
