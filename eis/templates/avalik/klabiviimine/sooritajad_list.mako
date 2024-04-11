<%
  on_tegemata = False
  test = c.testiosa.test
  on_psyhtest = test.testiliik_kood == const.TESTILIIK_KOOLIPSYH
  on_diag2 = test.testiliik_kood == const.TESTILIIK_DIAG2
  on_kursused = c.testiosa.test.on_kursused 
  on_kirjalik = c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE)
  on_keel = c.toimumisaeg and c.toimumisaeg.keel_admin and (len(test.keeled) > 1)
  hide1 = 'd-none d-xl-table-cell'
%>
<h2>${_("Sooritajad")}</h2>
<table class="table table-borderless table-striped tablesorter" id="sooritajad_tbl">
  <col width="20px"/>
  <thead>
    <tr>
      % if c.can_update:
      <th sorter="false">
        ${h.checkbox1('alls', 1, class_="nosave", title=_("Vali kõik"))}
      </th>
      % endif
      ${h.th(_("Isikukood"))}
      ${h.th(_("Nimi"))}
      % if on_kursused:
      ${h.th(_("Kursus"))}
      % endif
      ${h.th(_("Olek"))}
      % if on_keel:
      ${h.th(_("Soorituskeel"))}
      % endif
      ${h.th(_("Alustamise aeg"))}
      % if c.nimekiri and not on_psyhtest and c.test.naita_p:
      ${h.th(_("Tulemus"))}
      % endif
      % if c.testiruum and c.testiruum.arvuti_reg and on_kirjalik:
      ${h.th(_("Reg arvuti"), class_=hide1)}
      % endif
      ${h.th(_("Ajakulu"), class_=hide1)}
      % if on_diag2:
      ${h.th(_("Kuupäev"), class_=hide1)}
      % endif
      % if not on_diag2 and on_kirjalik:
      ${h.th(_("Arvuti"), class_=hide1)}
      ${h.th(_("Autentimine"), class_=hide1)}
      % endif
