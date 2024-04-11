<%
  c.on_alatestid = False 
  c.mitu_testiosa = 0
  test = c.item.test
  for testiosa in test.testiosad:
      c.mitu_testiosa += 1
      if testiosa.on_alatestid:
         c.on_alatestid = True
  c.mitu_testiosa = c.mitu_testiosa > 1
  c.test_pallideta = test.test_pallideta
  tails = [c.pos_ty_r, c.pos_ty_k, c.pos_ty_l, c.yhisosa, c.yhis_pos_ty_r, c.yhis_pos_ty_k, c.yhis_pos_ty_l]
  c.tail_cnt = sum([r and 1 or 0 for r in tails]) 

  c.sooritaja = c.item
  testimiskord = c.item.testimiskord

  visibility = c.item.tulemus_nahtav(None, c.app_ekk, c.sooritaja_roll, test, testimiskord)
  olen_tv = c.user.has_permission('toovaatamine', const.BT_SHOW, obj=c.item)
  if testimiskord:
      c.opetaja_vaatab_testimiskorrata = ''
  on_tagasiside = visibility.is_ts or c.opetaja_vaatab_testimiskorrata
%>

% if not test.diagnoosiv:
  ${self.tabel_sooritused(test, testimiskord)}
% endif

% if not (olen_tv or on_tagasiside):
${h.alert_notice(_("Tulemusi ei ole avaldatud"), False)}

% elif not c.test_pallideta and visibility.is_k:
<div>
      <b>${_("Tulemus")}</b>
      % if c.app_ekk and c.item.tulemus_aeg:
      (${h.str_from_date(c.item.tulemus_aeg)})
      % endif
      <br/>
      % if c.item.hindamine_staatus != const.H_STAATUS_HINNATUD:
      ${_("Hindamata")}
      % endif
      % if c.item.hindamine_staatus == const.H_STAATUS_HINNATUD or c.item.pallid is not None:
      ${c.item.get_tulemus()}
      % if c.item.keeletase_kood:
      ${c.item.keeletase_nimi}
      % endif
      % endif
</div>
% endif

% if on_tagasiside:
<div>
  ${c.tagasiside_html}
</div>
% endif

% if c.app_ekk:
${self.tabel_veriff()}
% endif
  
% if c.tulemuste_kohta_on_tehtud_vaie:
<div class="m-2 d-flex">
  ${_("Tulemuste kohta esitatud vaie")}
  ${h.link_to(_("Vaide avaldus"), h.url('vaie', sub='avaldus', id='%s.bdoc' % c.item.id), class_="ml-3")}
  ${h.link_to(_("Vaide otsus"), h.url('vaie', sub='otsus', id='%s.bdoc' % c.item.id), class_="ml-3")}
</div>
% endif

% if c.app_ekk:
${self.ylesandevastused_acc()}
% endif

<%def name="ylesandevastused_acc()">
<div class="accordion my-2" id="detaildata_acc">
  <div class="accordion-card card parent-accordion-card">
    <div class="card-header" id="heading_log1">
      <div class="accordion-title" style="background-color:transparent">
        <button class="btn btn-link collapsed" type="button"
                data-toggle="collapse"
                data-target="#collapsedetail"
                aria-controls="collapsedetail"
                aria-expanded="true"
                id="bdetail"
                data-href="${h.url_current('show', sub='detail')}"
                style="background-color:transparent">
          <span class="btn-label"><i class="mdi mdi-chevron-down"></i>
            ${_("Testisoorituse üksikasjad")}
          </span>
        </button>
      </div>
      <script>
        $('#bdetail').click(function(){
        var d = $('#detail_content');
        if(d.text()=='') dialog_load($(this).data('href'), '', 'GET', d);
        });
        % if request.params.get('detail'):
        $(function(){ $('#bdetail').click(); });
        % endif
      </script>
    </div>
    <div id="collapsedetail" class="collapse" aria-labelledby="headingdetail">
      <div class="card-body">
        <div class="content" id="detail_content"></div>
      </div>
    </div>
  </div>
</div>
</%def>

