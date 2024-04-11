<%
  on_alatestid = c.testiosa.on_alatestid
  on_yhisosa = len(c.test.opt_kursused) > 1
  on_kptest = c.testiosa.vastvorm_kood == const.VASTVORM_KP
%> 
${h.pager(c.items)}
<table class="table table-borderless table-striped" width="100%" border="0" >
  <tr>
    ${h.th('')}
    ${h.th(_("Testiosa"))}
    ${h.th_sort('komplekt.tahis', _("Ülesandekomplekt"))}
% if on_alatestid:
    ${h.th_sort('alatest.nimi', _("Alatest"))}
    ${h.th_sort('testiplokk.nimi', _("Plokk"))}
% endif
    ${h.th_sort('testiylesanne.seq', _("Testiül"))}
    ${h.th_sort('testiylesanne.valikute_arv', _("Valik"))}
    ${h.th_sort('ylesanne.id', _("Ülesande ID"))}
    ${h.th_sort('ylesanne.nimi', _("Ülesanne"))}
    ${h.th_sort('testiylesanne.hindamine_kood', _("Hindamise liik"))}
    ${h.th_sort('ylesanne.arvutihinnatav', _("Arvutiga hinnatav"))}
    ${h.th_sort('testiylesanne.max_pallid', _("Hindepallid"))}
    ${h.th_sort('ylesanne.max_pallid', _("Toorpunktid"))}
    ${h.th_sort('valitudylesanne.koefitsient', _("Koefitsient"))}
% if on_yhisosa:
    ${h.th_sort('testiylesanne.yhisosa_kood', _("Ühisosa"))}
    ${h.th(_("Ühisosa küsimused"))}
% endif
  </tr>
  % for item in c.items:
    ## item on Valitudylesanne
    <% 
      testiylesanne = item.testiylesanne
      alatest = testiylesanne.alatest
      testiplokk = testiylesanne.testiplokk
      ylesanne = item.ylesanne
      komplekt = item.komplekt
      is_err = message = None
      if c.kontroll: 
         if ylesanne is None:
            message = _("Ülesanne on valimata")
         else:
            rc, message = c.check_ylesanne(request.handler, ylesanne, testiylesanne, komplekt, True)
            rc2, c.y_errors, c.sp_errors, c.k_errors, c.k_warnings = c.b_check_ylesanne(request.handler, ylesanne)
            is_err = not rc2
    %>
    % if is_err or message or c.k_warnings:
  <tr>
    <td colspan="16" class="error">
      % if message:
      <div>${message}</div>
      % endif
      % if is_err:
      <div>
        % for err in c.y_errors:
        <div>${err}</div>
        % endfor
        <%
          errors = []
          for errors1 in c.sp_errors.values():
             errors.extend(errors1)
          for errors1 in c.k_errors.values():
             errors.extend(errors1)
        %>
        % for error in sorted(set(errors)):
        <div>${error}</div>
        % endfor
        % for error in sorted(set(c.k_warnings)):
        <div>${error}</div>
        % endfor        
      % endif
    </td>
  </tr>
    % endif

  <tr>
    <td>
      % if not c.test.is_encrypted and c.can_update and komplekt.staatus==const.K_STAATUS_KOOSTAMISEL:
      ${h.btn_to_dlg(_("Vali"), h.url('test_komplekt_edit_otsiylesanne', test_id=c.test.id,
      komplekt_id=komplekt.id, id=item.seq,
      testiylesanne_id=testiylesanne.id, komplekt_id2=c.komplekt_id),level=2,size='lg',
      title=_("Ülesande valimine"), width=800)}

      % if c.user.has_permission('ylesanded', const.BT_CREATE):
      % if on_kptest:
      ${h.btn_to(_("Loo uus"), h.url('ylesanne_new_psisu', vy_id=item.id))}
      % endif
      % endif
      
      % endif
    </td>
    <td>${testiylesanne.testiosa.tahis}</td>
    <td>${item.komplekt.tahis}</td>
% if on_alatestid:
    <td>
      % if alatest and alatest.tahis:
      ${alatest.tahis}. ${alatest.nimi}
      % elif alatest:
      ${alatest.nimi}
      % endif
      % if alatest and alatest.kursus_kood:
      ${alatest.kursus_nimi}
      % endif
    </td>
    <td>
      % if testiplokk:
      ${testiplokk.seq}.
      ${testiplokk.nimi}
      % endif
    </td>
% endif
    <td>
      % if testiylesanne.tahis == testiylesanne.nimi or not testiylesanne.tahis:
      ${testiylesanne.nimi}
      % else:
      ${testiylesanne.tahis}. ${testiylesanne.nimi}
      % endif
    </td>
    <td>${testiylesanne.on_valikylesanne and item.seq or 'Ei'}</td>
    <td>
      % if ylesanne and not c.user.has_permission('ylesanded', const.BT_SHOW, obj=ylesanne):
        ${ylesanne.id}
      % elif ylesanne:
        ${h.link_to(ylesanne.id, h.url('ylesanne', id=ylesanne.id))}
      % endif
    </td>
    <td>
      % if ylesanne:
        % if not c.user.has_permission('ylesanded', const.BT_SHOW, obj=ylesanne):
          ${ylesanne.nimi}
        % elif on_kptest and ylesanne.ptest and not ylesanne.etest:
           ${h.link_to(ylesanne.nimi or ' ', h.url('ylesanne_edit_psisu', id=ylesanne.id, vy_id=item.id))}
        % else:
           ${h.link_to(ylesanne.nimi or ' ', h.url('ylesanne', id=ylesanne.id))}
        % endif
        % if ylesanne.salastatud != const.SALASTATUD_POLE:
           (${ylesanne.salastatud_nimi()})
        % endif
        % if not c.test.is_encrypted and c.can_update and item.komplekt.staatus==const.K_STAATUS_KOOSTAMISEL:
        ${h.remove(h.url('test_delete_valitudylesanne', test_id=c.test.id,
        testiosa_id=c.testiosa.id, komplekt_id=c.komplekt_id, id=item.id))}
        % endif
      % endif
    </td>
    <td>${testiylesanne.hindamine_nimi}
      % if ylesanne and ylesanne.hindamine_kood and ylesanne.hindamine_kood != testiylesanne.hindamine_kood:
      / ${ylesanne.hindamine_nimi}
      % endif
    </td>
    <td>
      ${h.sbool(testiylesanne.arvutihinnatav)}
      % if ylesanne and ylesanne.arvutihinnatav != testiylesanne.arvutihinnatav:
      / ${h.sbool(ylesanne.arvutihinnatav)}
      % endif
    </td>
    <td>${h.fstr(testiylesanne.max_pallid)}</td>
    <td>
      % if ylesanne:
      ${h.fstr(ylesanne.max_pallid)}
      % endif
    </td>
    <td>
      ${h.fstr(item.koefitsient)}
    </td>
% if on_yhisosa:
    <td>
      ${testiylesanne.yhisosa_kood}
      % if testiylesanne.yhisosa_max_pallid:
      - ${h.fstr(testiylesanne.yhisosa_max_pallid)}p
      % endif
    </td>
    <td>
      % if testiylesanne.yhisosa_kood and ylesanne:
      % for t in ylesanne.tulemused:
      % if t.yhisosa_kood:
      ${t.yhisosa_kood} - ${h.fstr(t.get_max_pallid(item.koefitsient))}p <br/>
      % endif
      % endfor
      % endif
    </td>
% endif

  </tr>
  % endfor
</table>
