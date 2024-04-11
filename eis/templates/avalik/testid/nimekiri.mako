## Valitud nimekirja andmed
<% 
  c.can_add = c.user.has_permission('omanimekirjad', const.BT_UPDATE, test_id=c.test.id)
  if c.item.id:
     c.can_update = c.user.has_permission('nimekirjad', const.BT_UPDATE, c.item)
  
  else:
     c.can_update = c.can_add
  c.can_delete = c.user.has_permission('avtugi', const.BT_DELETE)
  is_test_valid = c.test.staatus == const.T_STAATUS_KINNITATUD
  on_pedagoog = c.user.koht_id and c.user.has_permission('klass', const.BT_UPDATE, obj=c.user.koht)
  nimekiri_id = c.item.id or 0
  on_regatud = False
  on_kutse = c.test.testiliik_kood == const.TESTILIIK_KUTSE \
             and c.test.avaldamistase == const.AVALIK_MAARATUD
  on_litsents = c.test.avaldamistase == const.AVALIK_LITSENTS
  # urli ei saa h.url_current kaudu teha, sest seda vormi kasuta ka sooritajad.py kontroller
  if c.item.id:
     url = h.url('test_update_nimekiri', id=c.item.id, test_id=c.test.id, testiruum_id=c.testiruum_id)
  else:
     url = h.url('test_nimekirjad', test_id=c.test.id, testiruum_id=0)
%>
${h.form_save(c.item.id, url)}
% if c.item.id or c.can_add:
<div class="d-flex justify-content-between align-items-md-center flex-column flex-md-row">
  <h3>${c.item.nimi or _("Nimekiri")}</h3>
  <div class="d-flex justify-content-end align-items-center mb-2">
  % if c.can_update and c.item.id:
    % if c.item.id and c.item.staatus == const.B_STAATUS_KEHTETU:
    <button type="button" class="btn btn-light btn-tag mr-2">
      <i class="mdi mdi-file-hidden mr-2" aria-hidden="true"></i> ${_("Peidetud nimekiri")}
    </button>
    % endif

    ${h.btn_to_dlg(_('Muuda'),      
      h.url_current('edit', id=nimekiri_id, sub='nimi', partial=True),
      dlgtitle=_('Nimekiri'), width=700, level=2, mdicls='mdi-file-edit')}
  % endif
  % if c.can_add:
    ${h.btn_to_dlg(_('Lisa uus nimekiri'), h.url_current('new'),
    dlgtitle=_('Uus nimekiri'), width=500, level=2)}
  % endif
  </div>
</div>
% endif
% if c.item.id:
${self.nimekiri_data(on_kutse, on_litsents)}
% endif


<div class="listdiv" width="100%">
  % if c.item.id:
  <%include file="sooritajad_list.mako"/>
  % endif
</div>

% if c.test.staatus == const.T_STAATUS_ARHIIV:
${h.alert_notice(_("Testi ei saa sooritajatele suunata, sest see test on arhiveeritud"), False)}
% elif not is_test_valid:
${h.alert_notice(_("Testi ei saa sooritajatele suunata, sest see pole valmis"), False)}
% elif not c.can_add and not c.can_update and c.test.avalik_kuni and c.test.avalik_kuni < model.date.today():
${h.alert_notice(_("Testi ei saa sooritajatele suunata, sest see pole enam avalik"), False)}
% elif not c.can_add and not c.can_update:
${h.alert_notice(_("Testi ei saa sooritajatele suunata"), False)}
% endif

<div class="d-flex flex-wrap justify-content-between">
  % if c.can_update and is_test_valid:
  <div>
    ${_("Lisa sooritajad:")}
    % if on_pedagoog and not on_kutse:
    ${h.btn_to_dlg(_('Õpilaste rühmast'), h.url('test_nimekiri_otsisooritajad', test_id=c.test.id, nimekiri_id=nimekiri_id, sub='ryhm'), title=_('Sooritajate lisamine'),
    width=700)}
    % endif
    ${h.btn_to_dlg(_('Isikukoodiga'),
    h.url('test_nimekiri_otsisooritajad', test_id=c.test.id, nimekiri_id=nimekiri_id, sub='ik'), title=_('Sooritaja lisamine'), width=700)}
    % if on_pedagoog:
    ${h.btn_to_dlg(_('EHISest'), h.url('test_nimekiri_otsisooritajad', test_id=c.test.id,
    nimekiri_id=nimekiri_id, sub='ehis'), title=_('Sooritajate lisamine'),
    width=700)}
    % endif
    ${h.btn_to_dlg(_('Failist'), h.url('test_nimekiri_otsisooritajad', test_id=c.test.id,
    nimekiri_id=nimekiri_id, sub='fail'), title=_('Sooritajate lisamine'), width=700)}
  </div>
  % endif

  <div>
    % if c.can_update and c.item.id and c.on_regatud:
    ${h.btn_to(_('Luba kohe alustada'), h.url_current('update', id=c.item.id, staatus=const.S_STAATUS_ALUSTAMATA), method='post', level=2)}
    % endif
    % if c.item.id and (c.can_update or c.can_delete):
    <%
        q = (model.Sooritaja.query
             .filter_by(nimekiri_id=c.item.id)
             .filter(model.Sooritaja.staatus.in_((const.S_STAATUS_POOLELI,
                                                  const.S_STAATUS_KATKESTATUD,
                                                  const.S_STAATUS_KATKESPROT,
                                                  const.S_STAATUS_TEHTUD)))
             )
        if q.count() == 0:
           msg = _("Kas oled kindel, et soovid nimekirja kustutada?")
        elif c.can_delete:
           msg = _("Kas oled kindel, et soovid nimekirja ja antud vastused kustutada?")
        else:
           # ei või kustutada
           msg = None
    %>
    % if msg:
    ${h.btn_remove(value=_('Kustuta nimekiri'), confirm=msg)}
    % endif
    % endif
    
  </div>
