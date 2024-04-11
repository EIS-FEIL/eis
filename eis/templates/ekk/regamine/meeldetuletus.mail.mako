## -*- coding: utf-8 -*- 
<%inherit file="/common/dlgpage.mako"/>
<%include file="/common/message.mako" />
${h.form(h.url('regamine_meeldetuletused'), method='post')}
##${h.hidden('sub', 'mail')}
<table width="100%" class="table" >
  <tr>
    <td>
      ${_("Teate teema")}
      <br/>
      ${h.text('subject', c.subject, size=65)}
    </td>
  </tr>
  <tr>
    <td>
      ${_("Teate sisu")}<br/>
      ${h.textarea('body', c.body, cols=65, rows=15)}
    </td>
  </tr>
  <tr>
    <td>
      ${_("Teate saajad")}<br/>
      ${', '.join(c.to_list)}
      ${h.hidden('sooritajad_id', c.sooritajad_id)} 
    </td>
  </tr>
  
</table>
${h.submit_dlg(_("Saada"))}
<span>
  ${h.checkbox('setdef', 1, checked=False, label=_("Salvesta vaikimisi tekstina"))}
</span>

${h.end_form()}
