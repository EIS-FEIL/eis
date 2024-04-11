% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<table class="table table-borderless table-striped table-align-top">
  <thead>
    <tr>
      ${h.th('Nimetus')}
      ${h.th('Üldleping')}
      ${h.th('Alates')}
      ${h.th('Kuni')}
      ${h.th('Sobivate testimiskordade arv')}
      ${h.th('Sõlmitud lepingute arv')}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <tr>
      <td>
          <%
            if c.user.has_permission('lepingud', const.BT_UPDATE):
               url = h.url_current('edit', id=rcd.id)
            else:
               url = h.url_current('show', id=rcd.id)
          %>
          ${h.link_to(rcd.nimetus, url)}
      </td>
      <td>${h.sbool(rcd.yldleping)}</td>
      <td>${rcd.aasta_alates}</td>
      <td>${rcd.aasta_kuni}</td>
      <td>
          <%
            q = (model.Session.query(model.sa.func.count(model.Testileping.testimiskord_id.distinct()))
                 .filter_by(leping_id=rcd.id))
          %>
          ${q.scalar()}
      </td>
      <td>
          <%
            q = (model.Session.query(model.sa.func.count(model.Labiviijaleping.id))
                .filter_by(leping_id=rcd.id))
          %>
          ${q.scalar()}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
