<% max_level=4 %>
<table width="100%" class="table table-borderless table-striped" border="0" >
% for n in range(max_level):
  <col width="25"/>
% endfor
  <col width="200"/>
  <col/>
  <thead>
    <tr>
      <th colspan="${max_level+1}">${_("Piirkond")}</th>
      <th>${_("Sooritajate arv")}</th>
    </tr>
  </thead>
  <tbody>
    <% roots = c.piirkond and [c.piirkond] or model.Piirkond.get_tree() %>
    ${self.treedata(roots, 0, max_level)}
  </tbody>
  <tfoot>
    <tr>
      <td colspan="${max_level+1}">
        ${_("KOKKU")}
        </td>
      <td>${c.cnt_total}</td>
    </tr>
  </tfoot>
</table>

<%def name="treedata(piirkonnad, level, max_level)">
% for prk in piirkonnad:
  % if prk.id in c.sooritajad_ylempiirkonniti:
    <% cnt = c.sooritajad_piirkonniti.get(prk.id) %>
    <tr>
      % if level:
      <td colspan="${level}">  </td>
      % endif
      <td colspan="${max_level+1-level}">
        % if cnt:
        ${h.link_to(prk.nimi, h.url_current('show', id=prk.id))}
        % else:
        ${prk.nimi}
        % endif
      </td>
      <td>
        ${cnt}
      </td>
    </tr>
    ${self.treedata(prk.alamad, level+1, max_level)}
  % endif
% endfor
</%def>

