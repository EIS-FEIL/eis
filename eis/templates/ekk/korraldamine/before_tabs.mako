<% 
c.testimiskord = c.toimumisaeg.testimiskord
c.test = c.testimiskord.test
c.testiosa = c.toimumisaeg.testiosa
ch = h.colHelper('col-lg-2 col-md-3 col-sm-6','col-lg-2 col-md-3 col-sm-6')
%>
<div class="gray-legend p-2 border-base-radius">
  <div class="form-group row mb-1">
    ${ch.flb(_("Test"), 'test')}
    <div class="col-md-8 col-sm-6" id="test">
      % if c.test.testityyp == const.TESTITYYP_KONS:
      ${h.link_to(c.test.nimi, h.url('konsultatsioon_kord', test_id=c.test.id,
      id=c.testimiskord.id), class_="pl-0")}
      % else:
      ${h.link_to(c.test.nimi, h.url('test_kord_toimumisaeg', test_id=c.test.id,
      kord_id=c.testimiskord.id, id=c.toimumisaeg.id), class_="pl-0")}
      % endif

      ## lingid kõigile toimumisaegadele
      % for ta2 in c.testimiskord.toimumisajad:
      % if ta2.id == c.toimumisaeg.id:
      ${c.toimumisaeg.tahised}
      % else:
      <%
        _tkoht_id = request.matchdict.get('testikoht_id')
        _tkoht2_id = ta2.get_testikoht_id(_tkoht_id)
        if not _tkoht_id:
            # soorituskoht pole valitud
            url2 = h.url_current(toimumisaeg_id=ta2.id)
        elif _tkoht2_id:
            # sama koht on teisel toimumisajal ka
            url2 = h.url_current(toimumisaeg_id=ta2.id, testikoht_id=_tkoht2_id)
        else:
            # sama kohta ei ole teisel toimumisajal
            url2 = h.url('korraldamine_soorituskohad', toimumisaeg_id=ta2.id)
      %>
      ${h.link_to(ta2.tahised, url2)}
      % endif
      % endfor
    </div>
    <div class="col text-right">
      <%
       url_h = None
       if c.user.has_permission('hindajamaaramine', const.BT_SHOW, obj=c.test):
           if c.testiosa.vastvorm_kood in (const.VASTVORM_KE, const.VASTVORM_SE, const.VASTVORM_KP, const.VASTVORM_I):
               url_h = h.url('hindamine_hindajad', toimumisaeg_id=c.toimumisaeg.id)
           elif c.testiosa.vastvorm_kood in (const.VASTVORM_SH, const.VASTVORM_SP):
               url_h = h.url('hindamine_hindajad3', toimumisaeg_id=c.toimumisaeg.id)
       elif c.user.has_permission('ekk-hindamine', const.BT_SHOW, obj=c.test):
           url_h = h.url('hindamine_arvutused', toimumisaeg_id=c.toimumisaeg.id)
       elif c.user.has_permission('vastusteanalyys', const.BT_SHOW, obj=c.test):
           url_h = h.url('hindamine_analyys_vastused', toimumisaeg_id=c.toimumisaeg.id)
      %>
      % if url_h:
      ${h.link_to(_("Hindamine"), url_h)}
      % endif
    </div>
  </div>
  <div class="form-group row mb-1">
    ${ch.flb(_("Toimumise aeg"), 'millal')}
    <div class="${ch.col2}" id="millal">
      ${c.toimumisaeg.millal}
    </div>
    <div class="col text-right brown">
    % if c.testiosa.vastvorm_kood != const.VASTVORM_KONS:
      % if not c.toimumisaeg.on_kogused:
      ${_("Kogused on arvutamata")}
      % elif not c.toimumisaeg.on_hindamisprotokollid:
      ${_("Hindamiskirjed on loomata")}
      % else:
      ${_("Hindamiskirjed on loodud")}
      % endif
    % endif
    </div>
  </div>
  <div class="form-group row mb-1">    
    ${ch.flb(_("Vastamise vorm"), 'vastvorm')}
    <div class="${ch.col2}" id="vastvorm">
      ${c.testiosa.vastvorm_nimi}
    </div>
    ${ch.flb(_("Soorituskeeled"), "langs")}
    <div class="${ch.col2}" id="langs">
      ${', '.join([model.Klrida.get_lang_nimi(lang) for lang in c.testimiskord.get_keeled()])}
    </div>
    % if c.testikoht:
    ${ch.flb(_("Soorituskoht"), 'testikoht')}
    <div class="col" id="testikoht">
      ${c.testikoht.tahised}
      ${c.testikoht.koht.nimi}
    </div>
    % endif
  </div>
</div>
