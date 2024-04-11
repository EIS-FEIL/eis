<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['subtabs'] = True %>
</%def>
<%def name="page_title()">
${_("Testi korraldamine")} | ${c.test.nimi} ${h.str_from_date(c.toimumisaeg.alates)}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Korraldamine"), h.url('korraldamised'))} 
${h.crumb('%s %s' % (c.test.nimi, h.str_from_date(c.toimumisaeg.alates)))} 
${h.crumb(_("Soorituskohtade planeerimine"), h.url('korraldamine_soorituskohad', toimumisaeg_id=c.toimumisaeg.id))}
% if c.testikoht:
${h.crumb(c.testikoht.koht.nimi)}
% else:
${h.crumb(_("Soorituskohata sooritajad"))}
% endif
</%def>
<%def name="active_menu()">
<% c.menu1 = 'korraldamised' %>
</%def>

<%def name="page_headers()">
<style>
  .ttabel .draggable {
    border: 1px #B22F16 dashed;
    float: left;
    clear: both;
    padding: 5px;
  }
</style>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'soorituskohad' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<%include file="koht.tabs.mako"/>
</%def>

${h.form_search(url=h.url('korraldamine_koht_sooritajad',
toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht_id))}

${self.pakettideinfo()}

% if c.items or c.is_filter:
${self.otsingufilter()}
% endif
${h.end_form()}

${h.form_save(None, h.url('korraldamine_koht_sooritajad',
toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht_id))}
<div class="listdiv">
% if c.ttabel:
<%include file="koht.sooritajad_ttabel.mako"/>
% else:
<%include file="koht.sooritajad_list.mako"/>
% endif
</div>

<script>
  function toggle_all_s(fld)
  {
     $('input[name="sooritus_id"]').prop('checked', fld.checked);
     toggle_sooritus();
  }
  function toggle_sooritus()
  {
     var visible = ($('input:checked[name="sooritus_id"]').length > 0);
     $('span.sooritus').toggleClass('d-none', !visible);
  }
  function gen_pwd()
  {
     var data = 'sub=parool';
     $.each($('input[name="sooritus_id"]:checked'), function(n, elem){
         data += '&sooritus_id=' + elem.value;
     });
     var title = "${_("Testiparoolid")}";
     open_dialog({'title': title, 'url': "${h.url_current('new')}", params: data});
  }      
  function set_klass()
  {
     var data = 'sub=klass';
     $.each($('input[name="sooritus_id"]:checked'), function(n, elem){
         data += '&sooritus_id=' + elem.value;
     });
     var title = "${_("Sooritaja õppimiskoha andmete muutmine")}";
     open_dialog({'title': title, 'url': "${h.url_current('new')}", params: data});
  }      
  $(function(){
     toggle_sooritus();
  });
</script>

<div class="d-flex flex-wrap">
<div class="flex-grow-1">
<% c.can_update = c.user.has_permission('korraldamine', const.BT_UPDATE, obj=c.testikoht or c.test) %>
% if c.testikoht and c.can_update:
<%
  on_koode = (model.SessionR.query(model.sa.func.count(model.Sooritus.id))
              .filter(model.Sooritus.tahis!=None)
              .filter(model.Sooritus.testikoht_id==c.testikoht.id)
              .scalar())
  msg = on_koode and _("Protokollirühmadesse jagamisel määratakse sooritajatele uued töökoodid. Kas oled kindel, et soovid jätkata?") or None
%>
${h.button(_("Jaga uuesti protokollirühmadesse"), id='proto', confirm=msg, level=2)}
<script>
$(function(){
  $('#proto').click(function(){
     var msg = $(this).attr('confirm');
% if on_koode:     
     var data = function(){
       return {'proto':1, 'list_sort': $('form#form_save input[name="list_sort"]').val()};
     }
% else:
     var data = {'proto': 1};
% endif
     post_confirm($(this), msg, data);
     return false;
  });
});
</script>

${h.btn_to_dlg(_("Lisa sooritajad"), h.url('korraldamine_koht_otsisooritajad',
toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht_id),
title=_("Sooritajate lisamine"),width=800, level=2, size='lg')}

% endif

% if c.items and c.can_update:
% if not c.testikoht:
${h.submit(_("Genereeri õppurite soorituskohad"), id='genereeri', level=2)}
% if not c.on_piirkondlik and c.test.testiliik_kood != const.TESTILIIK_RIIGIEKSAM:
${h.button(_("Jaota sooritajad soorituskohtadesse"),
onclick="dialog_el($('div#jaotamine'), '%s', 600);" % _("Testikohata sooritajate jagamine soovitud piirkonna järgi"), level=2)}
% endif
% elif len(c.testikoht.testiruumid) > 1:

${h.btn_to_dlg(_("Jaota ruumidesse"), 
h.url_current('new', sub='jaotaruumi'),
title=_("Juhuslik sooritajate ruumidesse jaotamine"), width=800, level=2)}

