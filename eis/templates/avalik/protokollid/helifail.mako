${h.form_save(c.item.id, multipart=True)}
<table class="table" width="100%">
  <tr>
    <td class="fh">${_("Helifail")}</td>
    <td>${h.file('filedata', value='Fail')}</td>
  </tr>
</table>
      <%
        if c.item:
           sooritused_id = [hv.sooritus_id for hv in c.item.helivastused]
        else:
           sooritused_id = []
      %>
<table class="table" width="100%">
  <caption>${_("Sooritajad")}</caption>
  % for testikoht in c.toimumisprotokoll.testikohad:
  % if testikoht.toimumisaeg.testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP):
  % for rcd in testikoht.sooritused:
    % if rcd.staatus != const.S_STAATUS_PUUDUS:
  <tr>
    <td>
      ${h.checkbox('sooritus_id', rcd.id, checkedif=sooritused_id)}
      ${rcd.tahis}
      ${rcd.sooritaja.nimi}

    </td>
  </tr>
    % endif
  % endfor
  % endif
  % endfor
</table>
${h.submit(_('Salvesta'), onclick='set_spinner()')}
${h.end_form()}
