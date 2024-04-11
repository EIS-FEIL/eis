% if c.items != '' and not c.items:
${_("Sooritajaid ei ole")}
% elif c.items:
<%
  testiosa = c.toimumisaeg.testiosa
  on_kursus = testiosa.test.on_kursused
  on_kirjalik = testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_KP)
  c.can_update = c.user.has_permission('korraldamine', const.BT_UPDATE, obj=c.testikoht or c.test) 
%>
${h.pager(c.items, msg_not_found=_("Sooritajaid ei leitud"), msg_found_one=_("Leiti 1 sooritaja"), msg_found_many=_("Leiti {n} sooritajat"))}

<%
  hide1 = 'd-none d-xl-table-cell'
  hide2 = 'd-xl-none'
%>
<table class="table table-borderless table-striped">
  <thead>
    <tr>
      <th>
        % if c.can_update:
        ${h.checkbox('all_s', 1, onclick="toggle_all_s(this)", class_="nosave", title=_("Vali kõik"))}
        % endif
      </th>
      ${h.th_sort('sooritus.tahised', _("Tähis"), class_=hide1)}
      ${h.th_sort('kasutaja.isikukood kasutaja.synnikpv', _("Isikukood või sünniaeg"), class_=hide1)}
      ${h.th_sort('sooritaja.perenimi sooritaja.eesnimi', _("Nimi"), class_=hide1)}
      ${h.th_sort('kasutaja.isikukood kasutaja.synnikpv sooritaja.perenimi sooritaja.eesnimi', _("Sooritaja"), class_=hide2)}
      % if c.testikoht:
      ${h.th_sort('testiruum.tahis', _("Testiruum"))}
      ${h.th_sort('ruum.tahis_NUM', _("Ruum"))}
      ${h.th_sort('testiprotokoll.tahised', _("Grupp"))}
      % endif
      ${h.th_sort('koolinimi.nimi', _("Õppeasutus"), class_=hide1)}
      ${h.th_sort('sooritaja.klass', _("Klass"), class_=hide1)}
      ${h.th_sort('sooritaja.paralleel', _("Paralleel"), class_=hide1)}
      ${h.th_sort('sooritaja.lang_LS', _("Soorituskeel"))}
      % if on_kursus:
      ${h.th_sort('sooritaja.kursus_kood', 'Kursus')}
      % endif
      ${h.th_sort('piirkond.nimi', _("Soovitav piirkond"), class_=hide1)}
      ${h.th_sort('sooritaja.regviis_kood', _("Reg-viis"), class_=hide1)}
      % if c.testikoht:
      % if on_kirjalik:
      ${h.th_sort('testiruum.algus', _("Aeg"))}
      % else:
      ${h.th_sort('sooritus.kavaaeg', _("Aeg"))}
      % endif
      % endif
      ${h.th_sort('sooritus.staatus,sooritaja.valimis', _("Olek"))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
      tos, s, k, koht_nimi, piirkond_nimi, testiruum = rcd
      testiprotokoll = tos.testiprotokoll
      ruum = testiruum and testiruum.ruum or None
    %>
    <tr>
      <td>
        % if c.can_update:
        ${h.checkbox('sooritus_id', tos.id, onclick="toggle_sooritus()",
        class_='nosave sooritus_id', title=_("Vali rida {s}").format(s=tos.tahised or ''))}
        % endif
        ${h.hidden('s-%d.sooritus_id' % n, tos.id)}
      </td>
      <td class="${hide1}">
        ${tos.tahised} <!--(${tos.id})--></td>
      <td class="${hide1}">
        ${k.isikukood or h.str_from_date(k.synnikpv)}</td>
      <td class="${hide1}">
        ${s.nimi}</td>
      <td class="${hide2}">
        ${k.isikukood or h.str_from_date(k.synnikpv)}
        <div>${s.nimi}</div>
      </td>
      % if c.testikoht:
      <td>${testiruum and testiruum.tahis}</td>
      <td>
        ${ruum and ruum.tahis or ''}
      </td>
      <td>${testiprotokoll and testiprotokoll.tahis}</td>
      % endif
      <td class="${hide1}">
        ${koht_nimi or ''}
      </td>
      <td class="${hide1}">
        ${s.klass}</td>
      <td class="${hide1}">
        ${s.paralleel}</td>
      <td>${model.Klrida.get_lang_nimi(s.lang) or ''}</td>
      % if on_kursus:
      <td>${s.kursus_nimi}</td>
      % endif
      <td class="${hide1}">${piirkond_nimi or ''}</td>
      <td class="${hide1}">${s.regviis_nimi}</td>
      % if c.testikoht:
      <td>
        <%
             ## kirjalikus kõik alustavad koos samal ajal või protokollirühma aja järgi
             algus = testiruum.algus
             if algus and testiprotokoll and testiprotokoll.algus:
                algus = h.datetime.combine(algus, testiprotokoll.algus.time())
             if not on_kirjalik and tos.kavaaeg:
                # suulises on igal oma kell
                algus = tos.kavaaeg
        %>
        % if on_kirjalik:
        ${h.str_from_datetime(algus, hour0=False)}
        % else:
        ${h.str_from_date(testiruum.algus)}
        ${h.time('s-%d.kellaaeg' % n, algus, allow_clear=False)}
        % endif
      </td>
      % endif
      <td>${tos.staatus_nimi}
        % if s.valimis:
        ${_("(valimis)")}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
