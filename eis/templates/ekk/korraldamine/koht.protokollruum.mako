<%inherit file="/common/dlgpage.mako"/>
<%include file="/common/message.mako"/>

${h.form_save(c.item.id)}
<table class="table table-borderless table-striped"  width="100%">
  <thead>
    <tr>
      <th>${_("Protokollirühm")}</th>
      <th>${_("Sooritajate arv")}</th>
      <th>${_("Alguskell")}</th>
    </tr>
  </thead>
  <tbody>
    % for n, tpr in enumerate([r for r in c.item.testiprotokollid if r.testipakett_id == c.pakett_id]):
    <tr>
      <td>
        <%
          prefix = 'tpr-%d' % n
          tpr_arv = tpr.soorituste_arv
        %>
        ${tpr.tahis}
        ${h.hidden('%s.id' % prefix, tpr.id)}
      </td>
      <td>
        % if tpr.kursus_kood:
        ${tpr.kursus_nimi}, ${tpr_arv}
        % else:
        ${tpr_arv}
        % endif
      </td>
      <td>
        ${h.time('%s.kell' % prefix, tpr.algus or c.item.algus, wide=False)}        
      </td>
    </tr>
    % endfor
</table>

% if c.testiosa.oma_kavaaeg:
<table class="table"  width="100%">
  <col width="220"/>
  <tbody>
    <tr>
      <td class="fh">${_("Intervall sooritajate vahel")}</td>
      <td>${h.posint5('intervall', c.intervall)} ${_("minutit")}</td>
    </tr>
    <tr>
      <td class="fh">${_("Pausi algus")}</td>
      <td>${h.time('paus_algus', c.paus_algus, wide=False)}</td>
    </tr>
    <tr>
      <td class="fh">${_("Pausi lõpp")}</td>
      <td>${h.time('paus_lopp', c.paus_lopp, wide=False)}</td>
    </tr>
  </tbody>
</table>
<br/>
% endif
${h.submit_dlg()}
${h.end_form()}
