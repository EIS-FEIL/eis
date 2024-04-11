<% 
   c.testiosa = c.toimumisaeg.testiosa
   c.testimiskord = c.toimumisaeg.testimiskord
   c.test = c.testimiskord.test
%>
<table width="100%" class="box">
  <tr>
    <td class="frh2">${_("Test")}</td>
    <td>${c.test.nimi}</td>
    <td class="frh2">${_("Toimumisaeg")}</td>
    <td>${c.toimumisaeg.tahised}</td>
    <td class="frh2">${_("Toimumise aeg")}</td>
    <td>${c.toimumisaeg.millal}</td>
    % if c.hindaja1:
    <td class="frh2">${_("Hindamiskogum")}</td>
    <td>${c.hindaja1.hindamiskogum.tahis}</td>
    % endif
  </tr>
</table>
