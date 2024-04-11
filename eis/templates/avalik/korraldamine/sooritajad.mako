<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Testi korraldamine")} | ${c.testimiskord.test.nimi} ${h.str_from_date(c.toimumisaeg.alates)}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Testi läbiviimise korraldamine"), h.url('korraldamised'))} 
${h.crumb('%s %s' % (c.testimiskord.test.nimi, c.toimumisaeg.tahised))}
${h.crumb(_("Ruumid ja sooritajad"), h.url('korraldamine_sooritajad', testikoht_id=c.testikoht.id))}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

<%def name="draw_before_tabs()">
<h1>${_("Testi läbiviimise korraldamine")}</h1>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'sooritajad' %>
<%include file="tabs.mako"/>
</%def>

<div class="border border-base-radius p-3 mb-1">
  <%include file="testiruumid_list.mako"/>

  <div class="d-flex flex-wrap">
    <div class="flex-grow-1">
  % if c.toimumisaeg.ruumide_jaotus:
      ${h.btn_to_dlg(_("Vali ruumid..."), h.url('korraldamine_sooritajad',
      testikoht_id=c.testikoht.id, sub='ruumid'),
      title=_("Ruumide valik"),width=700, size='lg', level=2)}
  % endif

  ${h.blink_to(_("Püsiruumide haldus"), h.url('admin_koht_ruumid',
  koht_id=c.testikoht.koht_id), target='_blank', level=2)}
    </div>
    ${h.btn_to(_("Väljasta CSV"), h.url_current('index', csv=1, csvr=1), id='csv', level=2)}
  </div>
</div>

<%
   c.test = c.testimiskord.test
   paketid = c.testikoht.testipaketid_sorted
   opt_kursused = c.test.opt_kursused or [(None, None)]
   c.tk_keeled = c.testimiskord.keeled
%>
${h.form_search(url=h.url('korraldamine_sooritajad', testikoht_id=c.testikoht.id))}
<div class="form-wrapper pl-3 pt-3 pb-0">
  <div class="form-group row">
    <div class="col-md-4">
      ${_("Testisooritajate arv kokku")}
      <span class="brown">${c.testikoht.get_sooritajatearv()}</span>
    </div>
  % for pakett in paketid:
  % for o_kursus in opt_kursused:
  <%
     lang = pakett.lang
     kursus = o_kursus[0]
     kursus_nimi = o_kursus[1]
  %>
    <div class="col-md-4">
      ${model.Klrida.get_lang_nimi(lang)}
      ${kursus_nimi or ''}
      <span class=" brown">${c.testikoht.get_sooritajatearv(lang, kursus)}</span>
    </div>
  % endfor
  % endfor
  </div>
  <div class="form-group row">
    <div class="col-md-4">
      <label class="font-weight-bold mr-2">${_("Märkused")}</label>
      ${h.btn_to_dlg(_("Sisesta..."), h.url('korraldamine_sooritajad',
      testikoht_id=c.testikoht.id, sub='markus'),
      title=_("Märkus"),width=500, level=2, mdicls="mdi-file-edit")}
    </div>
    <div class="col">
      ${c.testikoht.markus}
    </div>
  </div>
</div>

${self.otsingufilter()}

${h.end_form()}

${h.form_save(None, h.url('korraldamine_sooritajad',testikoht_id=c.testikoht.id))}
${h.hidden('testiruum_id', '')}
${h.hidden('tpr_id', '')}

% if c.is_edit:
<% koht = c.testikoht.koht %>
<h6 class="mb-1">
  ${_("Aineõpetajad")}: ${koht.nimi}, ${_("õppeaine")} "${c.test.aine_nimi}"
  <span class="helpable" id="aineopetajad"> </span>
</h6>
<div class="d-flex flex-wrap p-3">
  % for r in c.testikoht.koht.get_aineopetajad(c.test.aine_kood):
  ${h.checkbox('opetaja_id', r.id, label=r.nimi)}
  % endfor

  <div class="flex-grow-1 text-right">
    ${h.btn_to_dlg(_("Lisa aineõpetaja"), h.url('korraldamine_new_aineopetaja',
    testikoht_id=c.testikoht.id, sub='roll'), title=_("Uus aineõpetaja"), width=600,
    level=2, mdicls="mdi-plus")}
  </div>
