<%inherit file="/common/dlgpage.mako"/>
<%include file="/common/message.mako"/>

${h.form_search()}
${h.hidden('sub', 'valikomplekt')}
${h.hidden('test_id', c.test.id)}
<table width="100%" class="table" >
  <col width="100"/>
  <tr>
    <td class="fh">${_("Test")}</td>
    <td>${c.test.id} ${c.test.nimi}</td>
  </tr>
  <tr>
    <td class="fh">${_("Komplekt")}</td>
    <td>
      ${h.select('komplekt_id', c.komplekt_id, c.opt_komplekt, wide=False)}
    </td>
  </tr>
</table>
${h.submit_dlg(_("Jätka"))}
${h.end_form()}
