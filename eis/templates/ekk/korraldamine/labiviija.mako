${h.form_save(None)}
${h.hidden('testiruum_id', c.item.testiruum_id)}
${h.hidden('kasutajagrupp_id', c.item.kasutajagrupp_id)}
${h.hidden('hindamiskogum_id', c.item.hindamiskogum_id)}
${h.hidden('list_url', c.list_url)}
<% koht = c.item.testikoht.koht %>
<table width="100%" class="table" border="0" >
  <tbody>
    <tr>
      <td class="fh">${_("Soorituskoht")}</td>
      <td>${koht.nimi}</td>
    </tr>
    <tr>
      <td class="fh">${_("Läbiviija roll")}</td>
      <td>${c.item.kasutajagrupp.nimi}</td>
    </tr>
    <tr>
      <td class="fh">${_("Testi läbiviija")}</td>
      <td>
        ${h.select('kasutaja_id', None, c.item.get_labiviijad_opt())}
      </td>
    </tr>
  </tbody>
</table>
${h.submit()}
${h.end_form()}
