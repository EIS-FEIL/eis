<div container_sel="#hk_hindamiskriteeriumid">
<%
  items = list(c.item.hindamiskriteeriumid)
  can_update = c.user.has_permission('ekk-testid', const.BT_UPDATE, c.test)
  can_rm = can_update

  err = None
  if items:
     if c.item.arvutihinnatav:
        err = _("Hindamiskriteeriume saab kasutada e-testi käsitsi hindamisel, aga see hindamiskogum on arvutihinnatav, mistõttu tekib vastuolu")
     elif c.testiosa.vastvorm_kood not in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I):
        err = _("Vastamise vorm ei võimalda hindamiskriteeriumitega hindamist")
       
     if c.testiosa.lotv:
        alatestid_id = {vy.testiylesanne.alatest_id for vy in c.item.valitudylesanded}
     else:
        alatestid_id = {ty.alatest_id for ty in c.item.testiylesanded}
     if len(alatestid_id) > 1:
        err = _("Hindamiskriteeriumitega hindamiskogumi kõik ülesanded peavad kuuluma samasse alatesti")

  c.can_add_new_hindamiskrit = can_update and not err
%>
% if items:
% if err:
<div class="error">${err}</div>
% endif
<h3>${_("Hindamiskriteeriumid")}</h3>
% if c.is_edit or c.item.on_markus_sooritajale:
${h.checkbox('f_on_markus_sooritajale', 1, checked=c.item.on_markus_sooritajale,
label=_("Hindamisel saab jätta sooritajale märkusi"))}
% endif
<table width="100%" border="0"  class="table table-borderless table-striped tablesorter">
  <col width="50"/>
  <col/>
  <col/>
  <col/>
  <col/>
  <col/>
  <col width="30"/>
  <col width="30"/>
  <thead>
    <tr>
      <th>${_("Jrk")}</th>
      <th>${_("Õppeaine")}</th>
      <th>${_("Aspekt")}</th>
      <th>${_("Max toorpunktid")}</th>
      <th>${_("Kaal")}</th>
      <th>${_("Hindamisjuhend")}</th>
      <th sorter="false" colspan="2"></th>
    </tr>
  </thead>
  <tbody>
% for n, rcd in enumerate(items):
    <tr>
      <td>${rcd.seq}</td>
      <td>${rcd.aine_nimi}</td>
      <td>
        % if rcd.aspekt:
        ${rcd.aspekt_nimi}
        % else:
        <span class="error">
        ${_("Aspekt {s} on klassifikaatorist eemaldatud").format(s=rcd.aspekt_kood)}
        </span>
        % endif
      </td>
      <td>${h.fstr(rcd.max_pallid)}</td>
      <td>${h.fstr(rcd.kaal)}</td>
      <td>
        <% pkirjeldused = list(rcd.kritkirjeldused) %>
        % if len(pkirjeldused):
        <table width="100%"  class="table table-borderless table-striped">
          <col width="20"/>
          <col/>
          % for r in pkirjeldused:
          <tr>
            <td>${h.fstr(r.punktid)}p</td>
            <td>${r.kirjeldus and r.kirjeldus.replace('\n','<br/>')}</td>
          </tr>
          % endfor
        </table>
        % endif
        ${h.literal(rcd.hindamisjuhis or rcd.aspekt and rcd.aspekt.ctran.kirjeldus or '')}
      </td>
      % if can_rm:
      <td>
        ${h.remove(h.url('test_delete_hindamiskriteerium', test_id=c.test.id, hindamiskogum_id=c.item.id, id=rcd.id))}
      </td>
      % endif
      % if can_update:
      <td>
        ${h.dlg_edit(h.url('test_edit_hindamiskriteerium', test_id=c.test.id, hindamiskogum_id=c.item.id, id=rcd.id), _("Hindamiskriteerium"), size='lg')}
      </td>
      % endif
    </tr>
% endfor    
  </tbody>
</table>

% endif

</div>
