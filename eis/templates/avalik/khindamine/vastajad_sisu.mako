<%
   test = c.toimumisaeg.testimiskord.test
   c.testiosa = c.toimumisaeg.testiosa
   c.on_skannimine = c.hindamiskogum.sisestuskogum and c.hindamiskogum.sisestuskogum.on_skannimine
%>

<div class="question-status d-flex flex-wrap justify-content-between mb-2 bg-gray-50">
  <div class="item mr-5">
    ${h.flb(_("Test"),'test_nimi')}
    <div id="test_nimi">
      ${test.nimi}
    </div>
  </div>
  <% millal = c.toimumisaeg.millal %>
  % if millal:
  <div class="item mr-5">
    ${h.flb(_("Kuupäev"),'millal')}
    <div id="millal">
      ${millal}
    </div>
  </div>
  % endif
  % if c.opt_hkogumid and len(c.opt_hkogumid) > 1:
  <div class="item mr-5">
    ${h.flb(_("Hindamiskogum"),'lv_id')}
    <div>
      ${h.select('lv_id', c.hindaja.id, c.opt_hkogumid)}
      <script>
      <% data = {str(lv_id): href for lv_id, label, href in c.opt_hkogumid} %>
      var hkdata = ${str(data)};
      $('#lv_id').change(function(){
         var lv_id = $(this).val(), href = hkdata[lv_id];
         if(href) window.location.assign(href);
      });
      </script>
    </div>
  </div>
  % endif
  <div class="item mr-5">
    ${h.flb(_("Hindamise liik"),'liik_nimi')}
    <div id="liik_nimi">
      ${c.hindaja.liik_nimi}
    </div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Plaanitud hinnata"),'plaanitud')}
    <div id="plaanitud">
      % if c.hindaja.planeeritud_toode_arv is None:
      ${_("piiramata")}
      % else:
      ${c.hindaja.planeeritud_toode_arv}
      % endif
    </div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Hindamata"),'dhindamata')}
    <span class="helpable" id="hindamata"></span>
    <div id="dhindamata">
      ${c.alustamata or '0'}
    </div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Hindamisele võetud"),'toode_arv')}
    <div id="toode_arv">
      ${c.hindaja.toode_arv or 0}
    </div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Hindamiskeel"),'hlang')}
    <div id="hlang">
      ${model.Klrida.get_lang_nimi(c.hindaja.lang)}
    </div>
  </div>
  <%
    on_algus = c.toimumisaeg.hindamise_algus and c.toimumisaeg.hindamise_algus > model.datetime.now()
    on_lopp = c.toimumisaeg.hindamise_tahtaeg
  %>
  % if on_algus or on_lopp or not c.toimumisaeg.hindamise_luba:
  <div class="item mr-5">
    ${h.flb(_("Hindamise ajavahemik"))}
    <div id="haeg">
      % if on_algus and on_lopp:
      ${h.str_from_datetime(c.toimumisaeg.hindamise_algus, hour0=False)}
      -
      ${h.str_from_date(c.toimumisaeg.hindamise_tahtaeg)}
      % elif on_algus:
      ${_("alates")} ${h.str_from_datetime(c.toimumisaeg.hindamise_algus, hour0=False)}
      % elif on_lopp:
      ${_("kuni")} ${h.str_from_date(c.toimumisaeg.hindamise_tahtaeg)}      
      % endif
      % if not c.toimumisaeg.hindamise_luba:
      <div>
        ${_("Praegu ei saa hinnata")}
      </div>
      % endif
    </div>
  </div>
  % endif
  
</div>

<div class="d-flex flex-wrap align-items-end mb-2">
  <div class="mr-3 mb-1">
    <%include file="hindamiskogum.ylesanded.mako"/>
  </div>
  <div class="mb-1 flex-grow-1">
    % if c.toimumisaeg.on_hindamise_luba:
    ${self.start_form()}
    % else:
    <%
      if c.toimumisaeg.hindamise_algus and c.toimumisaeg.hindamise_algus > model.datetime.now():
         msg = _("Praegu ei saa hinnata. Hindamise algusaeg on {d}").format(d=h.str_from_datetime(c.toimumisaeg.hindamise_algus, hour0=False))
      else:
         msg = _("Praegu ei saa hinnata.")
    %>
    <div>${h.alert_notice(msg, False)}</div>
    % endif
  </div>
</div>

% if c.cnt_hindamata or c.cnt_pooleli or c.cnt_valmis or c.cnt_hinnatud:
<h2>${_("Hinnatavad tööd")}</h2>
${self.search_form()}
${self.list_form()}
% endif

<%def name="start_form()">
${h.form(h.url_current('create'), method='post', preventsubmit=True, id="form_alusta")}      
${h.hidden('sub', 'hinda')}
% if c.testiosa.vastvorm_kood == const.VASTVORM_KP and not c.on_skannimine:
% if c.alustamata or c.cnt_hindamata or c.cnt_pooleli or c.cnt_valmis:
<div class="form-wrapper p-3 d-flex flex-wrap">
  <div class="item mr-5 text-nowrap">
    ${h.flb(_("Paberil testitöö tähis"), 'tahised')}
    ${h.text('tahised', c.tahised, maxlength=7, pattern='\d+-\d+')}
  </div>
  % if c.sisestus_isikukoodiga:
  <div class="item mr-5 text-nowrap">
    ${h.flb(_("Isikukood"),'isikukood')}
    ${h.text('isikukood', c.isikukood)}
  </div>
  % endif
  <div class="item mr-5 d-flex align-items-end">
   ${h.submit(_("Alusta hindamist"), id='p_alusta')}
  </div>
</div>
% endif
% endif

% if not (c.testiosa.vastvorm_kood == const.VASTVORM_KP and not c.on_skannimine):
% if c.alustamata:
<div class="mb-2 mr-2">
  ${h.button(_("Alusta hindamist"), id='e_alusta')}
  <script>
    $('#e_alusta').click(function(){
    $('form#form_alusta').submit();
    });
  </script>
</div>
% endif
% endif

${h.end_form()}
</%def>

<%def name="search_form()">
${h.form_search()}
<div class="gray-legend p-3">
  <div class="d-flex flex-wrap justify-content-between align-items-end">
    <div>
      <% H_STAATUS_POOLELI_VALMIS = 3 %>
      ${h.radio('staatus', const.H_STAATUS_HINDAMATA, checkedif=c.staatus,
      label=_("Mulle hindamiseks suunatud ({n})").format(n=c.cnt_hindamata))}
      ${h.radio('staatus', const.H_STAATUS_POOLELI, checkedif=c.staatus,
      label=_("Pooleli ({n})").format(n=c.cnt_pooleli))}
      ${h.radio('staatus', H_STAATUS_POOLELI_VALMIS, checkedif=c.staatus,
      label=_("Kinnitamiseks valmis ({n})").format(n=c.cnt_valmis))}
      ${h.radio('staatus', const.H_STAATUS_HINNATUD, checkedif=c.staatus,      
      label=_("Kinnitatud ({n})").format(n=c.cnt_hinnatud))}
    </div>
  </div>
</div>
<script>
  $('input[name="staatus"]').click(function(){  $('#form_search').submit(); });
</script>
${h.end_form()}
</%def>

<%def name="list_form()">
${h.form_save(None)}
<div class="listdiv mb-2">
<%include file="vastajad_list.mako"/>
</div>

<span id="add" class="d-none">
${h.submit(_("Kinnita hindamised"))}
</span>
${h.end_form()}
</%def>