</div>
${h.end_form()}
  
% if c.testiruum and on_kutse:
<%include file="nimekiri.testiadminid.mako"/>
% endif
% if c.testiruum:
<%include file="nimekiri.hindajad.mako"/>
% endif

<div class="savetarget"></div>

% if c.can_update:
<script>
$(function(){
$('form .autosv').change(function(){
  submit_dlg(this, $('.savetarget'), null, null, null, null, null, true);
});
});
</script>
% endif

<%def name="nimekiri_data(on_kutse, on_litsents)">
<% testiruum = c.item.id and c.item.testiruum1 %>
<div class="data-box mb-5">
  <div class="row">
    <div class="column col-lg-3">
      ${h.flb(_("Lahendamise ajavahemik"), 'dalates')}
    </div>
    <div class="column col-lg-9" id="dalates">
      <%
        algus = testiruum and testiruum.algus
        lopp = testiruum and testiruum.lopp
        algus_k = c.item.alates
        lopp_k = c.item.kuni
      %>
      ${h.str_from_datetime(algus or algus_k, hour0=False)}
      -
      % if algus_k == lopp_k and lopp:
      ${h.str_time_from_datetime(lopp)}
      % else:
      ${h.str_from_datetime(lopp or lopp_k, hour0=False)}
      % endif
    </div>
  </div>

  % if testiruum and testiruum.aja_jargi_alustatav:
  <div class="row">
    <div class="column col-12">
      <%
        td = '%s - %s' % (h.str_time_from_datetime(testiruum.algus),
                          h.str_time_from_datetime(testiruum.alustamise_lopp))
      %>
      ${_("Etteantud alustamise ajavahemikul {s} saab sooritamist alustada ilma administraatori loata").format(s=td)}
    </div>
  </div>
  % endif
  % if testiruum and testiruum.algusaja_kontroll:
  <div class="row">
    <div class="column col-12">
      <%
        td = h.str_time_from_datetime(testiruum.algus)
      %>
      ${_("Enne alguse kellaaega ei saa sooritamist alustada")}
    </div>
  </div>
  % endif

  % if on_kutse and testiruum:
  <div class="row">
    <div class="column col-lg-3">
      ${h.flb(_("Arvutite registreerimine"),'darvutireg')}
    </div>
    <div class="column col-lg-12" id="darvutireg">
      % if testiruum.on_arvuti_reg:
      ${_("Jah")}
      % else:
      ${_("Arvuteid ei registreerita - testi läbiviimisel ei ole rakendatud maksimaalseid turvalisuse funktsioone")}
      ##${h.alert_error(_("Arvuteid ei registreerita, testi läbiviimine pole turvaline"))}
      % endif
    </div>
  </div>
  % elif not on_kutse:
  % if not c.item.tulemus_nahtav:
  <div class="row">
    <div class="column col-lg-6">
      ${_("Tulemus pole sooritajale nähtav")}
    </div>
  </div>
  % endif
  % endif

  % if c.item.esitaja_kasutaja_id:
  <div class="row">
    <div class="column col-lg-3">
      ${h.flb(_("Nimekirja looja"), 'esitaja_kasutaja')}
    </div>
    <div class="column col-lg-6" id="esitaja_kasutaja">
      ${c.item.esitaja_kasutaja.nimi}
    </div>
    % if c.test.testiliik_kood == const.TESTILIIK_TKY:
    <div class="column col-lg-3">
      <%
        tky = c.test.opilase_taustakysitlus
        if tky:
           opj = model.Sooritaja.get_tky_opetaja(c.item.id)
           if not opj and c.item.esitaja_kasutaja_id == c.user.id:
              opj = model.Sooritaja.reg_tky_opetaja(c.user.get_kasutaja(), c.test, c.item)
              model.Session.commit()
        else:
           opj = None
      %>
      % if opj:
      ${h.link_to(_("Õpetaja test"), h.url('sooritamine_alustamine', test_id=opj.test_id, sooritaja_id=opj.id))} ${opj.staatus_nimi}
      % endif
    </div>
    % endif
  </div>
  % endif

  % if not on_kutse and not on_litsents:
  % if c.can_update and c.user.on_pedagoog and c.item.esitaja_kasutaja_id==c.user.id:
  <div class="row">
    <div class="column col-lg-12">
      ${h.checkbox('f_pedag_nahtav', 1, checked=c.item.pedag_nahtav,
      label=_('Luban oma kooli pedagoogidel näha nimekirja ja tulemusi'),
      ronly=False, class_="autosv")}
    </div>
  </div>
  % elif c.item.pedag_nahtav:  
  <div class="row">
    <div class="column col-lg-12">
      ${_("Oma kooli pedagoogidel lubatud näha nimekirja ja tulemusi")}
    </div>
  </div>
  % endif
  % endif
</div>

</%def>
