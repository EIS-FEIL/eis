## -*- coding: utf-8 -*- 
${h.form(h.url_current('create', opperyhm_id=c.opperyhm.id), method='post', multipart=True)}
${h.hidden('sub', 'fail')}
${h.alert_notice(_("Laadida saab tekstifaile, mille sisuks on isikukoodid, iga isikukood eraldi real"), False)}
<table width="100%" class="search2" >
  <col width="150px"/>
  <tr>
    <td>${_("Õpilaste fail")}</td>
    <td>${h.file('ik_fail', value=_('Fail'))}</td>
  </tr>
</table>
<br/>
${h.submit(_('Salvesta'))}
${h.end_form()}
