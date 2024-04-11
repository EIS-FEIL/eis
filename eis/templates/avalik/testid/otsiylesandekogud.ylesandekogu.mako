  % for group_name, items in c.itemdata:
  <div class="ykg">
    <div class="ykg-title">
      <span class="glyphicon glyphicon-triangle-right"> </span>
      ${group_name} (${len(items)})
    </div>
    <div class="ykg-items">
      <table width="100%" class="table table-borderless table-striped" border="0" >
        <col width="20px"/>
        <col width="60px"/>
        <col/>
        <col width="60px"/>
        <col width="80px"/>
        <thead>
          <tr>
            <th>${h.checkbox('all_id', 1, ronly=False, title=_("Vali kõik"))}</th>
            ${h.th('ID')}
            ${h.th(_('Nimetus'))}
            ${h.th(_('Pallid'))}
            ${h.th(_('Arvutiga hinnatav'))}
          </tr>
        </thead>
        <tbody>
        % for item in items:
        <%
          url = h.url('lahendamine1', id=item.id)
        %>
        <tr>
          <td>${h.checkbox('ylesanne_id', item.id, ronly=False, title=_("Vali rida {s}").format(s=item.nimi))}</td>
          <td>${item.id}</td>
          <td>${h.link_to(item.nimi, url, target='ykitem')}</td>
          <td>${h.fstr(item.max_pallid)}</td>
          <td>${h.sbool(item.arvutihinnatav)}</td>
        </tr>
        % endfor
        </tbody>
      </table>
    </div>
  </div>
  % endfor
