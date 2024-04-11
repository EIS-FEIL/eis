## -*- coding: utf-8 -*- 
<%
   c.sooritaja = c.item.sooritaja
   test = c.sooritaja.test
   c.kasutaja = c.sooritaja.kasutaja
%>
${c.sooritaja.nimi}
<%include file="/common/message.mako"/>
${h.form_save(c.item.id)}
${h.hidden('sub', 'eri')}

<p>
    % for tos in c.sooritaja.sooritused:
    % if tos.staatus == const.S_STAATUS_VABASTATUD:
    ${_("Vabastatud testiosast:")} ${tos.testiosa.nimi}<br/>
    % else:
    % for atos in tos.alatestisooritused:
    % if atos.staatus == const.S_STAATUS_VABASTATUD:
    ${_("Vabastatud alatestist:")} ${atos.alatest.nimi}<br/>
    % endif
    % endfor
    % endif
    % endfor
</p>

<table width="100%"  class="table" id="erivajadustabel">
  <col/>
  <col width="80px"/>
  <col width="80px"/>
  <col width="80px"/>
  <tr>
    <td class="field-header">${_("Eritingimus")}</td>
    <td class="field-header">${_("Ei kasutatud")}</td>    
  </tr>
  % for cnt, rcd in enumerate(c.item.erivajadused):
  % if rcd.ei_vaja_kinnitust(test) or rcd.kinnitus:
  <tr>
    <td class="fh">${rcd.erivajadus_nimi}</td>
    <td>
      % if c.is_edit:
      ${h.checkbox('ev-%s.kasutamata' % cnt, 1, checked=rcd.kasutamata)}
      ${h.hidden('ev-%s.id' % cnt, rcd.id)}
      % elif rcd.kasutamata:
      ${_("Jah")}
      % endif
    </td>
  </tr>
  % endif
  % endfor
</table>

% if c.is_edit:
${h.submit_dlg()}
% endif
${h.end_form()}

% if c.must_close:
<script>
  close_dialog();
</script>
% endif