% endif

${h.btn_to_dlg(_("Jaota teisele testimiskorrale"), 
h.url_current('new', sub='teinekord'),
title=_("Sooritajate viimine teisele testimiskorrale"), level=2,
params="'default=True&'+$(this.form).find('input.sooritus_id').serialize()")}
</div>

<span class="sooritus d-none">
% if c.testikoht:
% if c.testikoht and not c.testikoht.koht.kool_id:
${h.button(_("Muuda õppimisandmed"), onclick="set_klass()", level=2)}
% endif
${h.button(_("Testiparoolid"), onclick="gen_pwd()", level=2)}
${h.btn_to_dlg(_("Suuna ümber"), 
h.url('korraldamine_koht_otsikohad', toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht_id),
method='post',
title=_("Sooritajate suunamine"),width=1000,size='lg',
params="'tkoht_id=%s&default=True&'+$(this.form).find('input.sooritus_id').serialize()" % (c.testikoht_id))}

% else:
${h.btn_to_dlg(_("Suuna soorituskohta"), 
h.url('korraldamine_koht_otsikohad', toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht_id),
method='post',
title=_("Sooritajate suunamine"),width=800, params="$(this.form).find('input.sooritus_id').serialize()")}
% endif
</span>
% endif

% if c.testiosa.oma_kavaaeg:
## suulise testi korral saab salvestada kellaajad
${h.submit(_("Salvesta kellaajad"), id='kell')}
% endif
</div>
${h.end_form()}

<div id="jaotamine" class="d-none">
<%include file="jaotusvalik.mako"/>
</div>

<%def name="pakettideinfo()">
<%
   if c.testikoht:
      sooritajatearvud = c.testikoht.get_sooritajatearvud()
   else:
      sooritajatearvud = c.toimumisaeg.get_sooritajatearvud(testikoht_id=0)
%>
<table width="100%"  class="table p-2 mb-1 table-align-top">
  <tr>
    <td class="frh">${_("Testisooritajate arv kokku")}</td>
    <td>
      <span class="brown">
        ${sooritajatearvud['total']}
      </span>
    </td>
% if c.testikoht:
    <td colspan="2">${_("Ruumid")}</td>
    <td>${_("Protokollirühmad")}</td>
    <td>${_("Algus")}</td>
% endif
  </tr>
% if c.testikoht:
  % for pakett in c.testikoht.testipaketid_sorted:
  ${self.tr_pakett(pakett, sooritajatearvud)}
  % endfor
  <tr>
    <td class="frh">${_("Märkused")}
      % if c.can_update:
      ${h.btn_to_dlg(_("Muuda..."), h.url('korraldamine_koht_sooritajad',
      toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht_id, sub='markus'),
      title=_("Märkus"),width=500, level=2)}
      % endif
    </td>
    <td colspan=5>
      ${c.testikoht.markus}
    </td>
  </tr>
% endif
</table>
</%def>

<%def name="tr_pakett(pakett, sooritajatearvud)">
<%
       # leiame sellele keelele vastavad ruumid
       paketiruumid = []
       for truum in c.testikoht.testiruumid:
          protokollid = []
          for tpr in truum.testiprotokollid:
             if tpr.testipakett_id == pakett.id:
                 protokollid.append(tpr)
          if len(protokollid):
             paketiruumid.append((truum, protokollid))
       pakett_row_cnt = len(paketiruumid) or 1
       on_sisse = c.test.testiliik_kood == const.TESTILIIK_SISSE
       oma_kavaaeg = c.testiosa.oma_kavaaeg
