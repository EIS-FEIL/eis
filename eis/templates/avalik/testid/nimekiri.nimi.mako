<%inherit file="/common/dlgpage.mako"/>
<%include file="/common/message.mako"/>
${h.form_save(c.item.id)}
${h.hidden('op','nimi')}
${h.rqexp()}
<div class="mb-2">
  <div class="row">
    ${h.flb3(_("Nimetus"),'f_nimi', rq=True)}
    <div class="col-md-9">
      ${h.text('f_nimi', c.item.nimi, maxlength=100)}
    </div>
  </div>
  <%
    on_kutse = c.test.testiliik_kood == const.TESTILIIK_KUTSE \
        and c.test.avaldamistase == const.AVALIK_MAARATUD
    testiruum = c.item.id and c.item.testiruum1
    testiosa = c.test.get_testiosa()    
  %>
  % if on_kutse:
  <div class="row">
    ${h.flb3(_("Toimumise kuupäev"),'f_alates')}
    <div class="col-md-9 d-flex flex-wrap">
      ${h.date_field('f_alates', c.item.alates, wide=False)}
    </div>
  </div>
  % else:
  <div class="row">
    ${h.flb3(_("Alguse kuupäev"),'f_alates')}
    <div class="col-md-9 d-flex flex-wrap">
      ${h.date_field('f_alates', c.item.alates, wide=False)}
    </div>
  </div>
  % endif

  <div class="row">
    <div class="col-12">
      <div class="m-1">
        ${h.checkbox1('r_aja_jargi_alustatav', 1,
        checked=testiruum and testiruum.aja_jargi_alustatav,
        label=_("Etteantud alustamise ajavahemikul saab sooritamist alustada ilma administraatori loata"))}
      </div>
      <div class="m-1">
        ${h.checkbox1('r_algusaja_kontroll', 1, checked=testiruum and testiruum.algusaja_kontroll,
        label=_("Enne alguse kellaaega ei saa sooritamist alustada"))}
      </div>
    </div>
  </div>
  <div class="row alustamise-kell">
    ${h.flb3(_("Alguse kellaaeg"),'akell')}
    <div class="col-md-9 d-flex flex-wrap" id="akell">
      ${h.time('r_kell', testiruum and testiruum.algus or '', wide=False)}
      <span class="mx-2 alustamise-lopp">${_("kuni")}</span>
      <span class="alustamise-lopp">
        ${h.time('r_lopp', testiruum and testiruum.alustamise_lopp or '', wide=False)}
      </span>
    </div>
  </div>
  % if not on_kutse:
  <div class="row">
    ${h.flb3(_("Lõpu kuupäev"),'f_kuni')}
    <div class="col-md-9 d-flex flex-wrap">
      ${h.date_field('f_kuni', c.item.kuni, wide=False, disabled=on_kutse)}
    </div>
  </div> 
  % endif
  % if testiosa and testiosa.piiraeg:
  <div class="row">
    ${h.flb3(_("Lõpu kellaaeg"),'akell')}
    <div class="col-md-9 d-flex flex-wrap" id="akell">
      ${h.time('t_lopp', testiruum and testiruum.lopp, wide=False)}      
    </div>
  </div>
  % endif

  <div class="row">
    <div class="col-12">
    % if on_kutse:
      ${h.checkbox('r_on_arvuti_reg', 1, checked=not c.item.id or testiruum and testiruum.on_arvuti_reg, label=_("Arvutite registreerimine nõutav"))}
      <br/>
      ${h.checkbox('n_tulemus_nahtav', 1, checked=not c.item.id or c.item.tulemus_nahtav, label=_("Koondtulemus sooritajale nähtav"))}
      <br/>
      ${h.checkbox('n_alatestitulemus_nahtav', 1, checked=not c.item.id or c.item.alatestitulemus_nahtav, label=_("Alatestitulemus sooritajale nähtav"))}
      <br/>
      ${h.checkbox('n_vastus_nahtav', 1, checked=not c.item.vastus_peidus, label=_("Tehtud töö sooritajale nähtav"))}
    % else:
      ${h.checkbox('n_tulemus_nahtav', 1, checked=not c.item.id or c.item.tulemus_nahtav, label=_("Tulemus sooritajale nähtav"))}
    % endif
    </div>
  </div>
  <div class="row">
    <div class="col-12">
      ${h.checkbox('notstaatus', 1, checked=c.item.id and not c.item.staatus,
      label=_("Peida nimekiri loetelust"))}
    </div>
  </div>
</div>

<div class="text-right">
  ${h.submit_dlg()}
</div>
${h.end_form()}

<script>
  $('.alustamise-lopp').toggle($('input[name="r_aja_jargi_alustatav"]').is(':checked'));
  $('.alustamise-kell').toggle($('input[name="r_aja_jargi_alustatav"],input[name="r_algusaja_kontroll"]').filter(':checked').length>0);
  $('input[name="r_aja_jargi_alustatav"]').click(function(){
     $('.alustamise-lopp').toggle($('input[name="r_aja_jargi_alustatav"]').is(':checked'));
     $('.alustamise-kell').toggle($('input[name="r_aja_jargi_alustatav"],input[name="r_algusaja_kontroll"]').filter(':checked').length>0);
  });
  $('input[name="r_algusaja_kontroll"]').click(function(){
     $('.alustamise-kell').toggle($('input[name="r_aja_jargi_alustatav"],input[name="r_algusaja_kontroll"]').filter(':checked').length>0);
  });
</script>