</div>
% endif

<div class="listdiv" id="sj_listdiv" style="max-height:800px;overflow:auto;">
<%include file="sooritajad_list.mako"/>
</div>
<div id="sj_cnt" class="invisible">
  ${_("Valitud {s} sooritajat").format(s='<span class="sj_cnt"></span>')}
</div>

<div class="py-2 d-flex flex-wrap">
  <div class="flex-grow-1">
    % if not c.items and not c.toimumisaeg.kohad_kinnitatud and c.user.has_permission('avalikadmin', const.BT_DELETE, c.testikoht):
    % if not model.Session.query(model.Sooritus.id).filter_by(testikoht_id=c.testikoht.id).first():
    ${h.btn_remove(h.url('delete_korraldamine', id=c.testikoht.id), value=_("Eemalda soorituskoht"), confirm_id="conf_del")}
    <span style="display:none" id="conf_del">
      ${_("Kas oled kindel, et siin koolis seda testi ei korraldata?")}
    </span>
    % endif
    % endif
    
    % if c.toimumisaeg.ruumide_jaotus:
    ${h.submit(_("Jaga uuesti protokollirühmadesse"), id='proto')}
    ${h.submit(_("Suuna valitud ruumi"), id='addr')}
    ${h.submit(_("Suuna valitud protokollirühma"), id='addp')}
    % endif

    ${h.submit(_("Märgi valitud aineõpetajad"), id='addo')}
    ${h.submit(_("Eemalda aineõpetaja"), id='unseto')}
    % if c.reg_kool_avatud and len(c.tk_keeled) > 1:
    ${h.btn_to_dlg(_("Muuda soorituskeel"), h.url('korraldamine_sooritajad',
    testikoht_id=c.testikoht.id, sub='keeled'),
    title=_("Muuda soorituskeel"), width=400, class_="chgl", form="$('form#form_save')")}
    % endif

    % if c.testikoht.testiosa.oma_kavaaeg:
    ## suulise testi korral saab salvestada kellaajad
    ${h.submit(_("Salvesta kellaajad"))}
    % endif
    ${h.button(_("Testiparoolid"), class_='setpwd', onclick="gen_pwd()")}
  </div>
  <div class="text-right">
  % if c.toimumisaeg.ruumide_jaotus:
    <% testimiskord = c.toimumisaeg.testimiskord %>
    % if len(testimiskord.toimumisajad) > 1:
      ${h.btn_to_dlg(_("Kopeeri korraldus"),
        h.url_current('index', sub='kopeeri'),
        title=_("Vali toimumisaeg, mille andmed kopeerida"), level=2)}
    % endif
  % endif
  % if c.items:  
    ${h.btn_to(_("Väljasta CSV"), h.url_current('index', getargs=True, csv=True), level=2)}
  % endif
  </div>
</div>
${h.end_form()}

<script>
  function gen_pwd()
  {
    var data = 'sub=parool';
    $.each($('#form_save input:checked[name="sooritus_id"]'), function(n, elem){
      data += '&sooritus_id=' + elem.value;
    });
    var title = "${_("Testiparoolid")}";
    open_dialog({'title': title, 'url': "${h.url_current('new')}", params: data});
  }      
  function toggle_add()
  {
     var selected = $('#form_save input:checked[name="sooritus_id"]'),
         cnt = selected.length,
         any_selected = cnt > 0,
         any_opetajaga = selected.filter('.opetajaga').length > 0;
     $('#sj_cnt').toggleClass('invisible', !any_selected);
     $('#sj_cnt .sj_cnt').text(cnt);
     $('#addr').toggle(any_selected && ($('#form_save #testiruum_id').val() != ''));
     $('#addp').toggle(any_selected && ($('#form_save #tpr_id').val() != ''));
     $('#addo').toggle(any_selected && ($('input[name="opetaja_id"]:checked').length > 0));
     ## õpetaja eemaldamise nupp on siis, kui õpetajaga õpilasi on valitud, aga õpetajaid pole valitud
     $('#unseto').toggle(any_opetajaga && ($('input[name="opetaja_id"]:checked').length == 0));
     $('.chgl,.setpwd').toggle(any_selected);
  }
  $(function(){
    dirty = false;
    toggle_add();
    $('input[name="opetaja_id"]').change(toggle_add);
    $('input#alls').click(function(){
       $('input.sooritus_id').prop('checked', this.checked); toggle_add();
    });
  });
