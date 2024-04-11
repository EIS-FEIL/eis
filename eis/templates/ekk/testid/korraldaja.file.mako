<%inherit file="/common/dlgpage.mako"/>
<%include file="/common/message.mako"/>
${h.not_top()}
${h.form(h.url('test_eeltest', test_id=c.test.id, id=c.komplekt_id), method='put', multipart=True)}
${h.hidden('sub','file')}
<table  class="table" width="100%">
  <tr>
    <td class="fh">
      ${_("Korraldajate isikukoodide fail")}
    </td>
    <td>${h.file('ik_fail', value=_("Fail"))}</td>
  </tr>
</table>
${h.submit(_("Laadi"))}
${h.end_form()}

