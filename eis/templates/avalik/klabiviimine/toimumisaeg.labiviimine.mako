<%inherit file="/common/page.mako"/>
## Testimiskorraga testi läbiviimise administraatori kuva
## Olemas on c.toimumisaeg ja c.test ja c.user.koht
<%def name="page_title()">
${_("E-testi läbiviimine")} | ${c.test.nimi} 
${c.toimumisaeg.millal}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("E-testi läbiviimine"), h.url('klabiviimine_toimumisajad'))} 
${h.crumb(c.test.nimi + ' ' + h.str_from_date(c.toimumisaeg.alates))}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

## formpage-body piirab nuppe, mis ei käivita being_clicked_args
<div class="formpage-body">
<%
  c.can_update = c.user.has_permission('testiadmin', const.BT_UPDATE, c.testiruum)
%>
<div class="question-status d-flex mb-3">
  <div class="item mr-5">
    ${h.flb(_("Test"), 'test_nimi')}
    <div id="test_nimi">
      ${c.test.nimi} ${c.testiosa.nimi}
      (${h.fstr(c.testiosa.max_pallid)} p)
      % if c.toimumisaeg.eelvaade_admin and not c.veel_ei_toimu:
      <%
        eelvaade_staatused = (const.S_STAATUS_POOLELI, const.S_STAATUS_KATKESTATUD, const.S_STAATUS_TEHTUD)
        on_alustatud = (model.SessionR.query(model.sa.func.count(model.Sooritus.id))
           .filter_by(testiruum_id=c.testiruum.id)
           .filter(model.Sooritus.staatus.in_(eelvaade_staatused))
           .scalar()) > 0
      %>
      <span class="b_eelvaade" style="display:${on_alustatud and 'block' or 'none'}">
      ${h.btn_to(_("Eelvaade"), h.url('klabiviimine_new_eelvaade', test_id=c.test.id, testiruum_id=c.testiruum.id, alatest_id=''))}
      </span>
      % endif
    </div>
  </div>
  % if c.testiosa.piiraeg:
  <div class="item mr-5">
    ${h.flb(_("Piiraeg"),'piiraeg')}
    <div id="piiraeg">
      ${h.str_from_time(c.testiosa.piiraeg)}
    </div>
  </div>
  % endif

  <div class="item mr-5">
    ${h.flb(_("Toimumise aeg"), 'ruum_algus')}
    <div id="ruum_algus">
      ${h.str_from_datetime(c.testiruum.algus, hour0=False)}
      % if c.testiruum.algus and c.testiruum.lopp and c.testiruum.lopp.date() != c.testiruum.algus.date():
      - ${h.str_from_datetime(c.testiruum.lopp, hour23=False)}
      % endif
    </div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Toimumisaja tähis"), 'ta_tahised')}
    <div id="ta_tahised">
      ${c.toimumisaeg.tahised}
    </div>
  </div>

  <div class="item mr-5">
    ${h.flb(_("Koht ja ruum"), 'koht_nimi')}
    <div id="koht_nimi">
      ${c.testikoht.koht.nimi}
      % if c.testiruum.ruum:
      ${c.testiruum.ruum.tahis}
      % endif
      (${c.testikoht.tahis}-${c.testiruum.tahis})
    </div>
  </div>
  <%
     opt_arvuti_reg = [(const.ARVUTI_REG_POLE, _("Pole alanud")),
                       (const.ARVUTI_REG_ON, _("On käimas")),
                       (const.ARVUTI_REG_LUKUS, _("On lõppenud")),
                      ]
     if c.testiruum.arvuti_reg != const.ARVUTI_REG_POLE:
        opt_arvuti_reg = opt_arvuti_reg[1:]
  %>
  % if c.toimumisaeg and c.toimumisaeg.on_arvuti_reg:
  <div class="item mr-5">
    ${h.flb(_("Arvutite registreerimine"), 'arvuti_reg')}
    <div>
      ${h.form_save(c.testiruum.id)}
      ${h.hidden('sub', 'reg')}
      ${h.select('arvuti_reg', c.testiruum.arvuti_reg, opt_arvuti_reg, class_='nosave', 
      wide=False, ronly=c.veel_ei_toimu or not c.can_update)}
      <script>
        $('#arvuti_reg').change(function(){
          this.form.submit();
        });
      </script>
      % if c.testiruum.arvuti_reg == const.ARVUTI_REG_ON:
      <div>
      ${_("Parool")}:
      ${c.testiruum.parool}
      </div>
      % endif
      ${h.end_form()}
    </div>
  </div>
  % endif
</div>

% if c.info_msg:
${h.alert_notice(c.info_msg, False)}
% endif

<div class="listdiv">
% if c.testiruum and c.toimumisaeg and c.toimumisaeg.on_arvuti_reg:
<%include file="arvutid_list.mako"/>
% endif
  <%include file="sooritajad.mako"/>
</div>

% if c.dialog_markus:
<div id="div_dialog_markus">
  <%include file="markus.mako"/>
</div>
<script>
  $(function(){
    open_dialog({'contents_elem': $('#div_dialog_markus'), 'title': '${_("Märkus")}'});
  });
</script>
% endif

% if c.dialog_lisaaeg:
<div id="div_dialog_lisaaeg">
  <%include file="lisaaeg.mako"/>
</div>
<script>
  $(function(){
    open_dialog({'contents_elem': $('#div_dialog_lisaaeg'), 'title':'${_("Lisaaeg")}'});
  });
</script>
% endif

<%
  prot_url = None
  if c.toimumisaeg and c.toimumisaeg.prot_admin and not c.veel_ei_toimu:

        protokollid = c.toimumisaeg.on_ruumiprotokoll and c.testiruum.toimumisprotokollid or c.testikoht.toimumisprotokollid     
        if len(protokollid) > 1:
           sessioon_id = c.toimumisaeg.testimiskord.testsessioon_id
           prot_url = h.url('protokollid', testsessioon_id=sessioon_id)
        elif len(protokollid) == 1:
           tprot = protokollid[0]
           prot_url = h.url('protokoll_osalejad', toimumisprotokoll_id=tprot.id, testiruum_id=c.testiruum_id)
%>
% if prot_url:
<script>
  being_clicked_args = {check_url: "${h.url_current('show', sub='checkprot')}",
                        message: "${_('Testi toimumise protokoll on veel täitmata!')}",
                        next_text: "${_("Ava protokoll")}",
                        next_url: "${prot_url}",
                        cancel_text: "${_("Hiljem")}",
  };
</script>
% endif               

## end formpage-body
</div>