</script>

% if c.dialog_ruumid:
  ${self.open_dialog('ruumid', '/avalik/korraldamine/sooritajad.ruumid.mako', _("Vali ruumid..."), 'lg')}
% endif

% if c.dialog_markus:
  ${self.open_dialog('markus', '/avalik/korraldamine/sooritajad.markus.mako', _("Märkus"))}
% endif


<%def name="otsingufilter()">
<% any_filter = False %>
<div class="gray-legend p-3 mb-1 filter-w">
  <div class="row">
    % if len(c.opt_ruum) > 1:
    <% any_filter = True %>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.ruum_id)}">
      <div class="form-group">    
        ${h.flb(_("Ruum"),'ruum_id')}
        ${h.select('ruum_id', c.ruum_id, c.opt_ruum, empty=True)}
      </div>
    </div>
    % endif
    % if len(c.opt_aeg) > 1:
    <% any_filter = True %>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.aeg)}">
      <div class="form-group">        
        ${h.flb(_("Aeg"),'aeg')}
        ${h.select('aeg', c.aeg, c.opt_aeg, empty=True)}
      </div>
    </div>
    % endif
    % if len(c.opt_koolinimi) > 1:
    <% any_filter = True %>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.koolinimi_id)}">
      <div class="form-group">        
        ${h.flb(_("Õppeasutus"),'koolinimi_id')}
        ${h.select('koolinimi_id', c.koolinimi_id, c.opt_koolinimi, empty=True)}
      </div>
    </div>
    % endif
    % if len(c.opt_klass) > 1:
    <% any_filter = True %>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.klass)}">
      <div class="form-group">        
        ${h.flb(_("Klass"),'klass')}
        ${h.select('klass', c.klass, c.opt_klass, empty=True)}
      </div>
    </div>
    % endif
    % if len(c.opt_paralleel) > 1:
    <% any_filter = True %>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.paralleel)}">
      <div class="form-group">        
        ${h.flb(_("Paralleel"),'paralleel')}
        ${h.select('paralleel', c.paralleel, c.opt_paralleel, empty=True)}
      </div>
    </div>
    % endif
    % if len(c.opt_opetaja) > 1:
    <% any_filter = True %>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.opetaja_id)}">
      <div class="form-group">        
        ${h.flb(_("Aineõpetaja"),'opetaja_id')}
        ${h.select('opetaja_id', c.opetaja_id, c.opt_opetaja, empty=True)}
      </div>
    </div>
    % endif
    % if len(c.opt_soorituskeel) > 1:
    <% any_filter = True %>
    <div class="col-12 col-md-4 col-lg-3 ${h.hidefilter(c.lang)}">
      <div class="form-group">        
        ${h.flb(_("Soorituskeel"),'lang')}
        ${h.select('lang', c.lang, c.opt_soorituskeel, empty=True)}
      </div>
    </div>
    % endif
    % if any_filter:
    <div class="col d-flex justify-content-end align-items-end">
      <div class="d-flex flex-wrap">
        ${h.toggle_filter(False)}
        <div class="${h.hidefilter(None)} ml-1">
          ${h.checkbox('filopen', 1, checked=c.filopen, label=_("Jäta filter lahti"))}
        </div>
      </div>
      ${h.btn_search()}
      ${h.button(_("Tühjenda"), onclick="$('form#form_search select').val('')", class_="searchb", level=2)}
    </div>
    % endif
  </div>
</div>
</%def>
