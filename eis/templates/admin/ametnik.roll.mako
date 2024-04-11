${h.not_top()}
<%include file="/common/message.mako"/>
${h.form_save(c.item.id)}
${h.rqexp()}
<div class="tbl-roll form-wrapper-lineborder">
  <div class="form-group row">
    ${h.flb3(_("Kasutajagrupp"), rq=True)}
    <div class="col">
    <%
      opt_rollid = c.opt.ametnikgrupp
      if not c.user.on_admin:
         opt_rollid = [r for r in opt_rollid if r[0] not in (const.GRUPP_ADMIN, const.GRUPP_SYSADMIN)]
    %>
    % if c.item.kasutajagrupp_id and (c.allg or not c.item.kasutajagrupp_id in [r[0] for r in opt_rollid]):
        <% grupp = model.Kasutajagrupp.get(c.item.kasutajagrupp_id) %>
        ${h.roxt(grupp.nimi)}
        ${h.hidden('r_kasutajagrupp_id', grupp.id)}
      % else:
        ${h.select('r_kasutajagrupp_id', c.item.kasutajagrupp_id, opt_rollid,
        names=True, rows=10, onchange='grupp_changed()')}
      % endif
    </div>
  </div>

  <div class="form-group row d-none r_aine">
    ${h.flb3(_("Õppeaine"), rq=True)}
    <div class="col">
      ${h.select('r_aine_kood', c.item.aine_kood, 
      c.opt.klread_kood('AINE', vaikimisi=c.item.aine_kood),
      onchange='aine_changed()')}
    </div>
  </div>
  <div class="form-group row d-none r_ained">
    ${h.flb3(_("Õppeaine"), rq=True)}
    <div class="col">
      ${h.select2('r_ained', c.ained, 
      c.opt.klread_kood('AINE'), multiple=True)}
    </div>
  </div>
  <div class="form-group row d-none r_oskus">
    ${h.flb3(_("Oskus"), rq=True)}
    <div class="col">
      ${h.select('r_oskus_kood', c.item.oskus_kood,
      c.opt.klread_kood('OSKUS',ylem_kood=c.item.aine_kood, ylem_required=True, vaikimisi=c.item.oskus_kood))}
    </div>
  </div>
  <div class="form-group row d-none r_testiliik">
    ${h.flb3(_("Testiliik"), rq=True)}
    <div class="col">
      ${h.select('r_testiliik_kood', c.item.testiliik_kood, c.opt.testiliik, empty=True)}
    </div>
  </div>
  <div class="form-group row d-none r_lang">
    ${h.flb3(_("Keel"))}
    <div class="col">
      ${h.select('r_lang', c.item.lang, c.opt.klread_kood('SOORKEEL', vaikimisi=c.item.lang), empty=True)}
    </div>
  </div>
  
  <div class="form-group row d-none r_piirkond">
    ${h.flb3(_("Piirkond"))}
    <div class="col">
      <%
         c.piirkond_id = c.item.piirkond_id
         c.piirkond_field = 'r_piirkond_id'
      %>
      <%include file="/admin/piirkonnavalik.mako"/>
    </div>
  </div>
  <div class="form-group row d-none r_allkiri">
    ${h.flb3(_("Otsusele allakirjutamise järjekord"))}
    <div class="col">
      <% opt_jrk = [('', _("Ei allkirjasta")), ('1','1.'),('2','2.'),('3','3.')] %>
      ${h.select('r_allkiri_jrk', c.item.allkiri_jrk, opt_jrk)}
    </div>
  </div>
  <div class="form-group row d-none r_allkiri">
    ${h.flb3(_("Allkirjastaja ametinimetus"), rq=True)}
    <div class="col">
      ${h.text('r_allkiri_tiitel1', c.item.allkiri_tiitel1)}
    </div>
  </div>
  <div class="form-group row d-none r_allkiri">
    ${h.flb3(_("Allkirjastaja roll komisjonis"))}
    <div class="col">
      ${h.text('r_allkiri_tiitel2', c.item.allkiri_tiitel2)}
    </div>
  </div>

  <div class="form-group row mb-3">
    ${h.flb3(_("Kehtib kuni"))}
    <div class="col">
      ${h.date_field('r_kehtib_kuni', c.item.kehtib_kuni_ui, wide=False)}
    </div>
  </div>
