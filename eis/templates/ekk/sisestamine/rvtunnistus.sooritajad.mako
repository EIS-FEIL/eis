<% tulemusviis = c.rveksam.tulemusviis %>
<table width="100%" class="form border tbl-sisestamine" cellpadding="4">
  % for sooritaja in c.sooritajad:
  <tr>
    <td>${h.radio('sooritaja_id', sooritaja.id, checkedif=c.item.sooritaja_id)}</td>
    <td>${sooritaja.testimiskord and sooritaja.testimiskord.tahised or sooritaja.test.id}</td>
    <td>${sooritaja.test.nimi}</td>
    <td>${sooritaja.millal}</td>
    <td>${sooritaja.get_tulemus()}</td>
    <td>
      <%
         sooritused = [('kokku', sooritaja)]
         for tos in sooritaja.sooritused:
             osa = tos.testiosa.rvosaoskus
             if osa:
                 sooritused.append((osa.id, tos))
             for atos in tos.alatestisooritused:
                 osa = atos.alatest.rvosaoskus
                 if osa:
                     sooritused.append((osa.id, atos))
         data = []     
         for osa_id, sooritus in sooritused:
             if tulemusviis == model.Rveksam.TULEMUSVIIS_PALL:
                tulemus = sooritus.pallid
             elif tulemusviis == model.Rveksam.TULEMUSVIIS_PROTSENT:
                tulemus = sooritus.tulemus_protsent
             else:
                tulemus = None
             if tulemus is not None:
                data.append([osa_id, h.fstr(tulemus)])
      %>
      % if data:
      ${h.button(_('Kanna tulemus tunnistusele'),
      onclick="kanna(this, %s)" % (str(data)))}
      % endif
    </td>
  </tr>
  % endfor
  <tr>
    <td colspan="6">
      ${h.radio('sooritaja_id', 0, checked=c.item.id and not c.item.sooritaja_id,
      label=_('Tunnistus ei ole seotud ühegi EISis oleva testisooritusega'))}
    </td>
  </tr>
</table>
<script>
  function kanna(fld, data)
  {
     $(fld).closest('tr').find('input[name="sooritaja_id"]').prop('checked', true);
     for(var n=0; n<data.length; n++)
     {
        var osa_id = data[n][0];
        var tulemus = data[n][1];
        $('tr#osa' + osa_id).find('input.tulemus').val(tulemus).change();
     }
  }
</script>
