## -*- coding: utf-8 -*- 

${c.sooritaja.nimi}
<br/>
${c.sooritaja.test.nimi}
<br/>
<table class="table" width="100%" >
  <thead>
    <tr>
      <th>${_("Testiosa")}</th>
      <th>${_("Eritingimused")}</th>
    </tr>
  </thead>
  <tbody>
    % for tos in c.sooritaja.sooritused:
    <tr>
      <td>
        ${tos.testiosa.nimi}
        <br/>
        (${tos.on_erivajadused_kinnitatud and _("kinnitatud eritingimused") or _("taotletud eritingimused")})
      </td>
      <td>
        ${tos.get_str_erivajadused('<br/>') or '-'}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
