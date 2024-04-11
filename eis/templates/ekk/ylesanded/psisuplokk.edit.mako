<%include file="/common/message.mako"/>
${h.form_save(c.item.id)}
${h.hidden('sub', 'sp')}
% if c.sisuplokid:
<table class="table table-borderless table-striped" >
  <thead>
    <tr>
      <th>${_("Küsimuse ID")}</th>
      <th>${_("Max punktide arv")}</th>
      % if c.tyyp == const.INTER_CHOICE:
      <th>${_("Max vastuste arv")}</th>
      <th>${_("Õige vastuse punktide arv")}</th>
      <th>${_("Õige valik")}</th>
      % elif c.tyyp == const.INTER_EXT_TEXT:
      <th>${_("Punktide intervall")}</th>
      % endif
    </tr>
  </thead>
  <tbody>
  % for ind, sp in enumerate(c.sisuplokid):
  <% kysimused = list(sp.pariskysimused) %>
  ${self.row_sisuplokk(sp, kysimused, 'sp','-%s' % (ind))}
  % endfor
  </tbody>
</table>
${h.submit_dlg()}
% endif
${h.end_form()}


<%def name="row_sisuplokk(item, kysimused, baseprefix, cnt)">
<%
  prefix = '%s%s' % (baseprefix, cnt) 
  cnt = len(kysimused) or 1
%>
% for ind, kysimus in enumerate(kysimused or [None]):
<%
  tulemus = kysimus and kysimus.tulemus or None
  kprefix = '%s.k-%d' % (prefix, ind)
%>
<tr>
  <td>
    ${h.hidden('%s.id' % prefix, item.id)}
    ${h.hidden('%s.tyyp' % prefix, item.tyyp)}
    ${h.text('%s.kood' % kprefix, kysimus.kood)}
    ${h.hidden('%s.id' % kprefix, kysimus.id)}
  </td>
  <td>
    <% max_pallid = tulemus and tulemus.max_pallid or '' %>
    ${h.posfloat('%s.max_pallid' % kprefix, max_pallid)}
  </td>
  % if c.tyyp == const.INTER_CHOICE:
  <td>
    ${h.posint5('%s.max_vastus' % kprefix, kysimus.max_vastus)}
  </td>
  <td>
    ${h.posfloat('%s.oige_pallid' % kprefix, tulemus.oige_pallid)}
  </td>
  <td>
      <%
        v_correct = []
        if tulemus:
           for v_hm in tulemus.hindamismaatriksid:
              if v_hm.pallid > 0:
                  v_correct.append(v_hm.kood1)
      %>
      % for indv, valik in enumerate(kysimus.valikud):
      <%
        vprefix = '%s.v-%d' % (kprefix, indv)
        label = valik.get_sisestusnimi(kysimus.rtf)
      %>
          ${h.hidden('%s.kood' % (vprefix), valik.kood)}
          % if kysimus.max_vastus == 1:
          ${h.radio('%s.oige' % kprefix, valik.kood, checked=valik.kood in v_correct, label=label)}
          % else:
          ${h.checkbox('%s.oige' % kprefix, valik.kood, checked=valik.kood in v_correct, label=label)}
          % endif
      % endfor
  </td>
  % elif c.tyyp == const.INTER_EXT_TEXT:
  <td>${h.posfloat('%s.pintervall' % kprefix, tulemus.pintervall)}</td>
  % endif
</tr>
% endfor
</%def>
