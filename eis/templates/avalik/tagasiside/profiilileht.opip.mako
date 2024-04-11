## -*- coding: utf-8 -*- 

<div class="border border-base-radius p-3">
  <div class="row">
  <div class="col-sm-6">
      <b>${c.sooritaja.test.nimi}</b>
      <br/>
      Nimi: ${c.sooritaja.nimi}
      <br/>
      % if c.sooritaja.klass:
      Klass: ${c.sooritaja.klass}${c.sooritaja.paralleel} &nbsp; &nbsp;
      % endif
      % if c.sooritaja.kool_koht:
      Kool: ${c.sooritaja.kool_koht.nimi}
      % endif
  </div>
  <div class="col-sm-6">
      <b>Profiilileht</b>
      <br/>
      Testimise aeg: ${c.sooritaja.millal}
      % if c.sooritaja.staatus != const.S_STAATUS_TEHTUD:
      (${c.sooritaja.staatus_nimi})
      % endif
  </div>
  </div>
</div>

% if c.sooritaja.staatus == const.S_STAATUS_TEHTUD:
% for sooritus in c.sooritaja.sooritused:
<%
   header, items, dgm_data = c.prepare_sooritus(sooritus)
%>
% if not model.is_temp_id(sooritus.id) and c.action != 'download':
<div class="d-flex p-3 justify-content-between">
  <div>
      % if c.app_eis and not c.on_sooritusaknas and c.sooritaja.nimekiri_id and c.user.has_permission('omanimekirjad', const.BT_SHOW, obj=c.sooritaja.nimekiri):
      ${h.link_to('Vastused',
      h.url('test_labiviimine_sooritus', test_id=c.sooritaja.test_id, testiruum_id=sooritus.testiruum_id, id=sooritus.id))}
      % endif
  </div>
  <div class="text-right">
      % if c.app_ekk:
      ${h.btn_to('PDF', h.url_current('download', id=sooritus.id, format='pdf'), level=2)}
      ${h.btn_to('Excel', h.url_current('download', id=sooritus.id, format='xls'), level=2)}
      % else:
      ${h.btn_to('PDF', h.url_current('download', format='pdf'), level=2)}
      ${h.btn_to('Excel', h.url_current('download', format='xls'), level=2)}
      % endif
  </div>
</div>
% endif
<table class="table" width="100%" >
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

##% if dgm_data and c.app_eis:
##<%  str_data = c.pickle_dumps(dgm_data) %>
##<img src="${h.url('psyhtulemus_profiilidiagramm', sooritaja_id=c.sooritaja.id, data=str_data, rid=True)}"
##     alt="${u'Profiili diagramm'}"/>
##% endif
##<br/>
% endfor
% endif
</div>

