<% 
  if c.item:
     c.can_update = c.user.has_permission('nimekirjad', const.BT_UPDATE, c.item)
  else:
     c.can_update = c.user.has_permission('testid', const.BT_UPDATE, c.test)
  test = c.test
  on_kursus = test.on_kursused 
  c.on_regatud = False
%>

% if len(c.item.sooritajad) > 0:
<table width="100%" border="0" class="table table-striped tablesorter">
  <caption>${_("Testi sooritajad")}</caption>
  <thead>
    <tr>
      ${h.th(_('Isikukood'))}
      ${h.th(_('Nimi'))}
      ${h.th(_('Keel'))}
      % if on_kursus:
      ${h.th(_('Kursus'))}
      % endif
      ${h.th(_("Olek"))}
      ${h.th(_("Tugiisik"))}
      % if c.can_update:
      ${h.th('', sorter='false', width="20px")}
      % endif
    </tr>
  </thead>
  <tbody>
    <%
      testiruumid_id = [r.id for r in c.item.testiruumid]
      ## jätame sooritajate loetlust välja taustakysitluse õpetaja soorituse 
      sooritajad = [r for r in c.item.sooritajad if not r.opetajatest]
    %>
    % for rcd in sooritajad:
    <%
      # kui mitme kooli all sisse loginult on pandud sooritajad samasse nimekirja,
      # siis on neil erinevad testiruumid
      if rcd.staatus == const.S_STAATUS_REGATUD:
         c.on_regatud = True
      testiruum_id = c.testiruum_id
      if len(testiruumid_id) > 1:
         for tos in rcd.sooritused: 
             if tos.testiruum_id in testiruumid_id:
                testiruum_id = tos.testiruum_id
                break
    %>
    <tr>
      <td>
        ${rcd.kasutaja.isikukood}
      </td>
      <td>
        % if c.can_update:
        ${h.link_to(rcd.eesnimi + ' ' + rcd.perenimi, h.url('test_nimekiri_kanne', nimekiri_id=rcd.nimekiri_id, id=rcd.id, test_id=c.test_id, testiruum_id=testiruum_id))}
        % else:
        ${rcd.eesnimi} ${rcd.perenimi}
        % endif
      </td>
      <td>${model.Klrida.get_lang_nimi(rcd.lang)}</td>
      % if on_kursus:
      <td>${rcd.kursus_nimi}</td>
      % endif
      <td>${rcd.staatus_nimi}</td>
      <td>
        <% sooritused = list(rcd.sooritused) %>
        % for tos in sooritused:
        <% tugik = tos.tugiisik_kasutaja %>
        % if tugik:
        <div>
          ${tugik.nimi}
          % if len(sooritused) > 1:
          (${tos.testiosa.nimi})
          % endif
        </div>
        % endif
        % endfor
      </td>
      % if c.can_update:
      <td>
        % if rcd.staatus <= const.S_STAATUS_ALUSTAMATA:
          ${h.remove(h.url('test_nimekiri_delete_sooritaja', test_id=c.test_id, testiruum_id=testiruum_id, nimekiri_id=rcd.nimekiri_id, id=rcd.id))}
        % endif
      </td>
      % endif
    </tr>
    % endfor    
  </tbody>
</table>
% else:
${h.alert_notice(_("Sooritajaid pole nimekirja lisatud"), False)}
% endif

