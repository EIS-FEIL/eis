## Nupule "Jaota sooritajad soorituskohtadesse" vajutamisel 
## avaneva dialoogiakna sisu

${h.form_save(None, h.url_current('create'), form_name='form_save_j')}
${h.hidden('sub', 'jaota')}
<table  class="table" width="100%">
  <col width="200"/>
  <col/>
  <col/>
  <tr>
    <td class="frh">${_("Jaotatakse piirkonnas")}</td>
    <td>
      <%
         c.piirkond_id = None
         c.piirkond_field = 'piirkond_id'
         c.piirkond_filtered = c.toimumisaeg.testimiskord.get_piirkonnad_id()
      %>
      <%include file="/admin/piirkonnavalik.mako"/>
    </td>
  </tr>
  <tr>
    <td class="frh">${_("Jaotatavate sooritajate arv")}</td>
    <td>
      ${h.posint5('arv', '')}
    </td>
  </tr>
  <tr>
    <td class="fh"></td>
    <td class="fh">
      ${h.submit(_("Jaota"), id='jaota')}
    </td>
  </tr>
</table>
${h.end_form()}
