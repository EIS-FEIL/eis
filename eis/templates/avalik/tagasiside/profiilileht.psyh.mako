<% sooritaja = c.sooritaja or c.sooritus.sooritaja %>
<div class="border border-base-radius p-3">
  <div class="row">
  <div class="col-sm-6">
      <b>${sooritaja.test.nimi}</b>
      <br/>
      ${_("Nimi")}: ${sooritaja.nimi}
      <br/>
      % if sooritaja.klass:
      ${_("Klass")}: ${sooritaja.klass}${sooritaja.paralleel} &nbsp; &nbsp;
      % endif
      % if sooritaja.kool_koht:
      ${_("Kool")}: ${sooritaja.kool_koht.nimi}
      % endif
      <br/>
      % if sooritaja.esitaja_kasutaja:
      ${_("Testija")}: ${sooritaja.esitaja_kasutaja.nimi}
      % endif
  </div>
  <div class="col-sm-6">
      <b>${_("Profiilileht")}</b>
      <br/>
      ${_("Testimise aeg")}: ${sooritaja.millal}
      % if sooritaja.staatus != const.S_STAATUS_TEHTUD:
      (${sooritaja.staatus_nimi})
      % endif
      <br/>
      ${_("Sünniaeg")}: ${h.str_from_date(sooritaja.kasutaja.synnikpv)}
      <br/>
      <% aastad, kuud = sooritaja.kasutaja.get_vanus(sooritaja.algus) %>
      ${_("Vanus")}: ${aastad}a ${kuud}k
  </div>
  </div>
</div>

% if sooritaja.staatus == const.S_STAATUS_TEHTUD:
% for sooritus in sooritaja.sooritused:
<%
   header, items, fig_json = c.prepare_sooritus(sooritus)
%>
<div class="d-flex p-3 justify-content-between">
  <div>
      % if c.app_eis and sooritaja.nimekiri_id and c.user.has_permission('omanimekirjad', const.BT_SHOW, obj=sooritaja.nimekiri):
      ${h.link_to(_("Vastused"),
      h.url('test_labiviimine_sooritus', test_id=sooritaja.test_id, testiruum_id=sooritus.testiruum_id, id=sooritus.id))}
      % endif
  </div>
  <div>
      % if c.app_ekk and c.controller == 'tagasisideeelvaade':
      ${h.btn_to('PDF', h.url_current('download', format='pdf', id='F1'), level=2)}
      ${h.btn_to('Excel', h.url_current('download', format='xls', id='F1'), level=2)}
      % elif c.download_by_sooritaja:
      ## avalik/testid/tagasiside.py
      ${h.btn_to('PDF', h.url_current('download', format='pdf', id=sooritaja.id), level=2)}
      ${h.btn_to('Excel', h.url_current('download', format='xls', id=sooritaja.id), level=2)}
      % else:
      ## avalik/testid/psyhtulemus.py
      ${h.btn_to('PDF', h.url_current('download', format='pdf', id=sooritus.id), level=2)}
      ${h.btn_to('Excel', h.url_current('download', format='xls', id=sooritus.id), level=2)}
      % endif
  </div>
</div>

<table class="table" width="100%">
  <col/>
  <col width="80"/>
  <col width="80"/>
  <col width="80"/>
  <col width="80"/>
  <col width="30"/>
  <col width="30"/>
  <col width="30"/>
  <col width="30"/>
  <col width="30"/>
  
  <thead>
    <tr>
      % for title in header:
      ${h.th(title)}
      % endfor
    </tr>
  </thead>
  <tbody>
    % for item in items:
    <tr>
      % if len(item) == 1:
      ## alatestide grupi nimetus
      <td colspan="11"><b>${item[0]}</b></td>
      % else:
      % for value in item:
      <td>${value}</td>
      % endfor
      % endif
    </tr>
    % endfor
  </tbody>
</table>  

% if fig_json:
    <div id="dgmk"></div>
    <script>
      Plotly.newPlot(document.getElementById("dgmk"), ${fig_json});
    </script>
% endif
<br/>
% endfor
% endif
</div>