%>
% for n, (truum, protokollid) in enumerate(paketiruumid):
    <tr>
      % if n == 0:
      <td class="frh" rowspan="${pakett_row_cnt}">${pakett.lang_nimi}</td>
      <td rowspan="${pakett_row_cnt}">
        <span class="brown">${sooritajatearvud.get(pakett.lang) or 0}</span>
        (${_("väljastatavate tühjade testitööde arv")} 
        <span class="brown">${pakett.toodearv}</span>)
      </td>
      % endif

      <td>${truum.tahis}</td>
      <td>${truum.ruum and truum.ruum.tahis}</td>
      <td>
        % if on_sisse or oma_kavaaeg:
        <table>
          % for tpr in protokollid:
          <tr>
            <td>
              <% tpr_arv = tpr.soorituste_arv %>
              ${tpr.tahis}
              % if tpr.kursus_kood:
              (${tpr.kursus_nimi}, ${tpr_arv})
              % else:
              (${tpr_arv})
              % endif
            </td>
            <td>
              <% aeg = tpr.algus or truum.algus %>
              % if aeg.hour or aeg.minute:
              ${_("kell")} ${h.str_time_from_datetime(aeg)}
              % endif
            </td>
            % if tpr_arv == 0:
            <td>${h.remove(h.url_current('delete', id=tpr.id, sub='tpr', lang=c.lang))}</td>
            % endif
          </tr>
          % endfor
        </table>
        % else:
          % for tpr in protokollid:
              <% tpr_arv = tpr.soorituste_arv %>
              ${tpr.tahis}
              % if tpr.kursus_kood:
              (${tpr.kursus_nimi}, ${tpr_arv})
              % else:
              (${tpr_arv})
              % endif
              % if tpr_arv == 0:
              ${h.remove(h.url_current('delete', id=tpr.id, sub='tpr', lang=c.lang))}
              % endif
          % endfor
        % endif
        ${h.add(h.url_current('create', pakett_id=pakett.id,
           testiruum_id=truum.id, sub='tpr', lang=c.lang))}
      </td>
      <td>
        % if on_sisse:
        ${h.str_from_date(truum.algus)}
        % else:
        ${h.str_from_datetime(truum.algus, hour0=False)}
        % endif
        % if on_sisse or oma_kavaaeg:
        ${h.btn_to_dlg(_("Muuda kellaaeg..."), h.url('korraldamine_koht_edit_protokollruum',
        toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht_id, pakett_id=pakett.id, id=truum.id),
        id="muuda_kellaaeg_%s" % truum.id,
        title="%s, %s" % (_("Protokollirühmad"), _("ruum {s}").format(s=truum.tahis)), width=500, level=2, mdicls="mdi-av-timer", class_="ml-2")}
        % endif
      </td>
    </tr>
% endfor
</%def>

<%def name="otsingufilter()">
<div class="gray-legend p-2 mr-0 filter-w">

  <div class="row">
    % if c.testikoht:
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.testiruum_id)}">
      <div class="form-group">
        ${h.flb(_("Testiruum"),'testiruum_id')}
        ${h.select('testiruum_id', c.testiruum_id, c.opt_testiruum, empty=True)}
      </div>         
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.ruum_id)}">
      <div class="form-group">    
        ${h.flb(_("Ruum"),'ruum_id')}
        ${h.select('ruum_id', c.ruum_id, c.opt_ruum, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.tprotokoll_id)}">
      <div class="form-group">        
        ${h.flb(_("Grupp"),'tprotokoll_id')}
        ${h.select('tprotokoll_id', c.tprotokoll_id, c.opt_tprotokoll, empty=True)}
      </div>
    </div>
    % endif
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.koolinimi_id)}">
      <div class="form-group">        
        ${h.flb(_("Õppeasutus"),'koolinimi_id')}
        ${h.select('koolinimi_id', c.koolinimi_id, c.opt_koolinimi, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.klass)}">
      <div class="form-group">        
        ${h.flb(_("Klass"),'klass')}
        ${h.select('klass', c.klass, c.opt_klass, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.paralleel)}">
      <div class="form-group">        
        ${h.flb(_("Paralleel"),'paralleel')}
        ${h.select('paralleel', c.paralleel, c.opt_paralleel, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.lang)}">
      <div class="form-group">        
        ${h.flb(_("Soorituskeel"),'lang')}
        ${h.select('lang', c.lang, c.opt_soorituskeel, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.piirkond_id)}">
      <div class="form-group">        
        ${h.flb(_("Soovitud piirkond"),'piirkond_id')}
        ${h.select('piirkond_id', c.piirkond_id, c.opt_piirkond, id="piirkond_id1", empty=True)}
      </div>
    </div>
    % if c.testikoht:
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.kuupaev)}">
      <div class="form-group">        
        ${h.flb(_("Kuupäev"),'kuupaev')}
        ${h.select('kuupaev', c.kuupaev, c.opt_kuupaev, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.aeg)}">
      <div class="form-group">        
        ${h.flb(_("Aeg"),'aeg')}
        ${h.select('aeg', c.aeg, c.opt_aeg, empty=True)}
      </div>
    </div>
    % else:
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.staatus)}">
      <div class="form-group">        
        ${h.flb(_("Olek"),'staatus')}
        ${h.select('staatus', c.staatus, c.opt_staatus, empty=True)}
      </div>
    </div>
    % endif

    % if c.testikoht and c.testiosa.oma_kavaaeg:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">          
        ${h.checkbox1('ttabel', 1, checked=c.ttabel, label=_("Kuva kellaaegade tabelina"))}
        <script>
          $('#ttabel').click(function(){ $('button.searchb#otsi').show(); });
        </script>
        <br/>
        ${_("Intervall")} ${h.posint5('intervall', c.intervall or 20)} ${_("minutit")}
      </div>
    </div>
    % endif
    <div class="col d-flex justify-content-end align-items-end">
        ${h.toggle_filter(False)}
        ${h.btn_search()}
        ${h.button(_("Tühjenda"), onclick="$('form#form_search select').val('')", class_="searchb", level=2)}
    </div>
  </div>
</div>

</%def>
