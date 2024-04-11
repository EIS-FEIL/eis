## -*- coding: utf-8 -*- 
## Lisaaja määramise dialoogiaken testi administraatori kuval

${h.form_save(c.testiruum.id)}
${h.hidden('sub', 'lisaaeg')}
${h.hidden('sooritus_id', c.sooritus.id)}

<%include file="/common/message.mako" />

${_("Testisooritaja")} ${c.sooritus.sooritaja.kasutaja.nimi} <br/>
<table width="100%" class="table" >
  <tr>
    <th></th>
    <th>${_("Piiraeg")}</th>
    <th>${_("Lisaaeg")} hh.mm</th>
  </tr>
  <tr>
    <td>${_("Testiosa")}</td>
    % if c.sooritus.testiosa.piiraeg:
    <td>${h.str_from_time(c.sooritus.testiosa.piiraeg)}</td>
    <td>${h.text5('tos_lisaaeg', h.str_from_time(c.sooritus.lisaaeg))}</td>
    % else:
    <td colspan="2">${_("Piiramata")}</td>
    % endif
  </tr>

<% n = 0 %>
% for alatest in c.sooritus.alatestid:
  <tr>
    <td>${_("Alatest")} ${h.roxt(alatest.nimi or '')}</td>
    % if alatest.piiraeg:
    <td>${h.str_from_time(alatest.piiraeg)}</td>
    <td>
      <% 
         alatestisooritus = c.sooritus.get_alatestisooritus(alatest.id) 
         n += 1
      %>
      ${h.text5('ats-%d.lisaaeg' % n, h.str_from_time(alatestisooritus and alatestisooritus.lisaaeg))}
      ${h.hidden('ats-%d.alatest_id' % n, alatest.id)}
    </td>
    % else:
    <td colspan="2">${_("Piiramata")}</td>
    % endif
  </tr>
% endfor

</table>

${h.submit_dlg()}
${h.end_form()}
