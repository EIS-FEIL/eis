<%inherit file="/common/dlgpage.mako"/>
<%include file="/common/message.mako"/>
${h.form_save(None, multipart=True)}
<% sub = c.params.get('sub') %>
${h.hidden('sub', sub)}
<table width="100%" class="table">
  <tr>
    <td class="fh">${_("Isikukoodide fail")}</td>
    <td>
      ${h.file('fail', value=_("Fail"))}
      <div style="margin:4px">
        ${_("Faili rea kuju: <i>isikukood; e-posti aadress</i> <br/> või:  <i>isikukood</i>")}
      </div>
    </td>
  </tr>
  <tr>
    <td class="fh">${_("Kehtib kuni")}</td>
    <td>${h.date_field('kehtib_kuni', '', wide=False)}</td>
  </tr>
</table>
<br/>
${h.submit()}
${h.end_form()}

