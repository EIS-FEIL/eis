## Nupule "Jaota sooritajad soorituskohtadesse" vajutamisel 
## avaneva dialoogiakna sisu

${h.form_save(None, h.url_current('create'))}
${h.hidden('sub', 'jaotaruumi')}
<table  class="table" width="100%">
  <col width="200"/>
  <col/>
  <col/>
  <tr>
    <td class="frh">${_("Jaotatavate sooritajate koguarv")}</td>
    <td>
      ${h.posint5('arv', '')}
    </td>
  </tr>
  <tr>
    <td class="frh">${_("Jaotatakse ruumidesse")}</td>
    <td>
      <table >      
        % for truum in c.testikoht.testiruumid:
        <% vabukohti = truum.vabukohti %>
        <tr>
          <td>
            ${h.checkbox('truum_id', truum.id, label='%s (%s)' % (truum.tahis, truum.ruum and truum.ruum.tahis or _("määramata")))}
          </td>
          <td>
            max
            % if vabukohti is not None:
            ${h.posint5('arv_%d' % truum.id, vabukohti, maxvalue=vabukohti)}
            % else:
            ${h.posint5('arv_%d' % truum.id, '')}
            % endif
            sooritajat
          </td>
        </tr>
        % endfor
      </table>
    </td>
  </tr>
  <tr>
    <td class="fh"></td>
    <td class="fh">
      ${h.submit(_("Jaota"), id='jaotaruumi')}
    </td>
  </tr>
</table>
${h.end_form()}
