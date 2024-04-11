<%include file="/common/message.mako" />
% if c.to_list:
${h.form(h.url('admin_kohad'), method='post')}
${h.hidden('sub', 'mail')}
<table width="100%" class="table" >
  <tr>
    <td>
      ${_("Teate pealkiri")}
      <br/>
      ${h.text('subject', c.subject, size=65)}
    </td>
  </tr>
  <tr>
    <td>
      ${_("Teate sisu")}<br/>
      ${h.textarea('body', c.body, cols=65, rows=8)}
    </td>
  </tr>
  <tr>
    <td>
      ${_("Teate saajad")}<br/>
      ${', '.join(c.to_list)}
      % for addr in c.to_list:
      ${h.hidden('to', addr)}
      % endfor
    </td>
  </tr>
</table>

${h.submit(_("Saada"))}
${h.end_form()}
% endif