</div>

${h.rqexp(None, _("Kohustuslik on sisestada kas JIRA pileti nr või selgitus"))}
<div class="tbl-roll form-wrapper-lineborder mb-2">
  <div class="form-group row">
    ${h.flb3(_("JIRA pilet"))}
    <div class="col d-flex">
      <span>EJ-</span>
      ${h.posint5('jira_nr', '')}
    </div>
  </div>
  <div class="form-group">
    <b>${_("Selgitus")}</b>
    ${h.textarea('selgitus', '', rows=5)}
  </div>
</div>

<script>
  $(function(){
    grupp_changed();
    $('input#r_kehtib_kuni').datepicker();
    hold_dlg_height(null, true, $('.tbl-roll'));    
  });
  function aine_changed()
  {
       var target = $('select#r_oskus_kood');
       update_options($('select#r_aine_kood'), 
                      "${h.url('pub_formatted_valikud', kood='OSKUS', format='json')}", 
                      'ylem_kood', 
                      target);
  }
  function grupp_changed()
  {
     var grupp_id = $('#r_kasutajagrupp_id').val();
     var b = (grupp_id == '${const.GRUPP_AINESPETS}' ||
          grupp_id == '${const.GRUPP_E_KORRALDUS}' ||
          grupp_id == '${const.GRUPP_AINETOORYHM}' ||
          grupp_id == '${const.GRUPP_HINDAMISJUHT}' ||
          grupp_id == '${const.GRUPP_HINDAMISEKSPERT}'); 
     $('.r_ained').toggleClass('d-none', !b);

     b = (grupp_id == '${const.GRUPP_OSASPETS}');
     $('.r_aine').toggleClass('d-none', !b);

     b = (grupp_id == '${const.GRUPP_OSASPETS}');
     $('.r_oskus').toggleClass('d-none', !b);

     b = (grupp_id == '${const.GRUPP_UI_TOLKIJA}');
     $('.r_lang').toggleClass('d-none', !b);  

     b = (grupp_id == '${const.GRUPP_VAIDEKOM}' ||
          grupp_id == '${const.GRUPP_VAIDEKOM_ESIMEES}' ||
          grupp_id == '${const.GRUPP_VAIDEKOM_SEKRETAR}');
     $('.r_allkiri').toggleClass('d-none', !b);  
     $('.r_testiliik .rqhint').toggleClass('d-none', !b);
  
     b = (grupp_id == '${const.GRUPP_AINESPETS}' ||
          grupp_id == '${const.GRUPP_INFOSPETS}' ||
          grupp_id == '${const.GRUPP_SISESTAJA}' ||
          grupp_id == '${const.GRUPP_REGAJA}' ||
          grupp_id == '${const.GRUPP_ERIVAJADUS}' ||
          grupp_id == '${const.GRUPP_KORRALDUS}' ||
          grupp_id == '${const.GRUPP_P_KORRALDUS}' ||
          grupp_id == '${const.GRUPP_VAIDEKOM_ESIMEES}' ||
          grupp_id == '${const.GRUPP_VAIDEKOM_SEKRETAR}' ||
          grupp_id == '${const.GRUPP_VAIDEKOM}'); 
     $('.r_testiliik').toggleClass('d-none', !b);

     b = (grupp_id == '${const.GRUPP_P_KORRALDUS}');
     $('.r_piirkond').toggleClass('d-none', !b);
  }
</script>

<div class="d-flex">
  <div class="flex-grow-1">
    % if c.item.id:
    ${h.submit_dlg(value=_("Kustuta"), op='delete',
    confirm=_("Kas oled kindel, et soovid kustutada?"), level=2)}    
    % endif
  </div>
  <div>
    ${h.submit_dlg()}
  </div>
</div>
${h.end_form()}
