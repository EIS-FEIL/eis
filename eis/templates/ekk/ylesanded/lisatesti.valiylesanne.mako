<%inherit file="/common/dlgpage.mako"/>
<%include file="/common/message.mako"/>

${h.form_save(None)}
${h.hidden('sub', 'valiylesanne')}
${h.hidden('test_id', c.test.id)}
${h.hidden('komplekt_id', c.komplekt.id)}
<table width="100%" class="table" >
  <col width="100"/>
  <tr>
    <td class="fh">${_("Test")}</td>
    <td>${c.test.id} ${c.test.nimi}</td>
  </tr>
  <tr>
    <td class="fh">${_("Komplekt")}</td>
    <td>
      ${c.komplekt.tahis}
    </td>
  </tr>
  % if c.lisatud_ty:
  <tr>
    <td class="fh">${_("Testiülesanne")}</td>
    <td>
      ${c.lisatud_ty.nimi or c.lisatud_ty.tahis}
    </td>
  </tr>
  % endif
</table>

% if c.items:
<% on_alatestid = c.items[0][0] %>
<table width="100%" class="table" >
  <thead>
    <tr>
      % if on_alatestid:
      <th>${_("Alatest")}</th>
      % endif
      <th>${_("Vali")}</th>
      <th>${_("Testiülesanne")}</th>
      <th>${_("Pallid")}</th>
      <th>${_("Komplekti valitud ülesanne")}</th>
    </tr>
  </thead>
  <tbody>
  % for a_nimi, testiylesanded in c.items:
  % for ind, ty in enumerate(testiylesanded):
  <% valitudylesanded = [ty.get_valitudylesanne(c.komplekt, n) for n in range(1, ty.valikute_arv+1)] %>
  <tr>
    % if ind == 0 and a_nimi:
    <td rowspan="${len(testiylesanded)}">
      ${a_nimi}
    </td>
    % endif
    <td>
      % if ty.valikute_arv > 1:
      % for seq in range(0, ty.valikute_arv):
      <%
        vy = valitudylesanded[seq]
        checked = vy and vy.ylesanne_id == c.item.id
      %>
      ${h.radio('ty_id', '%d#%d' % (ty.id, seq+1), label=_("Valik {n}").format(n=seq+1), checked=checked)}
      % endfor
      % else:
      <%
        vy = valitudylesanded[0]
        checked = vy and vy.ylesanne_id == c.item.id
      %>
      ${h.radio('ty_id', ty.id, label='', checked=checked)}
      % endif
    </td>
    <td>${ty.nimi or ty.tahis}</td>
    <td>
      % if ty.max_pallid is not None:
      ${h.fstr(ty.max_pallid)}p
      % endif
    </td>
    <td>
      % for vy in valitudylesanded:
      % if vy:
      <div>
        <% ylesanne = vy.ylesanne %>
        % if ylesanne:
        ${ylesanne.id}
        ${ylesanne.nimi}
        % endif
      </div>
      % endif
      % endfor
    </td>
  </tr>
  % endfor
  % endfor
  </tbody>
</table>
${h.submit_dlg(_("Salvesta"))}
% endif
${h.button(_("Sule"), onclick="close_dialog()")}
${h.end_form()}