<%def name="tabel_sooritused(test, testimiskord)">
<table width="100%"  class="table">
  <col width="180px"/>
  % if c.opetaja_vaatab_testimiskorrata:
  <tr>
    <td class="fh" valign="top">${_("Sooritaja")}</td>
    <td colspan="2">
      ${c.sooritaja.nimi}
    </td>
  </tr>
  % endif
  <tr>
    <td class="fh" valign="top">${_("Test")}</td>
    <td colspan="2">
      ${test.nimi}
      % if c.item.kursus_kood:
      (${c.item.kursus_nimi})
      % endif
    </td>
  </tr>
  <tr>
    <td colspan="3">
      <%
        sooritused = list(c.item.sooritused)
        on_tugik = on_isikudok = False
        for tos in sooritused:
            if tos.tugiisik_kasutaja_id:
                on_tugik = True
            if tos.isikudok_nr:
                on_isikudok = True
      %>
      <table  width="100%" class="table table-borderless table-striped">
        <thead>
          <tr>
            ${h.th(_("Aeg"))}
            % if c.item.testimiskord_id:
            ${h.th(_("Toimumisaja tähis"))}
            ${h.th(_("Soorituse tähis"))}
            % if on_tugik:
            ${h.th(_("Tugiisik"))}
            % endif
            % if on_isikudok:
            ${h.th(_("Esitatud dokumendi nr"))}
            % endif
            % else:
            % endif
            ${h.th(_("Soorituskoht"))}
            ${h.th(_("Vastamise vorm"))}
            ${h.th(_("Olek"))}
            ${h.th(_("Testiosa tulemus"))}
            % if c.on_alatestid:
            ${h.th(_("Alatest"))}
            % endif
          </tr>
        </thead>
        <tbody>
          % for tos in sooritused:
             <%
                 testiosa = tos.testiosa
                 toimumisaeg = tos.toimumisaeg
                 algus = tos.seansi_algus or tos.algus or tos.kavaaeg
                 if algus:
                    algus = h.str_from_date(algus)
                 elif tos.toimumisaeg:
                    algus = tos.toimumisaeg.millal
                 else:
                    algus = '-'

                 testikoht = tos.testikoht
                 koht = testikoht and testikoht.koht
                 tugik = tos.tugiisik_kasutaja
                 visibility = c.item.tulemus_nahtav(tos, c.app_ekk, c.sooritaja_roll, test, testimiskord)
              %>
          <tr>
            <td>
              ${algus}<!--tos ${tos.id}-->
            </td>
            % if c.item.testimiskord_id:
            <td>
              % if toimumisaeg:
              ${toimumisaeg.tahised}<!--${tos.toimumisaeg_id}-->
              % endif
            </td>
            <td>
              ${tos.tahised}
            </td>
            % if on_tugik:
            <td>
              % if tugik:
              ${tugik.nimi}
              % endif
            </td>
            % endif
            % if on_isikudok:
            <td>
              ${tos.isikudok_nr}
            </td>
            % endif
            % endif
            <td>
              % if koht:
              ${koht.nimi}
              % endif
            </td>
            <td>${testiosa.vastvorm_nimi}</td>
            <td>
              ${tos.staatus_nimi}
              % if visibility.is_resp and testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_I):
                % if c.on_kontroll:
               ${h.link_to(_("Vaata"), h.url('nimekirjad_kontroll_tulemus_osa', test_id=testiosa.test_id, testiosa_id=tos.testiosa_id, alatest_id='', id=tos.id))}
                % elif c.on_koolitulemus:
               ${h.link_to(_("Vaata"), h.url('koolitulemused_osa', test_id=c.item.test.id, alatest_id='', id=c.sooritus.id, klass_id=c.klass_id))}
                % elif c.on_ktulemus:
               ${h.link_to(_("Vaata"), h.url('ktulemused_osa', test_id=c.test.id, kursus=c.item.kursus_kood or '', testimiskord_id=c.testimiskord.id, testiosa_id=tos.testiosa_id, alatest_id='', id=tos.id))}
                % elif c.on_testitulemus:
               ${h.link_to(_("Vaata"), h.url('testitulemused_osa', alatest_id='', statistika_id=c.statistika.id, id=tos.id))}
                % elif c.opetaja_vaatab_testimiskorrata:
                  % if not c.test.opetajale_peidus:
                ${h.link_to(_("Vaata"), h.url('test_labiviimine_sooritus', test_id=c.test.id, testiruum_id=tos.testiruum_id, id=tos.id))}
                  % endif
                % else:
               ${h.link_to(_("Vaata"), h.url('tulemus_osa', test_id=testiosa.test_id, testiosa_id=tos.testiosa_id, alatest_id='', id=tos.id))}
                % endif             
              % endif
              % if tos.skannfail and testiosa.vastvorm_kood == const.VASTVORM_KP:
              <%
                if c.app_ekk:
                   skann_url = h.url('muud_skannid_tellimine', id='%s.pdf' % (tos.id))
                else:
                   skann_url = h.url('tulemus_skannfail', id=tos.id)
              %>
              ${h.pdflink_to(skann_url, _("Laadi alla"))}
              % endif
            </td>
            <td>
            % if not c.test_pallideta:
              % if visibility.is_k:
              % if tos.pallid is not None:
               ${tos.get_tulemus()}
              % endif
              % else:
              ${_("Avaldamata")}
              % endif
            % endif
            </td>
            % if c.on_alatestid:
            <td>
              % if visibility.is_a:
              % for alatest in tos.alatestid:
              <% atos = tos.get_alatestisooritus(alatest.id) %>
              <div>
              ${alatest.nimi}
                % if atos and atos.staatus==const.S_STAATUS_TEHTUD and not c.test_pallideta:
                ${atos.get_tulemus(alatest.max_pallid) or atos.staatus_nimi}
                  % if c.app_ekk and alatest.skoorivalem and atos.oigete_arv is not None:
                  ${_("(õigeid {n})").format(n=atos.oigete_arv)}
                  % endif
                % elif atos:
                  ${atos.staatus_nimi}
                % endif
              </div>
              % endfor
              % endif
            </td>
            % endif
          </tr>
          % if tos.markus:
          <tr>
            <td colspan="12">
              <i>${_("Märkus")}.</i> ${tos.markus}
            </td>            
          </tr>
          % endif
          % endfor
        </tbody>
      </table>
        <%
          mitu = len(sooritused) > 1
        %>
        % for tos in sooritused:
        % if tos.on_rikkumine:
        <% 
          if mitu:
             buf = _("Rikkumise tõttu on testiosa {s} hinnatud 0 punktiga.").format(s=tos.testiosa.tahis)
          else:
             buf = _("Rikkumise tõttu on töö hinnatud 0 punktiga.")
          buf += '<br/>' + tos.rikkumiskirjeldus
        %>
        ${h.alert_warning(buf, False)}
        % endif
        % endfor
    </td>
  </tr>

  % if c.tunnistus:
  <tr>
    <td class="fh">${_("Tunnistus")}</td>
    <td colspan="2">
      ${h.link_to(_("ava tunnistus"), h.url('tunnistus'))}
    </td>
  </tr>
  % endif