##      % if on_proctorio:
##      ${h.th(_("Proctorio"), class_=hide1)}
##      % endif
      % if not on_diag2:
      ${h.th('', sorter='false')}
      % endif
    </tr>
  </thead>
  <tbody>
    <%
       on_piiraeg = c.testiosa.on_piiraeg
       max_pallid = c.testiosa.max_pallid
    %>
    % for rcd in c.items:
       <%
          # rcd on Sooritus
          sooritaja = rcd.sooritaja
          kasutaja = sooritaja.kasutaja
          if rcd.staatus != const.S_STAATUS_TEHTUD:
             on_tegemata = True
       %>
    <tr data-vst="${rcd.staatus}" data-vrf="${rcd.luba_veriff and 1 or 0}" id="trtos${rcd.id}">
      % if c.can_update:
      <td>${h.checkbox('sooritus_id', rcd.id, checked=False, ronly=False, class_="sooritus nosave", title=_("Vali rida {s}").format(s=kasutaja.isikukood))}</td>
      % endif
      <td>${kasutaja.isikukood}</td>
      <td>
        % if on_kirjalik:
          <%
            if c.test.avaldamistase == const.AVALIK_LITSENTS and on_psyhtest:
               url = h.url('test_psyhtulemus', test_id=sooritaja.test_id, testiruum_id=rcd.testiruum_id, id=rcd.id)
            else:
               url = None
          %>
          % if url:
          ${h.link_to(sooritaja.nimi, url)}
          % else:
          ${sooritaja.nimi}
          % endif
        % else:
          <%
            if rcd.staatus in (const.S_STAATUS_REGATUD, const.S_STAATUS_ALUSTAMATA):
               url = h.url('sooritamine_alusta_osa', test_id=c.test.id, testiosa_id=rcd.testiosa_id, id=rcd.id)
            elif rcd.staatus in (const.S_STAATUS_POOLELI, const.S_STAATUS_KATKESTATUD):
               url = h.url('sooritamine_jatka_osa', test_id=c.test.id, testiosa_id=rcd.testiosa_id, id=rcd.id)
            else:
               url = None
          %>
          % if url:
          ${h.link_to(sooritaja.nimi, url, method='post', class_="pl-0")}        
          % else:
          ${sooritaja.nimi}
          % endif
        % endif
      </td>
      % if on_kursused:
      <td>${sooritaja.kursus_nimi}</td>
      % endif
      <td id="staatus_${rcd.id}">
        ${rcd.staatus_nimi}
        % if rcd.luba_veriff and c.toimumisaeg:
        % if c.toimumisaeg.verif:
        (${_("ei pea isikut tõendama")})
        % elif c.toimumisaeg.verif_seb:
        (${_("ei pea SEBi kasutama")})
        % endif
        % endif
        % if sooritaja.klaster_id:
        <span style="display:none" class="klaster">kl ${sooritaja.klaster_id}</span>
        % endif
      </td>
      % if on_keel:
      <td>
        ${sooritaja.lang_nimi}
      </td>
      % endif
      <td id="algus_${rcd.id}">
        ${h.str_time_from_datetime(rcd.algus)}
      </td>
 
      % if c.nimekiri and not on_psyhtest and c.test.naita_p:
      <td id="pallid_${rcd.id}">
        % if rcd.pallid:
        ${rcd.get_tulemus()}
        % endif
      </td>
      % endif

      % if c.testiruum and c.testiruum.arvuti_reg and on_kirjalik:
      <td id="arvuti_${rcd.id}" class="${hide1}">
        <% testiarvuti = rcd.testiarvuti %>
        % if testiarvuti:
        % if c.toimumisaeg and c.toimumisaeg.on_reg_test:
        ${testiarvuti.tahis}
        % else:
        ${testiarvuti.seq}
        % endif
        % endif
      </td>
      % endif
      <td id="ajakulu_${rcd.id}" class="${hide1}">
        ${h.str_from_time(rcd.ajakulu)}
      </td>
      % if on_diag2:
      <td class="${hide1}">
        ${h.str_from_date(rcd.lopp)}
      </td>
      % endif
      % if not on_diag2 and on_kirjalik:
      <td id="remote_${rcd.id}" class="${hide1}">
        ${rcd.remote_addr}
      </td>
      <td id="autentimine_${rcd.id}" class="${hide1}">
        ${rcd.autentimine_nimi or ''}
      </td>
      % endif
##      % if on_proctorio:
##      <td class="${hide1}">
##        <%
##          q = (model.Session.query(model.Proctoriolog.review_url)
##               .filter_by(sooritus_id=rcd.id)
##               .order_by(model.sa.desc(model.Proctoriolog.id)))
##          for r in q.all():
##             url = r[0]
##             break
##        %>
##        % if url:
##        ${h.link_to('Vaata', url, target='proctorio')}
##        % endif
##      </td>
##      % endif
      % if not on_diag2:
      <td>
      % if not c.veel_ei_toimu and c.can_update:  
      <%
        if c.nimekiri:
           url = h.url_current('edit', sub='markus', sooritus_id=rcd.id, partial=True)
        else:
           url = h.url_current('edit', sub='markus',id=c.testiruum.id, sooritus_id=rcd.id, partial=True)
        mdicls = (rcd.markus or rcd.stpohjus) and 'mdi-comment-edit' or 'mdi-comment-edit-outline'
      %>
        ${h.btn_to_dlg('', url, title=_("Märkus"), width=600, level=2, class_="mdibtn ml-2",
                       mdicls=mdicls)}

        % if on_piiraeg:
        <%
          lisaaeg = rcd.lisaaeg or len([s for s in rcd.alatestisooritused if s.lisaaeg])
          if c.nimekiri:
             url = h.url_current('edit', sooritus_id=rcd.id, partial=True, sub='lisaaeg')
          else:
             url = h.url_current('edit', id=c.testiruum.id, sooritus_id=rcd.id, partial=True, sub='lisaaeg')
          mdicls = lisaaeg and 'mdi-account-clock' or 'mdi-account-clock-outline'
        %>
        ${h.btn_to_dlg('', url, title=_("Lisaaeg"), width=600, level=2, class_="mdibtn ml-2",
                       mdicls=mdicls)}
        % endif
      % endif
      </td>
      % endif
    </tr>
    % endfor    
  </tbody>
</table>