</table>
</%def>

<%def name="tabel_veriff()">
<%
  q = (model.Session.query(model.Sooritus.id, model.Sooritus.verifflog_id)
       .filter_by(sooritaja_id=c.item.id))
  li = list(q.all())
  sooritused_id = [r[0] for r in li]
  logid_id = [r[1] for r in li]
  q = (model.Session.query(model.Verifflog)
       .filter(model.sa.or_(model.Verifflog.sooritus_id.in_(sooritused_id),
                      model.Verifflog.id.in_(logid_id)))
       .order_by(model.Verifflog.created))
  items = list(q.all())
%>
% if items:
<table  class="table table-borderless table-striped">
  <caption>Isiku tõendamine</caption>
  <thead>
    <tr>
      ${h.th(_("Alustatud"))}
      ${h.th(_("Lõpetatud"))}
      ${h.th(_("Testiosa"))}
      ${h.th(_("Otsus"))}
      ${h.th(_("Dokument"))}
      ${h.th(_("Isik"))}
      ${h.th(_("Isik tõendatud"))}
      ## ${h.th(_("Sessiooni ID"))}
    </tr>
  </thead>
  <tbody>
    % for item in items:
    <tr>
      <td>${h.str_from_datetime(item.created, True)}</td>
      <td>${h.str_from_datetime(item.submitted, True)}</td>
      <td>
        ## testiosad, mille sooritamiseks seda seanssi kasutati
        <%
           q1 = (model.Session.query(model.Testiosa.tahis)
             .join(model.Sooritus.testiosa)
             .filter(model.Sooritus.verifflog_id==item.id)
             .order_by(model.Testiosa.seq))
           lubab_osa = [tahis for tahis, in q1.all()]
         %>
         % if lubab_osa:
        ${', '.join(lubab_osa)}
         % endif

        ## testiosa, mille sooritamiseks veriffisse mindi
        % if item.sooritus_id in sooritused_id:
        <%
          tos = model.Sooritus.get(item.sooritus_id)
          osa_tahis = tos.testiosa.tahis
        %>
        (${osa_tahis})
        % endif
      </td>
      <td>
        <%
          data = item.dec_json
          verif = data and data.get('verification')
          status = verif and verif.get('status')
          reason = verif and verif.get('reason')
          doc = verif and verif.get('document')
          doctype = doc and doc.get('type')
          valid_until = doc and doc.get('validUntil')
          person = verif and verif.get('person')
          firstname = person and person.get('firstName')
          lastname = person and person.get('lastName')
        %>
        % if verif:
        ${status}
        % if reason:
        <br/>${reason}
        % endif
        % endif
      </td>
      <td>
        % if doctype:
        ${doctype}
        % endif
        % if valid_until:
        ${_("kehtib kuni")} ${valid_until}
        % endif
      </td>
      <td>${item.riik}${item.isikukood}
        % if person:
        ${firstname} ${lastname}
        % endif
      </td>
      <td>${h.sbool(item.rc)}</td>
     ## <td>${item.session_id}</td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
% for tos in c.item.sooritused:
% if tos.luba_veriff:
<div>${_("Testiosa {s} sooritamine lubatud ilma isikut tõendamata").format(s=tos.testiosa.tahis)}</div>
% endif
% endfor
</%def>
